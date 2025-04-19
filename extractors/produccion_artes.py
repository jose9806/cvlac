from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ProduccionArtesExtractor:
    """
    Clase para extraer información relacionada con producción en artes del investigador.
    """

    @staticmethod
    def extract_obras_productos(cod_rh, h3, connection):
        """
        Extrae información sobre obras o productos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para obras/productos en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if blockquote.find("img") else "NO"

                    blockquote_split = re.split(
                        "(Disciplina:)|(Nombre del producto:)|(Fecha de creación:)|(INSTANCIAS DE VALORACIÓN DE LA OBRA)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Disciplina:":
                                if i + 4 < len(blockquote_split):
                                    data["disciplina"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 4]
                                        )
                                    )
                            elif blockquote_split[i] == "Nombre del producto:":
                                if i + 3 < len(blockquote_split):
                                    data["nombre"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 3]
                                        )[:-1]
                                    )
                            elif blockquote_split[i] == "Fecha de creación:":
                                if i + 2 < len(blockquote_split):
                                    data["fecha_creacion"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 2]
                                        )
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de obra/producto para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("obras_productos", data, connection)
                    module_logger.debug(f"Obra/producto insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando obra/producto para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_obras_productos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_registro_licencia(cod_rh, h3, connection):
        """
        Extrae información sobre registros de acuerdo de licencia.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para registros de licencia en {cod_rh}"
                )
                return

            lis = table.find_all("li")

            for li in lis:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if li.find("img") else "NO"

                    li_split = re.split(
                        "(Institución u organización que tiene la licencia:)|(Fecha de otorgamiento de la licencia:)|"
                        "(Número de registro de la Dirección)|(Nacional de Derechos de Autor:)",
                        li.text,
                    )

                    for i in range(len(li_split)):
                        try:
                            if (
                                li_split[i]
                                == "Institución u organización que tiene la licencia:"
                            ):
                                if i + 4 < len(li_split):
                                    data["institucion"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            li_split[i + 4]
                                        )
                                    )
                            elif li_split[i] == "Fecha de otorgamiento de la licencia:":
                                if i + 3 < len(li_split):
                                    data["fecha_otorgamiento"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            li_split[i + 3]
                                        ).replace(",", "")
                                    )
                            elif li_split[i] == "Número de registro de la Dirección":
                                if i + 2 < len(li_split):
                                    data["numero_registro"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            li_split[i + 2]
                                        )
                                    )
                            elif li_split[i] == "Nacional de Derechos de Autor:":
                                if i + 1 < len(li_split):
                                    data["nacional_derechos"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            li_split[i + 1]
                                        )
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de registro de licencia para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("registro_licencia", data, connection)
                    module_logger.debug(f"Registro de licencia insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando registro de licencia para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_registro_licencia para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_industrias_creativas(cod_rh, h3, connection):
        """
        Extrae información sobre industrias creativas y culturales.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para industrias creativas en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Nombre de la empresa creativa:)|(Nit o codigo de registro:)|"
                        "(Fecha de registro ante la camara de comercio:)|(Tiene productos en el mercado)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre de la empresa creativa:":
                                if i + 4 < len(blockquote_split):
                                    data["nombre"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 4]
                                        )
                                    )
                            elif blockquote_split[i] == "Nit o codigo de registro:":
                                if i + 3 < len(blockquote_split):
                                    data["nit_registro"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 3]
                                        )
                                    )
                            elif (
                                blockquote_split[i]
                                == "Fecha de registro ante la camara de comercio:"
                            ):
                                if i + 2 < len(blockquote_split):
                                    data["fecha_registro"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 2]
                                        ).replace(",", "")
                                    )
                            elif blockquote_split[i] == "Tiene productos en el mercado":
                                if i + 1 < len(blockquote_split):
                                    data["tiene_productos"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 1]
                                        )
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de industria creativa para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("industrias_creativas_culturales", data, connection)
                    module_logger.debug(f"Industria creativa insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando industria creativa para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_industrias_creativas para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_eventos_artisticos(cod_rh, h3, connection):
        """
        Extrae información sobre eventos artísticos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para eventos artísticos en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if blockquote.find("img") else "NO"

                    blockquote_split = re.split(
                        "(Nombre del evento:)|(Fecha de inicio:)|(Tipo del evento:)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre del evento:":
                                if i + 3 < len(blockquote_split):
                                    data["nombre"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 3]
                                        )
                                    )
                            elif blockquote_split[i] == "Fecha de inicio:":
                                if i + 2 < len(blockquote_split):
                                    data["fecha_inicio"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 2]
                                        )
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de evento artístico para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("eventos_artisticos", data, connection)
                    module_logger.debug(f"Evento artístico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando evento artístico para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_eventos_artisticos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_talleres_creativos(cod_rh, h3, connection):
        """
        Extrae información sobre talleres creativos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para talleres creativos en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if blockquote.find("img") else "NO"

                    blockquote_split = re.split(
                        "(Nombre del taller:)|(Tipo de taller:)|(Participación:)|(Fecha de inicio:)|"
                        "(Fecha de finalización:)|(Lugar de realización:)|(Ámbito:)|(Distinción obtenida:)|"
                        "(Mecanismo de selección:)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre del taller:":
                                if i + 9 < len(blockquote_split):
                                    data["nombre"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 9]
                                        ).replace(",", "")
                                    )
                            elif blockquote_split[i] == "Tipo de taller:":
                                if i + 8 < len(blockquote_split):
                                    data["tipo"] = ProduccionArtesExtractor._clean_text(
                                        blockquote_split[i + 8]
                                    ).replace(",", "")
                            elif blockquote_split[i] == "Fecha de inicio:":
                                if i + 6 < len(blockquote_split):
                                    data["fecha_inicio"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 6]
                                        ).replace(",", "")
                                    )
                            elif blockquote_split[i] == "Fecha de finalización:":
                                if i + 5 < len(blockquote_split):
                                    fecha_fin = ProduccionArtesExtractor._clean_text(
                                        blockquote_split[i + 5]
                                    ).replace(",", "")
                                    if fecha_fin:
                                        data["fecha_fin"] = fecha_fin
                            elif blockquote_split[i] == "Participación:":
                                if i + 7 < len(blockquote_split):
                                    participacion = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 7]
                                        )
                                    )
                                    if participacion != "null":
                                        data["participacion"] = participacion
                            elif blockquote_split[i] == "Ámbito:":
                                if i + 3 < len(blockquote_split):
                                    data["ambito"] = blockquote_split[i + 3].replace(
                                        ",", ""
                                    )
                            elif blockquote_split[i] == "Distinción obtenida:":
                                if i + 2 < len(blockquote_split):
                                    data["distincion_obtenida"] = blockquote_split[
                                        i + 2
                                    ].replace(",", "")
                            elif blockquote_split[i] == "Mecanismo de selección:":
                                if i + 1 < len(blockquote_split):
                                    data["mecanismo_seleccion"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 1]
                                        )
                                    )
                            elif blockquote_split[i] == "Lugar de realización:":
                                if i + 4 < len(blockquote_split):
                                    data["lugar_realizacion"] = (
                                        ProduccionArtesExtractor._clean_text(
                                            blockquote_split[i + 4]
                                        )
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de taller creativo para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("talleres_creativos", data, connection)
                    module_logger.debug(f"Taller creativo insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando taller creativo para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_talleres_creativos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

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

        return (
            text.strip()
            .replace("'", '"')
            .replace("\t'", '"')
            .replace("  ", "")
            .replace("\n", "")
            .replace("\r", "")
        )


# Funciones de compatibilidad para el código existente
def extract_obras_productos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_obras_productos"""
    return ProduccionArtesExtractor.extract_obras_productos(cod_rh, h3, connection)


def extract_registro_licencia(cod_rh, h3, connection):
    """Función de compatibilidad para extract_registro_licencia"""
    return ProduccionArtesExtractor.extract_registro_licencia(cod_rh, h3, connection)


def extract_industrias_creativas(cod_rh, h3, connection):
    """Función de compatibilidad para extract_industrias_creativas"""
    return ProduccionArtesExtractor.extract_industrias_creativas(cod_rh, h3, connection)


def extract_eventos_artisticos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_eventos_artisticos"""
    return ProduccionArtesExtractor.extract_eventos_artisticos(cod_rh, h3, connection)


def extract_talleres_creativos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_talleres_creativos"""
    return ProduccionArtesExtractor.extract_talleres_creativos(cod_rh, h3, connection)
