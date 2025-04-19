from extractors.utils import *
from datetime import datetime

import re
import inspect

def extract_obras_productos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'

                blockquote_split = re.split('(Disciplina:)|(Nombre del producto:)|(Fecha de creación:)|(INSTANCIAS DE VALORACIÓN DE LA OBRA)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Disciplina:': 
                            data['disciplina'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Nombre del producto:': 
                            data['nombre'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[i] == 'Fecha de creación:': 
                            try:
                                data['fecha_creacion'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('obras_productos', data, connection)


def extract_registro_licencia(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')

        for li in lis:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = "SI" if lis[i].find('img') else "NO" 
                li_split = re.split('(Institución u organización que tiene la licencia:)|(Fecha de otorgamiento de la licencia:)|(Número de registro de la Dirección)|(Nacional de Derechos de Autor:)', li.text)
                for i in range(len(li_split)):
                    try:
                        if li_split[i] == 'Institución u organización que tiene la licencia:': 
                            data['institucion'] = li_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif li_split[i] == 'Fecha de otorgamiento de la licencia:': 
                            try:
                                data['fecha_otorgamiento'] = li_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except:
                                None
                        elif li_split[i] == 'Número de registro de la Dirección': 
                            data['numero_registro'] = li_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif li_split[i] == 'Nacional de Derechos de Autor:': 
                            data['nacional_derechos'] = li_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('registro_licencia', data, connection)


def extract_industrias_creativas(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre de la empresa creativa:)|(Nit o codigo de registro:)|(Fecha de registro ante la camara de comercio:)|(Tiene productos en el mercado)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre de la empresa creativa:': 
                            data['nombre'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Nit o codigo de registro:': 
                            data['nit_registro'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Fecha de registro ante la camara de comercio:': 
                            try:
                                data['fecha_registro'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except: 
                                None
                        elif blockquote_split[i] == 'Tiene productos en el mercado':
                            data['tiene_productos'] = blockquote_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('industrias_creativas_culturales', data, connection)


def extract_eventos_artisticos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'

                blockquote_split = re.split('(Nombre del evento:)|(Fecha de inicio:)|(Tipo del evento:)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre del evento:': 
                            data['nombre'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Fecha de inicio:': 
                            try:
                                data['fecha_inicio'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('eventos_artisticos', data, connection) 

            
def extract_talleres_creativos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'

                blockquote_split = re.split('(Nombre del taller:)|(Tipo de taller:)|(Participación:)|(Fecha de inicio:)|(Fecha de finalización:)|(Lugar de realización:)|(Ámbito:)|(Distinción obtenida:)|(Mecanismo de selección:)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre del taller:': 
                            data['nombre'] = blockquote_split[i+9].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                        elif blockquote_split[i] == 'Tipo de taller:': 
                            data['tipo'] = blockquote_split[i+8].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                        elif blockquote_split[i] == 'Fecha de inicio:': 
                            try:
                                data['fecha_inicio'] = blockquote_split[i+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except:
                                None
                        elif blockquote_split[i] == 'Fecha de finalización:':
                            try:
                                fecha_fin = blockquote_split[i+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                                if fecha_fin:
                                    data['fecha_fin'] = fecha_fin
                            except:
                                None

                        elif blockquote_split[i] == 'Participación:':
                            participacion = blockquote_split[i+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")    
                            if participacion != 'null':
                                data['participacion'] = participacion              
                        elif blockquote_split[i] == 'Ámbito:':
                            data['ambito'] = blockquote_split[i+3].replace(',','')
                        elif blockquote_split[i] == 'Distinción obtenida:':
                            data['distincion_obtenida'] = blockquote_split[i+2].replace(',','') 
                        elif blockquote_split[i] == 'Mecanismo de selección:':
                            data['mecanismo_seleccion'] = blockquote_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")  
                        elif blockquote_split[i] == 'Lugar de realización:':
                            data['lugar_realizacion'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))                                                    
            insert_data('talleres_creativos', data, connection)