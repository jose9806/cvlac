from extractors.utils import *


def extract(cod_rh, html, connection):
    data = dict()
    data['cvlac_id'] = cod_rh

    table = get_table(html, {'name': 'datos_generales'})

    if table:
        categoria = get_text_next_tag(table, 'Categoría', 'td')
        if categoria:
            data['categoria'] = " ".join(categoria.split())

        nombre_completo = get_text_next_tag(table, 'Nombre', 'td')
        if nombre_completo:
            data['nombre_completo'] = nombre_completo.strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "").replace(u'\xa0',' ')

        nombre_citaciones = get_text_next_tag(table, 'Nombre en citaciones', 'td')
        if nombre_citaciones:
            data['nombre_citaciones'] = nombre_citaciones

        nacionalidad = get_text_next_tag(table, 'Nacionalidad', 'td')
        if nacionalidad:
            data['nacionalidad'] = nacionalidad

        genero = get_text_next_tag(table, 'Sexo', 'td')
        if genero:
            data['genero'] = genero
    
        codigo_orcid = get_href(table, 'Código ORCID')
        if codigo_orcid:
            data['codigo_orcid'] = codigo_orcid

        author_id_scopus = get_href(table, 'Author ID SCOPUS')
        if author_id_scopus:
            data['author_id_scopus'] = author_id_scopus

        message_text = table.find('b')
        if message_text and message_text.text == 'Par evaluador reconocido por Minciencias.':
            data['reconocido_colciencias'] = "Sí"
            
        if nombre_completo:
            insert_data('identificacion', data, connection)
            return(data['nombre_completo'])