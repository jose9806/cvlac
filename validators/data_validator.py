"""
Módulo para validación de datos y manejo de duplicados.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from config import ProjectLogger

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class DataValidator:
    """
    Clase para validar datos, evitar duplicados y generar reportes.
    """

    def __init__(self, db_connection):
        """
        Inicializa el validador de datos.

        Args:
            db_connection: Instancia de la clase DatabaseConnection.
        """
        self.db = db_connection
        self.temp_dir = Path("temp")
        self.report_dir = self.temp_dir / "reports"
        self._ensure_dirs_exist()

        # Estadísticas de la extracción actual
        self.extraction_stats = {
            "started_at": datetime.now().isoformat(),
            "cvlacs_processed": 0,
            "tables": {},
            "errors": [],
        }

        # Validar el esquema de la base de datos al inicializar
        try:
            self.validate_database_schema(
                ["eventos_cientificos", "proyectos", "identificacion"]
            )
        except Exception as e:
            module_logger.error(f"Error validando esquema de base de datos: {str(e)}")

    def _ensure_dirs_exist(self):
        """Asegura que los directorios necesarios existan."""
        self.temp_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)

    def validate_database_schema(self, tables_to_check=None):
        """
        Valida que las tablas y columnas necesarias existan en la base de datos.

        Args:
            tables_to_check (list): Lista de tablas a verificar. Si es None, verifica todas.

        Returns:
            dict: Reporte de estado de las tablas y columnas.
        """
        report = {
            "tables_checked": 0,
            "tables_missing": 0,
            "tables_with_issues": 0,
            "details": {},
        }

        try:
            with self.db.get_connection_context() as connection:
                cursor = connection.cursor()

                # Obtener lista de tablas a verificar
                if tables_to_check is None:
                    cursor.execute(
                        """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """
                    )
                    tables_to_check = [row[0] for row in cursor.fetchall()]

                for table in tables_to_check:
                    report["tables_checked"] += 1
                    report["details"][table] = {
                        "exists": False,
                        "columns": {},
                        "issues": [],
                    }

                    # Verificar si la tabla existe
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """,
                        (table,),
                    )

                    table_exists = cursor.fetchone()[0]
                    report["details"][table]["exists"] = table_exists

                    if not table_exists:
                        report["tables_missing"] += 1
                        report["details"][table]["issues"].append(
                            "Table does not exist"
                        )
                        continue

                    # Verificar columnas
                    cursor.execute(
                        """
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    """,
                        (table,),
                    )

                    columns = {row[0]: row[1] for row in cursor.fetchall()}
                    report["details"][table]["columns"] = columns

                    # Verificar si existe la columna cvlac_id
                    if "cvlac_id" not in columns:
                        report["tables_with_issues"] += 1
                        report["details"][table]["issues"].append(
                            "Missing 'cvlac_id' column"
                        )

                # Mostrar informe en el log
                for table, info in report["details"].items():
                    if info["exists"]:
                        if len(info["issues"]) > 0:
                            module_logger.warning(
                                f"Tabla '{table}' existe pero tiene problemas: {', '.join(info['issues'])}"
                            )
                            module_logger.warning(
                                f"Columnas en '{table}': {list(info['columns'].keys())}"
                            )
                        else:
                            module_logger.info(
                                f"Tabla '{table}' verificada correctamente"
                            )
                    else:
                        module_logger.error(
                            f"Tabla '{table}' no existe en la base de datos"
                        )

                return report

        except Exception as e:
            module_logger.error(
                f"Error validando esquema de la base de datos: {str(e)}"
            )
            report["error"] = str(e)
            return report

    def check_column_exists(self, table, column):
        """
        Verifica si una columna existe en una tabla.

        Args:
            table (str): Nombre de la tabla.
            column (str): Nombre de la columna.

        Returns:
            bool: True si la columna existe, False en caso contrario.
        """
        try:
            with self.db.get_connection_context() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = %s 
                        AND column_name = %s
                    )
                """,
                    (table, column),
                )

                return cursor.fetchone()[0]
        except Exception as e:
            module_logger.error(
                f"Error verificando columna {column} en {table}: {str(e)}"
            )
            return False

    def check_duplicate(self, table, data, key_columns=None):
        """
        Verifica si un registro ya existe en la base de datos.

        Args:
            table (str): Nombre de la tabla.
            data (dict): Datos a verificar.
            key_columns (list, optional): Columnas que definen la unicidad.
                                          Si es None, se usa cvlac_id más las claves primarias.

        Returns:
            tuple: (bool, dict) - (Es duplicado, Registro existente si lo hay)
        """
        try:
            # Verificar primero si la columna cvlac_id existe en la tabla
            if "cvlac_id" in data and not self.check_column_exists(table, "cvlac_id"):
                module_logger.warning(
                    f"La columna 'cvlac_id' no existe en la tabla {table}. Verificar si el esquema es correcto."
                )
                return False, None

            # Si no se especifican columnas clave, usar cvlac_id más otras claves candidatas
            if key_columns is None:
                # Intentar obtener información de las claves primarias
                key_columns = self._get_primary_key_columns(table)
                # Si no se puede, usar solo cvlac_id como clave
                if not key_columns or len(key_columns) == 0:
                    key_columns = ["cvlac_id"]

            # Verificar que las columnas clave existan en la tabla
            for col in key_columns[:]:
                if not self.check_column_exists(table, col):
                    module_logger.warning(
                        f"La columna '{col}' no existe en la tabla {table}. Omitiendo esta columna."
                    )
                    key_columns.remove(col)

            # Si no quedan columnas válidas, no podemos verificar duplicados
            if not key_columns:
                module_logger.warning(
                    f"No se encontraron columnas válidas para verificar duplicados en {table}"
                )
                return False, None

            # Construir la consulta
            conditions = []
            query_params = {}

            for col in key_columns:
                if col in data and data[col] is not None:
                    conditions.append(f"{col} = %({col})s")
                    query_params[col] = data[col]

            # Si no hay condiciones, no podemos verificar duplicados
            if not conditions:
                return False, None

            # Construir la consulta SQL
            query = f"SELECT * FROM public.{table} WHERE {' AND '.join(conditions)}"

            # Ejecutar la consulta
            with self.db.get_connection_context() as connection:
                cursor = connection.cursor()
                cursor.execute(query, query_params)
                result = cursor.fetchone()

                if result:
                    # Obtener los nombres de las columnas
                    columns = [desc[0] for desc in cursor.description]
                    existing_record = dict(zip(columns, result))
                    return True, existing_record

                return False, None

        except Exception as e:
            module_logger.error(f"Error verificando duplicados en {table}: {str(e)}")
            return False, None

    def _get_primary_key_columns(self, table):
        """
        Obtiene las columnas de clave primaria de una tabla.

        Args:
            table (str): Nombre de la tabla.

        Returns:
            list: Lista de nombres de columnas de clave primaria.
        """
        try:
            query = """
            SELECT a.attname
            FROM pg_constraint c
            JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
            WHERE c.contype = 'p' AND c.conrelid = %s::regclass
            """

            with self.db.get_connection_context() as connection:
                cursor = connection.cursor()
                cursor.execute(query, (table,))
                result = cursor.fetchall()

                if result:
                    return [row[0] for row in result]
                else:
                    return ["cvlac_id"]  # Default si no se encuentra clave primaria

        except Exception as e:
            module_logger.error(
                f"Error obteniendo claves primarias de {table}: {str(e)}"
            )
            return ["cvlac_id"]  # Default en caso de error

    def record_operation(
        self, table, operation, data=None, existing_record=None, error=None
    ):
        """
        Registra una operación para el reporte.

        Args:
            table (str): Nombre de la tabla.
            operation (str): Tipo de operación ('insert', 'update', 'skip', 'error').
            data (dict, optional): Datos que se intentaron insertar/actualizar.
            existing_record (dict, optional): Registro existente en caso de duplicado.
            error (str, optional): Mensaje de error si ocurrió alguno.
        """
        # Inicializar estadísticas para la tabla si no existen
        if table not in self.extraction_stats["tables"]:
            self.extraction_stats["tables"][table] = {
                "inserts": 0,
                "updates": 0,
                "skips": 0,
                "errors": 0,
            }

        # Actualizar estadísticas
        if operation in ["insert", "update", "skip", "error"]:
            self.extraction_stats["tables"][table][operation + "s"] += 1

        # Registrar errores detallados
        if error:
            self.extraction_stats["errors"].append(
                {
                    "table": table,
                    "operation": operation,
                    "error": str(error),
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def insert_or_update(
        self, table, data, connection, update_if_exists=True, key_columns=None
    ):
        """
        Inserta o actualiza un registro evitando duplicados.

        Args:
            table (str): Nombre de la tabla.
            data (dict): Datos a insertar o actualizar.
            connection: Conexión a la base de datos.
            update_if_exists (bool): Si es True, actualiza registros existentes.
            key_columns (list, optional): Columnas que definen la unicidad.

        Returns:
            tuple: (operación realizada, error si ocurrió)
        """
        try:
            # Verificar primero que las columnas existan en la tabla
            for column in list(data.keys()):
                if not self.check_column_exists(table, column):
                    module_logger.warning(
                        f"La columna '{column}' no existe en la tabla {table}. Eliminando del conjunto de datos."
                    )
                    del data[column]

            # Si no quedan datos después de la verificación, no podemos hacer nada
            if not data:
                error_msg = f"No hay columnas válidas para insertar en {table}"
                module_logger.error(error_msg)
                self.record_operation(table, "error", data=None, error=error_msg)
                return "error", error_msg

            # Verificar si el registro ya existe
            is_duplicate, existing_record = self.check_duplicate(
                table, data, key_columns
            )

            if is_duplicate:
                if update_if_exists:
                    # Actualizar el registro existente
                    update_columns = []
                    update_values = []

                    # Identificar columnas a actualizar (excluyendo claves)
                    primary_keys = key_columns or self._get_primary_key_columns(table)
                    for column, value in data.items():
                        if column not in primary_keys and value is not None:
                            update_columns.append(column)
                            update_values.append(value)

                    # Construir condición WHERE basada en claves primarias
                    where_conditions = []
                    where_values = []
                    for key in primary_keys:
                        if key in data and data[key] is not None:
                            where_conditions.append(f"{key} = %s")
                            where_values.append(data[key])

                    # Ejecutar actualización si hay columnas para actualizar
                    if update_columns and where_conditions:
                        update_query = f"UPDATE public.{table} SET {', '.join([f'{col} = %s' for col in update_columns])} WHERE {' AND '.join(where_conditions)}"
                        cursor = connection.cursor()
                        cursor.execute(update_query, update_values + where_values)
                        connection.commit()
                        self.record_operation(table, "update", data, existing_record)
                        return "update", None
                    else:
                        self.record_operation(table, "skip", data, existing_record)
                        return "skip", None
                else:
                    # Omitir inserción
                    self.record_operation(table, "skip", data, existing_record)
                    return "skip", None
            else:
                # Insertar nuevo registro
                columns = list(data.keys())
                values = list(data.values())

                placeholders = ", ".join(["%s"] * len(values))
                insert_query = f"INSERT INTO public.{table} ({', '.join(columns)}) VALUES ({placeholders})"

                cursor = connection.cursor()
                cursor.execute(insert_query, values)
                connection.commit()
                self.record_operation(table, "insert", data)
                return "insert", None

        except Exception as e:
            connection.rollback()
            error_msg = f"Error en insert_or_update para {table}: {str(e)}"
            module_logger.error(error_msg, exc_info=True)
            self.record_operation(table, "error", data, error=str(e))
            return "error", error_msg

    def finish_extraction(self, cod_rh=None):
        """
        Finaliza la extracción y genera un reporte.

        Args:
            cod_rh (str, optional): Código del investigador específico.

        Returns:
            str: Ruta al archivo de reporte generado.
        """
        # Completar estadísticas
        self.extraction_stats["ended_at"] = datetime.now().isoformat()
        self.extraction_stats["cvlacs_processed"] += 1

        # Crear nombre de archivo para el reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_suffix = f"_{cod_rh}" if cod_rh else ""
        report_file = (
            self.report_dir / f"extraction_report{filename_suffix}_{timestamp}.json"
        )

        # Guardar reporte en formato JSON
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.extraction_stats, f, indent=2, ensure_ascii=False)

        # Crear reporte CSV para estadísticas por tabla
        csv_file = self.report_dir / f"table_stats{filename_suffix}_{timestamp}.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Tabla", "Inserciones", "Actualizaciones", "Omitidos", "Errores"]
            )

            for table, stats in self.extraction_stats["tables"].items():
                writer.writerow(
                    [
                        table,
                        stats["inserts"],
                        stats["updates"],
                        stats["skips"],
                        stats["errors"],
                    ]
                )

        # Crear reporte de errores si hay alguno
        if self.extraction_stats["errors"]:
            error_file = self.report_dir / f"errors{filename_suffix}_{timestamp}.json"
            with open(error_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.extraction_stats["errors"], f, indent=2, ensure_ascii=False
                )

        module_logger.info(f"Reporte de extracción generado: {report_file}")
        return str(report_file)

    def start_new_extraction(self):
        """Inicia una nueva extracción, reiniciando las estadísticas."""
        self.extraction_stats = {
            "started_at": datetime.now().isoformat(),
            "cvlacs_processed": 0,
            "tables": {},
            "errors": [],
        }
        return self.extraction_stats
