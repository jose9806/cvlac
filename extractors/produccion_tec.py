from extractors.utils import *
from datetime import datetime

import re
import inspect


def extract_maps(cod_rh, h3, connection):
    
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

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre_producto'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano']  = int(temp[1])               
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
            insert_data('cartas_mapas', data, connection)


def extract_conceptos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Institución solicitante:)|(En:)|(Fecha solicitud:)|(Fecha de envío:)|(Número consecutivo del concepto:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Institución solicitante:':
                            data['titulo'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['institucion'] = blockquote_split[j+5][:-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            data['ciudad']  = blockquote_split[j+4][:-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")   
                        elif blockquote_split[j] == 'Fecha solicitud:':
                            try:
                                data['fecha_solicitud'] = "".join(blockquote_split[j+3].split()).replace('y','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                        elif blockquote_split[j] == 'Fecha de envío:':
                            try:
                                data['fecha_envio'] = "".join(blockquote_split[j+2].split()).replace('.',''),
                            except:
                                None
                        elif blockquote_split[j] == 'Número consecutivo del concepto:':
                            data['numero'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('conceptos_tecnicos', data, connection)



def extract_disenos_industrial(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('diseno_industrial', data, connection)

def extract_empresa_base_tec(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')
        blockquotes = table.find_all('blockquote')
        for i in range(len(lis)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = "SI" if lis[i].parent.parent.find('img') else "NO" 
                data['tipo'] = lis[i].text.split(' - ')[2]

                blockquote_split = re.split('(Nit)|(Registrado ante la c´mara el:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nit':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = "".join(re.sub(r'[A-Z]{2,}[ [A-Z]{2,}]*','', blockquote_split[:j][0])).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['nombre'] = re.sub('^,', '', data['nombre'])
                            data['nombre'] = re.sub(',$', '', data['nombre'])
                            data['nit'] = blockquote_split[j+5].replace(',','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Registrado ante la c´mara el:':
                            try:
                                data['fecha_registro'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except:
                                None
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
            insert_data('empresas_base_tecnologica', data, connection)


def extract_esquemas_trazado(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = "".join(re.sub(r'[A-Z]{2,}[ [A-Z]{2,}]*','', blockquote_split[:j][0])).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['nombre'] = re.sub('^,', '', data['nombre'])
                            data['nombre'] = re.sub(',$', '', data['nombre'])
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('esquemas_trazado', data, connection)


def extract_informes(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'contrato/registro:':
                            data['contrato_registro'] = blockquote_split[j+5].split(',')[0]
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('informes_tecnicos', data, connection)


def extract_innovacion_proc(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = blockquote_split[j-1].split('\n')[-2][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('innovacion_procesos', data, connection)


def extract_innovacion_gestion(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        bs = [b for b in table.find_all('b') if b.parent.name == 'td']
        blockquotes = table.find_all('blockquote')
        for i in range(len(bs)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['tipo'] = bs[i].text.split(' - ')[2]

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = blockquote_split[j-1].split('\n')[-2][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('innovacion_gestion', data, connection)


def extract_variedad_animal(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = blockquote_split[j-1].split('\n')[-2][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('variedad_animal', data, connection)


def extract_poblaciones_mej(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent
    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(En:)|(Número o consecutivo del certificado del Ministerio de Agricultura:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = blockquote_split[j-1].split('\n')[-2][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            
                            temp = blockquote_split[j+2].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[1])
                        if blockquote_split[j] == 'Número o consecutivo del certificado del Ministerio de Agricultura:':
                            data['numero_certificado'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('poblaciones_mejoradas', data, connection)


def extract_variedad_vegetal(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent
    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(Ciclo:)|(Estado de la variedad:)|(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Ciclo:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = blockquote_split[j-1].split('\n')[-2][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            
                            data['ciclo'] = blockquote_split[j+8].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]

                        elif blockquote_split[j] == 'Estado de la variedad:':
                            data['estado'] = blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+4].split(',')
                            data['pais']  = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2])
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
            insert_data('variedad_vegetal', data, connection)


def extract_registro_cientifico(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent
    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(En:)|(Nombre de base de datos donde está incluido el registro:)|(disponible en)|(Institución que emite el registro:)|(Institución certificadora:)|(artículo vinculado:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = blockquote_split[j-1].split('\n')[-3][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(re.findall(r'[0-9]+', blockquote_split[j-1].split('\n')[-2])[0])

                            data['pais'] =  blockquote_split[j+9].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Nombre de base de datos donde está incluido el registro:':
                            data['base_datos'] = blockquote_split[j+8][:-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'disponible en':
                            data['sitio_web'] = blockquote_split[j+7][:-2].replace(',\xa0\n', '').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Institución que emite el registro:':
                            data['institucion_registro'] = blockquote_split[j+6][:-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")     
                        elif blockquote_split[j] == 'Institución certificadora:':
                            data['institucion_certificadora'] = blockquote_split[j+5][:-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'artículo vinculado:':
                            data['articulo_vinculado'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")                                                              
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
            insert_data('registro_cientifico', data, connection)


def extract_planta_piloto(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            data['nombre_comercial'] = blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano']  = int(temp[1])               
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
            insert_data('plantas_piloto', data, connection)


def extract_productos_nutra(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(Fecha de obtención del registro del INVIMA:)|(En:)|(Titular del registro:)|(Número de registro:)|(proyecto vinculado:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Fecha de obtención del registro del INVIMA:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            try:
                                data['fecha_registro'] = blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                        elif blockquote_split[j] == 'En:':
                            data['pais'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Titular del registro:':
                            data['titular'] = blockquote_split[j+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[j] == 'Número de registro:':
                            data['numero_registro'] = blockquote_split[j+2].split('\xa0')[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'proyecto vinculado:':
                            data['proyecto_vinculado'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('productos_nutraceuticos', data, connection)


def extract_productos_tec(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                li_split = blockquote.parent.parent.previous_sibling.previous_sibling.get_text().split('-')
                if len(li_split) > 2:
                    data['tipo'] = blockquote.parent.parent.previous_sibling.previous_sibling.get_text().split('-')[2].strip()

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            data['nombre_comercial'] = blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano']  = int(temp[1])               
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
            insert_data('productos_tecnologicos', data, connection)


def extract_prototipos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        bs = [b for b in table.find_all('b') if b.parent.name == 'td']
        blockquotes = table.find_all('blockquote')

        for i in range(len(bs)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquotes[i].parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                b_split = bs[i].text.split('-')
                data['tipo'] = b_split[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            data['nombre_comercial'] = blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano']  = int(temp[1])               
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
            insert_data('prototipos', data, connection)


def extract_normas(cod_rh, h3, connection):
    
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

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(ed:)|(regulación:)|(tipo:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            data['nombre_comercial'] = blockquote_split[j+9].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano']  = int(temp[1])               
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
            insert_data('normas_regulaciones', data, connection)


def extract_protocolos_vigilancia(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent
    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(En:)|(Institución:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            if j == 1:

                                data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                data['nombre'] = blockquote_split[j-1].split('\n')[-2][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                                try:
                                    data['fecha'] = "".join(blockquote_split[j+5].split()).replace('.','')
                                except:
                                    None
                            else:
                                data['ciudad'] =  blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Institución:':
                            data['institucion'] =  blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")                             
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
            insert_data('protocolos_vigilancia', data, connection)


def extract_reglamentos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(ed:)|(regulación:)|(tipo:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            data['nombre_comercial'] = blockquote_split[j+9].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano']  = int(temp[1])               
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
            insert_data('reglamentos', data, connection)


def extract_signos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'

                blockquote_split = re.split('(En)|(Registro:)|(Titular:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En':
                            data['nombre'] = blockquote_split[j-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                            temp = re.split(r'([0-9]+)', blockquote_split[j+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0]).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                            data['ano']  = int(temp[1])               
                        elif blockquote_split[j] == 'Registro:':
                            data['registro'] = blockquote_split[j+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[j] == 'Titular:':
                            data['titular'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('signos_distintivos', data, connection)


def extract_software(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        bs = [b for b in table.find_all('b') if b.parent.name == 'td']
        blockquotes = table.find_all('blockquote')

        for i in range(len(bs)):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['tipo'] = bs[i].text.split(' - ')[2]

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(plataforma:)|(ambiente:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            data['nombre_comercial'] = blockquote_split[j+8].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'contrato/registro:':
                            data['contrato_registro'] = blockquote_split[j+7].split('\n')[0][:-1]
                        elif blockquote_split[j] == 'En:':
                            temp = re.split(r'([0-9]+)', blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                            data['ano'] = int(temp[1])    
                        elif blockquote_split[j] == 'plataforma:':       
                            data['plataforma'] = blockquote_split[j+5].split('\xa0')[0]
                        elif blockquote_split[j] == 'ambiente:':       
                            data['ambiente'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")                        
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
            insert_data('software', data, connection)