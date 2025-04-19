from extractors.utils import *

import inspect


def extract(cod_rh, h3, connection):

    table = h3.parent.parent.parent
    if table:
        links = table.find_all('a')
        for link in links:
            try:
                data = {'red': link.get_text(), 'link': link['href'], 'cvlac_id': cod_rh}
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('redes_sociales', data, connection)
            