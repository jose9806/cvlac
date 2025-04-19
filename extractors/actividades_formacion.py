from extractors.utils import *
from datetime import datetime

import re
import inspect

def extract_cursos_cortos(cod_rh, h3, connection):

    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')
        blockquotes = table.find_all('blockquote')

        for i in range(len(lis)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = "SI" if lis[i].find('img') else "NO" 
                li_split = lis[i].text.split('-')
                data['nivel_programa_academico'] = li_split[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(Finalidad:)|(En:)|(participación:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Finalidad:':
                            data['coautores'] = ", ".join(re.findall('[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre_producto'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            finalidad = blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            if finalidad != '.':
                                data['finalidad'] = finalidad
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+5].split(',')
                            data['ano'] = int(temp[1])
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['institucion_financiadora'] = temp[3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[j] == 'participación:':
                            temp = blockquote_split[j+4].split(',')
                            data['participacion'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['duracion'] = temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Palabras:':
                            data['palabras'] = blockquote_split[j+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Areas:':
                            data['areas'] = blockquote_split[j+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Sectores:':
                            data['sectores'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('cursos_corta_duracion', data, connection)



def extract_trabajos_dirigidos(cod_rh, h3, connection):

    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')
        blockquotes = table.find_all('blockquote')

        for i in range(len(lis)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = "SI" if lis[i].find('img') else "NO" 
                li_split = lis[i].text.split('-')
                data['tipo_producto'] = li_split[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(Estado:)|(Persona orientada:)|(Dirigió como:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Estado:':
                            split1 =  re.split("[A-Z]{2,},", blockquote_split[j-1])
                            split2 =  re.split("([A-Z]{2,}[ A-Z]*)", split1[1])

                            data['nombre'] = split2[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            if len(split2) > 1:
                                data['institucion'] = split2[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            temp = blockquote_split[j+6].split(u'\xa0')
                            data['estado'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['programa_academico'] = temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['fecha_inicio'] = int(temp[2].replace(',',''))

                            data['coautores'] =  ", ".join(re.findall('[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0].split('.')[0]))

                        elif blockquote_split[j] == 'Dirigió como:':
                            data['tipo_orientacion'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").split(',')[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Persona orientada:':
                            data['persona_orientada'] = blockquote_split[j+5].split(u'\xa0')[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Palabras:':
                            data['palabras'] = blockquote_split[j+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Areas:':
                            data['areas'] = blockquote_split[j+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Sectores:':
                            data['sectores'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('trabajos_dirigidos', data, connection)



def extract_asesorias(cod_rh, h3, connection):

    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')
        blockquotes = table.find_all('blockquote')

        for i in range(len(lis)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if lis[i].find('img') else 'NO'
                data['nombre_proyecto_ondas'] = lis[i].text.strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(Institución:)|(Ciudad:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Institución:':
                            data['institucion'] = blockquote_split[j+2][:-1]
                        elif blockquote_split[j] == 'Ciudad:':
                            data['ciudad'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))      

            insert_data('asesorias', data, connection)
