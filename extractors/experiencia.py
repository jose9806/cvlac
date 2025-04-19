from extractors.utils import *
from datetime import datetime

import inspect
import re


def extract(cod_rh, h3, connection):
    table = h3.parent.parent.parent

    if table:
        institucion_actual = ''
        for b in table.find_all('b'):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                if b.text != '':
                    institucion_actual = b.text
                
                strs = [str_.strip('') or None for str_ in b.parent.strings]
                data['institucion'] = institucion_actual
                for i in range(len(strs)):
                    try:
                        if strs[i] == 'Dedicación: ':
                            temp_dates = strs[i+1].split('\n')
                            data['dedicacion'] = temp_dates[0].replace(u'\xa0', ' ')
                            ano_inicio = re.findall(r'[0-9]{4}', temp_dates[1])
                            if len(ano_inicio):
                                data['ano_inicio'] = int(ano_inicio[0])
                            ano_fin = re.findall(r'[0-9]{4}',temp_dates[2])
                            if len(ano_fin):
                                data['ano_fin'] = int(ano_fin[0])
                            break
                    except Exception as ex: 
                        f = open("logs.txt", "a")
                        f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('experiencia', data, connection)