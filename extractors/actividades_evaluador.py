from extractors.utils import *
from datetime import datetime

import re
import inspect

def extract_jurados(cod_rh, h3, connection):

    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')
        blockquotes = table.find_all('blockquote')

        for i in range(len(lis)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                li_split = lis[i].text.split('-')
                data['chulo'] = "SI" if lis[i].find('img') else "NO" 
                data['nivel_programa_academico'] = li_split[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(Titulo:)|(Tipo de trabajo presentado:)|(en:)|(programa académico)|(Nombre del orientado:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Titulo:':
                            data['coautores'] = blockquote_split[j-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['titulo'] = blockquote_split[j+8].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                        elif blockquote_split[j] == 'Tipo de trabajo presentado:':
                            data['tipo_trabajo'] = blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'en:':
                            data['institucion'] = blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")                  
                        elif blockquote_split[j] == 'programa académico':
                            data['programa_academico'] = blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Nombre del orientado:':
                            data['nombre_orientado'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Palabras:':
                            data['palabras'] = blockquote_split[j+3].rstrip()
                        elif blockquote_split[j] == 'Areas:':
                            data['areas'] = blockquote_split[j+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Sectores:':
                            data['sectores'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
                insert_data('jurados', data, connection)
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))


def extract_par_evaluador(cod_rh, h3, connection):

    table = h3.parent.parent.parent

    if table:
        data = dict()
        data['cvlac_id'] = cod_rh

        blockquotes = table.find_all('blockquote')
        for blockquote in  blockquotes:
            try:
                blockquote_split = re.split('(Ámbito:)|(Par evaluador de:)|(Institución:)|(Revista:)|(Editorial:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Ámbito:':
                            data['ambito'] = blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        if blockquote_split[j] == 'Par evaluador de:':
                            data['par_evaluador_de'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        if blockquote_split[j] == 'Institución:':
                            temp = blockquote_split[j+3].split(u'\xa0')
                            if len(temp) == 4:
                                data['entidad_convocadora'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        if blockquote_split[j] in ['Revista:', 'Editorial:']:
                            data['tipo_material'] = ''.join(filter(None,blockquote_split[j:])).replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").split(u'\xa0')[0][:-1]
                        if j == len(blockquote_split) - 1:
                            temp = blockquote_split[j].split(',')
                            data['ano'] = re.findall(r'[0-9]+', blockquote_split[j])[0]
                            data['mes'] = temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('par_evaluador', data, connection)


def extract_participacion_comites_evaluacion(cod_rh, h3, connection):
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
                data['tipo'] = li_split[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(en:)|(Areas:)|(Palabras:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'en:':
                            data['institucion'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['nombre_producto'] = "".join(blockquote_split[j-1].split(',')[1:]).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            ano = re.findall(r'[0-9]{4}=', data['nombre_producto'])
                            if len(ano):
                                data['ano'] = int(ano)
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('participacion_comites_evaluacion', data, connection)