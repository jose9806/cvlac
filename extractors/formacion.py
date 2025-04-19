from extractors.utils import *
from datetime import datetime 

import inspect


def extract_academic_formation(cod_rh, h3, connection):
    table = h3.parent.parent.parent
    if table:
        for b in table.find_all('b'):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh

                strs = [str_.strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "") or None for str_ in b.parent.strings]

                fechas = strs[3].split('-')
                try:
                    data['fecha_inicio'] = fechas[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace('de','')
                    data['fecha_fin'] = fechas[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace('de','')
                except:
                    None
                
                data['nivel_formacion'] = strs[0]
                institucion = strs[1]
                if institucion:
                    data['institucion'] = institucion
                    
                programa_academico = strs[2]
                if programa_academico:
                    data['programa_academico'] = programa_academico
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n']))
            insert_data('formacion_academica', data, connection)


def extract_complementary_formation(cod_rh, h3, connection):
    table = h3.parent.parent.parent

    if table:
        for b in table.find_all('b'):
            try:
                data = dict()
                data['cvlac_id'] = cod_rh
                strs = [str_.strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "") or None for str_ in b.parent.strings]

                fechas = strs[3].split('-')
                try:
                    data['fecha_inicio'] = fechas[0].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace('de','')
                    data['fecha_fin'] = fechas[1].strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace('de','')
                except:
                    None
                    
                data['nivel_formacion'] = strs[0]
                
                institucion = strs[1]
                if institucion:
                    data['institucion'] = institucion

                programa_academico = strs[2]
                if programa_academico:
                    data['programa_academico'] = programa_academico
            except Exception as ex: 
                f = open("logs.txt", "a")
                f.write(" -- ".join([data['cvlac_id'], str(datetime.now()), str(ex), inspect.currentframe().f_code.co_name, '\n'])) 
            insert_data('formacion_complementaria', data, connection)
