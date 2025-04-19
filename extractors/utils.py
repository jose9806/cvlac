from config import ProjectLogger
from validators import DataValidator
from config import db

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)

# Inicializar el validador como una variable global
data_validator = DataValidator(db)


class ExtractorUtils:
    """
    Clase de utilidades para los extractores de CvLAC.
    """

    @staticmethod
    def get_table(html, name_tag):
        """
        Obtiene una tabla a partir de una etiqueta de nombre.

        Args:
            html (BeautifulSoup): Documento HTML.
            name_tag (dict): Diccionario con los atributos de la etiqueta de nombre.

        Returns:
            BeautifulSoup: Elemento de tabla encontrado o None.
        """
        try:
            tag = html.find("a", name_tag)
            return tag and tag.find_next_sibling("table")
        except Exception as ex:
            module_logger.error(f"Error en get_table: {str(ex)}", exc_info=True)
            return None

    @staticmethod
    def get_text_next_tag(table, string, tag):
        """
        Obtiene el texto del siguiente elemento de la etiqueta especificada que contiene la cadena.

        Args:
            table (BeautifulSoup): Elemento de tabla.
            string (str): Cadena a buscar.
            tag (str): Nombre de la etiqueta a buscar.

        Returns:
            str: Texto encontrado o None.
        """
        try:
            tag_search = table.find(string=string)
            return tag_search and tag_search.find_next(tag).contents[0]
        except Exception as ex:
            module_logger.error(f"Error en get_text_next_tag: {str(ex)}", exc_info=True)
            return None

    @staticmethod
    def get_href(table, string):
        """
        Obtiene el valor del atributo href de la etiqueta 'a' que contiene la cadena.

        Args:
            table (BeautifulSoup): Elemento de tabla.
            string (str): Cadena a buscar.

        Returns:
            str: Valor del atributo href o None.
        """
        try:
            a = table.find("a", text=string)
            return a and a["href"]
        except Exception as ex:
            module_logger.error(f"Error en get_href: {str(ex)}", exc_info=True)
            return None

    @staticmethod
    def delete_data(cod_rh, connection):
        """
        Elimina los datos de un investigador de la base de datos.

        Args:
            cod_rh (str): Código del investigador.
            connection: Conexión a la base de datos.
        """
        try:
            cursor = connection.cursor()
            cursor.execute(
                "delete from identificacion where cvlac_id = '{}'".format(cod_rh)
            )
            connection.commit()
            module_logger.info(f"Datos eliminados para {cod_rh}")
        except Exception as ex:
            connection.rollback()
            module_logger.error(
                f"Error eliminando datos para {cod_rh}: {str(ex)}", exc_info=True
            )

    @staticmethod
    def insert_data(table, dictionary, connection, update_if_exists=True):
        """
        Inserta datos en una tabla de la base de datos, validando duplicados.

        Args:
            table (str): Nombre de la tabla.
            dictionary (dict): Diccionario con los datos a insertar.
            connection: Conexión a la base de datos.
            update_if_exists (bool, optional): Si es True, actualiza registros
                                              existentes. Por defecto es True.

        Returns:
            str: Operación realizada ('insert', 'update', 'skip', 'error')
        """
        try:
            # Usar el validador para insertar o actualizar evitando duplicados
            operation, error = data_validator.insert_or_update(
                table, dictionary, connection, update_if_exists
            )

            if operation == "insert":
                module_logger.debug(f"Insertado nuevo registro en tabla {table}")
            elif operation == "update":
                module_logger.debug(f"Actualizado registro existente en tabla {table}")
            elif operation == "skip":
                module_logger.debug(f"Omitido registro duplicado en tabla {table}")
            else:  # error
                cvlac_id = dictionary.get("cvlac_id", "desconocido")
                module_logger.error(
                    f"Error insertando datos para {cvlac_id} en tabla {table}: {error}"
                )

            return operation

        except Exception as ex:
            connection.rollback()
            cvlac_id = dictionary.get("cvlac_id", "desconocido")
            module_logger.error(
                f"Error insertando datos para {cvlac_id} en tabla {table}: {str(ex)}",
                exc_info=True,
            )
            data_validator.record_operation(table, "error", dictionary, error=str(ex))
            return "error"

    @staticmethod
    def start_extraction():
        """
        Inicia una nueva extracción, reiniciando estadísticas.

        Returns:
            dict: Estadísticas iniciales de la extracción
        """
        return data_validator.start_new_extraction()

    @staticmethod
    def finish_extraction(cod_rh=None):
        """
        Finaliza la extracción y genera un reporte.

        Args:
            cod_rh (str, optional): Código del investigador específico.

        Returns:
            str: Ruta al archivo de reporte generado.
        """
        return data_validator.finish_extraction(cod_rh)


# Funciones de compatibilidad para el código existente
def get_table(html, name_tag):
    """Función de compatibilidad para get_table"""
    return ExtractorUtils.get_table(html, name_tag)


def get_text_next_tag(table, string, tag):
    """Función de compatibilidad para get_text_next_tag"""
    return ExtractorUtils.get_text_next_tag(table, string, tag)


def get_href(table, string):
    """Función de compatibilidad para get_href"""
    return ExtractorUtils.get_href(table, string)


def delete_data(cod_rh, connection):
    """Función de compatibilidad para delete_data"""
    return ExtractorUtils.delete_data(cod_rh, connection)


def insert_data(table, dictionary, connection):
    """Función de compatibilidad para insert_data"""
    return ExtractorUtils.insert_data(table, dictionary, connection)


def start_extraction():
    """Función de compatibilidad para start_extraction"""
    return ExtractorUtils.start_extraction()


def finish_extraction(cod_rh=None):
    """Función de compatibilidad para finish_extraction"""
    return ExtractorUtils.finish_extraction(cod_rh)
