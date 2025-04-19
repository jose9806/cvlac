from extractors.utils import *
from datetime import datetime

import re
import inspect


def extract_articulos(cod_rh, h3, connection):
    
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

                blockquote_split = re.split('(En:)|(ISSN:)|(ed:)|(fasc.)|(DOI:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] = ", ".join(re.findall('[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['titulo'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            temp = blockquote_split[j+8].split(u'\xa0\n')
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['revista'] = temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'ISSN:':
                            data['issn'] = blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'ed:':
                            temp = blockquote_split[j+6].split(u'\n')
                            data['editorial'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['volumen'] = temp[1]
                        elif blockquote_split[j] == 'fasc.':
                            temp = blockquote_split[j+5].split('\n')
                            data['fasciculo'] = temp[0]
                            pagina_inicial = re.findall(r'[0-9]+' , temp[1])
                            if len(pagina_inicial):
                                data['pagina_inicial'] = int(pagina_inicial[0])
                            
                            pagina_final = re.findall(r'[0-9]+' , temp[2])
                            if len(pagina_final):
                                data['pagina_final'] = int(pagina_final[0])
                            data['ano'] = int(re.findall(r'[0-9]+' , temp[3])[0])
                        elif blockquote_split[j] == 'DOI:':
                            data['doi'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
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
            insert_data('articulos', data, connection)


def extract_capitulos(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'
                data['coautores'] = ""

                blockquote_split = re.split('(Tipo:)|(En:)|(ISBN:)|(ed:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)[2:]
                data['tipo'] = blockquote_split[6].split('\n')[0]
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'Tipo:':
                            data['coautores'] += re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[i-1])[0] + ", "
                        elif blockquote_split[i] == 'En:':
                            data['coautores'] +=  re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[i-2])[0] + ", "
                            data['titulo_capitulo'] = re.findall(r'".*"', blockquote_split[i-2])[0]
                            data['libro'] =  blockquote_split[i-2].split('\n')[-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['lugar_publicacion'] = blockquote_split[i+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'ISBN:':
                            data['isbn'] = blockquote_split[i+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[i] == 'ed:':
                            temp = blockquote_split[i+4].split('\n')
                            data['editorial'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        
                            volumen = re.findall(r'[0-9]+', temp[1])
                            if len(volumen):
                                data['volumen'] = volumen[0]

                            temp = blockquote_split[i+4].split('\n')
                            pagina_inicial = re.findall(r'[0-9]+', temp[2])
                            if len(pagina_inicial):
                                data['pagina_inicial'] = int(pagina_inicial[0])
                            
                            pagina_final = re.findall(r'[0-9]+', temp[3])
                            if len(pagina_final):
                                data['pagina_final'] = int(pagina_final[0])
                            data['ano'] = int(re.findall(r'[0-9]+', temp[5])[0])

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
            insert_data('capitulos_libro', data, connection)  


def extract_libros(cod_rh, h3, connection):
    
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
                blockquote_split = re.split('(En:)|(ed:)|(ISBN:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)

                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] =  ", ".join(re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j-1]))
                            data['titulo'] = re.findall(r'".*"', blockquote_split[j-1])[0].replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['lugar_publicacion'] = re.sub(r'[0-9]+','', blockquote_split[j+6]).replace('.','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(re.findall(r'[0-9]+', blockquote_split[j+6])[0])
                        elif blockquote_split[j] == 'ed:':
                            data['editorial'] = blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'ISBN:':
                            temp = blockquote_split[j+4].split('\n')
                            data['isbn'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['volumen'] = "".join(re.findall(r"[0-9]+", temp[1]))
                            data['paginas'] = "".join(re.findall(r"[0-9]+", temp[2]))               
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
            insert_data('libros', data, connection)              


def extract_working_papers(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(En:)', blockquote.text)
                for i in range(len(blockquote_split)):
                    try:
                        if blockquote_split[i] == 'En:':
                            data['nombre'] = re.findall(r'".*"', blockquote_split[i-1])[0]
                            data['ano'] = int(blockquote_split[i+1].split('\n')[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1])
                            paginas = re.findall(r'[0-9]+', blockquote_split[-2])
                            if len(paginas):
                                data['paginas'] = paginas
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('documentos_trabajo', data, connection)              


def extract_otra_produccion(cod_rh, h3, connection):
    
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

                blockquote_split = re.split('(En:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)

                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] =  ", ".join(re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j-1]))
                            data['titulo'] = re.findall(r'".*"', blockquote_split[j-1])[0].replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['ano'] = int(blockquote_split[j+4].split('\n')[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1])
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
            insert_data('otra_produccion', data, connection)              


def extract_textos_no_cientificas(cod_rh, h3, connection):
    
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

                blockquote_split = re.split('(En:)|(ISSN:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] =  ", ".join(re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j-1]))
                            data['titulo'] = re.findall(r'".*"', blockquote_split[j-1])[0].replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            
                            temp = blockquote_split[j+5].split('\n')
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                            data['ano'] = int(temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1])
                            data['revista'] = temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                        elif blockquote_split[j] == 'ISSN:':
                            temp = blockquote_split[j+4].split('\n')
                            data['issn'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            pagina_inicial = re.findall(r'[0-9]+', temp[1])
                            if len(pagina_inicial):
                                data['pagina_inicial'] = int(pagina_inicial[0])

                            pagina_final = re.findall(r'[0-9]+', temp[2])
                            if len(pagina_final):
                                data['pagina_final'] = int(pagina_final[0])
                            data['volumen'] = temp[3].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
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
            insert_data('textos_no_cientificas', data, connection)              


def extract_traducciones(cod_rh, h3, connection):
    
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

                blockquote_split = re.split('(En:)|(Idioma original:)|(Idioma traducción:)|(Autor:)|(Nombre original:)|(Palabras:)|(Areas:)|(Sectores:)', blockquotes[i].text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] =  ", ".join(re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j-1]))
                            data['nombre'] = re.findall(r'".*"', blockquote_split[j-1])[0]

                            temp = blockquote_split[j+8].split('\n')
                            data['pais'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                            data['ano'] = int(temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1])
                        elif blockquote_split[j] == 'Idioma original:':
                            data['idioma_original'] = blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Idioma traducción:':
                            data['idioma_traduccion'] = blockquote_split[j+6].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")        
                        elif blockquote_split[j] == 'Autor:':
                            data['autor'] = blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")      
                        elif blockquote_split[j] == 'Nombre original:':
                            data['volumen'] = re.findall(r'v.[0-9]*', blockquote_split[j+4])[0]                              
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
            insert_data('traducciones', data, connection)     


def extract_notas_cientificas(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'

                blockquote_split = re.split('(medio de divulgación:)|(Idioma original:)|(ISSN:)|(ed:)|(Sitio web:)|(DOI:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'medio de divulgación:':
                            temp = re.split(r'(".*")', blockquote_split[j-1])
                            data['coautores'] =  ", ".join(re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", temp[0]))
                            data['titulo_nota'] = temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['revista'] = temp[2][1:].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['medio_divulgacion'] = blockquote_split[j+9].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                        elif blockquote_split[j] == 'Idioma original:':
                            data['idioma_original'] = blockquote_split[j+8].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'ISSN:':
                            data['issn'] = blockquote_split[j+7].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")     
                        elif blockquote_split[j] == 'ed:':
                            temp = blockquote_split[j+6].split('\n')        
                            data['editorial'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['volumen'] = temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")  
                            data['fasc'] = temp[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")  
                            data['pagina_inicial'] = int(re.findall(r'[0-9]+', temp[3])[0])
                            data['pagina_final'] = int(re.findall(r'[0-9]+', temp[4])[0])
                            data['ano'] = int(re.findall(r'[0-9]+', temp[5])[0])
                        elif blockquote_split[j] == 'Sitio web:':
                            data['sitio_web'] = blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")  
                        elif blockquote_split[j] == 'DOI:':
                            data['doi'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")                                     
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
            insert_data('notas_cientificas', data, connection) 
