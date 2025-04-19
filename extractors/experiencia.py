from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ExperienciaExtractor:
    """
    Clase para extraer información relacionada con experiencia profesional del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre experiencia profesional.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para experiencia en {cod_rh}"
                )
                return

            institucion_actual = ""

            for b in table.find_all("b"):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Actualizar institución actual si existe texto en el elemento b
                    if b.text.strip():
                        institucion_actual = b.text.strip()

                    # Asignar institución actual al registro
                    data["institucion"] = institucion_actual

                    # Extraer cadenas de texto del elemento padre de b
                    strs = [str_.strip() or None for str_ in b.parent.strings]

                    # Buscar y extraer información de dedicación y fechas
                    for i in range(len(strs)):
                        try:
                            if strs[i] == "Dedicación: ":
                                temp_dates = strs[i + 1].split("\n")  # type: ignore
                                data["dedicacion"] = temp_dates[0].replace("\xa0", " ")

                                # Extraer año de inicio
                                ano_inicio = re.findall(r"[0-9]{4}", temp_dates[1])
                                if ano_inicio:
                                    try:
                                        data["ano_inicio"] = int(ano_inicio[0])
                                    except (ValueError, TypeError):
                                        module_logger.warning(
                                            f"No se pudo convertir el año de inicio a entero: {ano_inicio[0]}"
                                        )

                                # Extraer año de fin
                                if len(temp_dates) > 2:
                                    ano_fin = re.findall(r"[0-9]{4}", temp_dates[2])
                                    if ano_fin:
                                        try:
                                            data["ano_fin"] = int(ano_fin[0])
                                        except (ValueError, TypeError):
                                            module_logger.warning(
                                                f"No se pudo convertir el año de fin a entero: {ano_fin[0]}"
                                            )

                                break
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo dedicación y fechas para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    # Insertar en la base de datos
                    insert_data("experiencia", data, connection)
                    module_logger.debug(
                        f"Experiencia insertada para {cod_rh} en {institucion_actual}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando experiencia para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract para {cod_rh}: {str(ex)}", exc_info=True
            )


# Función de compatibilidad para el código existente
def extract(cod_rh, h3, connection):
    """Función de compatibilidad para extract"""
    return ExperienciaExtractor.extract(cod_rh, h3, connection)
