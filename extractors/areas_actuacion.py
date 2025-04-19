from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class AreasActuacion:
    """
    Clase para extraer información relacionada con áreas de actuación del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre áreas de actuación.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para áreas de actuación en {cod_rh}"
                )
                return

            lis = table.find_all("li")

            for li in lis:
                try:
                    data = {"cvlac_id": cod_rh}

                    text = li.text.split("--")
                    if len(text) > 0:
                        data["gran_area"] = AreasActuacion._clean_text(text[0])
                    if len(text) > 1:
                        data["area"] = AreasActuacion._clean_text(text[1])
                    if len(text) > 2:
                        data["especialidad"] = AreasActuacion._clean_text(text[2])

                    insert_data("areas_actuacion", data, connection)
                    module_logger.debug(f"Área de actuación insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando área de actuación para {cod_rh}: {str(ex)}",
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
    return AreasActuacion.extract(cod_rh, h3, connection)
