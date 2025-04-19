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

    def _ensure_dirs_exist(self):
        """Asegura que los directorios necesarios existan."""
        self.temp_dir.mkdir(exist_ok=True)
        self.report_dir.mkdir(exist_ok=True)

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
            # Si no se especifican columnas clave, usar cvlac_id más otras claves candidatas
            if key_columns is None:
                # Intentar obtener información de las claves primarias
                key_columns = self._get_primary_key_columns(table)
                # Si no se puede, usar solo cvlac_id como clave
                if not key_columns or len(key_columns) == 0:
                    key_columns = ["cvlac_id"]

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
            query = f"SELECT * FROM {table} WHERE {' AND '.join(conditions)}"

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
                        update_query = f"UPDATE {table} SET {', '.join([f'{col} = %s' for col in update_columns])} WHERE {' AND '.join(where_conditions)}"
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
                insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

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
