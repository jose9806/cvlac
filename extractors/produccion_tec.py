from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ProduccionTecnologicaExtractor:
    """
    Clase para extraer información relacionada con producción tecnológica del investigador.
    """
    
    @staticmethod
    def extract_maps(cod_rh, h3, connection):
        """
        Extrae información sobre cartas, mapas y similares.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para cartas/mapas en {cod_rh}")
                return

            lis = table.find_all('li')
            blockquotes = table.find_all('blockquote')

            if len(lis) != len(blockquotes):
                module_logger.warning(f"Número desigual de elementos li y blockquote en cartas/mapas: {cod_rh}")

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer información del elemento li
                    data['chulo'] = "SI" if lis[i].find('img') else "NO" 
                    li_split = lis[i].text.split('-')
                    if len(li_split) > 2:
                        data['tipo'] = ProduccionTecnologicaExtractor._clean_text(li_split[2])

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                            blockquotes[i].text
                        )
                        
                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == 'Nombre comercial:':
                                    if j > 0:
                                        data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                        nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                        if len(nombre_split) > 0:
                                            data['nombre_producto'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                elif blockquote_split[j] == 'En:':
                                    if j+4 < len(blockquote_split):
                                        temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4]))
                                        if len(temp) > 0:
                                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                        if len(temp) > 1:
                                            try:
                                                data['ano'] = int(temp[1])
                                            except (ValueError, TypeError):
                                                module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                                elif blockquote_split[j] == 'Palabras:':
                                    if j+3 < len(blockquote_split):
                                        data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                                elif blockquote_split[j] == 'Areas:':
                                    if j+2 < len(blockquote_split):
                                        data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                                elif blockquote_split[j] == 'Sectores:':
                                    if j+1 < len(blockquote_split):
                                        data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                            except Exception as ex:
                                module_logger.error(f"Error extrayendo datos de carta/mapa para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    # Insertar en la base de datos
                    insert_data('cartas_mapas', data, connection)
                    module_logger.debug(f"Carta/mapa insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando carta/mapa {i} para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_maps para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_conceptos(cod_rh, h3, connection):
        """
        Extrae información sobre conceptos técnicos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para conceptos técnicos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    blockquote_split = re.split(
                        '(Institución solicitante:)|(En:)|(Fecha solicitud:)|(Fecha de envío:)|'
                        '(Número consecutivo del concepto:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Institución solicitante:':
                                if j-1 >= 0:
                                    titulo_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(titulo_split) > 0:
                                        data['titulo'] = ProduccionTecnologicaExtractor._clean_text(titulo_split[-1][:-1])
                                
                                if j+5 < len(blockquote_split):
                                    data['institucion'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+5][:-2])
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    data['ciudad'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4][:-2])
                            elif blockquote_split[j] == 'Fecha solicitud:':
                                if j+3 < len(blockquote_split):
                                    try:
                                        data['fecha_solicitud'] = "".join(blockquote_split[j+3].split()).replace('y','').strip().replace("'",'"').replace("\t'",'"').replace("  ", "").replace("\n", "").replace("\r", "")
                                    except Exception as ex:
                                        module_logger.warning(f"Error extrayendo fecha_solicitud para {cod_rh}: {str(ex)}")
                            elif blockquote_split[j] == 'Fecha de envío:':
                                if j+2 < len(blockquote_split):
                                    try:
                                        data['fecha_envio'] = "".join(blockquote_split[j+2].split()).replace('.','')
                                    except Exception as ex:
                                        module_logger.warning(f"Error extrayendo fecha_envio para {cod_rh}: {str(ex)}")
                            elif blockquote_split[j] == 'Número consecutivo del concepto:':
                                if j+1 < len(blockquote_split):
                                    data['numero'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de concepto técnico para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('conceptos_tecnicos', data, connection)
                    module_logger.debug(f"Concepto técnico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando concepto técnico para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_conceptos para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_disenos_industrial(cod_rh, h3, connection):
        """
        Extrae información sobre diseños industriales.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para diseños industriales en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(nombre_split) > 0:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = blockquote_split[j+4].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 2:
                                        try:
                                            data['ano'] = int(temp[2])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de diseño industrial para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('diseno_industrial', data, connection)
                    module_logger.debug(f"Diseño industrial insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando diseño industrial para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_disenos_industrial para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_empresa_base_tec(cod_rh, h3, connection):
        """
        Extrae información sobre empresas de base tecnológica.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para empresas base tecnológica en {cod_rh}")
                return

            lis = table.find_all('li')
            blockquotes = table.find_all('blockquote')

            if len(lis) != len(blockquotes):
                module_logger.warning(f"Número desigual de elementos li y blockquote en empresas base tecnológica: {cod_rh}")

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer información del elemento li
                    data['chulo'] = "SI" if lis[i].parent.parent.find('img') else "NO" 
                    li_split = lis[i].text.split(' - ')
                    if len(li_split) > 2:
                        data['tipo'] = li_split[2]

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            '(Nit)|(Registrado ante la c´mara el:)|(Palabras:)|(Areas:)|(Sectores:)', 
                            blockquotes[i].text
                        )
                        
                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == 'Nit':
                                    if j > 0:
                                        data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                        nombre = "".join(re.sub(r'[A-Z]{2,}[ [A-Z]{2,}]*', '', blockquote_split[:j][0]))
                                        nombre = ProduccionTecnologicaExtractor._clean_text(nombre)
                                        nombre = re.sub('^,', '', nombre)
                                        nombre = re.sub(',$', '', nombre)
                                        data['nombre'] = nombre
                                    
                                    if j+5 < len(blockquote_split):
                                        data['nit'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+5].replace(',',''))
                                elif blockquote_split[j] == 'Registrado ante la c´mara el:':
                                    if j+4 < len(blockquote_split):
                                        try:
                                            data['fecha_registro'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4]).replace(',','')
                                        except Exception as ex:
                                            module_logger.warning(f"Error extrayendo fecha_registro para {cod_rh}: {str(ex)}")
                                elif blockquote_split[j] == 'Palabras:':
                                    if j+3 < len(blockquote_split):
                                        data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                                elif blockquote_split[j] == 'Areas:':
                                    if j+2 < len(blockquote_split):
                                        data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                                elif blockquote_split[j] == 'Sectores:':
                                    if j+1 < len(blockquote_split):
                                        data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                            except Exception as ex:
                                module_logger.error(f"Error extrayendo datos de empresa base tecnológica para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('empresas_base_tecnologica', data, connection)
                    module_logger.debug(f"Empresa base tecnológica insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando empresa base tecnológica {i} para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_empresa_base_tec para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_esquemas_trazado(cod_rh, h3, connection):
        """
        Extrae información sobre esquemas de trazado de circuitos integrados.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para esquemas de trazado en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre = "".join(re.sub(r'[A-Z]{2,}[ [A-Z]{2,}]*', '', blockquote_split[:j][0]))
                                    nombre = ProduccionTecnologicaExtractor._clean_text(nombre)
                                    nombre = re.sub('^,', '', nombre)
                                    nombre = re.sub(',$', '', nombre)
                                    data['nombre'] = nombre
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = blockquote_split[j+4].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 2:
                                        try:
                                            data['ano'] = int(temp[2])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de esquema de trazado para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('esquemas_trazado', data, connection)
                    module_logger.debug(f"Esquema de trazado insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando esquema de trazado para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_esquemas_trazado para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_informes(cod_rh, h3, connection):
        """
        Extrae información sobre informes técnicos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para informes técnicos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(nombre_split) > 0:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                            elif blockquote_split[j] == 'contrato/registro:':
                                if j+5 < len(blockquote_split):
                                    contratos = blockquote_split[j+5].split(',')
                                    if len(contratos) > 0:
                                        data['contrato_registro'] = contratos[0]
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = blockquote_split[j+4].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 2:
                                        try:
                                            data['ano'] = int(temp[2])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de informe técnico para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('informes_tecnicos', data, connection)
                    module_logger.debug(f"Informe técnico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando informe técnico para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_informes para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_innovacion_proc(cod_rh, h3, connection):
        """
        Extrae información sobre innovación de proceso o procedimiento.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para innovación de proceso en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    split_lines = blockquote_split[j-1].split('\n')
                                    if len(split_lines) > 1:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-2][:-1])
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = blockquote_split[j+4].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 2:
                                        try:
                                            data['ano'] = int(temp[2])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de innovación de proceso para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('innovacion_procesos', data, connection)
                    module_logger.debug(f"Innovación de proceso insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando innovación de proceso para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_innovacion_proc para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_innovacion_gestion(cod_rh, h3, connection):
        """
        Extrae información sobre innovación generada en la gestión empresarial.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para innovación en gestión empresarial en {cod_rh}")
                return

            bs = [b for b in table.find_all('b') if b.parent.name == 'td']
            blockquotes = table.find_all('blockquote')

            if len(bs) != len(blockquotes):
                module_logger.warning(f"Número desigual de elementos b y blockquote en innovación en gestión empresarial: {cod_rh}")

            for i in range(len(bs)):
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer información del elemento b
                    b_split = bs[i].text.split(' - ')
                    if len(b_split) > 2:
                        data['tipo'] = b_split[2]

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                            blockquotes[i].text
                        )
                        
                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == 'Nombre comercial:':
                                    if j > 0:
                                        data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                        split_lines = blockquote_split[j-1].split('\n')
                                        if len(split_lines) > 1:
                                            data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-2][:-1])
                                elif blockquote_split[j] == 'En:':
                                    if j+4 < len(blockquote_split):
                                        temp = blockquote_split[j+4].split(',')
                                        if len(temp) > 0:
                                            data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                        if len(temp) > 2:
                                            try:
                                                data['ano'] = int(temp[2])
                                            except (ValueError, TypeError):
                                                module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                                elif blockquote_split[j] == 'Palabras:':
                                    if j+3 < len(blockquote_split):
                                        data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                                elif blockquote_split[j] == 'Areas:':
                                    if j+2 < len(blockquote_split):
                                        data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                                elif blockquote_split[j] == 'Sectores:':
                                    if j+1 < len(blockquote_split):
                                        data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                            except Exception as ex:
                                module_logger.error(f"Error extrayendo datos de innovación en gestión empresarial para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('innovacion_gestion', data, connection)
                    module_logger.debug(f"Innovación en gestión empresarial insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando innovación en gestión empresarial {i} para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_innovacion_gestion para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_variedad_animal(cod_rh, h3, connection):
        """
        Extrae información sobre variedad animal.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para variedad animal en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    split_lines = blockquote_split[j-1].split('\n')
                                    if len(split_lines) > 1:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-2][:-1])
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = blockquote_split[j+4].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 2:
                                        try:
                                            data['ano'] = int(temp[2])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de variedad animal para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('variedad_animal', data, connection)
                    module_logger.debug(f"Variedad animal insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando variedad animal para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_variedad_animal para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_poblaciones_mej(cod_rh, h3, connection):
        """
        Extrae información sobre poblaciones mejoradas de razas pecuarias.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para poblaciones mejoradas en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    blockquote_split = re.split(
                        '(En:)|(Número o consecutivo del certificado del Ministerio de Agricultura:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'En:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    split_lines = blockquote_split[j-1].split('\n')
                                    if len(split_lines) > 1:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-2][:-1])
                                
                                if j+2 < len(blockquote_split):
                                    temp = blockquote_split[j+2].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 1:
                                        try:
                                            data['ano'] = int(temp[1])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                            elif blockquote_split[j] == 'Número o consecutivo del certificado del Ministerio de Agricultura:':
                                if j+1 < len(blockquote_split):
                                    data['numero_certificado'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de población mejorada para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('poblaciones_mejoradas', data, connection)
                    module_logger.debug(f"Población mejorada insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando población mejorada para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_poblaciones_mej para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_variedad_vegetal(cod_rh, h3, connection):
        """
        Extrae información sobre variedad vegetal.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para variedad vegetal en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Ciclo:)|(Estado de la variedad:)|(Nombre comercial:)|(contrato/registro:)|'
                        '(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Ciclo:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    split_lines = blockquote_split[j-1].split('\n')
                                    if len(split_lines) > 1:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-2][:-1])
                                
                                if j+8 < len(blockquote_split):
                                    data['ciclo'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+8])[:-1]
                            elif blockquote_split[j] == 'Estado de la variedad:':
                                if j+7 < len(blockquote_split):
                                    data['estado'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+7])[:-1]
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = blockquote_split[j+4].split(',')
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(temp[0])
                                    if len(temp) > 2:
                                        try:
                                            data['ano'] = int(temp[2])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[2]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de variedad vegetal para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('variedad_vegetal', data, connection)
                    module_logger.debug(f"Variedad vegetal insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando variedad vegetal para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_variedad_vegetal para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_registro_cientifico(cod_rh, h3, connection):
        """
        Extrae información sobre nuevos registros científicos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para registros científicos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(En:)|(Nombre de base de datos donde está incluido el registro:)|(disponible en)|'
                        '(Institución que emite el registro:)|(Institución certificadora:)|(artículo vinculado:)|'
                        '(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'En:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    split_lines = blockquote_split[j-1].split('\n')
                                    if len(split_lines) > 2:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-3][:-1])
                                    if len(split_lines) > 1:
                                        ano_match = re.findall(r'[0-9]+', split_lines[-2])
                                        if ano_match:
                                            try:
                                                data['ano'] = int(ano_match[0])
                                            except (ValueError, TypeError):
                                                module_logger.warning(f"No se pudo convertir el año a entero: {ano_match[0]}")
                                
                                if j+9 < len(blockquote_split):
                                    data['pais'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+9])
                            elif blockquote_split[j] == 'Nombre de base de datos donde está incluido el registro:':
                                if j+8 < len(blockquote_split):
                                    data['base_datos'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+8][:-2])
                            elif blockquote_split[j] == 'disponible en':
                                if j+7 < len(blockquote_split):
                                    data['sitio_web'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+7][:-2].replace(',\xa0\n', ''))
                            elif blockquote_split[j] == 'Institución que emite el registro:':
                                if j+6 < len(blockquote_split):
                                    data['institucion_registro'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+6][:-2])
                            elif blockquote_split[j] == 'Institución certificadora:':
                                if j+5 < len(blockquote_split):
                                    data['institucion_certificadora'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+5][:-2])
                            elif blockquote_split[j] == 'artículo vinculado:':
                                if j+4 < len(blockquote_split):
                                    data['articulo_vinculado'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4])
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de registro científico para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('registro_cientifico', data, connection)
                    module_logger.debug(f"Registro científico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando registro científico para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_registro_cientifico para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_planta_piloto(cod_rh, h3, connection):
        """
        Extrae información sobre planta piloto.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para planta piloto en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(nombre_split) > 0:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                
                                if j+6 < len(blockquote_split):
                                    data['nombre_comercial'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+6])
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4]))
                                    if len(temp) > 0:
                                        data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                    if len(temp) > 1:
                                        try:
                                            data['ano'] = int(temp[1])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de planta piloto para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('plantas_piloto', data, connection)
                    module_logger.debug(f"Planta piloto insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando planta piloto para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_planta_piloto para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_productos_nutra(cod_rh, h3, connection):
        """
        Extrae información sobre productos nutracéuticos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para productos nutracéuticos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Fecha de obtención del registro del INVIMA:)|(En:)|(Titular del registro:)|'
                        '(Número de registro:)|(proyecto vinculado:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Fecha de obtención del registro del INVIMA:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(nombre_split) > 0:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                
                                if j+5 < len(blockquote_split):
                                    try:
                                        data['fecha_registro'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+5])
                                    except Exception as ex:
                                        module_logger.warning(f"Error extrayendo fecha_registro para {cod_rh}: {str(ex)}")
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    data['pais'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4])
                            elif blockquote_split[j] == 'Titular del registro:':
                                if j+3 < len(blockquote_split):
                                    data['titular'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])[:-1]
                            elif blockquote_split[j] == 'Número de registro:':
                                if j+2 < len(blockquote_split):
                                    registro_split = blockquote_split[j+2].split('\xa0')
                                    if len(registro_split) > 0:
                                        data['numero_registro'] = ProduccionTecnologicaExtractor._clean_text(registro_split[0])
                            elif blockquote_split[j] == 'proyecto vinculado:':
                                if j+1 < len(blockquote_split):
                                    data['proyecto_vinculado'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de producto nutracéutico para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('productos_nutraceuticos', data, connection)
                    module_logger.debug(f"Producto nutracéutico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando producto nutracéutico para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_productos_nutra para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_productos_tec(cod_rh, h3, connection):
        """
        Extrae información sobre productos tecnológicos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para productos tecnológicos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer tipo del producto
                    li_element = blockquote.parent.parent.previous_sibling.previous_sibling
                    if li_element:
                        li_split = li_element.get_text().split('-')
                        if len(li_split) > 2:
                            data['tipo'] = li_split[2].strip()
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(nombre_split) > 0:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                
                                if j+6 < len(blockquote_split):
                                    data['nombre_comercial'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+6])
                            elif blockquote_split[j] == 'En:':
                                if j+4 < len(blockquote_split):
                                    temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4]))
                                    if len(temp) > 0:
                                        data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                    if len(temp) > 1:
                                        try:
                                            data['ano'] = int(temp[1])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de producto tecnológico para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('productos_tecnologicos', data, connection)
                    module_logger.debug(f"Producto tecnológico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando producto tecnológico para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_productos_tec para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_prototipos(cod_rh, h3, connection):
        """
        Extrae información sobre prototipos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para prototipos en {cod_rh}")
                return

            bs = [b for b in table.find_all('b') if b.parent.name == 'td']
            blockquotes = table.find_all('blockquote')

            if len(bs) != len(blockquotes):
                module_logger.warning(f"Número desigual de elementos b y blockquote en prototipos: {cod_rh}")

            for i in range(len(bs)):
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer información del elemento b
                    if i < len(blockquotes):
                        data['chulo'] = 'SI' if blockquotes[i].parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    b_split = bs[i].text.split('-')
                    if len(b_split) > 2:
                        data['tipo'] = ProduccionTecnologicaExtractor._clean_text(b_split[2])

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            '(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)', 
                            blockquotes[i].text
                        )
                        
                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == 'Nombre comercial:':
                                    if j > 0:
                                        data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                        nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                        if len(nombre_split) > 0:
                                            data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                    
                                    if j+6 < len(blockquote_split):
                                        data['nombre_comercial'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+6])
                                elif blockquote_split[j] == 'En:':
                                    if j+4 < len(blockquote_split):
                                        temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4]))
                                        if len(temp) > 0:
                                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                        if len(temp) > 1:
                                            try:
                                                data['ano'] = int(temp[1])
                                            except (ValueError, TypeError):
                                                module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                                elif blockquote_split[j] == 'Palabras:':
                                    if j+3 < len(blockquote_split):
                                        data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                                elif blockquote_split[j] == 'Areas:':
                                    if j+2 < len(blockquote_split):
                                        data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                                elif blockquote_split[j] == 'Sectores:':
                                    if j+1 < len(blockquote_split):
                                        data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                            except Exception as ex:
                                module_logger.error(f"Error extrayendo datos de prototipo para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('prototipos', data, connection)
                    module_logger.debug(f"Prototipo insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando prototipo {i} para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_prototipos para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_normas(cod_rh, h3, connection):
        """
        Extrae información sobre normas y regulaciones.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para normas y regulaciones en {cod_rh}")
                return

            lis = table.find_all('li')
            blockquotes = table.find_all('blockquote')

            if len(lis) != len(blockquotes):
                module_logger.warning(f"Número desigual de elementos li y blockquote en normas y regulaciones: {cod_rh}")

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer información del elemento li
                    data['chulo'] = "SI" if lis[i].find('img') else "NO" 
                    li_split = lis[i].text.split('-')
                    if len(li_split) > 2:
                        data['tipo'] = ProduccionTecnologicaExtractor._clean_text(li_split[2])

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            '(Nombre comercial:)|(contrato/registro:)|(En:)|(ed:)|(regulación:)|(tipo:)|'
                            '(Palabras:)|(Areas:)|(Sectores:)', 
                            blockquotes[i].text
                        )
                        
                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == 'Nombre comercial:':
                                    if j > 0:
                                        data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                        nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                        if len(nombre_split) > 0:
                                            data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                    
                                    if j+9 < len(blockquote_split):
                                        data['nombre_comercial'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+9])
                                elif blockquote_split[j] == 'En:':
                                    if j+7 < len(blockquote_split):
                                        temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+7]))
                                        if len(temp) > 0:
                                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                        if len(temp) > 1:
                                            try:
                                                data['ano'] = int(temp[1])
                                            except (ValueError, TypeError):
                                                module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                                elif blockquote_split[j] == 'Palabras:':
                                    if j+3 < len(blockquote_split):
                                        data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                                elif blockquote_split[j] == 'Areas:':
                                    if j+2 < len(blockquote_split):
                                        data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                                elif blockquote_split[j] == 'Sectores:':
                                    if j+1 < len(blockquote_split):
                                        data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                            except Exception as ex:
                                module_logger.error(f"Error extrayendo datos de norma y regulación para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('normas_regulaciones', data, connection)
                    module_logger.debug(f"Norma y regulación insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando norma y regulación {i} para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_normas para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_protocolos_vigilancia(cod_rh, h3, connection):
        """
        Extrae información sobre protocolos de vigilancia epidemiológica.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para protocolos de vigilancia en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(En:)|(Institución:)|(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'En:':
                                if j == 1 and j-1 >= 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    split_lines = blockquote_split[j-1].split('\n')
                                    if len(split_lines) > 1:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(split_lines[-2][:-1])
                                    
                                    try:
                                        if j+5 < len(blockquote_split):
                                            data['fecha'] = "".join(blockquote_split[j+5].split()).replace('.','')
                                    except Exception as ex:
                                        module_logger.warning(f"Error extrayendo fecha para {cod_rh}: {str(ex)}")
                                else:
                                    if j+5 < len(blockquote_split):
                                        data['ciudad'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+5])
                            elif blockquote_split[j] == 'Institución:':
                                if j+4 < len(blockquote_split):
                                    data['institucion'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4])
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de protocolo de vigilancia para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('protocolos_vigilancia', data, connection)
                    module_logger.debug(f"Protocolo de vigilancia insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando protocolo de vigilancia para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_protocolos_vigilancia para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_reglamentos(cod_rh, h3, connection):
        """
        Extrae información sobre reglamentos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para reglamentos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.parent.parent.previous_sibling.previous_sibling.find('img') else 'NO'
                    
                    blockquote_split = re.split(
                        '(Nombre comercial:)|(contrato/registro:)|(En:)|(ed:)|(regulación:)|(tipo:)|'
                        '(Palabras:)|(Areas:)|(Sectores:)', 
                        blockquote.text
                    )
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'Nombre comercial:':
                                if j > 0:
                                    data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                    nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                    if len(nombre_split) > 0:
                                        data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                
                                if j+9 < len(blockquote_split):
                                    data['nombre_comercial'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+9])
                            elif blockquote_split[j] == 'En:':
                                if j+7 < len(blockquote_split):
                                    temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+7]))
                                    if len(temp) > 0:
                                        data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                    if len(temp) > 1:
                                        try:
                                            data['ano'] = int(temp[1])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                            elif blockquote_split[j] == 'Palabras:':
                                if j+3 < len(blockquote_split):
                                    data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                            elif blockquote_split[j] == 'Areas:':
                                if j+2 < len(blockquote_split):
                                    data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                            elif blockquote_split[j] == 'Sectores:':
                                if j+1 < len(blockquote_split):
                                    data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de reglamento para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('reglamentos', data, connection)
                    module_logger.debug(f"Reglamento insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando reglamento para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_reglamentos para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def extract_signos(cod_rh, h3, connection):
        """
        Extrae información sobre signos distintivos.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para signos distintivos en {cod_rh}")
                return

            blockquotes = table.find_all('blockquote')
            
            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data['chulo'] = 'SI' if blockquote.find('img') else 'NO'
                    
                    blockquote_split = re.split('(En)|(Registro:)|(Titular:)', blockquote.text)
                    
                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == 'En':
                                if j-1 >= 0:
                                    data['nombre'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j-1])[:-1]
                                
                                if j+3 < len(blockquote_split):
                                    temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3]))
                                    if len(temp) > 0:
                                        data['pais'] = ProduccionTecnologicaExtractor._clean_text(re.sub(r',\xa0\n\s+,', '', temp[0]))[:-1]
                                    if len(temp) > 1:
                                        try:
                                            data['ano'] = int(temp[1])
                                        except (ValueError, TypeError):
                                            module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                            elif blockquote_split[j] == 'Registro:':
                                if j+2 < len(blockquote_split):
                                    data['registro'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])[:-1]
                            elif blockquote_split[j] == 'Titular:':
                                if j+1 < len(blockquote_split):
                                    data['titular'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                        except Exception as ex:
                            module_logger.error(f"Error extrayendo datos de signo distintivo para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('signos_distintivos', data, connection)
                    module_logger.debug(f"Signo distintivo insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando signo distintivo para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_signos para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    @staticmethod
    def extract_software(cod_rh, h3, connection):
        """
        Extrae información sobre software.
        
        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para software en {cod_rh}")
                return

            bs = [b for b in table.find_all('b') if b.parent.name == 'td']
            blockquotes = table.find_all('blockquote')

            if len(bs) != len(blockquotes):
                module_logger.warning(f"Número desigual de elementos b y blockquote en software: {cod_rh}")

            for i in range(len(bs)):
                try:
                    data = {"cvlac_id": cod_rh}
                    
                    # Extraer información del elemento b
                    b_split = bs[i].text.split(' - ')
                    if len(b_split) > 2:
                        data['tipo'] = b_split[2]

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            '(Nombre comercial:)|(contrato/registro:)|(En:)|(plataforma:)|(ambiente:)|'
                            '(Palabras:)|(Areas:)|(Sectores:)', 
                            blockquotes[i].text
                        )
                        
                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == 'Nombre comercial:':
                                    if j > 0:
                                        data['coautores'] = ", ".join(re.findall(r'[A-Z]{2,}[ [A-Z]{2,}]*', blockquote_split[:j][0]))
                                        nombre_split = re.split("[A-Z]{2,},", blockquote_split[j-1])
                                        if len(nombre_split) > 0:
                                            data['nombre'] = ProduccionTecnologicaExtractor._clean_text(nombre_split[-1][:-1])
                                    
                                    if j+8 < len(blockquote_split):
                                        data['nombre_comercial'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+8])
                                elif blockquote_split[j] == 'contrato/registro:':
                                    if j+7 < len(blockquote_split):
                                        split_lines = blockquote_split[j+7].split('\n')
                                        if len(split_lines) > 0:
                                            data['contrato_registro'] = split_lines[0][:-1]
                                elif blockquote_split[j] == 'En:':
                                    if j+6 < len(blockquote_split):
                                        temp = re.split(r'([0-9]+)', ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+6]))
                                        if len(temp) > 0:
                                            data['pais'] = re.sub(r',\xa0\n\s+,', '', temp[0])
                                        if len(temp) > 1:
                                            try:
                                                data['ano'] = int(temp[1])
                                            except (ValueError, TypeError):
                                                module_logger.warning(f"No se pudo convertir el año a entero: {temp[1]}")
                                elif blockquote_split[j] == 'plataforma:':
                                    if j+5 < len(blockquote_split):
                                        split_plataforma = blockquote_split[j+5].split('\xa0')
                                        if len(split_plataforma) > 0:
                                            data['plataforma'] = split_plataforma[0]
                                elif blockquote_split[j] == 'ambiente:':
                                    if j+4 < len(blockquote_split):
                                        data['ambiente'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+4])
                                elif blockquote_split[j] == 'Palabras:':
                                    if j+3 < len(blockquote_split):
                                        data['palabras'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+3])
                                elif blockquote_split[j] == 'Areas:':
                                    if j+2 < len(blockquote_split):
                                        data['areas'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+2])
                                elif blockquote_split[j] == 'Sectores:':
                                    if j+1 < len(blockquote_split):
                                        data['sectores'] = ProduccionTecnologicaExtractor._clean_text(blockquote_split[j+1])
                            except Exception as ex:
                                module_logger.error(f"Error extrayendo datos de software para {cod_rh}: {str(ex)}", exc_info=True)
                    
                    insert_data('software', data, connection)
                    module_logger.debug(f"Software insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(f"Error procesando software {i} para {cod_rh}: {str(ex)}", exc_info=True)
        except Exception as ex:
            module_logger.error(f"Error general en extract_software para {cod_rh}: {str(ex)}", exc_info=True)

    @staticmethod
    def _clean_text(text):
        """
        Limpia el texto de caracteres no deseados.
        
        Args:
            text (str): Texto a limpiar.
            
        Returns:
            str: Texto limpio.
        """
        if not text:
            return ""
            
        return text.strip().replace("'", '"').replace("\t'", '"').replace("  ", "").replace("\n", "").replace("\r", "")


# Funciones de compatibilidad para el código existente
def extract_maps(cod_rh, h3, connection):
    """Función de compatibilidad para extract_maps"""
    return ProduccionTecnologicaExtractor.extract_maps(cod_rh, h3, connection)

def extract_conceptos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_conceptos"""
    return ProduccionTecnologicaExtractor.extract_conceptos(cod_rh, h3, connection)

def extract_disenos_industrial(cod_rh, h3, connection):
    """Función de compatibilidad para extract_disenos_industrial"""
    return ProduccionTecnologicaExtractor.extract_disenos_industrial(cod_rh, h3, connection)

def extract_empresa_base_tec(cod_rh, h3, connection):
    """Función de compatibilidad para extract_empresa_base_tec"""
    return ProduccionTecnologicaExtractor.extract_empresa_base_tec(cod_rh, h3, connection)

def extract_esquemas_trazado(cod_rh, h3, connection):
    """Función de compatibilidad para extract_esquemas_trazado"""
    return ProduccionTecnologicaExtractor.extract_esquemas_trazado(cod_rh, h3, connection)

def extract_informes(cod_rh, h3, connection):
    """Función de compatibilidad para extract_informes"""
    return ProduccionTecnologicaExtractor.extract_informes(cod_rh, h3, connection)

def extract_innovacion_proc(cod_rh, h3, connection):
    """Función de compatibilidad para extract_innovacion_proc"""
    return ProduccionTecnologicaExtractor.extract_innovacion_proc(cod_rh, h3, connection)

def extract_innovacion_gestion(cod_rh, h3, connection):
    """Función de compatibilidad para extract_innovacion_gestion"""
    return ProduccionTecnologicaExtractor.extract_innovacion_gestion(cod_rh, h3, connection)

def extract_variedad_animal(cod_rh, h3, connection):
    """Función de compatibilidad para extract_variedad_animal"""
    return ProduccionTecnologicaExtractor.extract_variedad_animal(cod_rh, h3, connection)

def extract_poblaciones_mej(cod_rh, h3, connection):
    """Función de compatibilidad para extract_poblaciones_mej"""
    return ProduccionTecnologicaExtractor.extract_poblaciones_mej(cod_rh, h3, connection)

def extract_variedad_vegetal(cod_rh, h3, connection):
    """Función de compatibilidad para extract_variedad_vegetal"""
    return ProduccionTecnologicaExtractor.extract_variedad_vegetal(cod_rh, h3, connection)

def extract_registro_cientifico(cod_rh, h3, connection):
    """Función de compatibilidad para extract_registro_cientifico"""
    return ProduccionTecnologicaExtractor.extract_registro_cientifico(cod_rh, h3, connection)

def extract_planta_piloto(cod_rh, h3, connection):
    """Función de compatibilidad para extract_planta_piloto"""
    return ProduccionTecnologicaExtractor.extract_planta_piloto(cod_rh, h3, connection)

def extract_productos_nutra(cod_rh, h3, connection):
    """Función de compatibilidad para extract_productos_nutra"""
    return ProduccionTecnologicaExtractor.extract_productos_nutra(cod_rh, h3, connection)

def extract_productos_tec(cod_rh, h3, connection):
    """Función de compatibilidad para extract_productos_tec"""
    return ProduccionTecnologicaExtractor.extract_productos_tec(cod_rh, h3, connection)

def extract_prototipos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_prototipos"""
    return ProduccionTecnologicaExtractor.extract_prototipos(cod_rh, h3, connection)

def extract_normas(cod_rh, h3, connection):
    """Función de compatibilidad para extract_normas"""
    return ProduccionTecnologicaExtractor.extract_normas(cod_rh, h3, connection)

def extract_protocolos_vigilancia(cod_rh, h3, connection):
    """Función de compatibilidad para extract_protocolos_vigilancia"""
    return ProduccionTecnologicaExtractor.extract_protocolos_vigilancia(cod_rh, h3, connection)

def extract_reglamentos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_reglamentos"""
    return ProduccionTecnologicaExtractor.extract_reglamentos(cod_rh, h3, connection)

def extract_signos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_signos"""
    return ProduccionTecnologicaExtractor.extract_signos(cod_rh, h3, connection)

def extract_software(cod_rh, h3, connection):
    """Función de compatibilidad para extract_software"""
    return ProduccionTecnologicaExtractor.extract_software(cod_rh, h3, connection)