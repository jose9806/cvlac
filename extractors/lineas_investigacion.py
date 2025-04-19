from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class LineasInvestigacionExtractor:
    """
    Clase para extraer información relacionada con líneas de investigación del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre líneas de investigación.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para líneas de investigación en {cod_rh}"
                )
                return

            for li in table.find_all("li"):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer elementos del li
                    strs = [str_ for str_ in li]

                    # Verificar que haya suficiente información
                    if len(strs) > 0:
                        # Extraer línea de investigación
                        linea = strs[0].strip()
                        if linea.endswith(","):
                            linea = linea[:-1]  # Eliminar la coma al final
                        data["linea_investigacion"] = (
                            LineasInvestigacionExtractor._clean_text(linea)
                        )

                    # Verificar si la línea está activa
                    if len(strs) > 2:
                        data["activa"] = strs[2]

                    # Insertar en la base de datos
                    insert_data("lineas_investigacion", data, connection)
                    module_logger.debug(
                        f"Línea de investigación insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando línea de investigación para {cod_rh}: {str(ex)}",
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
    return LineasInvestigacionExtractor.extract(cod_rh, h3, connection)
