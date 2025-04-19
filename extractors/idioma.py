from extractors.utils import *
from datetime import datetime 

import inspect


def extract(cod_rh, h3, connection):
    data = dict()
    data['cvlac_id'] = cod_rh
    
    table = h3.parent.parent.parent

    for tr in table.find_all('tr'):
        try:
            info_language = [a for a in tr.strings]
            if len(info_language) == 11 and info_language[1] != u'\xa0':
                data['idioma'] = info_language[1].replace('\xa0', '')
                data['habla'] = info_language[3]
                data['escribe'] = info_language[5]
                data['lee'] = info_language[7]
                data['entiende'] = info_language[9]
                insert_data('idioma', data, connection)
        except Exception as ex: 
            f = open("logs.txt", "a")
            f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))      




