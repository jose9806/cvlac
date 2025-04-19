from extractors.utils import *
from datetime import datetime

import inspect


def extract(cod_rh, h3, connection):
    data = dict()
    data['cvlac_id'] = cod_rh
    
    table = h3.parent.parent.parent

    for li in table.find_all('li'):
        try:
            strs = [str_ for str_ in li]
            
            data['linea_investigacion'] = strs[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")[:-1]
            data['activa'] = strs[2]
        except Exception as ex: 
            f = open("logs.txt", "a")
            f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
        insert_data('lineas_investigacion', data, connection)