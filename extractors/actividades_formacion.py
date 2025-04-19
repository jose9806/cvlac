from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ActividadesFormacion:
    """
    Clase para extraer información relacionada con actividades de formación de un investigador.
    """

    @staticmethod
    def extract_cursos_cortos(cod_rh, h3, connection):
        """
        Extrae información sobre cursos de corta duración.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para cursos cortos en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en cursos cortos: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["nivel_programa_academico"] = (
                            ActividadesFormacion._clean_text(li_split[2])
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(Finalidad:)|(En:)|(participación:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ActividadesFormacion._extract_blockquote_cursos_cortos(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("cursos_corta_duracion", data, connection)
                    module_logger.debug(f"Curso corto insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando curso corto {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_cursos_cortos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_cursos_cortos(blockquote_split, data):
        """
        Extrae información del blockquote para cursos cortos.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "Finalidad:":
                    data["coautores"] = ", ".join(
                        re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[:j][0])
                    )
                    nombre_producto = re.split("[A-Z]{2,},", blockquote_split[j - 1])
                    if len(nombre_producto) > 1:
                        data["nombre_producto"] = ActividadesFormacion._clean_text(
                            nombre_producto[1]
                        )
                    finalidad = ActividadesFormacion._clean_text(
                        blockquote_split[j + 6]
                    )
                    if finalidad != ".":
                        data["finalidad"] = finalidad
                elif blockquote_split[j] == "En:":
                    temp = blockquote_split[j + 5].split(",")
                    if len(temp) > 1:
                        try:
                            data["ano"] = int(temp[1])
                        except (ValueError, TypeError):
                            module_logger.warning(
                                f"No se pudo convertir el año a entero: {temp[1]}"
                            )
                    if len(temp) > 0:
                        data["pais"] = ActividadesFormacion._clean_text(temp[0])
                    if len(temp) > 3:
                        data["institucion_financiadora"] = (
                            ActividadesFormacion._clean_text(temp[3])[:-1]
                        )
                elif blockquote_split[j] == "participación:":
                    temp = blockquote_split[j + 4].split(",")
                    if len(temp) > 0:
                        data["participacion"] = ActividadesFormacion._clean_text(
                            temp[0]
                        )
                    if len(temp) > 1:
                        data["duracion"] = ActividadesFormacion._clean_text(temp[1])
                elif blockquote_split[j] == "Palabras:":
                    data["palabras"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 3]
                    )
                elif blockquote_split[j] == "Areas:":
                    data["areas"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 2]
                    )
                elif blockquote_split[j] == "Sectores:":
                    data["sectores"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 1]
                    )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote cursos cortos: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_trabajos_dirigidos(cod_rh, h3, connection):
        """
        Extrae información sobre trabajos dirigidos/tutorías.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para trabajos dirigidos en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en trabajos dirigidos: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 1:
                        data["tipo_producto"] = ActividadesFormacion._clean_text(
                            li_split[1]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(Estado:)|(Persona orientada:)|(Dirigió como:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ActividadesFormacion._extract_blockquote_trabajos_dirigidos(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("trabajos_dirigidos", data, connection)
                    module_logger.debug(f"Trabajo dirigido insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando trabajo dirigido {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_trabajos_dirigidos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_trabajos_dirigidos(blockquote_split, data):
        """
        Extrae información del blockquote para trabajos dirigidos.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "Estado:":
                    split1 = re.split("[A-Z]{2,},", blockquote_split[j - 1])
                    if len(split1) > 1:
                        split2 = re.split("([A-Z]{2,}[ A-Z]*)", split1[1])

                        if len(split2) > 0:
                            data["nombre"] = ActividadesFormacion._clean_text(split2[0])
                        if len(split2) > 1:
                            data["institucion"] = ActividadesFormacion._clean_text(
                                split2[1]
                            )

                    temp = blockquote_split[j + 6].split("\xa0")
                    if len(temp) > 0:
                        data["estado"] = ActividadesFormacion._clean_text(temp[0])
                    if len(temp) > 1:
                        data["programa_academico"] = ActividadesFormacion._clean_text(
                            temp[1]
                        )
                    if len(temp) > 2:
                        try:
                            data["fecha_inicio"] = int(temp[2].replace(",", ""))
                        except (ValueError, TypeError):
                            module_logger.warning(
                                f"No se pudo convertir la fecha de inicio a entero: {temp[2]}"
                            )

                    data["coautores"] = ", ".join(
                        re.findall(
                            "[A-Z]{2,}[ [A-Z]{2,}]*",
                            blockquote_split[:j][0].split(".")[0],
                        )
                    )

                elif blockquote_split[j] == "Dirigió como:":
                    tipo_split = blockquote_split[j + 4].split(",")
                    if tipo_split:
                        data["tipo_orientacion"] = ActividadesFormacion._clean_text(
                            tipo_split[0]
                        )
                elif blockquote_split[j] == "Persona orientada:":
                    persona_split = blockquote_split[j + 5].split("\xa0")
                    if len(persona_split) > 1:
                        data["persona_orientada"] = ActividadesFormacion._clean_text(
                            persona_split[1]
                        )
                elif blockquote_split[j] == "Palabras:":
                    data["palabras"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 3]
                    )
                elif blockquote_split[j] == "Areas:":
                    data["areas"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 2]
                    )
                elif blockquote_split[j] == "Sectores:":
                    data["sectores"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 1]
                    )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote trabajos dirigidos: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_asesorias(cod_rh, h3, connection):
        """
        Extrae información sobre asesorías.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para asesorías en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en asesorías: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    data["nombre_proyecto_ondas"] = ActividadesFormacion._clean_text(
                        lis[i].text
                    )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(Institución:)|(Ciudad:)", blockquotes[i].text
                        )

                        ActividadesFormacion._extract_blockquote_asesorias(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("asesorias", data, connection)
                    module_logger.debug(f"Asesoría insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando asesoría {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_asesorias para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_asesorias(blockquote_split, data):
        """
        Extrae información del blockquote para asesorías.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "Institución:":
                    if j + 2 < len(blockquote_split):
                        data["institucion"] = blockquote_split[j + 2][:-1]
                elif blockquote_split[j] == "Ciudad:":
                    data["ciudad"] = ActividadesFormacion._clean_text(
                        blockquote_split[j + 1]
                    )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote asesorías: {str(ex)}",
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
def extract_cursos_cortos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_cursos_cortos"""
    return ActividadesFormacion.extract_cursos_cortos(cod_rh, h3, connection)


def extract_trabajos_dirigidos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_trabajos_dirigidos"""
    return ActividadesFormacion.extract_trabajos_dirigidos(cod_rh, h3, connection)


def extract_asesorias(cod_rh, h3, connection):
    """Función de compatibilidad para extract_asesorias"""
    return ActividadesFormacion.extract_asesorias(cod_rh, h3, connection)
