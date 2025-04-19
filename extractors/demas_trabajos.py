from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class DemasTrabajosExtractor:
    """
    Clase para extraer información relacionada con demás trabajos del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre demás trabajos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para demás trabajos en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(En:)|(finalidad:)|(Palabras:)|(Areas:)|(Sectores:)",
                        blockquote.text,
                    )

                    DemasTrabajosExtractor._extract_blockquote_demas_trabajos(
                        blockquote_split, data
                    )

                    insert_data("demas_trabajos", data, connection)
                    module_logger.debug(f"Demás trabajo insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando demás trabajo para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract para {cod_rh}: {str(ex)}", exc_info=True
            )

    @staticmethod
    def _extract_blockquote_demas_trabajos(blockquote_split, data):
        """
        Extrae información del blockquote para demás trabajos.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "En:":
                    if j > 0:
                        data["coautores"] = ", ".join(
                            re.findall(
                                r"[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[:j][0]
                            )
                        )
                        nombre_split = re.split("[A-Z]{2,},", blockquote_split[j - 1])
                        if len(nombre_split) > 0:
                            data["nombre"] = DemasTrabajosExtractor._clean_text(
                                nombre_split[-1][:-2]
                            )

                    if j + 5 < len(blockquote_split):
                        temp = re.split(r"([0-9]+)", blockquote_split[j + 5])
                        if len(temp) > 0:
                            data["pais"] = DemasTrabajosExtractor._clean_text(
                                re.sub(r",\xa0\n\s+,", "", temp[0])
                            )[:-1]
                        if len(temp) > 1:
                            try:
                                data["ano"] = int(temp[1])
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {temp[1]}"
                                )
                elif blockquote_split[j] == "finalidad:":
                    if j + 4 < len(blockquote_split):
                        data["finalidad"] = DemasTrabajosExtractor._clean_text(
                            blockquote_split[j + 4]
                        )
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = DemasTrabajosExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = DemasTrabajosExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = DemasTrabajosExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote demás trabajos: {str(ex)}",
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


# Función de compatibilidad para el código existente
def extract(cod_rh, h3, connection):
    """Función de compatibilidad para extract"""
    return DemasTrabajosExtractor.extract(cod_rh, h3, connection)
