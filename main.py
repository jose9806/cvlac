from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
from extractors import actividades_evaluador, actividades_formacion, apropiacion_social, areas_actuacion, \
    demas_trabajos, experiencia, formacion,identificacion, idioma,lineas_investigacion,produccion_artes, \
        produccion_bibliografica, produccion_tec, proyectos, reconocimientos, redes_sociales
from multiprocessing import Pool
from psycopg2 import connect
from extractors.utils import delete_data

import argparse
import requests
import time
import random
import datetime
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)
f = open("cvlac_id_tries.txt", "r")
LINES = f.readlines()


SWITCHER = {
    'Formación Académica': formacion.extract_academic_formation,
    'Formación Complementaria': formacion.extract_complementary_formation,
    'Experiencia profesional': experiencia.extract,
    'Líneas de investigación': lineas_investigacion.extract,
    'Áreas de actuación': areas_actuacion.extract,
    'Idiomas': idioma.extract,
    'Cursos de corta duración': actividades_formacion.extract_cursos_cortos,
    'Trabajos dirigidos/tutorías': actividades_formacion.extract_trabajos_dirigidos,
    'Asesorías': actividades_formacion.extract_asesorias,
    'Jurado en comités de evaluación': actividades_evaluador.extract_jurados,
    'Par evaluador': actividades_evaluador.extract_par_evaluador,
    'Participación en comites de evaluación': actividades_evaluador.extract_participacion_comites_evaluacion,
    'Consultorías': apropiacion_social.extract_consultorias,
    'Ediciones/revisiones': apropiacion_social.extract_ediciones_revisiones,
    'Eventos científicos': apropiacion_social.extract_eventos_cientificos,
    'Informes de investigaci&oacuten': apropiacion_social.extract_informes,
    'Nueva secuencia genética': apropiacion_social.extract_secuencia,
    'Redes de conocimiento especializado': apropiacion_social.extract_redes_conocimiento,
    'Generación de contenido de audio': apropiacion_social.extract_audio,
    'Generación de contenido impresa': apropiacion_social.extract_impreso,
    'Generación de contenido multimedia': apropiacion_social.extract_multimedia,
    'Generación de contenido virtual': apropiacion_social.extract_contenido_virtual,
    'Estrategias de comunicación del conocimiento': apropiacion_social.extract_estrategias_conocimiento,
    'Estrategias pedagógicas para el fomento a la CTI': apropiacion_social.extract_estrategias_pedagogicas,
    'Espacios de participación ciudadana': apropiacion_social.extract_espacios_participacion,
    'Participación ciudadana en proyectos de CTI': apropiacion_social.extract_participacion_proyectos,
    'Obras o productos': produccion_artes.extract_obras_productos,
    'Registros de acuerdo de licencia': produccion_artes.extract_registro_licencia,
    'Industrias Creativas y culturales': produccion_artes.extract_industrias_creativas,
    'Eventos artísticos': produccion_artes.extract_eventos_artisticos,
    'Talleres Creativos': produccion_artes.extract_talleres_creativos,
    'Artículos': produccion_bibliografica.extract_articulos,
    'Capitulos de libro': produccion_bibliografica.extract_capitulos,
    'Libros': produccion_bibliografica.extract_libros,
    'Documentos de trabajo': produccion_bibliografica.extract_working_papers,
    'Otra producción blibliográfica': produccion_bibliografica.extract_otra_produccion,
    'Textos en publicaciones no científicas': produccion_bibliografica.extract_textos_no_cientificas,
    'Traducciones': produccion_bibliografica.extract_traducciones,
    'Notas científicas': produccion_bibliografica.extract_notas_cientificas,
    'Cartas, mapas y similares': produccion_tec.extract_maps,
    'Concepto técnico': produccion_tec.extract_conceptos,
    'Diseño industrial': produccion_tec.extract_disenos_industrial,
    'Empresas de base tecnológica': produccion_tec.extract_empresa_base_tec,
    'Esquemas de trazado de circuitos integrados': produccion_tec.extract_esquemas_trazado,
    'Informes técnicos': produccion_tec.extract_informes,
    'Innovación de proceso o procedimiento': produccion_tec.extract_innovacion_proc,
    'Innovación generada en la gestión empresarial': produccion_tec.extract_innovacion_gestion,
    'Variedad animal': produccion_tec.extract_variedad_animal,
    'Poblaciones mejoradas de razas pecuarias': produccion_tec.extract_poblaciones_mej,
    'Variedad vegetal': produccion_tec.extract_variedad_vegetal,
    'Nuevos registros científicos': produccion_tec.extract_registro_cientifico,
    'Planta piloto': produccion_tec.extract_planta_piloto,
    'Productos nutracéuticos': produccion_tec.extract_productos_nutra,
    'Productos tecnológicos': produccion_tec.extract_productos_tec,
    'Prototipos': produccion_tec.extract_prototipos,
    'Normas y Regulaciones': produccion_tec.extract_normas,
    'Protocolos de vigilancia epidemiológica': produccion_tec.extract_protocolos_vigilancia,
    'Reglamentos': produccion_tec.extract_reglamentos,
    'Signos distintivos': produccion_tec.extract_signos,
    'Softwares': produccion_tec.extract_software,
    'Demás trabajos': demas_trabajos.extract,
    'Proyectos': proyectos.extract,
    'Reconocimientos': reconocimientos.extract, 
    'Redes sociales académicas': redes_sociales.extract
}

def extract_cvlac(cod_rh, connection):
    try:
        url = f'https://scienti.minciencias.gov.co/cvlac/visualizador/generarCurriculoCv.do?cod_rh={cod_rh}'
        with requests.get(url, verify=False) as response:            
            html = BeautifulSoup(response.content, 'lxml')
            delete_data(cod_rh, connection)
            """
                Extraer los campos necesarios por tabla
            """
            if len(html.findAll('table')) <=2:
                return
            nombre_completo = identificacion.extract(cod_rh, html, connection)
            if not nombre_completo:
                return
                
            for h3 in html.find_all('h3'):
                func = SWITCHER.get(h3.text)
                if func:
                    if h3.text == 'Eventos científicos':
                        func(cod_rh, h3, nombre_completo, connection)
                    else: 
                        func(cod_rh, h3, connection)

    except Exception as ex:
        f = open("logs.txt", "a")
        f.write(" -- ".join([cod_rh, str(datetime.datetime.now()), str(ex),  '\n']))
    f = open("procesados.txt", "a")
    f.write(str(cod_rh) + '\n')


def start_range_cod_rh(start):
    connection = connect(user="postgres",
        password="root",
        host="",
        port="5432",
        database="scrap")

    steps = 31250
    for cod_rh in range(start,start + steps):
        if "{:010d}".format(cod_rh) + '\n' in LINES:
            continue
        f = open("cvlac_id_tries.txt", "a")
        f.write("{:010d}".format(cod_rh)+ '\n')
        extract_cvlac("{:010d}".format(cod_rh), connection)
    connection.close()
    
"""
    Comando a leer: python main.py --cod_rh=0001655135
"""
if __name__ == "__main__":
    # # Para Pruebas con un solo cvlac
    # connection = connect(user="postgres",
    # password="root",
    # host="localhost",
    # port="5432",
    # database="scrap")

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--cod_rh', help='cod_rh de inventisgador (CvLAC ID)')
    # args = parser.parse_args()

    # if 'cod_rh' in args:
    #     extract_cvlac(args.cod_rh, connection)
    

    # Para pruebas con múltiples cvlac multiprocesos
    pool = Pool(64)
    processes = []
    steps = 31250
    parts = [i for i in range(0,2000000, steps)]
    pool.map(start_range_cod_rh, parts)    


