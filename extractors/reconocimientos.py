from extractors.utils import *
from datetime import datetime

import re
import inspect


def extract(cod_rh, h3, connection):
    
    table = h3.parent.parent.parent

    if table:
        lis = table.find_all('li')

        for li in lis:
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                li_split = re.split(',| - ', li.text)
                data['nombre'] = li_split[0]
                data['institucion'] = ", ".join(li_split[1:-1])
                fecha = li_split[-1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace('de','')
                try:
                    if fecha:
                        data['fecha'] = fecha
                except:
                    None
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('reconocimientos', data, connection)