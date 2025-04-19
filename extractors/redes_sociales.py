from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class RedesSocialesExtractor:
    """
    Clase para extraer información relacionada con redes sociales académicas del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre redes sociales académicas.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para redes sociales en {cod_rh}"
                )
                return

            lis = table.find_all("li")

            if not lis:
                module_logger.warning(
                    f"No se encontraron elementos li para redes sociales en {cod_rh}"
                )
                return

            for li in lis:
                try:
                    data = {"cvlac_id": cod_rh}

                    # Separar el texto por comas o por guiones
                    li_split = re.split(",| - ", li.text)

                    if len(li_split) > 0:
                        data["nombre"] = li_split[0]

                    if len(li_split) > 1:
                        # Todos los elementos intermedios forman la institución
                        data["institucion"] = ", ".join(li_split[1:-1])

                    # El último elemento es la fecha
                    if len(li_split) > 0:
                        fecha = RedesSocialesExtractor._clean_text(
                            li_split[-1]
                        ).replace("de", "")
                        if fecha:
                            try:
                                data["fecha"] = fecha
                            except Exception as ex:
                                module_logger.warning(
                                    f"Error extrayendo fecha para {cod_rh}: {str(ex)}"
                                )

                    insert_data("redes_sociales_academicas", data, connection)
                    module_logger.debug(f"Red social académica insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando red social académica para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract para {cod_rh}: {str(ex)}", exc_info=True
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
    return RedesSocialesExtractor.extract(cod_rh, h3, connection)
