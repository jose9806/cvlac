from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ProyectosExtractor:
    """
    Clase para extraer información relacionada con proyectos del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre proyectos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para proyectos en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if blockquote.find("img") else "NO"

                    blockquote_split = re.split(
                        "(Tipo de proyecto:)|(Inicio:)|(Fin:)|(Duración)|(Resumen)",
                        blockquote.text,
                    )

                    for j in range(len(blockquote_split)):
                        try:
                            if blockquote_split[j] == "Tipo de proyecto:":
                                if j + 5 < len(blockquote_split):
                                    temp = blockquote_split[j + 5].split("\n")
                                    if len(temp) > 0:
                                        data["tipo"] = ProyectosExtractor._clean_text(
                                            temp[0]
                                        )
                                    if len(temp) > 1:
                                        data["nombre"] = ProyectosExtractor._clean_text(
                                            temp[1]
                                        )
                            elif blockquote_split[j] == "Inicio:":
                                if j + 4 < len(blockquote_split):
                                    try:
                                        data["fecha_inicio"] = "".join(
                                            blockquote_split[j + 4].split()
                                        )
                                    except Exception as ex:
                                        module_logger.warning(
                                            f"Error extrayendo fecha de inicio para {cod_rh}: {str(ex)}"
                                        )
                            elif blockquote_split[j] == "Fin:":
                                if j + 3 < len(blockquote_split):
                                    try:
                                        data["fecha_fin"] = "".join(
                                            blockquote_split[j + 3].split()
                                        )
                                    except Exception as ex:
                                        module_logger.warning(
                                            f"Error extrayendo fecha de fin para {cod_rh}: {str(ex)}"
                                        )
                            elif blockquote_split[j] == "Duración":
                                if j + 2 < len(blockquote_split):
                                    data["duracion"] = ProyectosExtractor._clean_text(
                                        blockquote_split[j + 2]
                                    )
                            elif blockquote_split[j] == "Resumen":
                                if j + 1 < len(blockquote_split):
                                    data["resumen"] = ProyectosExtractor._clean_text(
                                        blockquote_split[j + 1]
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de proyecto para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("proyectos", data, connection)
                    module_logger.debug(f"Proyecto insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando proyecto para {cod_rh}: {str(ex)}",
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
    return ProyectosExtractor.extract(cod_rh, h3, connection)
