#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de integración entre CvLAC y GrupLAC.

Este script permite sincronizar y enriquecer datos entre las bases de datos
de CvLAC y GrupLAC, identificando relaciones entre investigadores y grupos
de investigación, y transfiriendo información relevante entre ambas fuentes.
"""

import os
import sys
import json
import datetime
import argparse
import psycopg2
from psycopg2.extras import DictCursor
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/integration.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("integrator")


class DatabaseConnection:
    """Clase para manejar conexiones a la base de datos."""

    def __init__(self, db_config):
        """
        Inicializa la conexión a la base de datos.

        Args:
            db_config (dict): Configuración de la base de datos.
        """
        self.db_config = db_config
        self.conn = None

    def connect(self):
        """Establece una conexión a la base de datos."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            logger.info(
                f"Conexión establecida con éxito a {self.db_config['database']}"
            )
            return self.conn
        except Exception as e:
            logger.error(f"Error conectando a la base de datos: {str(e)}")
            raise

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            logger.info(f"Conexión cerrada a {self.db_config['database']}")

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
                return None
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error ejecutando query: {str(e)}")
            logger.error(f"Query: {query}")
            if params:
                logger.error(f"Params: {params}")
            raise
        finally:
            cursor.close()


class IntegrationTool:
    """Herramienta para integrar datos entre CvLAC y GrupLAC."""

    def __init__(self, cvlac_config, gruplac_config):
        """
        Inicializa la herramienta de integración.

        Args:
            cvlac_config (dict): Configuración de la base de datos CvLAC.
            gruplac_config (dict): Configuración de la base de datos GrupLAC.
        """
        self.cvlac_db = DatabaseConnection(cvlac_config)
        self.gruplac_db = DatabaseConnection(gruplac_config)
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

        # Mapeo entre tablas de GrupLAC y CvLAC
        self.table_mapping = {
            "integrantes": {
                "target_table": "identificacion",
                "field_mapping": {
                    "nombre": "nombre_completo",
                    "url_cvlac": "cvlac_url",
                },
                "key_field": "cvlac_id",  # Campo para identificar duplicados
                "extraction_method": self._extract_cvlac_id_from_url,
            },
            "articulos_publicados": {
                "target_table": "articulos",
                "field_mapping": {
                    "titulo": "titulo",
                    "ano": "ano",
                    "revista": "revista",
                    "issn": "issn",
                    "volumen": "volumen",
                    "fasciculo": "fasciculo",
                    "autores": "coautores",
                },
                "key_fields": ["titulo", "ano"],  # Campos para identificar duplicados
            },
            "libros_publicados": {
                "target_table": "libros",
                "field_mapping": {
                    "titulo": "titulo",
                    "ano": "ano",
                    "editorial": "editorial",
                    "isbn": "isbn",
                    "autores": "coautores",
                },
                "key_fields": ["titulo", "ano"],
            },
            "capitulos_libro": {
                "target_table": "capitulos_libro",
                "field_mapping": {
                    "titulo": "titulo_capitulo",
                    "libro": "libro",
                    "ano": "ano",
                    "editorial": "editorial",
                    "autores": "coautores",
                },
                "key_fields": ["titulo_capitulo", "libro"],
            },
            "proyectos": {
                "target_table": "proyectos",
                "field_mapping": {
                    "nombre": "nombre",
                    "tipo": "tipo",
                    "fecha_inicio": "fecha_inicio",
                    "fecha_fin": "fecha_fin",
                },
                "key_fields": ["nombre"],
            },
            "software": {
                "target_table": "software",
                "field_mapping": {
                    "titulo": "nombre",
                    "tipo": "tipo",
                    "ano": "ano",
                    "pais": "pais",
                    "autores": "coautores",
                },
                "key_fields": ["nombre", "ano"],
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

    def backup_data(self, table_name):
        """
        Realiza una copia de seguridad de los datos de una tabla.

        Args:
            table_name (str): Nombre de la tabla a respaldar.

        Returns:
            str: Ruta al archivo de respaldo.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"{table_name}_{timestamp}.json"

            # Obtener datos de la tabla
            conn = self.cvlac_db.connect()
            query = f"SELECT * FROM {table_name}"
            results = self.cvlac_db.execute_query(query)

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
            self.cvlac_db.close()
            return str(backup_file)
        except Exception as e:
            logger.error(f"Error respaldando tabla {table_name}: {str(e)}")
            raise

    def find_researchers_in_groups(self):
        """
        Busca investigadores que están en grupos de investigación.

        Returns:
            dict: Mapa de investigadores a grupos.
        """
        try:
            researcher_to_groups = {}

            # Conectar a GrupLAC
            self.gruplac_db.connect()

            # Obtener todos los integrantes de grupos
            query = """
            SELECT i.nro, i.nombre, i.url_cvlac, 
                   g.nombre as nombre_grupo, g.clasificacion
            FROM integrantes i
            JOIN datos_basicos g ON i.nro = g.nro
            WHERE i.url_cvlac IS NOT NULL
            """

            results = self.gruplac_db.execute_query(query)

            for row in results:
                cvlac_id = self._extract_cvlac_id_from_url(row["url_cvlac"])
                if cvlac_id:
                    if cvlac_id not in researcher_to_groups:
                        researcher_to_groups[cvlac_id] = []

                    researcher_to_groups[cvlac_id].append(
                        {
                            "grupo_id": row["nro"],
                            "nombre_grupo": row["nombre_grupo"],
                            "clasificacion": row["clasificacion"],
                            "nombre_investigador": row["nombre"],
                        }
                    )

            self.gruplac_db.close()
            logger.info(
                f"Se encontraron {len(researcher_to_groups)} investigadores en grupos"
            )
            return researcher_to_groups
        except Exception as e:
            logger.error(f"Error encontrando investigadores en grupos: {str(e)}")
            raise

    def enrich_cvlac_from_gruplac(self, researcher_to_groups):
        """
        Enriquece la base de datos CvLAC con información de GrupLAC.

        Args:
            researcher_to_groups (dict): Mapa de investigadores a grupos.

        Returns:
            dict: Estadísticas del proceso de enriquecimiento.
        """
        try:
            stats = {"processed": 0, "updated": 0, "error": 0, "tables": {}}

            # Conectar a CvLAC
            self.cvlac_db.connect()

            # Crear tabla para relaciones entre investigadores y grupos si no existe
            self._create_relation_table()

            # Actualizar tabla de relaciones
            for cvlac_id, groups in researcher_to_groups.items():
                try:
                    stats["processed"] += 1

                    # Verificar si el investigador existe en CvLAC
                    check_query = (
                        "SELECT cvlac_id FROM identificacion WHERE cvlac_id = %s"
                    )
                    result = self.cvlac_db.execute_query(check_query, (cvlac_id,))

                    if result:
                        # Actualizar relaciones con grupos
                        for group in groups:
                            self._insert_researcher_group_relation(cvlac_id, group)
                        stats["updated"] += 1
                except Exception as e:
                    logger.error(f"Error procesando investigador {cvlac_id}: {str(e)}")
                    stats["error"] += 1

            # Actualizar tablas con datos de GrupLAC
            self._update_tables_from_gruplac(stats)

            self.cvlac_db.close()
            return stats
        except Exception as e:
            logger.error(f"Error enriqueciendo CvLAC desde GrupLAC: {str(e)}")
            raise

    def _create_relation_table(self):
        """Crea la tabla para relaciones entre investigadores y grupos."""
        try:
            # Crear tabla de relaciones si no existe
            create_table_query = """
            CREATE TABLE IF NOT EXISTS investigador_grupo (
                cvlac_id VARCHAR NOT NULL,
                grupo_id VARCHAR NOT NULL,
                nombre_grupo VARCHAR,
                clasificacion VARCHAR,
                nombre_investigador VARCHAR,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (cvlac_id, grupo_id),
                FOREIGN KEY (cvlac_id) REFERENCES identificacion(cvlac_id) ON DELETE CASCADE
            )
            """
            self.cvlac_db.execute_query(create_table_query, fetch=False)
            logger.info("Tabla investigador_grupo creada o verificada")
        except Exception as e:
            logger.error(f"Error creando tabla de relaciones: {str(e)}")
            raise

    def _insert_researcher_group_relation(self, cvlac_id, group):
        """
        Inserta o actualiza una relación entre investigador y grupo.

        Args:
            cvlac_id (str): ID del investigador.
            group (dict): Datos del grupo.
        """
        try:
            # Insertar o actualizar relación
            upsert_query = """
            INSERT INTO investigador_grupo (cvlac_id, grupo_id, nombre_grupo, clasificacion, nombre_investigador)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (cvlac_id, grupo_id) 
            DO UPDATE SET 
                nombre_grupo = EXCLUDED.nombre_grupo,
                clasificacion = EXCLUDED.clasificacion,
                nombre_investigador = EXCLUDED.nombre_investigador,
                fecha_actualizacion = CURRENT_TIMESTAMP
            """

            params = (
                cvlac_id,
                group["grupo_id"],
                group["nombre_grupo"],
                group["clasificacion"],
                group["nombre_investigador"],
            )

            self.cvlac_db.execute_query(upsert_query, params, fetch=False)
        except Exception as e:
            logger.error(f"Error insertando relación investigador-grupo: {str(e)}")
            raise

    def _update_tables_from_gruplac(self, stats):
        """
        Actualiza tablas en CvLAC con datos de GrupLAC.

        Args:
            stats (dict): Estadísticas para actualizar.
        """
        try:
            # Conectar a GrupLAC
            self.gruplac_db.connect()

            # Procesar cada tabla mapeada
            for gruplac_table, mapping in self.table_mapping.items():
                if gruplac_table == "integrantes":
                    continue  # Ya procesado en find_researchers_in_groups

                target_table = mapping["target_table"]
                field_mapping = mapping["field_mapping"]
                key_fields = mapping.get("key_fields", [])

                # Inicializar estadísticas para esta tabla
                if target_table not in stats["tables"]:
                    stats["tables"][target_table] = {
                        "processed": 0,
                        "inserted": 0,
                        "updated": 0,
                        "skipped": 0,
                        "error": 0,
                    }

                # Respaldar tabla antes de modificar
                self.backup_data(target_table)

                # Obtener datos de GrupLAC
                query = f"SELECT * FROM {gruplac_table}"
                results = self.gruplac_db.execute_query(query)

                # Procesar cada registro
                for row in results:
                    try:
                        stats["tables"][target_table]["processed"] += 1

                        # Crear diccionario con campos mapeados
                        data = {"cvlac_id": None}  # Se asignará después
                        for src_field, dst_field in field_mapping.items():
                            if src_field in row and row[src_field] is not None:
                                data[dst_field] = row[src_field]

                        # Obtener grupo_id
                        grupo_id = row["nro"]

                        # Buscar investigadores relacionados con este grupo
                        self._assign_data_to_researchers(
                            grupo_id, data, target_table, key_fields, stats
                        )
                    except Exception as e:
                        logger.error(
                            f"Error procesando registro en {gruplac_table}: {str(e)}"
                        )
                        stats["tables"][target_table]["error"] += 1

            self.gruplac_db.close()
        except Exception as e:
            logger.error(f"Error actualizando tablas desde GrupLAC: {str(e)}")
            raise

    def _assign_data_to_researchers(
        self, grupo_id, data, target_table, key_fields, stats
    ):
        """
        Asigna datos a investigadores relacionados con un grupo.

        Args:
            grupo_id (str): ID del grupo.
            data (dict): Datos a asignar.
            target_table (str): Tabla destino.
            key_fields (list): Campos clave para identificar duplicados.
            stats (dict): Estadísticas para actualizar.
        """
        try:
            # Buscar investigadores relacionados con este grupo
            query = """
            SELECT cvlac_id FROM investigador_grupo
            WHERE grupo_id = %s
            """
            researchers = self.cvlac_db.execute_query(query, (grupo_id,))

            for researcher in researchers:
                cvlac_id = researcher["cvlac_id"]
                data["cvlac_id"] = cvlac_id

                # Verificar si el registro ya existe
                if key_fields:
                    conditions = []
                    params = [cvlac_id]

                    for field in key_fields:
                        if field in data and data[field] is not None:
                            conditions.append(f"{field} = %s")
                            params.append(data[field])

                    check_query = f"""
                    SELECT * FROM {target_table} 
                    WHERE cvlac_id = %s AND {" AND ".join(conditions)}
                    LIMIT 1
                    """

                    existing = self.cvlac_db.execute_query(check_query, params)

                    if existing:
                        # El registro ya existe, considerar actualización
                        # Para simplicidad, se omite la actualización
                        stats["tables"][target_table]["skipped"] += 1
                        continue

                # Insertar nuevo registro
                fields = list(data.keys())
                placeholders = ["%s"] * len(fields)
                values = [data[field] for field in fields]

                insert_query = f"""
                INSERT INTO {target_table} ({", ".join(fields)})
                VALUES ({", ".join(placeholders)})
                """

                try:
                    self.cvlac_db.execute_query(insert_query, values, fetch=False)
                    stats["tables"][target_table]["inserted"] += 1
                except Exception as e:
                    if "duplicate key" in str(e).lower():
                        stats["tables"][target_table]["skipped"] += 1
                    else:
                        raise
        except Exception as e:
            logger.error(
                f"Error asignando datos a investigadores para grupo {grupo_id}: {str(e)}"
            )
            stats["tables"][target_table]["error"] += 1
            raise


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
        description="Herramienta de integración CvLAC-GrupLAC"
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

        # Inicializar herramienta de integración
        integrator = IntegrationTool(config["cvlac_db"], config["gruplac_db"])

        # Si solo se requiere respaldo
        if args.backup_only:
            tables = (
                args.tables.split(",")
                if args.tables
                else config.get("tables_to_backup", [])
            )
            for table in tables:
                integrator.backup_data(table)
            return

        # Encontrar investigadores en grupos
        researcher_to_groups = integrator.find_researchers_in_groups()

        # Enriquecer CvLAC con datos de GrupLAC
        stats = integrator.enrich_cvlac_from_gruplac(researcher_to_groups)

        # Guardar estadísticas
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_file = Path("logs") / f"integration_stats_{timestamp}.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        logger.info(f"Integración completada. Estadísticas guardadas en {stats_file}")

    except Exception as e:
        logger.error(f"Error en el proceso de integración: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
