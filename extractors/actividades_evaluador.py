from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ActividadesEvaluador:
    """
    Clase para extraer información relacionada con actividades de evaluador de un investigador.
    """

    @staticmethod
    def extract_jurados(cod_rh, h3, connection):
        """
        Extrae información sobre participación como jurado.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para jurados en {cod_rh}")
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en jurados: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    li_split = lis[i].text.split("-")
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    data["nivel_programa_academico"] = ActividadesEvaluador._clean_text(
                        li_split[2]
                    )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(Titulo:)|(Tipo de trabajo presentado:)|(en:)|(programa académico)|"
                            "(Nombre del orientado:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ActividadesEvaluador._extract_blockquote_jurados(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("jurados", data, connection)
                    module_logger.debug(f"Jurado insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando jurado {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_jurados para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_jurados(blockquote_split, data):
        """
        Extrae información del blockquote para jurados.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "Titulo:":
                    data["coautores"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j - 1]
                    )
                    data["titulo"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 8]
                    )
                elif blockquote_split[j] == "Tipo de trabajo presentado:":
                    data["tipo_trabajo"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 7]
                    )
                elif blockquote_split[j] == "en:":
                    data["institucion"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 6]
                    )
                elif blockquote_split[j] == "programa académico":
                    data["programa_academico"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 5]
                    )
                elif blockquote_split[j] == "Nombre del orientado:":
                    data["nombre_orientado"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 4]
                    )
                elif blockquote_split[j] == "Palabras:":
                    data["palabras"] = blockquote_split[j + 3].rstrip()
                elif blockquote_split[j] == "Areas:":
                    data["areas"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 2]
                    )
                elif blockquote_split[j] == "Sectores:":
                    data["sectores"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 1]
                    )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote jurados: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_par_evaluador(cod_rh, h3, connection):
        """
        Extrae información sobre participación como par evaluador.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para par evaluador en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            if not blockquotes:
                module_logger.warning(
                    f"No se encontraron blockquotes para par evaluador en {cod_rh}"
                )
                return

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Ámbito:)|(Par evaluador de:)|(Institución:)|(Revista:)|(Editorial:)",
                        blockquote.text,
                    )

                    ActividadesEvaluador._extract_blockquote_par_evaluador(
                        blockquote_split, data
                    )

                    # Insertar en la base de datos
                    insert_data("par_evaluador", data, connection)
                    module_logger.debug(f"Par evaluador insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando par evaluador para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_par_evaluador para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_par_evaluador(blockquote_split, data):
        """
        Extrae información del blockquote para par evaluador.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "Ámbito:":
                    data["ambito"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 5]
                    )
                if blockquote_split[j] == "Par evaluador de:":
                    data["par_evaluador_de"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 4]
                    )
                if blockquote_split[j] == "Institución:":
                    temp = blockquote_split[j + 3].split("\xa0")
                    if len(temp) == 4:
                        data["entidad_convocadora"] = ActividadesEvaluador._clean_text(
                            temp[0]
                        )[:-1]
                if blockquote_split[j] in ["Revista:", "Editorial:"]:
                    data["tipo_material"] = ActividadesEvaluador._clean_text(
                        "".join(filter(None, blockquote_split[j:]))
                    ).split("\xa0")[0][:-1]
                if j == len(blockquote_split) - 1:
                    temp = blockquote_split[j].split(",")
                    anos = re.findall(r"[0-9]+", blockquote_split[j])
                    if anos:
                        data["ano"] = anos[0]
                    if len(temp) > 2:
                        data["mes"] = ActividadesEvaluador._clean_text(temp[2])
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote par evaluador: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_participacion_comites_evaluacion(cod_rh, h3, connection):
        """
        Extrae información sobre participación en comités de evaluación.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para comités de evaluación en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en comités de evaluación: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ActividadesEvaluador._clean_text(li_split[2])

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(en:)|(Areas:)|(Palabras:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ActividadesEvaluador._extract_blockquote_comites_evaluacion(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("participacion_comites_evaluacion", data, connection)
                    module_logger.debug(
                        f"Participación en comité evaluación insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando participación en comité {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_participacion_comites_evaluacion para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_comites_evaluacion(blockquote_split, data):
        """
        Extrae información del blockquote para comités de evaluación.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "en:":
                    data["institucion"] = ActividadesEvaluador._clean_text(
                        blockquote_split[j + 4]
                    )
                    if j > 0:
                        parts = blockquote_split[j - 1].split(",")
                        if len(parts) > 1:
                            data["nombre_producto"] = ActividadesEvaluador._clean_text(
                                "".join(parts[1:])
                            )
                            # Buscar año en el formato ####=
                            anos = re.findall(r"[0-9]{4}=", data["nombre_producto"])
                            if anos:
                                data["ano"] = int(
                                    anos[0][:-1]
                                )  # Quitar el = y convertir a int
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote comité evaluación: {str(ex)}",
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
def extract_jurados(cod_rh, h3, connection):
    """Función de compatibilidad para extract_jurados"""
    return ActividadesEvaluador.extract_jurados(cod_rh, h3, connection)


def extract_par_evaluador(cod_rh, h3, connection):
    """Función de compatibilidad para extract_par_evaluador"""
    return ActividadesEvaluador.extract_par_evaluador(cod_rh, h3, connection)


def extract_participacion_comites_evaluacion(cod_rh, h3, connection):
    """Función de compatibilidad para extract_participacion_comites_evaluacion"""
    return ActividadesEvaluador.extract_participacion_comites_evaluacion(
        cod_rh, h3, connection
    )
