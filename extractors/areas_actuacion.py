from extractors.utils import *
from datetime import datetime

import inspect

def extract(cod_rh, h3, connection):
    data = dict()
    data['cvlac_id'] = cod_rh
    
    table = h3.parent.parent.parent
    if table:

        for li in table.find_all('li'):
            try:
                text = li.text.split('--')
                data['gran_area'] = text[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                data['area'] = text[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                data['especialidad'] = text[2].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('areas_actuacion', data, connection)


