from extractors.utils import *
from datetime import datetime

import locale
import inspect
import re
import unidecode
import uuid

locale.setlocale(locale.LC_TIME, '')

def extract_consultorias(cod_rh, h3, connection):
    
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
                data['tipo_clase'] = li_split[2]

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Nombre comercial:': 
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'contrato/registro:': 
                            temp = blockquote_split[j+5]
                            data['numero_contrato'] = temp.replace(',','').replace('.','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'En:': 
                            temp = blockquote_split[j+4].split(',')
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['duracion'] = temp[3].split(u'\xa0')[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
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
            insert_data('consultorias', data, connection)


def extract_ediciones_revisiones(cod_rh, h3, connection):
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
                data['tipo_producto'] = li_split[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                blockquote_split = re.split('(Nombre comercial:)|(contrato/registro:)|(En:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            temp = blockquote_split[j+1].split(u'\xa0')
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            data['ano'] = int(re.findall(r'[0-9]{4}',temp[1])[0])
                            data['editorial'] = temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            temp2 = re.findall(r'p\.[0-9]+',temp[3])
                            if temp2:
                                data['paginas'] = int(temp2[0].replace('p.',''))
                        elif blockquote_split[j] == 'Nombre comercial:':
                            data['revista'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex:
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('ediciones_revisiones', data, connection)


def extract_eventos_cientificos(cod_rh, h3, nombre_completo, connection):
    
    table = h3.parent.parent.parent

    if table:
        eventos = table.find_all('tr', recursive=False)[1:]
        
        for evento in eventos:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if evento.find('img') else 'NO'

                trs = evento.find_all('tr')
                # Datos evento
                datos_evento = re.split('(Nombre del evento:)|(Tipo de evento:)|(Ámbito:)|(Realizado el:)', trs[0].text)
                for i in range(len(datos_evento)):
                    try:
                        if datos_evento[i] == 'Nombre del evento:':
                            data['nombre_evento'] = datos_evento[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif datos_evento[i] == 'Tipo de evento:':
                            data['tipo_evento'] = datos_evento[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif datos_evento[i] == 'Ámbito:':
                            data['ambito'] = datos_evento[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif datos_evento[i] == 'Realizado el:':
                            temp = re.split(',|(en)', datos_evento[i+1])
                            if temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""):
                                try:
                                    data['fecha_inicio'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                                except:
                                    None
                            if temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""):
                                try:
                                    data['fecha_fin'] = temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                                except:
                                    None

                            temp2 = temp[4].split('-')
                            data['ciudad'] = temp2[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            if len(temp2) == 2:
                                data['lugar'] = temp2[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex:
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))

                    # Extracción rol de cvlac_id analizado actualmente
                    lis = trs[3].find_all('li')
                    for li in lis:
                        if unidecode.unidecode(nombre_completo.upper()) in li.text:
                            data['rol'] = li.text.split('Rol en el evento:')[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            break
                    data['id'] = str(uuid.uuid1())
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('eventos_cientificos', data, connection)

            # Extracción participantes
            for li in lis:
                try:
                    data2 = dict()
                    participante = re.split('(Nombre:)|(Rol en el evento:)', li.text)
                    data2['nombre'] = participante[3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    data2['rol'] = participante[6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    data2['evento_id'] = data['id']
                except Exception as ex: 
                    f = open("logs.txt", "a")
                    f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
                insert_data('eventos_participantes', data2, connection)

            # Extracción productos
            lis = trs[1].find_all('li')
            for li in lis:
                try:
                    data_producto = dict()
                    producto = re.split('(Nombre del producto:)|(Tipo de producto:)', li.text)
                    data_producto['nombre'] = producto[3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    data_producto['tipo_producto'] = producto[6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    data_producto['evento_id'] = data['id']
                except Exception as ex: 
                    f = open("logs.txt", "a")
                    f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
                insert_data('eventos_productos', data_producto, connection)

            # Extracción instituciones
            lis = trs[2].find_all('li')
            for li in lis:
                try:
                    data_institucion = dict()
                    institucion = re.split('(Nombre de la institución:)|(Tipo de vinculación)', li.text)
                    data_institucion['nombre'] = institucion[3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    data_institucion['tipo_vinculacion'] = institucion[6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    data_institucion['evento_id'] = data['id']
                except Exception as ex: 
                    f = open("logs.txt", "a")
                    f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))                    
                insert_data('eventos_instituciones', data_institucion, connection)

def extract_informes(cod_rh, h3, connection):
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                temp = blockquote.text.split('En:')
                data['coautores'] = ", ".join(re.findall(r'([A-Z]{2,}[ [A-Z]{2,}]*)', temp[0]))
                data['ano'] = int(re.findall(r'[0-9]{4}', temp[1])[0])
                
                blockquote_split = re.split('(Informe de investigación:)|(En:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    if blockquote_split[j] == 'Informe de investigación:':
                        data['titulo'] = blockquote_split[j+2].replace('\n', '').replace('.','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))      
            insert_data('informes_investigacion', data, connection)


def extract_redes_conocimiento(cod_rh, h3, connection):
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')
        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre de la red)|(Tipo de red)|(Creada el:)', blockquote.text)

                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre de la red':
                            data['nombre'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Tipo de red':
                            data['tipo'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[i] == 'Creada el:':
                            temp = blockquote_split[i+1].split(u'\xa0')
                            try:
                                data['fecha_inicio'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except:
                                None
                            data['lugar'] = temp[2].split('en ')[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            participantes = re.findall(r'con\s*([0-9]*)\s*participantes', temp[3])[0]
                            if participantes != '':
                                data['participantes'] = int(participantes)
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))    
            insert_data('redes_conocimiento', data, connection)


def extract_audio(cod_rh, h3, connection):
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(En:)|(Formato:)|(Descripción:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'En:':
                            if i == 1:
                                data['coautores'] = ", ".join(re.findall(r'([A-Z]{2,}[ [A-Z]{2,}]*)', blockquote_split[i-1]))
                                data['titulo'] = re.sub(r'([A-Z]{2,}[ [A-Z]{2,}]*)','', blockquote_split[i-1]).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(', ','') 
                                try:
                                    data['fecha'] = "".join(blockquote_split[i+6].split()).replace('.','')
                                except:
                                    None
                            else:
                                data['lugar'] = blockquote_split[i+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Formato:':
                            data['formato'] = blockquote_split[i+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Descripción:':
                            data['descripcion'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Palabras:':
                            data['palabras'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Areas:':
                            data['areas'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Sectores:':
                            data['sectores'] = blockquote_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('audio', data, connection)


def extract_impreso(cod_rh, h3, connection):
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'

                blockquote_split = re.split('(Nombre)|(Tipo)|(Medio de circulación:)|(disponible en)|(en la fecha)|(en el ámbito)', blockquote.text)

                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre':
                            data['nombre'] = blockquote_split[i+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Tipo':
                            data['tipo'] = blockquote_split[i+5].split('-')[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1] 
                        elif blockquote_split[i] == 'Medio de circulación:':
                            data['medio_circulacion'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]                      
                        elif blockquote_split[i] == 'disponible en':
                            data['sitio_web'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")  
                        elif blockquote_split[i] == 'en la fecha':
                            try:
                                data['fecha'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                        elif blockquote_split[i] == 'en el ámbito':
                            data['ambito'] = blockquote_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('impresa', data, connection) 


def extract_multimedia(cod_rh, h3, connection):
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

                blockquote_split = re.split('(En:)|(Emisora:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] = ", ".join(re.findall(r'([A-Z]{2,}[ [A-Z]{2,}]*)', blockquote_split[j-1]))
                            data['nombre'] = re.sub(r'([A-Z]{2,}[ [A-Z]{2,}]*)','', blockquote_split[j-1]).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(', ','') 
                            
                            temp = blockquote_split[j+5].split(',')
                            data['ano'] = int(temp[2])
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Emisora:':
                            temp = blockquote_split[j+4].split(u'\xa0')
                            data['emisora'] = temp[0]
                            minutos = re.findall(r'[0-9]+', temp[1])
                            if minutos:
                                data['duracion'] = int(minutos[0])
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
            insert_data('multimedia', data, connection)


def extract_secuencia(cod_rh, h3, connection): 
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                
                blockquote_split = re.split('(En:)|(Emisora:)|(Base de datos donde está incluido el registro:)|(disponible en)|(Institución:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'En:':
                            if i == 1:
                                data['coautores'] = ", ".join(re.findall(r'([A-Z]{2,}[ [A-Z]{2,}]*)', blockquote_split[i-1]))
                                data['nombre'] = re.sub(r'([A-Z]{2,}[ [A-Z]{2,}]*)','', blockquote_split[i-1]).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(', ','') 
                                try:
                                    data['fecha'] = "".join(blockquote_split[i+8].split()).replace('.','')
                                except:
                                    None
                            else:
                                data['ciudad'] = blockquote_split[i+8].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[i] == 'Base de datos donde está incluido el registro:':
                            data['base_datos'] = blockquote_split[i+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'disponible en':
                            data['disponible_en'] = blockquote_split[i+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Institución:':
                            data['institucion'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")   
                        elif blockquote_split[i] == 'Palabras:':
                            data['palabras'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Areas:':
                            data['areas'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Sectores:':
                            data['sectores'] = blockquote_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))                                                                
            insert_data('secuencias_geneticas', data, connection)


def extract_contenido_virtual(cod_rh, h3, connection): 
    table = h3.parent.parent.parent

    if table:

        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre)|(Tipo)|(disponible en)|(Descripción:)', blockquote.text)

                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre':
                            data['titulo'] = blockquote_split[i+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Tipo':
                            data['tipo'] = blockquote_split[i+3].split('-')[2].split(',')[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            try:
                                data['fecha'] = re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}.*', blockquote_split[i+3])[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                        elif blockquote_split[i] == 'disponible en':   
                            data['disponible_en'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Descripción:':
                            data['descripcion'] = blockquote_split[i+1]
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('contenido_virtual', data, connection)


def extract_estrategias_conocimiento(cod_rh, h3, connection): 
    table = h3.parent.parent.parent

    if table:

        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre de la estrategia)|(Inicio en)|(Finalizó en :)', blockquote.text)

                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre de la estrategia':
                            data['nombre'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Inicio en':
                            try:
                                data['fecha_inicio'] = blockquote_split[i+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except:
                                None
                        elif blockquote_split[i] == 'Finalizó en :':
                            try:
                                data['fecha_fin'] = blockquote_split[i+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(',','')
                            except: 
                                None
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('estrategias_comunicacion', data, connection)


def extract_estrategias_pedagogicas(cod_rh, h3, connection): 
    table = h3.parent.parent.parent

    if table:

        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre de la estrategia)|(Inicio en)|(Finalizó en :)', blockquote.text)

                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre de la estrategia':
                            data['nombre'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Inicio en':
                            try:
                                data['fecha_inicio'] = blockquote_split[i+2].replace(',','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                        elif blockquote_split[i] == 'Finalizó en :':
                            try:
                                data['fecha_fin'] = blockquote_split[i+1].replace(',','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('estrategias_pedagogicas', data, connection)


def extract_espacios_participacion(cod_rh, h3, connection): 
    table = h3.parent.parent.parent

    if table:

        tds = table.find_all('td')[1:]

        for td in tds:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                td_split = re.split('(Nombre del espacio)|(Realizado el:)|(Finalizó en :)', td.text)

                for i in range(len(td_split)):
                    try:
                        if td_split[i] == 'Nombre del espacio':
                            data['nombre'] = td_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif td_split[i] == 'Realizado el:':
                            fechas = re.findall(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', td_split[i+2])
                            try:
                                data['fecha_inicio'] = fechas[0]
                                if len(fechas) > 1:
                                    data['fecha_fin'] = fechas[1]
                            except:
                                None

                            temp = re.split('en|Con', td_split[i+2])
                            data['ciudad'] = temp[1].replace('-','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            participantes = re.findall(r'[0-9]+', temp[2])[0]
                            if participantes != '':
                                data['participantes'] = int(participantes)
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('espacios_participacion', data, connection)
      

def extract_participacion_proyectos(cod_rh, h3, connection): 
    table = h3.parent.parent.parent

    if table:

        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(Nombre del proyecto)|(Inicio en)|(Finalizó en :)', blockquote.text)

                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Nombre del proyecto':
                            data['nombre'] = blockquote_split[i+3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'Inicio en':
                            try:
                                data['fecha_inicio'] = blockquote_split[i+2].replace(',','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                        elif blockquote_split[i] == 'Finalizó en :':
                            try:
                                data['fecha_fin'] = blockquote_split[i+1].replace(',','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            except:
                                None
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('participacion_proyectos', data, connection)
