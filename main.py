#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scraper principal para CvLAC.
"""
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from multiprocessing import Pool
from config import ProjectLogger
from extractors.utils import delete_data, start_extraction, finish_extraction
from config import project_settings, db

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

    def __init__(self):
        """
        Inicializa el scraper.
        """
        # Cargar CVLACs ya procesados e intentados
        self.processed_ids = self._load_processed_ids()
        self.tried_ids = self._load_tried_ids()

        # Configuración del scraper
        self.scraper_config = project_settings.scraper

        # Verificar conexión a BD al inicializar
        if not db.test_connection():
            main_logger.warning(
                "Database connection failed. Some functionality may be limited."
            )

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

    def extract_cvlac(self, cod_rh):
        """
        Extrae la información de un CvLAC.

        Args:
            cod_rh (str): Código del investigador.

        Returns:
            str: Ruta al reporte de extracción generado.
        """
        connection = None
        report_path = None
        try:
            main_logger.info(f"Iniciando extracción para CvLAC: {cod_rh}")

            # Iniciar nueva extracción para estadísticas
            start_extraction()

            # Obtener conexión a la base de datos
            connection = db.get_connection()

            # Obtener la página CvLAC
            url = f"https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh={cod_rh}"

            headers = {"User-Agent": self.scraper_config.get("user_agent")}
            timeout = self.scraper_config.get("timeout", 30)
            verify_ssl = self.scraper_config.get("verify_ssl", False)

            with requests.get(
                url, headers=headers, timeout=timeout, verify=verify_ssl
            ) as response:
                if response.status_code != 200:
                    main_logger.warning(
                        f"Error al obtener CvLAC {cod_rh}. Status: {response.status_code}"
                    )
                    return None

                html = BeautifulSoup(response.content, "lxml")

                # Verificar si hay suficientes tablas
                if len(html.findAll("table")) <= 2:  # type: ignore
                    main_logger.warning(f"CvLAC {cod_rh} no tiene suficientes tablas")
                    return None

                # Eliminar datos previos si se está realizando una actualización completa
                if self.scraper_config.get("remove_existing_data", True):
                    delete_data(cod_rh, connection)

                # Extraer identificación
                nombre_completo = identificacion.extract(cod_rh, html, connection)
                if not nombre_completo:
                    main_logger.warning(
                        f"No se pudo extraer identificación para CvLAC {cod_rh}"
                    )
                    return None

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

            # Generar reporte de extracción
            report_path = finish_extraction(cod_rh)
            main_logger.info(f"Extracción completada para CvLAC: {cod_rh}")
            main_logger.info(f"Reporte generado en: {report_path}")

        except Exception as ex:
            main_logger.error(
                f"Error general en extract_cvlac para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

        finally:
            if connection:
                connection.close()

        return report_path

    def process_range(self, start_id, range_size=31250):
        """
        Procesa un rango de IDs de CvLAC.

        Args:
            start_id (int): ID inicial.
            range_size (int, optional): Tamaño del rango. Por defecto 31250.

        Returns:
            list: Lista de rutas a los reportes generados
        """
        main_logger.info(
            f"Procesando rango desde {start_id} hasta {start_id + range_size - 1}"
        )

        connection = None
        reports = []

        try:
            connection = db.get_connection()

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
                report_path = self.extract_cvlac(cod_rh_formatted)
                if report_path:
                    reports.append(report_path)

            # Generar reporte de resumen para todo el rango
            if reports:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                summary_file = os.path.join(
                    "temp",
                    "reports",
                    f"range_summary_{start_id}_{start_id+range_size}_{timestamp}.txt",
                )

                with open(summary_file, "w") as f:
                    f.write(
                        f"Resumen de extracción para rango {start_id} - {start_id+range_size-1}\n"
                    )
                    f.write(
                        f"Fecha de extracción: {datetime.datetime.now().isoformat()}\n"
                    )
                    f.write(f"Total de CVLACs procesados: {len(reports)}\n\n")
                    f.write("Reportes individuales generados:\n")
                    for report in reports:
                        f.write(f"- {report}\n")

                main_logger.info(f"Resumen del rango generado en: {summary_file}")
                reports.append(summary_file)

        except Exception as ex:
            main_logger.error(f"Error en process_range: {str(ex)}", exc_info=True)

        finally:
            if connection:
                connection.close()

        return reports


def process_range_wrapper(start_id):
    """
    Función wrapper para procesar rangos en multiproceso.

    Args:
        start_id (int): ID inicial.

    Returns:
        list: Lista de rutas a los reportes generados
    """
    try:
        scraper = CvlacScraper()
        return scraper.process_range(start_id)
    except Exception as ex:
        main_logger.error(f"Error en process_range_wrapper: {str(ex)}", exc_info=True)
        return []


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
    parser.add_argument(
        "--test_db",
        action="store_true",
        help="Probar conexión a la base de datos y salir",
    )
    parser.add_argument(
        "--update_only",
        action="store_true",
        help="Solo actualizar registros sin eliminar datos existentes",
    )
    parser.add_argument(
        "--validate_only",
        action="store_true",
        help="Solo validar sin actualizar ni insertar nuevos registros",
    )
    parser.add_argument(
        "--report_dir",
        help="Directorio para almacenar los reportes de extracción",
    )

    args = parser.parse_args()

    # Actualizar configuración basada en argumentos de línea de comandos
    if args.update_only:
        project_settings.scraper["remove_existing_data"] = False

    if args.validate_only:
        project_settings.scraper["update_if_exists"] = False

    if args.report_dir:
        # Asegurarse de que el directorio de reportes exista
        os.makedirs(args.report_dir, exist_ok=True)
        # Actualizar la ruta del directorio de reportes en la configuración
        if not hasattr(project_settings, "_config"):
            project_settings._config = {}
        if "reporting" not in project_settings._config:
            project_settings._config["reporting"] = {}
        project_settings._config["reporting"]["report_dir"] = args.report_dir

    # Probar la conexión a la base de datos si se solicita
    if args.test_db:
        print("Probando conexión a la base de datos...")
        if db.test_connection():
            print("✅ Conexión exitosa a la base de datos")
        else:
            print("❌ No se pudo conectar a la base de datos")
        return

    scraper = CvlacScraper()
    all_reports = []

    # Modo de ejecución: un solo CvLAC
    if args.cod_rh:
        main_logger.info(f"Extrayendo información para CvLAC: {args.cod_rh}")
        report_path = scraper.extract_cvlac(args.cod_rh)
        if report_path:
            all_reports.append(report_path)
            main_logger.info(f"Reporte generado: {report_path}")

    # Modo de ejecución: multiprocesamiento
    elif args.multiprocess:
        main_logger.info(f"Iniciando extracción con {args.workers} workers")

        parts = list(range(args.range_start, args.range_end, args.step))

        if args.workers > 1:
            with Pool(args.workers) as pool:
                results = pool.map(process_range_wrapper, parts)
                # Aplanar la lista de resultados
                for reports in results:
                    if reports:
                        all_reports.extend(reports)
        else:
            for start_id in parts:
                reports = process_range_wrapper(start_id)
                if reports:
                    all_reports.extend(reports)

    # Modo por defecto: un solo proceso, todos los rangos
    else:
        main_logger.info("Iniciando extracción en modo single-process")

        for start_id in range(args.range_start, args.range_end, args.step):
            reports = scraper.process_range(start_id, args.step)
            if reports:
                all_reports.extend(reports)

    # Generar un reporte final con todos los resultados
    if all_reports:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        final_report = os.path.join(
            "temp", "reports", f"extraccion_completa_{timestamp}.txt"
        )

        with open(final_report, "w") as f:
            f.write(f"REPORTE FINAL DE EXTRACCIÓN\n")
            f.write(f"=========================\n\n")
            f.write(f"Fecha de finalización: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Total de reportes generados: {len(all_reports)}\n\n")
            f.write("Reportes individuales:\n")
            for report in all_reports:
                f.write(f"- {report}\n")

        main_logger.info(f"Reporte final generado en: {final_report}")
        print(f"Extracción completada. Reporte final: {final_report}")


if __name__ == "__main__":
    main()
