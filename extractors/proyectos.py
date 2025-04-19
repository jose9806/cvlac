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
                data['chulo'] = 'SI' if blockquote.find('img') else 'NO'

                blockquote_split = re.split('(Tipo de proyecto:)|(Inicio:)|(Fin:)|(Duración)|(Resumen)', blockquote.text)
                for j in range(len(blockquote_split)):
                    try:
                        if blockquote_split[j] == 'Tipo de proyecto:':
                            temp = blockquote_split[j+5].split('\n')
                            data['tipo'] = temp[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                            data['nombre'] = temp[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Inicio:':
                            try:
                                data['fecha_inicio'] = "".join(blockquote_split[j+4].split())
                            except:
                                None
                        elif blockquote_split[j] == 'Fin:':
                            try:
                                data['fecha_fin'] = "".join(blockquote_split[j+3].split())
                            except:
                                None
                        elif blockquote_split[j] == 'Duración':
                            data['duracion'] = blockquote_split[j+2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                        elif blockquote_split[j] == 'Resumen':
                            data['resumen'] = blockquote_split[j+1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")    
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('proyectos', data, connection)