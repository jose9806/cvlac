from extractors.utils import *
from datetime import datetime

import re
import inspect


def extract(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        blockquotes = table.find_all('blockquote')

        for blockquote in blockquotes:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                blockquote_split = re.split('(En:)|(finalidad:)|(Palabras:)|(Areas:)|(Sectores:)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'En:':
                            data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                            data['nombre'] = re.split("[A-Z]{2,},", blockquote_split[j-1])[-1][:-2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")

                            temp = re.split(r'([0-9]+)', blockquote_split[j+5].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", ""))
                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0]).strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
                            data['ano']  = int(temp[1])               
                        elif blockquote_split[j] == 'finalidad:':
                            data['finalidad'] = blockquote_split[j+4].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
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
            insert_data('demas_trabajos', data, connection)