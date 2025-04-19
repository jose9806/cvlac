#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scraper principal para CvLAC.
"""
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from multiprocessing import Pool
from psycopg2 import connect
from config import ProjectLogger
from extractors.utils import delete_data

# Importar módulos de extracción específicos
from extractors import (
    actividades_evaluador,
    actividades_formacion,
    apropiacion_social,
    areas_actuacion,
    demas_trabajos,
    experiencia,
    formacion,
    identificacion,
    idioma,
    lineas_investigacion,
    produccion_artes,
    produccion_bibliografica,
    produccion_tec,
    proyectos,
    reconocimientos,
    redes_sociales,
)

import argparse
import requests
import datetime
import urllib3
import os
import json
import sys

# Configurar el logger
logger = ProjectLogger()
main_logger = logger.get_logger("main")

# Desactivar advertencias de certificados SSL
urllib3.disable_warnings(InsecureRequestWarning)


class CvlacScraper:
    """
    Clase principal para el scraper de CvLAC.
    """

    # Diccionario de funciones de extracción por título de sección
    EXTRACTORS = {
        "Formación Académica": formacion.extract_academic_formation,
        "Formación Complementaria": formacion.extract_complementary_formation,
        "Experiencia profesional": experiencia.extract,
        "Líneas de investigación": lineas_investigacion.extract,
        "Áreas de actuación": areas_actuacion.extract,
        "Idiomas": idioma.extract,
        "Cursos de corta duración": actividades_formacion.extract_cursos_cortos,
        "Trabajos dirigidos/tutorías": actividades_formacion.extract_trabajos_dirigidos,
        "Asesorías": actividades_formacion.extract_asesorias,
        "Jurado en comités de evaluación": actividades_evaluador.extract_jurados,
        "Par evaluador": actividades_evaluador.extract_par_evaluador,
        "Participación en comites de evaluación": actividades_evaluador.extract_participacion_comites_evaluacion,
        "Consultorías": apropiacion_social.extract_consultorias,
        "Ediciones/revisiones": apropiacion_social.extract_ediciones_revisiones,
        "Eventos científicos": apropiacion_social.extract_eventos_cientificos,
        "Informes de investigaci&oacuten": apropiacion_social.extract_informes,
        "Nueva secuencia genética": apropiacion_social.extract_secuencia,
        "Redes de conocimiento especializado": apropiacion_social.extract_redes_conocimiento,
        "Generación de contenido de audio": apropiacion_social.extract_audio,
        "Generación de contenido impresa": apropiacion_social.extract_impreso,
        "Generación de contenido multimedia": apropiacion_social.extract_multimedia,
        "Generación de contenido virtual": apropiacion_social.extract_contenido_virtual,
        "Estrategias de comunicación del conocimiento": apropiacion_social.extract_estrategias_conocimiento,
        "Estrategias pedagógicas para el fomento a la CTI": apropiacion_social.extract_estrategias_pedagogicas,
        "Espacios de participación ciudadana": apropiacion_social.extract_espacios_participacion,
        "Participación ciudadana en proyectos de CTI": apropiacion_social.extract_participacion_proyectos,
        "Obras o productos": produccion_artes.extract_obras_productos,
        "Registros de acuerdo de licencia": produccion_artes.extract_registro_licencia,
        "Industrias Creativas y culturales": produccion_artes.extract_industrias_creativas,
        "Eventos artísticos": produccion_artes.extract_eventos_artisticos,
        "Talleres Creativos": produccion_artes.extract_talleres_creativos,
        "Artículos": produccion_bibliografica.extract_articulos,
        "Capitulos de libro": produccion_bibliografica.extract_capitulos,
        "Libros": produccion_bibliografica.extract_libros,
        "Documentos de trabajo": produccion_bibliografica.extract_working_papers,
        "Otra producción blibliográfica": produccion_bibliografica.extract_otra_produccion,
        "Textos en publicaciones no científicas": produccion_bibliografica.extract_textos_no_cientificas,
        "Traducciones": produccion_bibliografica.extract_traducciones,
        "Notas científicas": produccion_bibliografica.extract_notas_cientificas,
        "Cartas, mapas y similares": produccion_tec.extract_maps,
        "Concepto técnico": produccion_tec.extract_conceptos,
        "Diseño industrial": produccion_tec.extract_disenos_industrial,
        "Empresas de base tecnológica": produccion_tec.extract_empresa_base_tec,
        "Esquemas de trazado de circuitos integrados": produccion_tec.extract_esquemas_trazado,
        "Informes técnicos": produccion_tec.extract_informes,
        "Innovación de proceso o procedimiento": produccion_tec.extract_innovacion_proc,
        "Innovación generada en la gestión empresarial": produccion_tec.extract_innovacion_gestion,
        "Variedad animal": produccion_tec.extract_variedad_animal,
        "Poblaciones mejoradas de razas pecuarias": produccion_tec.extract_poblaciones_mej,
        "Variedad vegetal": produccion_tec.extract_variedad_vegetal,
        "Nuevos registros científicos": produccion_tec.extract_registro_cientifico,
        "Planta piloto": produccion_tec.extract_planta_piloto,
        "Productos nutracéuticos": produccion_tec.extract_productos_nutra,
        "Productos tecnológicos": produccion_tec.extract_productos_tec,
        "Prototipos": produccion_tec.extract_prototipos,
        "Normas y Regulaciones": produccion_tec.extract_normas,
        "Protocolos de vigilancia epidemiológica": produccion_tec.extract_protocolos_vigilancia,
        "Reglamentos": produccion_tec.extract_reglamentos,
        "Signos distintivos": produccion_tec.extract_signos,
        "Softwares": produccion_tec.extract_software,
        "Demás trabajos": demas_trabajos.extract,
        "Proyectos": proyectos.extract,
        "Reconocimientos": reconocimientos.extract,
        "Redes sociales académicas": redes_sociales.extract,
    }

    def __init__(self, db_config=None):
        """
        Inicializa el scraper con la configuración de base de datos.

        Args:
            db_config (dict, optional): Configuración de la base de datos.
        """
        self.db_config = db_config or {
            "user": "postgres",
            "password": "root",
            "host": "",
            "port": "5432",
            "database": "scrap",
        }

        # Cargar CVLACs ya procesados e intentados
        self.processed_ids = self._load_processed_ids()
        self.tried_ids = self._load_tried_ids()

    def _load_processed_ids(self):
        """
        Carga los IDs de CVLACs ya procesados.

        Returns:
            set: Conjunto de IDs procesados.
        """
        processed = set()
        try:
            if os.path.exists("procesados.txt"):
                with open("procesados.txt", "r") as f:
                    for line in f:
                        processed.add(line.strip())
            return processed
        except Exception as ex:
            main_logger.error(
                f"Error cargando IDs procesados: {str(ex)}", exc_info=True
            )
            return processed

    def _load_tried_ids(self):
        """
        Carga los IDs de CVLACs ya intentados.

        Returns:
            set: Conjunto de IDs intentados.
        """
        tried = set()
        try:
            if os.path.exists("cvlac_id_tries.txt"):
                with open("cvlac_id_tries.txt", "r") as f:
                    for line in f:
                        tried.add(line.strip())
            return tried
        except Exception as ex:
            main_logger.error(
                f"Error cargando IDs intentados: {str(ex)}", exc_info=True
            )
            return tried

    def _get_db_connection(self):
        """
        Obtiene una conexión a la base de datos.

        Returns:
            connection: Conexión a la base de datos.
        """
        try:
            connection = connect(**self.db_config)
            return connection
        except Exception as ex:
            main_logger.error(
                f"Error conectando a la base de datos: {str(ex)}", exc_info=True
            )
            raise

    def extract_cvlac(self, cod_rh):
        """
        Extrae la información de un CvLAC.

        Args:
            cod_rh (str): Código del investigador.
        """
        connection = None
        try:
            main_logger.info(f"Iniciando extracción para CvLAC: {cod_rh}")

            # Obtener conexión a la base de datos
            connection = self._get_db_connection()

            # Obtener la página CvLAC
            url = f"https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh={cod_rh}"
            with requests.get(url, verify=False) as response:
                if response.status_code != 200:
                    main_logger.warning(
                        f"Error al obtener CvLAC {cod_rh}. Status: {response.status_code}"
                    )
                    return

                html = BeautifulSoup(response.content, "lxml")

                # Verificar si hay suficientes tablas
                if len(html.findAll("table")) <= 2:
                    main_logger.warning(f"CvLAC {cod_rh} no tiene suficientes tablas")
                    return

                # Eliminar datos previos
                delete_data(cod_rh, connection)

                # Extraer identificación
                nombre_completo = identificacion.extract(cod_rh, html, connection)
                if not nombre_completo:
                    main_logger.warning(
                        f"No se pudo extraer identificación para CvLAC {cod_rh}"
                    )
                    return

                # Extraer el resto de secciones
                for h3 in html.find_all("h3"):
                    section_title = h3.text
                    extractor_func = self.EXTRACTORS.get(section_title)

                    if extractor_func:
                        try:
                            main_logger.debug(
                                f"Extrayendo sección: {section_title} para {cod_rh}"
                            )

                            # Caso especial para eventos científicos
                            if section_title == "Eventos científicos":
                                extractor_func(cod_rh, h3, nombre_completo, connection)
                            else:
                                extractor_func(cod_rh, h3, connection)

                            main_logger.debug(
                                f"Sección {section_title} extraída correctamente para {cod_rh}"
                            )
                        except Exception as ex:
                            main_logger.error(
                                f"Error extrayendo sección {section_title} para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

            # Registrar como procesado
            with open("procesados.txt", "a") as f:
                f.write(str(cod_rh) + "\n")
            self.processed_ids.add(cod_rh)

            main_logger.info(f"Extracción completada para CvLAC: {cod_rh}")

        except Exception as ex:
            main_logger.error(
                f"Error general en extract_cvlac para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

        finally:
            if connection:
                connection.close()

    def process_range(self, start_id, range_size=31250):
        """
        Procesa un rango de IDs de CvLAC.

        Args:
            start_id (int): ID inicial.
            range_size (int, optional): Tamaño del rango. Por defecto 31250.
        """
        main_logger.info(
            f"Procesando rango desde {start_id} hasta {start_id + range_size - 1}"
        )

        connection = None
        try:
            connection = self._get_db_connection()

            for i in range(start_id, start_id + range_size):
                cod_rh_formatted = "{:010d}".format(i)

                # Verificar si ya se ha procesado o intentado
                if cod_rh_formatted in self.tried_ids:
                    continue

                # Registrar como intentado
                with open("cvlac_id_tries.txt", "a") as f:
                    f.write(cod_rh_formatted + "\n")
                self.tried_ids.add(cod_rh_formatted)

                # Extraer información
                self.extract_cvlac(cod_rh_formatted)

        except Exception as ex:
            main_logger.error(f"Error en process_range: {str(ex)}", exc_info=True)

        finally:
            if connection:
                connection.close()


def process_range_wrapper(start_id):
    """
    Función wrapper para procesar rangos en multiproceso.

    Args:
        start_id (int): ID inicial.
    """
    try:
        scraper = CvlacScraper()
        scraper.process_range(start_id)
    except Exception as ex:
        main_logger.error(f"Error en process_range_wrapper: {str(ex)}", exc_info=True)


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Extraer información de CvLAC")
    parser.add_argument("--cod_rh", help="Código CvLAC del investigador")
    parser.add_argument(
        "--multiprocess", action="store_true", help="Usar multiprocesamiento"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=64,
        help="Número de workers para multiprocesamiento",
    )
    parser.add_argument(
        "--range_start",
        type=int,
        default=0,
        help="ID inicial para procesamiento en rango",
    )
    parser.add_argument(
        "--range_end",
        type=int,
        default=2000000,
        help="ID final para procesamiento en rango",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=31250,
        help="Tamaño del paso para procesamiento en rango",
    )
    parser.add_argument("--config", help="Ruta al archivo de configuración")

    args = parser.parse_args()

    # Configuración de la base de datos desde archivo o valores por defecto
    db_config = {
        "user": "postgres",
        "password": "root",
        "host": "",
        "port": "5432",
        "database": "scrap",
    }

    # Intentar cargar configuración desde archivo
    try:
        if args.config and os.path.exists(args.config):
            with open(args.config, "r") as f:
                db_config.update(json.load(f))
        elif os.path.exists("db_config.json"):
            with open("db_config.json", "r") as f:
                db_config.update(json.load(f))
    except Exception as ex:
        main_logger.error(
            f"Error cargando configuración de BD: {str(ex)}", exc_info=True
        )

    scraper = CvlacScraper(db_config)

    # Modo de ejecución: un solo CvLAC
    if args.cod_rh:
        main_logger.info(f"Extrayendo información para CvLAC: {args.cod_rh}")
        scraper.extract_cvlac(args.cod_rh)

    # Modo de ejecución: multiprocesamiento
    elif args.multiprocess:
        main_logger.info(f"Iniciando extracción con {args.workers} workers")

        parts = list(range(args.range_start, args.range_end, args.step))

        if args.workers > 1:
            with Pool(args.workers) as pool:
                pool.map(process_range_wrapper, parts)
        else:
            for start_id in parts:
                process_range_wrapper(start_id)

    # Modo por defecto: un solo proceso, todos los rangos
    else:
        main_logger.info("Iniciando extracción en modo single-process")

        for start_id in range(args.range_start, args.range_end, args.step):
            scraper.process_range(start_id, args.step)


if __name__ == "__main__":
    main()
