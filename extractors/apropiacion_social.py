from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re
import locale
import unidecode
import uuid

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)

# Configuración de locale para fechas
try:
    locale.setlocale(locale.LC_TIME, "")
except Exception as ex:
    module_logger.warning(f"No se pudo configurar el locale: {str(ex)}")


class ApropiacionSocial:
    """
    Clase para extraer información relacionada con la apropiación social del conocimiento.
    """

    @staticmethod
    def extract_consultorias(cod_rh, h3, connection):
        """
        Extrae información sobre consultorías.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para consultorías en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en consultorías: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo_clase"] = li_split[2]

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(Nombre comercial:)|(contrato/registro:)|(En:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ApropiacionSocial._extract_blockquote_consultorias(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("consultorias", data, connection)
                    module_logger.debug(f"Consultoría insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando consultoría {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_consultorias para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_consultorias(blockquote_split, data):
        """
        Extrae información del blockquote para consultorías.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "Nombre comercial:":
                    split_nombre = re.split("[A-Z]{2,},", blockquote_split[j - 1])
                    if len(split_nombre) > 0:
                        data["nombre"] = ApropiacionSocial._clean_text(split_nombre[-1])
                elif blockquote_split[j] == "contrato/registro:":
                    if j + 5 < len(blockquote_split):
                        temp = blockquote_split[j + 5]
                        data["numero_contrato"] = ApropiacionSocial._clean_text(
                            temp.replace(",", "").replace(".", "")
                        )
                elif blockquote_split[j] == "En:":
                    if j + 4 < len(blockquote_split):
                        temp = blockquote_split[j + 4].split(",")
                        if len(temp) > 0:
                            data["pais"] = ApropiacionSocial._clean_text(temp[0])
                        if len(temp) > 2:
                            try:
                                data["ano"] = int(
                                    ApropiacionSocial._clean_text(temp[2])
                                )
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {temp[2]}"
                                )
                        if len(temp) > 3:
                            split_duracion = temp[3].split("\xa0")
                            if len(split_duracion) > 1:
                                data["duracion"] = ApropiacionSocial._clean_text(
                                    split_duracion[1]
                                )
                elif blockquote_split[j] == "Palabras:":
                    data["palabras"] = ApropiacionSocial._clean_text(
                        blockquote_split[j + 3]
                    )
                elif blockquote_split[j] == "Areas:":
                    data["areas"] = ApropiacionSocial._clean_text(
                        blockquote_split[j + 2]
                    )
                elif blockquote_split[j] == "Sectores:":
                    data["sectores"] = ApropiacionSocial._clean_text(
                        blockquote_split[j + 1]
                    )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote consultorías: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_ediciones_revisiones(cod_rh, h3, connection):
        """
        Extrae información sobre ediciones y revisiones.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para ediciones/revisiones en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en ediciones/revisiones: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo_producto"] = ApropiacionSocial._clean_text(
                            li_split[2]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(Nombre comercial:)|(contrato/registro:)|(En:)",
                            blockquotes[i].text,
                        )

                        ApropiacionSocial._extract_blockquote_ediciones_revisiones(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("ediciones_revisiones", data, connection)
                    module_logger.debug(f"Edición/revisión insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando edición/revisión {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_ediciones_revisiones para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_ediciones_revisiones(blockquote_split, data):
        """
        Extrae información del blockquote para ediciones/revisiones.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "En:":
                    if j + 1 < len(blockquote_split):
                        temp = blockquote_split[j + 1].split("\xa0")
                        if len(temp) > 0:
                            data["pais"] = ApropiacionSocial._clean_text(
                                temp[0].replace(",", "")
                            )
                        if len(temp) > 1:
                            anos = re.findall(r"[0-9]{4}", temp[1])
                            if anos:
                                try:
                                    data["ano"] = int(anos[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir el año a entero: {anos[0]}"
                                    )
                        if len(temp) > 2:
                            data["editorial"] = ApropiacionSocial._clean_text(temp[2])
                        if len(temp) > 3:
                            paginas = re.findall(r"p\.[0-9]+", temp[3])
                            if paginas:
                                try:
                                    data["paginas"] = int(paginas[0].replace("p.", ""))
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir las páginas a entero: {paginas[0]}"
                                    )
                elif blockquote_split[j] == "Nombre comercial:":
                    if j - 1 >= 0:
                        nombre_split = re.split("[A-Z]{2,},", blockquote_split[j - 1])
                        if len(nombre_split) > 0:
                            data["revista"] = ApropiacionSocial._clean_text(
                                nombre_split[-1]
                            )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote ediciones/revisiones: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_eventos_cientificos(cod_rh, h3, nombre_completo, connection):
        """
        Extrae información sobre eventos científicos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            nombre_completo (str): Nombre completo del investigador.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para eventos científicos en {cod_rh}"
                )
                return

            eventos = table.find_all("tr", recursive=False)

            # Eliminamos el primer elemento (encabezado)
            if len(eventos) > 1:
                eventos = eventos[1:]
            else:
                module_logger.warning(
                    f"No se encontraron eventos científicos para {cod_rh}"
                )
                return

            for evento in eventos:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if evento.find("img") else "NO"
                    data["id"] = str(uuid.uuid1())  # Identificador único para el evento

                    trs = evento.find_all("tr")
                    if len(trs) < 4:
                        module_logger.warning(
                            f"Estructura incompleta para evento científico en {cod_rh}"
                        )
                        continue

                    # Extraer datos del evento
                    ApropiacionSocial._extract_datos_evento(trs[0], data)

                    # Extraer participantes
                    ApropiacionSocial._extract_participantes_evento(
                        trs[3], data, nombre_completo, connection
                    )

                    # Extraer productos
                    ApropiacionSocial._extract_productos_evento(
                        trs[1], data, connection
                    )

                    # Extraer instituciones
                    ApropiacionSocial._extract_instituciones_evento(
                        trs[2], data, connection
                    )

                    # Insertar en la base de datos
                    insert_data("eventos_cientificos", data, connection)
                    module_logger.debug(f"Evento científico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando evento científico para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_eventos_cientificos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_datos_evento(tr, data):
        """
        Extrae datos generales del evento.

        Args:
            tr (BeautifulSoup): Elemento HTML que contiene la información.
            data (dict): Diccionario donde se almacenará la información.
        """
        try:
            datos_evento = re.split(
                "(Nombre del evento:)|(Tipo de evento:)|(Ámbito:)|(Realizado el:)",
                tr.text,
            )
            for i in range(len(datos_evento)):
                try:
                    if datos_evento[i] == "Nombre del evento:":
                        data["nombre_evento"] = ApropiacionSocial._clean_text(
                            datos_evento[i + 4]
                        )
                    elif datos_evento[i] == "Tipo de evento:":
                        data["tipo_evento"] = ApropiacionSocial._clean_text(
                            datos_evento[i + 3]
                        )
                    elif datos_evento[i] == "Ámbito:":
                        data["ambito"] = ApropiacionSocial._clean_text(
                            datos_evento[i + 2]
                        )
                    elif datos_evento[i] == "Realizado el:":
                        temp = re.split(",|(en)", datos_evento[i + 1])
                        if len(temp) > 0 and temp[0].strip():
                            data["fecha_inicio"] = ApropiacionSocial._clean_text(
                                temp[0]
                            )
                        if len(temp) > 2 and temp[2].strip():
                            data["fecha_fin"] = ApropiacionSocial._clean_text(temp[2])
                        if len(temp) > 4:
                            temp2 = temp[4].split("-")
                            if len(temp2) > 0:
                                data["ciudad"] = ApropiacionSocial._clean_text(temp2[0])
                            if len(temp2) > 1:
                                data["lugar"] = ApropiacionSocial._clean_text(temp2[1])
                except Exception as ex:
                    module_logger.error(
                        f"Error extrayendo datos del evento: {str(ex)}", exc_info=True
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en _extract_datos_evento: {str(ex)}", exc_info=True
            )

    @staticmethod
    def _extract_participantes_evento(tr, data, nombre_completo, connection):
        """
        Extrae participantes del evento.

        Args:
            tr (BeautifulSoup): Elemento HTML que contiene la información.
            data (dict): Diccionario donde se almacenará la información.
            nombre_completo (str): Nombre completo del investigador.
            connection: Conexión a la base de datos.
        """
        try:
            lis = tr.find_all("li")

            # Extraer rol del investigador principal
            for li in lis:
                if unidecode.unidecode(nombre_completo.upper()) in li.text:
                    rol_split = li.text.split("Rol en el evento:")
                    if len(rol_split) > 1:
                        data["rol"] = ApropiacionSocial._clean_text(rol_split[1])
                    break

            # Extraer todos los participantes
            for li in lis:
                try:
                    data_participante = {}
                    participante = re.split("(Nombre:)|(Rol en el evento:)", li.text)

                    if len(participante) > 3:
                        data_participante["nombre"] = ApropiacionSocial._clean_text(
                            participante[3]
                        )
                    if len(participante) > 6:
                        data_participante["rol"] = ApropiacionSocial._clean_text(
                            participante[6]
                        )

                    data_participante["evento_id"] = data["id"]

                    insert_data("eventos_participantes", data_participante, connection)
                except Exception as ex:
                    module_logger.error(
                        f"Error extrayendo participante del evento: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en _extract_participantes_evento: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_productos_evento(tr, data, connection):
        """
        Extrae productos del evento.

        Args:
            tr (BeautifulSoup): Elemento HTML que contiene la información.
            data (dict): Diccionario donde se almacenará la información.
            connection: Conexión a la base de datos.
        """
        try:
            lis = tr.find_all("li")

            for li in lis:
                try:
                    data_producto = {}
                    producto = re.split(
                        "(Nombre del producto:)|(Tipo de producto:)", li.text
                    )

                    if len(producto) > 3:
                        data_producto["nombre"] = ApropiacionSocial._clean_text(
                            producto[3]
                        )
                    if len(producto) > 6:
                        data_producto["tipo_producto"] = ApropiacionSocial._clean_text(
                            producto[6]
                        )

                    data_producto["evento_id"] = data["id"]

                    insert_data("eventos_productos", data_producto, connection)
                except Exception as ex:
                    module_logger.error(
                        f"Error extrayendo producto del evento: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en _extract_productos_evento: {str(ex)}", exc_info=True
            )

    @staticmethod
    def _extract_instituciones_evento(tr, data, connection):
        """
        Extrae instituciones del evento.

        Args:
            tr (BeautifulSoup): Elemento HTML que contiene la información.
            data (dict): Diccionario donde se almacenará la información.
            connection: Conexión a la base de datos.
        """
        try:
            lis = tr.find_all("li")

            for li in lis:
                try:
                    data_institucion = {}
                    institucion = re.split(
                        "(Nombre de la institución:)|(Tipo de vinculación)", li.text
                    )

                    if len(institucion) > 3:
                        data_institucion["nombre"] = ApropiacionSocial._clean_text(
                            institucion[3]
                        )
                    if len(institucion) > 6:
                        data_institucion["tipo_vinculacion"] = (
                            ApropiacionSocial._clean_text(institucion[6])
                        )

                    data_institucion["evento_id"] = data["id"]

                    insert_data("eventos_instituciones", data_institucion, connection)
                except Exception as ex:
                    module_logger.error(
                        f"Error extrayendo institución del evento: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en _extract_instituciones_evento: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_informes(cod_rh, h3, connection):
        """
        Extrae información sobre informes de investigación.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para informes en {cod_rh}")
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    temp = blockquote.text.split("En:")
                    if len(temp) > 0:
                        data["coautores"] = ", ".join(
                            re.findall(r"([A-Z]{2,}[ [A-Z]{2,}]*)", temp[0])
                        )

                    if len(temp) > 1:
                        anos = re.findall(r"[0-9]{4}", temp[1])
                        if anos:
                            try:
                                data["ano"] = int(anos[0])
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {anos[0]}"
                                )

                    blockquote_split = re.split(
                        "(Informe de investigación:)|(En:)", blockquote.text
                    )
                    for j in range(len(blockquote_split)):
                        if blockquote_split[j] == "Informe de investigación:":
                            if j + 2 < len(blockquote_split):
                                data["titulo"] = ApropiacionSocial._clean_text(
                                    blockquote_split[j + 2]
                                    .replace("\n", "")
                                    .replace(".", "")
                                )

                    insert_data("informes_investigacion", data, connection)
                    module_logger.debug(
                        f"Informe de investigación insertado para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando informe para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_informes para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_redes_conocimiento(cod_rh, h3, connection):
        """
        Extrae información sobre redes de conocimiento especializado.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para redes de conocimiento en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Nombre de la red)|(Tipo de red)|(Creada el:)", blockquote.text
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre de la red":
                                if i + 3 < len(blockquote_split):
                                    data["nombre"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "Tipo de red":
                                if i + 2 < len(blockquote_split):
                                    data["tipo"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 2]
                                    )[:-1]
                            elif blockquote_split[i] == "Creada el:":
                                if i + 1 < len(blockquote_split):
                                    temp = blockquote_split[i + 1].split("\xa0")
                                    if len(temp) > 0:
                                        data["fecha_inicio"] = (
                                            ApropiacionSocial._clean_text(
                                                temp[0].replace(",", "")
                                            )
                                        )
                                    if len(temp) > 2:
                                        lugar_split = temp[2].split("en ")
                                        if len(lugar_split) > 1:
                                            data["lugar"] = (
                                                ApropiacionSocial._clean_text(
                                                    lugar_split[1]
                                                )
                                            )
                                    if len(temp) > 3:
                                        participantes = re.findall(
                                            r"con\s*([0-9]*)\s*participantes", temp[3]
                                        )
                                        if participantes and participantes[0] != "":
                                            try:
                                                data["participantes"] = int(
                                                    participantes[0]
                                                )
                                            except (ValueError, TypeError):
                                                module_logger.warning(
                                                    f"No se pudo convertir los participantes a entero: {participantes[0]}"
                                                )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de red de conocimiento: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("redes_conocimiento", data, connection)
                    module_logger.debug(f"Red de conocimiento insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando red de conocimiento para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_redes_conocimiento para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_audio(cod_rh, h3, connection):
        """
        Extrae información sobre generación de contenido de audio.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para contenido de audio en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(En:)|(Formato:)|(Descripción:)|(Palabras:)|(Areas:)|(Sectores:)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "En:":
                                if i == 1 and i - 1 >= 0:
                                    data["coautores"] = ", ".join(
                                        re.findall(
                                            r"([A-Z]{2,}[ [A-Z]{2,}]*)",
                                            blockquote_split[i - 1],
                                        )
                                    )
                                    data["titulo"] = ApropiacionSocial._clean_text(
                                        re.sub(
                                            r"([A-Z]{2,}[ [A-Z]{2,}]*)",
                                            "",
                                            blockquote_split[i - 1],
                                        ).replace(", ", "")
                                    )
                                    try:
                                        if i + 6 < len(blockquote_split):
                                            data["fecha"] = "".join(
                                                blockquote_split[i + 6].split()
                                            ).replace(".", "")
                                    except Exception:
                                        pass
                                else:
                                    if i + 6 < len(blockquote_split):
                                        data["lugar"] = ApropiacionSocial._clean_text(
                                            blockquote_split[i + 6]
                                        )
                            elif blockquote_split[i] == "Formato:":
                                if i + 5 < len(blockquote_split):
                                    data["formato"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 5]
                                    )
                            elif blockquote_split[i] == "Descripción:":
                                if i + 4 < len(blockquote_split):
                                    data["descripcion"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 4]
                                    )
                            elif blockquote_split[i] == "Palabras:":
                                if i + 3 < len(blockquote_split):
                                    data["palabras"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "Areas:":
                                if i + 2 < len(blockquote_split):
                                    data["areas"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 2]
                                    )
                            elif blockquote_split[i] == "Sectores:":
                                if i + 1 < len(blockquote_split):
                                    data["sectores"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 1]
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de contenido de audio: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("audio", data, connection)
                    module_logger.debug(f"Contenido de audio insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando contenido de audio para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_audio para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_impreso(cod_rh, h3, connection):
        """
        Extrae información sobre generación de contenido impreso.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para contenido impreso en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if blockquote.find("img") else "NO"

                    blockquote_split = re.split(
                        "(Nombre)|(Tipo)|(Medio de circulación:)|(disponible en)|(en la fecha)|(en el ámbito)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre":
                                if i + 6 < len(blockquote_split):
                                    data["nombre"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 6]
                                    )
                            elif blockquote_split[i] == "Tipo":
                                if i + 5 < len(blockquote_split):
                                    tipo_split = blockquote_split[i + 5].split("-")
                                    if len(tipo_split) > 2:
                                        data["tipo"] = ApropiacionSocial._clean_text(
                                            tipo_split[2]
                                        )[:-1]
                            elif blockquote_split[i] == "Medio de circulación:":
                                if i + 4 < len(blockquote_split):
                                    data["medio_circulacion"] = (
                                        ApropiacionSocial._clean_text(
                                            blockquote_split[i + 4]
                                        )[:-1]
                                    )
                            elif blockquote_split[i] == "disponible en":
                                if i + 3 < len(blockquote_split):
                                    data["sitio_web"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "en la fecha":
                                if i + 2 < len(blockquote_split):
                                    data["fecha"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 2]
                                    )
                            elif blockquote_split[i] == "en el ámbito":
                                if i + 1 < len(blockquote_split):
                                    data["ambito"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 1]
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de contenido impreso: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("impresa", data, connection)
                    module_logger.debug(f"Contenido impreso insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando contenido impreso para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_impreso para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_multimedia(cod_rh, h3, connection):
        """
        Extrae información sobre generación de contenido multimedia.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para contenido multimedia en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en multimedia: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ApropiacionSocial._clean_text(li_split[2])

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(En:)|(Emisora:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        for j in range(len(blockquote_split)):
                            try:
                                if blockquote_split[j] == "En:":
                                    if j - 1 >= 0:
                                        data["coautores"] = ", ".join(
                                            re.findall(
                                                r"([A-Z]{2,}[ [A-Z]{2,}]*)",
                                                blockquote_split[j - 1],
                                            )
                                        )
                                        data["nombre"] = ApropiacionSocial._clean_text(
                                            re.sub(
                                                r"([A-Z]{2,}[ [A-Z]{2,}]*)",
                                                "",
                                                blockquote_split[j - 1],
                                            ).replace(", ", "")
                                        )

                                    if j + 5 < len(blockquote_split):
                                        temp = blockquote_split[j + 5].split(",")
                                        if len(temp) > 2:
                                            try:
                                                data["ano"] = int(temp[2])
                                            except (ValueError, TypeError):
                                                module_logger.warning(
                                                    f"No se pudo convertir el año a entero: {temp[2]}"
                                                )
                                        if len(temp) > 0:
                                            data["pais"] = (
                                                ApropiacionSocial._clean_text(temp[0])
                                            )
                                elif blockquote_split[j] == "Emisora:":
                                    if j + 4 < len(blockquote_split):
                                        temp = blockquote_split[j + 4].split("\xa0")
                                        if len(temp) > 0:
                                            data["emisora"] = temp[0]
                                        if len(temp) > 1:
                                            minutos = re.findall(r"[0-9]+", temp[1])
                                            if minutos:
                                                try:
                                                    data["duracion"] = int(minutos[0])
                                                except (ValueError, TypeError):
                                                    module_logger.warning(
                                                        f"No se pudo convertir la duración a entero: {minutos[0]}"
                                                    )
                                elif blockquote_split[j] == "Palabras:":
                                    if j + 3 < len(blockquote_split):
                                        data["palabras"] = (
                                            ApropiacionSocial._clean_text(
                                                blockquote_split[j + 3]
                                            )
                                        )
                                elif blockquote_split[j] == "Areas:":
                                    if j + 2 < len(blockquote_split):
                                        data["areas"] = ApropiacionSocial._clean_text(
                                            blockquote_split[j + 2]
                                        )
                                elif blockquote_split[j] == "Sectores:":
                                    if j + 1 < len(blockquote_split):
                                        data["sectores"] = (
                                            ApropiacionSocial._clean_text(
                                                blockquote_split[j + 1]
                                            )
                                        )
                            except Exception as ex:
                                module_logger.error(
                                    f"Error extrayendo datos de contenido multimedia: {str(ex)}",
                                    exc_info=True,
                                )

                    insert_data("multimedia", data, connection)
                    module_logger.debug(f"Contenido multimedia insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando contenido multimedia {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_multimedia para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_secuencia(cod_rh, h3, connection):
        """
        Extrae información sobre nueva secuencia genética.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para secuencia genética en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = (
                        "SI"
                        if blockquote.parent.parent.previous_sibling.previous_sibling.find(
                            "img"
                        )
                        else "NO"
                    )

                    blockquote_split = re.split(
                        "(En:)|(Emisora:)|(Base de datos donde está incluido el registro:)|(disponible en)|"
                        "(Institución:)|(Palabras:)|(Areas:)|(Sectores:)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "En:":
                                if i == 1:
                                    if i - 1 >= 0:
                                        data["coautores"] = ", ".join(
                                            re.findall(
                                                r"([A-Z]{2,}[ [A-Z]{2,}]*)",
                                                blockquote_split[i - 1],
                                            )
                                        )
                                        data["nombre"] = ApropiacionSocial._clean_text(
                                            re.sub(
                                                r"([A-Z]{2,}[ [A-Z]{2,}]*)",
                                                "",
                                                blockquote_split[i - 1],
                                            ).replace(", ", "")
                                        )
                                    try:
                                        if i + 8 < len(blockquote_split):
                                            data["fecha"] = "".join(
                                                blockquote_split[i + 8].split()
                                            ).replace(".", "")
                                    except Exception:
                                        pass
                                else:
                                    if i + 8 < len(blockquote_split):
                                        data["ciudad"] = ApropiacionSocial._clean_text(
                                            blockquote_split[i + 8]
                                        )[:-1]
                            elif (
                                blockquote_split[i]
                                == "Base de datos donde está incluido el registro:"
                            ):
                                if i + 6 < len(blockquote_split):
                                    data["base_datos"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 6]
                                    )
                            elif blockquote_split[i] == "disponible en":
                                if i + 5 < len(blockquote_split):
                                    data["disponible_en"] = (
                                        ApropiacionSocial._clean_text(
                                            blockquote_split[i + 5]
                                        )
                                    )
                            elif blockquote_split[i] == "Institución:":
                                if i + 4 < len(blockquote_split):
                                    data["institucion"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 4]
                                    )
                            elif blockquote_split[i] == "Palabras:":
                                if i + 3 < len(blockquote_split):
                                    data["palabras"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "Areas:":
                                if i + 2 < len(blockquote_split):
                                    data["areas"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 2]
                                    )
                            elif blockquote_split[i] == "Sectores:":
                                if i + 1 < len(blockquote_split):
                                    data["sectores"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 1]
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de secuencia genética: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("secuencias_geneticas", data, connection)
                    module_logger.debug(f"Secuencia genética insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando secuencia genética para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_secuencia para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_contenido_virtual(cod_rh, h3, connection):
        """
        Extrae información sobre generación de contenido virtual.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para contenido virtual en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Nombre)|(Tipo)|(disponible en)|(Descripción:)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre":
                                if i + 4 < len(blockquote_split):
                                    data["titulo"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 4]
                                    )
                            elif blockquote_split[i] == "Tipo":
                                if i + 3 < len(blockquote_split):
                                    tipo_split = blockquote_split[i + 3].split("-")
                                    if len(tipo_split) > 2:
                                        tipo_comma_split = tipo_split[2].split(",")
                                        if len(tipo_comma_split) > 0:
                                            data["tipo"] = (
                                                ApropiacionSocial._clean_text(
                                                    tipo_comma_split[0]
                                                )
                                            )

                                    fecha = re.findall(
                                        r"[0-9]{4}-[0-9]{2}-[0-9]{2}.*",
                                        blockquote_split[i + 3],
                                    )
                                    if fecha:
                                        data["fecha"] = ApropiacionSocial._clean_text(
                                            fecha[0]
                                        )
                            elif blockquote_split[i] == "disponible en":
                                if i + 2 < len(blockquote_split):
                                    data["disponible_en"] = (
                                        ApropiacionSocial._clean_text(
                                            blockquote_split[i + 2]
                                        )
                                    )
                            elif blockquote_split[i] == "Descripción:":
                                if i + 1 < len(blockquote_split):
                                    data["descripcion"] = blockquote_split[i + 1]
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de contenido virtual: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("contenido_virtual", data, connection)
                    module_logger.debug(f"Contenido virtual insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando contenido virtual para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_contenido_virtual para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_estrategias_conocimiento(cod_rh, h3, connection):
        """
        Extrae información sobre estrategias de comunicación del conocimiento.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para estrategias de comunicación en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Nombre de la estrategia)|(Inicio en)|(Finalizó en :)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre de la estrategia":
                                if i + 3 < len(blockquote_split):
                                    data["nombre"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "Inicio en":
                                if i + 2 < len(blockquote_split):
                                    data["fecha_inicio"] = (
                                        ApropiacionSocial._clean_text(
                                            blockquote_split[i + 2].replace(",", "")
                                        )
                                    )
                            elif blockquote_split[i] == "Finalizó en :":
                                if i + 1 < len(blockquote_split):
                                    data["fecha_fin"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 1].replace(",", "")
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de estrategia de comunicación: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("estrategias_comunicacion", data, connection)
                    module_logger.debug(
                        f"Estrategia de comunicación insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando estrategia de comunicación para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_estrategias_conocimiento para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_estrategias_pedagogicas(cod_rh, h3, connection):
        """
        Extrae información sobre estrategias pedagógicas para el fomento a la CTI.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para estrategias pedagógicas en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Nombre de la estrategia)|(Inicio en)|(Finalizó en :)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre de la estrategia":
                                if i + 3 < len(blockquote_split):
                                    data["nombre"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "Inicio en":
                                if i + 2 < len(blockquote_split):
                                    data["fecha_inicio"] = (
                                        ApropiacionSocial._clean_text(
                                            blockquote_split[i + 2].replace(",", "")
                                        )
                                    )
                            elif blockquote_split[i] == "Finalizó en :":
                                if i + 1 < len(blockquote_split):
                                    data["fecha_fin"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 1].replace(",", "")
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de estrategia pedagógica: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("estrategias_pedagogicas", data, connection)
                    module_logger.debug(
                        f"Estrategia pedagógica insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando estrategia pedagógica para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_estrategias_pedagogicas para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_espacios_participacion(cod_rh, h3, connection):
        """
        Extrae información sobre espacios de participación ciudadana.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para espacios de participación en {cod_rh}"
                )
                return

            tds = table.find_all("td")

            # Eliminar el primer elemento (encabezado) si existe
            if len(tds) > 1:
                tds = tds[1:]
            else:
                module_logger.warning(
                    f"No se encontraron espacios de participación para {cod_rh}"
                )
                return

            for td in tds:
                try:
                    data = {"cvlac_id": cod_rh}

                    td_split = re.split(
                        "(Nombre del espacio)|(Realizado el:)|(Finalizó en :)", td.text
                    )

                    for i in range(len(td_split)):
                        try:
                            if td_split[i] == "Nombre del espacio":
                                if i + 3 < len(td_split):
                                    data["nombre"] = ApropiacionSocial._clean_text(
                                        td_split[i + 3]
                                    )
                            elif td_split[i] == "Realizado el:":
                                if i + 2 < len(td_split):
                                    fechas = re.findall(
                                        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", td_split[i + 2]
                                    )
                                    if len(fechas) > 0:
                                        data["fecha_inicio"] = fechas[0]
                                    if len(fechas) > 1:
                                        data["fecha_fin"] = fechas[1]

                                    temp = re.split("en|Con", td_split[i + 2])
                                    if len(temp) > 1:
                                        data["ciudad"] = ApropiacionSocial._clean_text(
                                            temp[1].replace("-", "")
                                        )
                                    if len(temp) > 2:
                                        participantes = re.findall(r"[0-9]+", temp[2])
                                        if participantes and participantes[0] != "":
                                            try:
                                                data["participantes"] = int(
                                                    participantes[0]
                                                )
                                            except (ValueError, TypeError):
                                                module_logger.warning(
                                                    f"No se pudo convertir los participantes a entero: {participantes[0]}"
                                                )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de espacio de participación: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("espacios_participacion", data, connection)
                    module_logger.debug(
                        f"Espacio de participación insertado para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando espacio de participación para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_espacios_participacion para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_participacion_proyectos(cod_rh, h3, connection):
        """
        Extrae información sobre participación ciudadana en proyectos de CTI.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para participación en proyectos de CTI en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split(
                        "(Nombre del proyecto)|(Inicio en)|(Finalizó en :)",
                        blockquote.text,
                    )

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "Nombre del proyecto":
                                if i + 3 < len(blockquote_split):
                                    data["nombre"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 3]
                                    )
                            elif blockquote_split[i] == "Inicio en":
                                if i + 2 < len(blockquote_split):
                                    data["fecha_inicio"] = (
                                        ApropiacionSocial._clean_text(
                                            blockquote_split[i + 2].replace(",", "")
                                        )
                                    )
                            elif blockquote_split[i] == "Finalizó en :":
                                if i + 1 < len(blockquote_split):
                                    data["fecha_fin"] = ApropiacionSocial._clean_text(
                                        blockquote_split[i + 1].replace(",", "")
                                    )
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de participación en proyecto: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("participacion_proyectos", data, connection)
                    module_logger.debug(
                        f"Participación en proyecto de CTI insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando participación en proyecto para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_participacion_proyectos para {cod_rh}: {str(ex)}",
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
def extract_consultorias(cod_rh, h3, connection):
    """Función de compatibilidad para extract_consultorias"""
    return ApropiacionSocial.extract_consultorias(cod_rh, h3, connection)


def extract_ediciones_revisiones(cod_rh, h3, connection):
    """Función de compatibilidad para extract_ediciones_revisiones"""
    return ApropiacionSocial.extract_ediciones_revisiones(cod_rh, h3, connection)


def extract_eventos_cientificos(cod_rh, h3, nombre_completo, connection):
    """Función de compatibilidad para extract_eventos_cientificos"""
    return ApropiacionSocial.extract_eventos_cientificos(
        cod_rh, h3, nombre_completo, connection
    )


def extract_informes(cod_rh, h3, connection):
    """Función de compatibilidad para extract_informes"""
    return ApropiacionSocial.extract_informes(cod_rh, h3, connection)


def extract_redes_conocimiento(cod_rh, h3, connection):
    """Función de compatibilidad para extract_redes_conocimiento"""
    return ApropiacionSocial.extract_redes_conocimiento(cod_rh, h3, connection)


def extract_audio(cod_rh, h3, connection):
    """Función de compatibilidad para extract_audio"""
    return ApropiacionSocial.extract_audio(cod_rh, h3, connection)


def extract_impreso(cod_rh, h3, connection):
    """Función de compatibilidad para extract_impreso"""
    return ApropiacionSocial.extract_impreso(cod_rh, h3, connection)


def extract_multimedia(cod_rh, h3, connection):
    """Función de compatibilidad para extract_multimedia"""
    return ApropiacionSocial.extract_multimedia(cod_rh, h3, connection)


def extract_secuencia(cod_rh, h3, connection):
    """Función de compatibilidad para extract_secuencia"""
    return ApropiacionSocial.extract_secuencia(cod_rh, h3, connection)


def extract_contenido_virtual(cod_rh, h3, connection):
    """Función de compatibilidad para extract_contenido_virtual"""
    return ApropiacionSocial.extract_contenido_virtual(cod_rh, h3, connection)


def extract_estrategias_conocimiento(cod_rh, h3, connection):
    """Función de compatibilidad para extract_estrategias_conocimiento"""
    return ApropiacionSocial.extract_estrategias_conocimiento(cod_rh, h3, connection)


def extract_estrategias_pedagogicas(cod_rh, h3, connection):
    """Función de compatibilidad para extract_estrategias_pedagogicas"""
    return ApropiacionSocial.extract_estrategias_pedagogicas(cod_rh, h3, connection)


def extract_espacios_participacion(cod_rh, h3, connection):
    """Función de compatibilidad para extract_espacios_participacion"""
    return ApropiacionSocial.extract_espacios_participacion(cod_rh, h3, connection)


def extract_participacion_proyectos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_participacion_proyectos"""
    return ApropiacionSocial.extract_participacion_proyectos(cod_rh, h3, connection)
