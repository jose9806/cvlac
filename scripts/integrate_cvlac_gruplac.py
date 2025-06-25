#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de integración desde CvLAC hacia GrupLAC.

Este script permite enriquecer la base de datos de GrupLAC con información
proveniente de CvLAC, identificando relaciones entre investigadores y grupos
de investigación, y transfiriendo información relevante entre ambas fuentes
mientras se evitan duplicados.
"""
import sys
import json
import datetime
import argparse
import psycopg2
from psycopg2.extras import DictCursor
import logging
from pathlib import Path
import hashlib
import uuid

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/integration_cvlac_to_gruplac.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("cvlac_to_gruplac_integrator")


class DatabaseConnection:
    """Clase para manejar conexiones a la base de datos."""

    def __init__(self, db_config, name=""):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_config (dict): Configuración de la base de datos.
            name (str): Nombre descriptivo de la conexión.
        """
        self.db_config = db_config
        self.name = name or db_config.get("database", "unknown")
        self.conn = None

    def connect(self):
        """Establece una conexión a la base de datos."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info(f"Conexión establecida con éxito a {self.name}")
            return self.conn
        except Exception as e:
            logger.error(f"Error conectando a la base de datos {self.name}: {str(e)}")
            raise

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            logger.info(f"Conexión cerrada a {self.name}")

    def execute_query(self, query, params=None, fetch=True):
        """
        Ejecuta una consulta en la base de datos.

        Args:
            query (str): Consulta SQL a ejecutar.
            params (tuple, dict, optional): Parámetros para la consulta.
            fetch (bool): Si se deben recuperar resultados.

        Returns:
            list: Resultados de la consulta o None.
        """
        cursor = self.conn.cursor(cursor_factory=DictCursor)
        try:
            cursor.execute(query, params)

            if fetch:
                results = cursor.fetchall()
                return results
            else:
                self.conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error ejecutando query en {self.name}: {str(e)}")
            logger.error(f"Query: {query}")
            if params:
                logger.error(f"Params: {params}")
            raise
        finally:
            cursor.close()


class CvLACToGrupLACIntegrator:
    """Herramienta para integrar datos desde CvLAC hacia GrupLAC."""

    def __init__(self, cvlac_config, gruplac_config):
        """
        Inicializa la herramienta de integración.

        Args:
            cvlac_config (dict): Configuración de la base de datos CvLAC.
            gruplac_config (dict): Configuración de la base de datos GrupLAC.
        """
        self.cvlac_db = DatabaseConnection(cvlac_config, "cvlac_db")
        self.gruplac_db = DatabaseConnection(gruplac_config, "scrap_db")
        self.backup_dir = Path("backups")
        self.reports_dir = Path("reports")

        # Crear directorios si no existen
        self.backup_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Estadísticas de integración
        self.stats = {
            "started_at": datetime.datetime.now().isoformat(),
            "tables": {},
            "researcher_stats": {
                "total_processed": 0,
                "total_associated": 0,
                "total_skipped": 0,
            },
            "process_id": str(uuid.uuid4()),  # ID único para esta ejecución
        }

        # Mapa de investigadores a grupos (se llenará durante la ejecución)
        self.researcher_to_groups = {}

        # Mapeo entre tablas de CvLAC y GrupLAC
        self.table_mapping = {
            # Mapeo desde artículos en CvLAC a artículos_publicados en GrupLAC
            "articulos": {
                "target_table": "articulos_publicados",
                "field_mapping": {
                    "titulo": "titulo",
                    "ano": "ano",
                    "revista": "revista",
                    "issn": "issn",
                    "volumen": "volumen",
                    "fasciculo": "fasciculo",
                    "coautores": "autores",
                    "doi": "doi",
                    "pais": "pais",
                    "pagina_inicial": "paginas",  # Nota: solo mapeo parcial, se procesará
                },
                "key_fields": ["titulo", "ano"],  # Campos para identificar duplicados
                "gruplac_fields": [
                    "nro",
                    "consecutivo",
                    "chulo",
                    "tipo",
                    "titulo",
                    "pais",
                    "revista",
                    "issn",
                    "volumen",
                    "fasciculo",
                    "paginas",
                    "ano",
                    "doi",
                    "autores",
                ],
                "special_processing": self._process_articulos,
            },
            # Mapeo desde libros en CvLAC a libros_publicados en GrupLAC
            "libros": {
                "target_table": "libros_publicados",
                "field_mapping": {
                    "titulo": "titulo",
                    "ano": "ano",
                    "editorial": "editorial",
                    "isbn": "isbn",
                    "volumen": "volumen",
                    "coautores": "autores",
                    "lugar_publicacion": "pais",
                    "paginas": "paginas",
                },
                "key_fields": ["titulo", "ano"],
                "gruplac_fields": [
                    "nro",
                    "consecutivo",
                    "chulo",
                    "tipo",
                    "titulo",
                    "pais",
                    "isbn",
                    "volumen",
                    "paginas",
                    "ano",
                    "editorial",
                    "autores",
                ],
                "special_processing": None,
            },
            # Mapeo desde capitulos_libro en CvLAC a capitulos_libro en GrupLAC
            "capitulos_libro": {
                "target_table": "capitulos_libro",
                "field_mapping": {
                    "titulo_capitulo": "titulo",
                    "libro": "libro",
                    "ano": "ano",
                    "editorial": "editorial",
                    "isbn": "isbn",
                    "coautores": "autores",
                    "lugar_publicacion": "pais",
                    "volumen": "volumen",
                    "pagina_inicial": "paginas",  # Nota: solo mapeo parcial, se procesará
                },
                "key_fields": ["titulo", "libro"],
                "gruplac_fields": [
                    "nro",
                    "consecutivo",
                    "chulo",
                    "tipo",
                    "titulo",
                    "pais",
                    "isbn",
                    "volumen",
                    "paginas",
                    "ano",
                    "libro",
                    "editorial",
                    "autores",
                ],
                "special_processing": self._process_capitulos,
            },
            # Mapeo desde software en CvLAC a softwares en GrupLAC
            "software": {
                "target_table": "softwares",
                "field_mapping": {
                    "nombre": "titulo",
                    "tipo": "tipo",
                    "ano": "ano",
                    "pais": "pais",
                    "coautores": "autores",
                    "nombre_comercial": "nombre_comercial",
                    "contrato_registro": "sitio_web",  # Mapeo aproximado
                },
                "key_fields": ["nombre", "ano"],
                "gruplac_fields": [
                    "nro",
                    "consecutivo",
                    "chulo",
                    "tipo",
                    "titulo",
                    "pais",
                    "ano",
                    "disponibilidad",
                    "sitio_web",
                    "nombre_comercial",
                    "nombre_proyecto",
                    "institucion_financiadora",
                    "autores",
                ],
                "special_processing": self._process_software,
            },
            # Mapeo desde proyectos en CvLAC a proyectos en GrupLAC
            "proyectos": {
                "target_table": "proyectos",
                "field_mapping": {
                    "nombre": "nombre",
                    "tipo": "tipo",
                    "fecha_inicio": "fecha_inicio",
                    "fecha_fin": "fecha_fin",
                },
                "key_fields": ["nombre"],
                "gruplac_fields": [
                    "nro",
                    "consecutivo",
                    "chulo",
                    "tipo",
                    "nombre",
                    "fecha_inicio",
                    "fecha_fin",
                ],
                "special_processing": None,
            },
            # Mapeo desde trabajos_dirigidos en CvLAC a trabajos_dirigidos en GrupLAC
            "trabajos_dirigidos": {
                "target_table": "trabajos_dirigidos",
                "field_mapping": {
                    "nombre": "nombre",
                    "tipo_producto": "tipo",
                    "fecha_inicio": "ano_inicio",
                    "institucion": "institucion",
                    "programa_academico": "programa",
                    "coautores": "autores",
                    "persona_orientada": "estudiante",
                    "tipo_orientacion": "tipo_orientacion",
                },
                "key_fields": ["nombre", "persona_orientada"],
                "gruplac_fields": [
                    "nro",
                    "consecutivo",
                    "chulo",
                    "nombre",
                    "tipo",
                    "ano_inicio",
                    "ano_fin",
                    "tipo_orientacion",
                    "estudiante",
                    "programa",
                    "paginas",
                    "valoracion",
                    "institucion",
                    "autores",
                ],
                "special_processing": self._process_trabajos_dirigidos,
            },
        }

    def _extract_cvlac_id_from_url(self, url):
        """
        Extrae el código CvLAC desde una URL.

        Args:
            url (str): URL de CvLAC.

        Returns:
            str: Código CvLAC extraído o None.
        """
        if not url:
            return None

        try:
            # La URL típica es: https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh=0000123456
            import re

            match = re.search(r"cod_rh=(\d+)", url)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"Error extrayendo código CvLAC de URL {url}: {str(e)}")

        return None

    def backup_data(self, db_conn, table_name):
        """
        Realiza una copia de seguridad de los datos de una tabla.

        Args:
            db_conn (DatabaseConnection): Conexión a la base de datos.
            table_name (str): Nombre de la tabla a respaldar.

        Returns:
            str: Ruta al archivo de respaldo.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            db_name = db_conn.name
            backup_file = self.backup_dir / f"{db_name}_{table_name}_{timestamp}.json"

            # Obtener datos de la tabla
            query = f"SELECT * FROM {table_name}"
            results = db_conn.execute_query(query)

            # Convertir resultados a lista de diccionarios
            data = []
            for row in results:
                item = dict(row)
                # Convertir tipos complejos a strings para serialización JSON
                for k, v in item.items():
                    if isinstance(v, (datetime.date, datetime.datetime)):
                        item[k] = v.isoformat()
                    elif isinstance(v, (bytes, bytearray)):
                        item[k] = str(v)
                data.append(item)

            # Escribir a archivo JSON
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Respaldo de tabla {table_name} guardado en {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Error respaldando tabla {table_name}: {str(e)}")
            raise

    def find_researchers_in_groups(self):
        """
        Identifica relaciones entre investigadores en CvLAC y grupos en GrupLAC.

        Returns:
            dict: Mapa de investigadores (cvlac_id) a grupos (grupo_id).
        """
        try:
            # Conectar a ambas bases de datos
            self.cvlac_db.connect()
            self.gruplac_db.connect()

            # Obtener todos los investigadores de CvLAC
            cvlac_researchers_query = """
            SELECT cvlac_id, nombre_completo FROM identificacion
            """
            cvlac_researchers = self.cvlac_db.execute_query(cvlac_researchers_query)
            logger.info(
                f"Se encontraron {len(cvlac_researchers)} investigadores en CvLAC"
            )

            # Obtener todos los integrantes de grupos de GrupLAC
            gruplac_members_query = """
            SELECT i.nro, i.nombre, i.url_cvlac, g.nombre as nombre_grupo 
            FROM integrantes i
            JOIN datos_basicos g ON i.nro = g.nro
            WHERE i.url_cvlac IS NOT NULL
            """
            gruplac_members = self.gruplac_db.execute_query(gruplac_members_query)
            logger.info(
                f"Se encontraron {len(gruplac_members)} integrantes con URL CvLAC en GrupLAC"
            )

            # Crear mapa de URL CvLAC a investigadores en GrupLAC
            gruplac_cvlac_urls = {}
            for member in gruplac_members:
                cvlac_id = self._extract_cvlac_id_from_url(member["url_cvlac"])
                if cvlac_id:
                    if cvlac_id not in gruplac_cvlac_urls:
                        gruplac_cvlac_urls[cvlac_id] = []

                    gruplac_cvlac_urls[cvlac_id].append(
                        {
                            "grupo_id": member["nro"],
                            "nombre_grupo": member["nombre_grupo"],
                            "nombre_investigador": member["nombre"],
                        }
                    )

            # Asociar investigadores de CvLAC con sus grupos en GrupLAC
            researcher_to_groups = {}
            for researcher in cvlac_researchers:
                cvlac_id = researcher["cvlac_id"]
                self.stats["researcher_stats"]["total_processed"] += 1

                if cvlac_id in gruplac_cvlac_urls:
                    researcher_to_groups[cvlac_id] = gruplac_cvlac_urls[cvlac_id]
                    self.stats["researcher_stats"]["total_associated"] += 1
                else:
                    self.stats["researcher_stats"]["total_skipped"] += 1
                    logger.debug(
                        f"Investigador {cvlac_id} no encontrado en ningún grupo de GrupLAC"
                    )

            self.researcher_to_groups = researcher_to_groups
            logger.info(
                f"Se asociaron {len(researcher_to_groups)} investigadores con grupos de GrupLAC"
            )

            return researcher_to_groups
        except Exception as e:
            logger.error(f"Error encontrando investigadores en grupos: {str(e)}")
            raise
        finally:
            self.cvlac_db.close()
            self.gruplac_db.close()

    def _get_next_consecutivo(self, grupo_id, tabla):
        """
        Obtiene el siguiente número consecutivo para una tabla y grupo específico.

        Args:
            grupo_id (str): ID del grupo de investigación.
            tabla (str): Nombre de la tabla.

        Returns:
            int: Siguiente número consecutivo.
        """
        try:
            query = f"""
            SELECT MAX(consecutivo) as max_consec FROM {tabla}
            WHERE nro = %s
            """

            result = self.gruplac_db.execute_query(query, (grupo_id,))

            if result and result[0]["max_consec"] is not None:
                return result[0]["max_consec"] + 1
            else:
                return 1
        except Exception as e:
            logger.error(
                f"Error obteniendo consecutivo para {tabla}, grupo {grupo_id}: {str(e)}"
            )
            return 1

    def _process_articulos(self, cvlac_data, grupo_id):
        """
        Procesamiento especial para artículos.

        Args:
            cvlac_data (dict): Datos del artículo en CvLAC.
            grupo_id (str): ID del grupo de investigación.

        Returns:
            dict: Datos procesados para GrupLAC.
        """
        processed_data = {}

        # Copiar campos mapeados
        for cvlac_field, gruplac_field in self.table_mapping["articulos"][
            "field_mapping"
        ].items():
            if cvlac_field in cvlac_data and cvlac_data[cvlac_field] is not None:
                processed_data[gruplac_field] = cvlac_data[cvlac_field]

        # Procesar campos especiales
        if "pagina_inicial" in cvlac_data and "pagina_final" in cvlac_data:
            pag_ini = cvlac_data.get("pagina_inicial")
            pag_fin = cvlac_data.get("pagina_final")
            if pag_ini is not None and pag_fin is not None:
                processed_data["paginas"] = f"{pag_ini}-{pag_fin}"
            elif pag_ini is not None:
                processed_data["paginas"] = str(pag_ini)

        # Asignar campos requeridos
        processed_data["nro"] = grupo_id
        processed_data["consecutivo"] = self._get_next_consecutivo(
            grupo_id, "articulos_publicados"
        )
        processed_data["chulo"] = "SI"  # Valor por defecto
        processed_data["tipo"] = cvlac_data.get(
            "tipo", "Artículo en revista especializada"
        )

        return processed_data

    def _process_capitulos(self, cvlac_data, grupo_id):
        """
        Procesamiento especial para capítulos de libro.

        Args:
            cvlac_data (dict): Datos del capítulo en CvLAC.
            grupo_id (str): ID del grupo de investigación.

        Returns:
            dict: Datos procesados para GrupLAC.
        """
        processed_data = {}

        # Copiar campos mapeados
        for cvlac_field, gruplac_field in self.table_mapping["capitulos_libro"][
            "field_mapping"
        ].items():
            if cvlac_field in cvlac_data and cvlac_data[cvlac_field] is not None:
                processed_data[gruplac_field] = cvlac_data[cvlac_field]

        # Procesar campos especiales
        if "pagina_inicial" in cvlac_data and "pagina_final" in cvlac_data:
            pag_ini = cvlac_data.get("pagina_inicial")
            pag_fin = cvlac_data.get("pagina_final")
            if pag_ini is not None and pag_fin is not None:
                processed_data["paginas"] = f"{pag_ini}-{pag_fin}"
            elif pag_ini is not None:
                processed_data["paginas"] = str(pag_ini)

        # Asignar campos requeridos
        processed_data["nro"] = grupo_id
        processed_data["consecutivo"] = self._get_next_consecutivo(
            grupo_id, "capitulos_libro"
        )
        processed_data["chulo"] = "SI"  # Valor por defecto
        processed_data["tipo"] = cvlac_data.get("tipo", "Capítulo de libro")

        return processed_data

    def _process_software(self, cvlac_data, grupo_id):
        """
        Procesamiento especial para software.

        Args:
            cvlac_data (dict): Datos del software en CvLAC.
            grupo_id (str): ID del grupo de investigación.

        Returns:
            dict: Datos procesados para GrupLAC.
        """
        processed_data = {}

        # Copiar campos mapeados
        for cvlac_field, gruplac_field in self.table_mapping["software"][
            "field_mapping"
        ].items():
            if cvlac_field in cvlac_data and cvlac_data[cvlac_field] is not None:
                processed_data[gruplac_field] = cvlac_data[cvlac_field]

        # Asignar campos requeridos
        processed_data["nro"] = grupo_id
        processed_data["consecutivo"] = self._get_next_consecutivo(
            grupo_id, "softwares"
        )
        processed_data["chulo"] = "SI"  # Valor por defecto
        processed_data["disponibilidad"] = cvlac_data.get(
            "disponibilidad", "Disponible"
        )
        processed_data["institucion_financiadora"] = cvlac_data.get(
            "institucion", "No definida"
        )

        # Si no existe nombre_comercial, usar el nombre
        if "nombre_comercial" not in processed_data and "titulo" in processed_data:
            processed_data["nombre_comercial"] = processed_data["titulo"]

        return processed_data

    def _process_trabajos_dirigidos(self, cvlac_data, grupo_id):
        """
        Procesamiento especial para trabajos dirigidos.

        Args:
            cvlac_data (dict): Datos del trabajo dirigido en CvLAC.
            grupo_id (str): ID del grupo de investigación.

        Returns:
            dict: Datos procesados para GrupLAC.
        """
        processed_data = {}

        # Copiar campos mapeados
        for cvlac_field, gruplac_field in self.table_mapping["trabajos_dirigidos"][
            "field_mapping"
        ].items():
            if cvlac_field in cvlac_data and cvlac_data[cvlac_field] is not None:
                processed_data[gruplac_field] = cvlac_data[cvlac_field]

        # Asignar campos requeridos
        processed_data["nro"] = grupo_id
        processed_data["consecutivo"] = self._get_next_consecutivo(
            grupo_id, "trabajos_dirigidos"
        )
        processed_data["chulo"] = "SI"  # Valor por defecto
        processed_data["ano_fin"] = cvlac_data.get("fecha_fin", None)

        return processed_data

    def _generate_item_fingerprint(self, item, key_fields):
        """
        Genera una huella digital única para un registro basada en sus campos clave.

        Args:
            item (dict): Registro a procesar.
            key_fields (list): Lista de campos clave.

        Returns:
            str: Huella digital (hash) del registro.
        """
        # Crear un string con los valores de los campos clave
        values = []
        for field in key_fields:
            if field in item and item[field] is not None:
                values.append(str(item[field]).lower().strip())
            else:
                values.append("")

        # Generar hash
        fingerprint = hashlib.md5("|".join(values).encode("utf-8")).hexdigest()
        return fingerprint

    def _check_existing_record(self, grupo_id, target_table, item, key_fields):
        """
        Verifica si ya existe un registro similar en la tabla objetivo.

        Args:
            grupo_id (str): ID del grupo de investigación.
            target_table (str): Tabla objetivo en GrupLAC.
            item (dict): Datos del registro.
            key_fields (list): Campos clave para identificar duplicados.

        Returns:
            bool: True si existe, False si no.
        """
        if not key_fields:
            return False

        conditions = ["nro = %s"]
        params = [grupo_id]

        for field in key_fields:
            if field in item and item[field] is not None:
                if isinstance(item[field], str):
                    # Para strings, usar ILIKE para comparación insensible a mayúsculas/minúsculas
                    conditions.append(f"UPPER({field}) LIKE UPPER(%s)")
                    params.append(f"%{item[field]}%")
                else:
                    # Para otros tipos de datos, usar igualdad exacta
                    conditions.append(f"{field} = %s")
                    params.append(item[field])

        query = f"""
        SELECT * FROM {target_table} 
        WHERE {" AND ".join(conditions)}
        LIMIT 1
        """

        result = self.gruplac_db.execute_query(query, params)
        return len(result) > 0

    def _insert_record(self, target_table, data, gruplac_fields):
        """
        Inserta un registro en la tabla objetivo.

        Args:
            target_table (str): Tabla objetivo en GrupLAC.
            data (dict): Datos a insertar.
            gruplac_fields (list): Campos disponibles en la tabla GrupLAC.

        Returns:
            int: 1 si se insertó, 0 si no.
        """
        # Filtrar solo los campos que existen en la tabla objetivo
        filtered_data = {k: v for k, v in data.items() if k in gruplac_fields}

        fields = list(filtered_data.keys())
        placeholders = ["%s"] * len(fields)
        values = [filtered_data[field] for field in fields]

        insert_query = f"""
        INSERT INTO {target_table} ({", ".join(fields)})
        VALUES ({", ".join(placeholders)})
        """

        return self.gruplac_db.execute_query(insert_query, values, fetch=False)

    def enrich_gruplac_from_cvlac(self):
        """
        Enriquece GrupLAC con datos de CvLAC.

        Returns:
            dict: Estadísticas del proceso.
        """
        # Inicializar estadísticas
        for mapping in self.table_mapping.values():
            target_table = mapping["target_table"]
            self.stats["tables"][target_table] = {
                "total": 0,
                "inserted": 0,
                "skipped_no_group": 0,
                "skipped_existing": 0,
                "error": 0,
                "details": [],
            }

        try:
            # Conectar a ambas bases de datos
            self.cvlac_db.connect()
            self.gruplac_db.connect()

            # Procesar cada tipo de producción académica
            for source_table, mapping in self.table_mapping.items():
                target_table = mapping["target_table"]
                field_mapping = mapping["field_mapping"]
                key_fields = mapping.get("key_fields", [])
                gruplac_fields = mapping.get("gruplac_fields", [])
                special_processing = mapping.get("special_processing", None)

                logger.info(f"Procesando tabla {source_table} -> {target_table}")

                # Respaldar tabla objetivo antes de modificar
                self.backup_data(self.gruplac_db, target_table)

                # Obtener todos los registros de la tabla fuente
                query = f"SELECT * FROM {source_table}"
                source_records = self.cvlac_db.execute_query(query)

                self.stats["tables"][target_table]["total"] = len(source_records)
                logger.info(
                    f"Se encontraron {len(source_records)} registros en {source_table}"
                )

                # Procesar cada registro
                for record in source_records:
                    try:
                        cvlac_id = record["cvlac_id"]

                        # Verificar si el investigador está asociado a algún grupo
                        if cvlac_id not in self.researcher_to_groups:
                            self.stats["tables"][target_table]["skipped_no_group"] += 1
                            continue

                        # Obtener grupos asociados al investigador
                        groups = self.researcher_to_groups[cvlac_id]

                        # Crear registro básico con campos mapeados
                        record_dict = dict(record)

                        # Para cada grupo asociado, intentar insertar el registro
                        for group in groups:
                            grupo_id = group["grupo_id"]

                            # Aplicar procesamiento especial si existe
                            if special_processing:
                                processed_data = special_processing(
                                    record_dict, grupo_id
                                )
                            else:
                                # Procesamiento estándar
                                processed_data = {}
                                for src_field, dst_field in field_mapping.items():
                                    if (
                                        src_field in record_dict
                                        and record_dict[src_field] is not None
                                    ):
                                        processed_data[dst_field] = record_dict[
                                            src_field
                                        ]

                                # Agregar campos requeridos por GrupLAC
                                processed_data["nro"] = grupo_id
                                processed_data["consecutivo"] = (
                                    self._get_next_consecutivo(grupo_id, target_table)
                                )
                                processed_data["chulo"] = "SI"  # Valor por defecto

                            # Verificar si ya existe un registro similar
                            if self._check_existing_record(
                                grupo_id, target_table, processed_data, key_fields
                            ):
                                self.stats["tables"][target_table][
                                    "skipped_existing"
                                ] += 1
                                continue

                            # Insertar registro
                            inserted = self._insert_record(
                                target_table, processed_data, gruplac_fields
                            )

                            if inserted:
                                self.stats["tables"][target_table]["inserted"] += 1

                                # Registrar detalle de la inserción
                                item_fingerprint = self._generate_item_fingerprint(
                                    processed_data, key_fields
                                )
                                self.stats["tables"][target_table]["details"].append(
                                    {
                                        "grupo_id": grupo_id,
                                        "cvlac_id": cvlac_id,
                                        "item_id": item_fingerprint,
                                        "title": processed_data.get(
                                            "titulo", "Sin título"
                                        ),
                                        "consecutivo": processed_data["consecutivo"],
                                    }
                                )

                    except Exception as e:
                        logger.error(
                            f"Error procesando registro en {source_table}: {str(e)}"
                        )
                        self.stats["tables"][target_table]["error"] += 1

            # Actualizar estadísticas finales
            self.stats["completed_at"] = datetime.datetime.now().isoformat()

            # Guardar informe detallado
            self._save_detailed_report()

            return self.stats

        except Exception as e:
            logger.error(f"Error enriqueciendo GrupLAC desde CvLAC: {str(e)}")
            raise
        finally:
            self.cvlac_db.close()
            self.gruplac_db.close()

    def _save_detailed_report(self):
        """
        Guarda un informe detallado del proceso de integración.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            process_id = self.stats["process_id"]
            report_file = (
                self.reports_dir
                / f"integracion_cvlac_to_gruplac_{timestamp}_{process_id}.json"
            )

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)

            logger.info(f"Informe detallado guardado en {report_file}")

            # Crear un resumen para mostrar en consola
            summary = {
                "process_id": process_id,
                "start_time": self.stats["started_at"],
                "end_time": self.stats["completed_at"],
                "researchers": self.stats["researcher_stats"],
                "tables_summary": {},
            }

            for table, stats in self.stats["tables"].items():
                table_summary = {k: v for k, v in stats.items() if k != "details"}
                summary["tables_summary"][table] = table_summary

            summary_file = self.reports_dir / f"resumen_{timestamp}_{process_id}.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            logger.info(f"Resumen guardado en {summary_file}")

            return str(report_file)
        except Exception as e:
            logger.error(f"Error guardando informe detallado: {str(e)}")
            return None


def load_config(config_file):
    """
    Carga la configuración desde un archivo JSON.

    Args:
        config_file (str): Ruta al archivo de configuración.

    Returns:
        dict: Configuración cargada.
    """
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error cargando configuración desde {config_file}: {str(e)}")
        raise


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Herramienta de integración desde CvLAC hacia GrupLAC"
    )
    parser.add_argument(
        "--config", default="config/integration.json", help="Archivo de configuración"
    )
    parser.add_argument(
        "--backup-only",
        action="store_true",
        help="Solo realizar respaldo sin integración",
    )
    parser.add_argument(
        "--tables", help="Lista de tablas específicas a procesar, separadas por comas"
    )
    args = parser.parse_args()

    try:
        # Asegurar que exista el directorio de logs
        Path("logs").mkdir(exist_ok=True)

        # Cargar configuración
        config = load_config(args.config)
        cvlac_config = config.get("cvlac_db", {})
        gruplac_config = config.get("gruplac_db", {})

        # Inicializar herramienta de integración
        integrator = CvLACToGrupLACIntegrator(cvlac_config, gruplac_config)

        # Si solo se requiere respaldo
        if args.backup_only:
            tables = (
                args.tables.split(",")
                if args.tables
                else config.get("tables_to_backup", [])
            )

            # Conectar a las bases de datos
            integrator.cvlac_db.connect()
            integrator.gruplac_db.connect()

            for table in tables:
                if table.startswith("cvlac:"):
                    table_name = table.replace("cvlac:", "")
                    integrator.backup_data(integrator.cvlac_db, table_name)
                elif table.startswith("gruplac:"):
                    table_name = table.replace("gruplac:", "")
                    integrator.backup_data(integrator.gruplac_db, table_name)
                else:
                    # Por defecto, respaldar de ambas bases si existe la tabla
                    try:
                        integrator.backup_data(integrator.cvlac_db, table)
                    except:
                        pass
                    try:
                        integrator.backup_data(integrator.gruplac_db, table)
                    except:
                        pass

            # Cerrar conexiones
            integrator.cvlac_db.close()
            integrator.gruplac_db.close()
            return

        # Filtrar tablas específicas si se solicita
        if args.tables:
            tables_to_process = args.tables.split(",")
            integrator.table_mapping = {
                k: v
                for k, v in integrator.table_mapping.items()
                if k in tables_to_process or v["target_table"] in tables_to_process
            }

            if not integrator.table_mapping:
                logger.warning(
                    f"No se encontraron tablas válidas para procesar entre: {args.tables}"
                )
                return

        # Encontrar relaciones entre investigadores y grupos
        researcher_to_groups = integrator.find_researchers_in_groups()

        if not researcher_to_groups:
            logger.warning(
                "No se encontraron investigadores asociados a grupos. No hay datos para integrar."
            )
            return

        # Enriquecer GrupLAC con datos de CvLAC
        stats = integrator.enrich_gruplac_from_cvlac()

        # Mostrar resumen en consola
        print("\n===== RESUMEN DE INTEGRACIÓN =====")
        print(f"ID de proceso: {stats['process_id']}")
        print(f"Inicio: {stats['started_at']}")
        print(f"Fin: {stats['completed_at']}")
        print("\nEstadísticas de investigadores:")
        for key, value in stats["researcher_stats"].items():
            print(f"  {key}: {value}")

        print("\nEstadísticas por tabla:")
        for table, table_stats in stats["tables"].items():
            print(f"\n  {table}:")
            for key, value in table_stats.items():
                if key != "details":
                    print(f"    {key}: {value}")

        print("\nInforme detallado guardado en el directorio 'reports'")

    except Exception as e:
        logger.error(f"Error en el proceso de integración: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
