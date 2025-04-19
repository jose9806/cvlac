from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class FormacionExtractor:
    """
    Clase para extraer información relacionada con formación académica y complementaria.
    """

    @staticmethod
    def extract_academic_formation(cod_rh, h3, connection):
        """
        Extrae información sobre formación académica.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para formación académica en {cod_rh}"
                )
                return

            for b in table.find_all("b"):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer cadenas de texto del elemento padre de b y limpiarlas
                    strs = [
                        str_.strip()
                        .replace("'", '"')
                        .replace("\t'", '"')
                        .replace("  ", "")
                        .replace("\n", "")
                        .replace("\r", "")
                        or None
                        for str_ in b.parent.strings
                    ]

                    # Extraer fechas
                    if len(strs) > 3 and strs[3]:
                        fechas = strs[3].split("-")
                        try:
                            if len(fechas) > 0:
                                data["fecha_inicio"] = (
                                    fechas[0]
                                    .strip()
                                    .replace("'", '"')
                                    .replace("\t'", '"')
                                    .replace("  ", "")
                                    .replace("\n", "")
                                    .replace("\r", "")
                                    .replace("de", "")
                                )
                            if len(fechas) > 1:
                                data["fecha_fin"] = (
                                    fechas[1]
                                    .strip()
                                    .replace("'", '"')
                                    .replace("\t'", '"')
                                    .replace("  ", "")
                                    .replace("\n", "")
                                    .replace("\r", "")
                                    .replace("de", "")
                                )
                        except Exception as ex:
                            module_logger.warning(
                                f"Error extrayendo fechas para {cod_rh}: {str(ex)}"
                            )

                    # Extraer nivel de formación
                    if len(strs) > 0 and strs[0]:
                        data["nivel_formacion"] = strs[0]

                    # Extraer institución
                    if len(strs) > 1 and strs[1]:
                        data["institucion"] = strs[1]

                    # Extraer programa académico
                    if len(strs) > 2 and strs[2]:
                        data["programa_academico"] = strs[2]

                    # Insertar en la base de datos
                    insert_data("formacion_academica", data, connection)
                    module_logger.debug(f"Formación académica insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando formación académica para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_academic_formation para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_complementary_formation(cod_rh, h3, connection):
        """
        Extrae información sobre formación complementaria.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para formación complementaria en {cod_rh}"
                )
                return

            for b in table.find_all("b"):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer cadenas de texto del elemento padre de b y limpiarlas
                    strs = [
                        str_.strip()
                        .replace("'", '"')
                        .replace("\t'", '"')
                        .replace("  ", "")
                        .replace("\n", "")
                        .replace("\r", "")
                        or None
                        for str_ in b.parent.strings
                    ]

                    # Extraer fechas
                    if len(strs) > 3 and strs[3]:
                        fechas = strs[3].split("-")
                        try:
                            if len(fechas) > 0:
                                data["fecha_inicio"] = (
                                    fechas[0]
                                    .strip()
                                    .replace("'", '"')
                                    .replace("\t'", '"')
                                    .replace("  ", "")
                                    .replace("\n", "")
                                    .replace("\r", "")
                                    .replace("de", "")
                                )
                            if len(fechas) > 1:
                                data["fecha_fin"] = (
                                    fechas[1]
                                    .strip()
                                    .replace("'", '"')
                                    .replace("\t'", '"')
                                    .replace("  ", "")
                                    .replace("\n", "")
                                    .replace("\r", "")
                                    .replace("de", "")
                                )
                        except Exception as ex:
                            module_logger.warning(
                                f"Error extrayendo fechas para {cod_rh}: {str(ex)}"
                            )

                    # Extraer nivel de formación
                    if len(strs) > 0 and strs[0]:
                        data["nivel_formacion"] = strs[0]

                    # Extraer institución
                    if len(strs) > 1 and strs[1]:
                        data["institucion"] = strs[1]

                    # Extraer programa académico
                    if len(strs) > 2 and strs[2]:
                        data["programa_academico"] = strs[2]

                    # Insertar en la base de datos
                    insert_data("formacion_complementaria", data, connection)
                    module_logger.debug(
                        f"Formación complementaria insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando formación complementaria para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_complementary_formation para {cod_rh}: {str(ex)}",
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
def extract_academic_formation(cod_rh, h3, connection):
    """Función de compatibilidad para extract_academic_formation"""
    return FormacionExtractor.extract_academic_formation(cod_rh, h3, connection)


def extract_complementary_formation(cod_rh, h3, connection):
    """Función de compatibilidad para extract_complementary_formation"""
    return FormacionExtractor.extract_complementary_formation(cod_rh, h3, connection)
