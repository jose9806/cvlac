from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime
import re

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class ProduccionBibliograficaExtractor:
    """
    Clase para extraer información relacionada con producción bibliográfica del investigador.
    """

    @staticmethod
    def extract_articulos(cod_rh, h3, connection):
        """
        Extrae información sobre artículos.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para artículos en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en artículos: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ProduccionBibliograficaExtractor._clean_text(
                            li_split[2]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(En:)|(ISSN:)|(ed:)|(fasc.)|(DOI:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ProduccionBibliograficaExtractor._extract_blockquote_articulos(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("articulos", data, connection)
                    module_logger.debug(f"Artículo insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando artículo {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_articulos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_articulos(blockquote_split, data):
        """
        Extrae información del blockquote para artículos.

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
                                "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[:j][0]
                            )
                        )
                        titulo_split = re.split("[A-Z]{2,},", blockquote_split[j - 1])
                        if len(titulo_split) > 0:
                            data["titulo"] = (
                                ProduccionBibliograficaExtractor._clean_text(
                                    titulo_split[-1][:-1]
                                )
                            )

                    if j + 8 < len(blockquote_split):
                        temp = blockquote_split[j + 8].split("\xa0\n")
                        if len(temp) > 0:
                            data["pais"] = ProduccionBibliograficaExtractor._clean_text(
                                temp[0]
                            )
                        if len(temp) > 1:
                            data["revista"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[1])
                            )
                elif blockquote_split[j] == "ISSN:":
                    if j + 7 < len(blockquote_split):
                        data["issn"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 7]
                        )
                elif blockquote_split[j] == "ed:":
                    if j + 6 < len(blockquote_split):
                        temp = blockquote_split[j + 6].split("\n")
                        if len(temp) > 0:
                            data["editorial"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[0])
                            )
                        if len(temp) > 1:
                            data["volumen"] = temp[1]
                elif blockquote_split[j] == "fasc.":
                    if j + 5 < len(blockquote_split):
                        temp = blockquote_split[j + 5].split("\n")
                        if len(temp) > 0:
                            data["fasciculo"] = temp[0]

                        # Extraer página inicial
                        if len(temp) > 1:
                            pagina_inicial = re.findall(r"[0-9]+", temp[1])
                            if pagina_inicial:
                                try:
                                    data["pagina_inicial"] = int(pagina_inicial[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página inicial a entero: {pagina_inicial[0]}"
                                    )

                        # Extraer página final
                        if len(temp) > 2:
                            pagina_final = re.findall(r"[0-9]+", temp[2])
                            if pagina_final:
                                try:
                                    data["pagina_final"] = int(pagina_final[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página final a entero: {pagina_final[0]}"
                                    )

                        # Extraer año
                        if len(temp) > 3:
                            ano = re.findall(r"[0-9]+", temp[3])
                            if ano:
                                try:
                                    data["ano"] = int(ano[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir el año a entero: {ano[0]}"
                                    )
                elif blockquote_split[j] == "DOI:":
                    if j + 4 < len(blockquote_split):
                        data["doi"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 4]
                        )
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote artículos: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_capitulos(cod_rh, h3, connection):
        """
        Extrae información sobre capítulos de libro.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para capítulos de libro en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}
                    data["chulo"] = "SI" if blockquote.find("img") else "NO"
                    data["coautores"] = ""

                    blockquote_split = re.split(
                        "(Tipo:)|(En:)|(ISBN:)|(ed:)|(Palabras:)|(Areas:)|(Sectores:)",
                        blockquote.text,
                    )

                    # Verificar que haya suficientes elementos
                    if len(blockquote_split) > 6:
                        tipo_split = blockquote_split[6].split("\n")
                        if tipo_split:
                            data["tipo"] = tipo_split[0]

                    ProduccionBibliograficaExtractor._extract_blockquote_capitulos(
                        blockquote_split, data
                    )

                    # Insertar en la base de datos
                    insert_data("capitulos_libro", data, connection)
                    module_logger.debug(f"Capítulo de libro insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando capítulo de libro para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_capitulos para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_capitulos(blockquote_split, data):
        """
        Extrae información del blockquote para capítulos de libro.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for i in range(len(blockquote_split)):
            try:
                if blockquote_split[i] == "Tipo:":
                    if i - 1 >= 0:
                        coautores = re.findall(
                            "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[i - 1]
                        )
                        if coautores:
                            data["coautores"] += coautores[0] + ", "
                elif blockquote_split[i] == "En:":
                    if i - 2 >= 0:
                        coautores = re.findall(
                            "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[i - 2]
                        )
                        if coautores:
                            data["coautores"] += coautores[0] + ", "

                        titulo = re.findall(r'".*"', blockquote_split[i - 2])
                        if titulo:
                            data["titulo_capitulo"] = titulo[0]

                        libro_split = blockquote_split[i - 2].split("\n")
                        if len(libro_split) > 1:
                            data["libro"] = (
                                ProduccionBibliograficaExtractor._clean_text(
                                    libro_split[-2]
                                )
                            )

                    if i + 6 < len(blockquote_split):
                        data["lugar_publicacion"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[i + 6]
                            )
                        )
                elif blockquote_split[i] == "ISBN:":
                    if i + 5 < len(blockquote_split):
                        data["isbn"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[i + 5]
                        )
                elif blockquote_split[i] == "ed:":
                    if i + 4 < len(blockquote_split):
                        temp = blockquote_split[i + 4].split("\n")
                        if len(temp) > 0:
                            data["editorial"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[0])
                            )

                        # Extraer volumen
                        if len(temp) > 1:
                            volumen = re.findall(r"[0-9]+", temp[1])
                            if volumen:
                                data["volumen"] = volumen[0]

                        # Extraer página inicial
                        if len(temp) > 2:
                            pagina_inicial = re.findall(r"[0-9]+", temp[2])
                            if pagina_inicial:
                                try:
                                    data["pagina_inicial"] = int(pagina_inicial[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página inicial a entero: {pagina_inicial[0]}"
                                    )

                        # Extraer página final
                        if len(temp) > 3:
                            pagina_final = re.findall(r"[0-9]+", temp[3])
                            if pagina_final:
                                try:
                                    data["pagina_final"] = int(pagina_final[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página final a entero: {pagina_final[0]}"
                                    )

                        # Extraer año
                        if len(temp) > 5:
                            ano = re.findall(r"[0-9]+", temp[5])
                            if ano:
                                try:
                                    data["ano"] = int(ano[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir el año a entero: {ano[0]}"
                                    )
                elif blockquote_split[i] == "Palabras:":
                    if i + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[i + 3]
                        )
                elif blockquote_split[i] == "Areas:":
                    if i + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[i + 2]
                        )
                elif blockquote_split[i] == "Sectores:":
                    if i + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[i + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote capítulos: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_libros(cod_rh, h3, connection):
        """
        Extrae información sobre libros.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para libros en {cod_rh}")
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en libros: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ProduccionBibliograficaExtractor._clean_text(
                            li_split[2]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(En:)|(ed:)|(ISBN:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ProduccionBibliograficaExtractor._extract_blockquote_libros(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("libros", data, connection)
                    module_logger.debug(f"Libro insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando libro {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_libros para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_libros(blockquote_split, data):
        """
        Extrae información del blockquote para libros.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "En:":
                    if j - 1 >= 0:
                        data["coautores"] = ", ".join(
                            re.findall(
                                "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j - 1]
                            )
                        )
                        titulo = re.findall(r'".*"', blockquote_split[j - 1])
                        if titulo:
                            data["titulo"] = (
                                titulo[0]
                                .replace("\t'", '"')
                                .replace("  ", "")
                                .replace("\n", "")
                                .replace("\r", "")
                            )

                    if j + 6 < len(blockquote_split):
                        lugar = re.sub(r"[0-9]+", "", blockquote_split[j + 6]).replace(
                            ".", ""
                        )
                        data["lugar_publicacion"] = (
                            ProduccionBibliograficaExtractor._clean_text(lugar)
                        )

                        anos = re.findall(r"[0-9]+", blockquote_split[j + 6])
                        if anos:
                            try:
                                data["ano"] = int(anos[0])
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {anos[0]}"
                                )
                elif blockquote_split[j] == "ed:":
                    if j + 5 < len(blockquote_split):
                        data["editorial"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[j + 5]
                            )
                        )
                elif blockquote_split[j] == "ISBN:":
                    if j + 4 < len(blockquote_split):
                        temp = blockquote_split[j + 4].split("\n")
                        if len(temp) > 0:
                            data["isbn"] = ProduccionBibliograficaExtractor._clean_text(
                                temp[0]
                            )

                        # Extraer volumen
                        if len(temp) > 1:
                            data["volumen"] = "".join(re.findall(r"[0-9]+", temp[1]))

                        # Extraer páginas
                        if len(temp) > 2:
                            data["paginas"] = "".join(re.findall(r"[0-9]+", temp[2]))
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote libros: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_working_papers(cod_rh, h3, connection):
        """
        Extrae información sobre documentos de trabajo.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para documentos de trabajo en {cod_rh}"
                )
                return

            blockquotes = table.find_all("blockquote")

            for blockquote in blockquotes:
                try:
                    data = {"cvlac_id": cod_rh}

                    blockquote_split = re.split("(En:)", blockquote.text)

                    for i in range(len(blockquote_split)):
                        try:
                            if blockquote_split[i] == "En:":
                                if i - 1 >= 0:
                                    nombre = re.findall(
                                        r'".*"', blockquote_split[i - 1]
                                    )
                                    if nombre:
                                        data["nombre"] = nombre[0]

                                if i + 1 < len(blockquote_split):
                                    temp_split = blockquote_split[i + 1].split("\n")
                                    if len(temp_split) > 1:
                                        ano_text = ProduccionBibliograficaExtractor._clean_text(
                                            temp_split[1]
                                        )[
                                            :-1
                                        ]
                                        try:
                                            data["ano"] = int(ano_text)
                                        except (ValueError, TypeError):
                                            module_logger.warning(
                                                f"No se pudo convertir el año a entero: {ano_text}"
                                            )

                                if len(blockquote_split) > (i + 1):
                                    paginas = re.findall(
                                        r"[0-9]+", blockquote_split[-2]
                                    )
                                    if paginas:
                                        data["paginas"] = paginas
                        except Exception as ex:
                            module_logger.error(
                                f"Error extrayendo datos de documento de trabajo para {cod_rh}: {str(ex)}",
                                exc_info=True,
                            )

                    insert_data("documentos_trabajo", data, connection)
                    module_logger.debug(f"Documento de trabajo insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando documento de trabajo para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_working_papers para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def extract_otra_produccion(cod_rh, h3, connection):
        """
        Extrae información sobre otra producción bibliográfica.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para otra producción bibliográfica en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en otra producción: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ProduccionBibliograficaExtractor._clean_text(
                            li_split[2]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(En:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ProduccionBibliograficaExtractor._extract_blockquote_otra_produccion(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("otra_produccion", data, connection)
                    module_logger.debug(
                        f"Otra producción bibliográfica insertada para {cod_rh}"
                    )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando otra producción {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_otra_produccion para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_otra_produccion(blockquote_split, data):
        """
        Extrae información del blockquote para otra producción bibliográfica.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "En:":
                    if j - 1 >= 0:
                        data["coautores"] = ", ".join(
                            re.findall(
                                "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j - 1]
                            )
                        )
                        titulo = re.findall(r'".*"', blockquote_split[j - 1])
                        if titulo:
                            data["titulo"] = (
                                titulo[0]
                                .replace("\t'", '"')
                                .replace("  ", "")
                                .replace("\n", "")
                                .replace("\r", "")
                            )

                    if j + 4 < len(blockquote_split):
                        temp = blockquote_split[j + 4].split("\n")
                        if len(temp) > 1:
                            ano_text = ProduccionBibliograficaExtractor._clean_text(
                                temp[1]
                            )[:-1]
                            try:
                                data["ano"] = int(ano_text)
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {ano_text}"
                                )
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote otra producción: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_textos_no_cientificas(cod_rh, h3, connection):
        """
        Extrae información sobre textos en publicaciones no científicas.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para textos no científicos en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en textos no científicos: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ProduccionBibliograficaExtractor._clean_text(
                            li_split[2]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(En:)|(ISSN:)|(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ProduccionBibliograficaExtractor._extract_blockquote_textos_no_cientificas(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("textos_no_cientificas", data, connection)
                    module_logger.debug(f"Texto no científico insertado para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando texto no científico {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_textos_no_cientificas para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_textos_no_cientificas(blockquote_split, data):
        """
        Extrae información del blockquote para textos en publicaciones no científicas.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "En:":
                    if j - 1 >= 0:
                        data["coautores"] = ", ".join(
                            re.findall(
                                "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j - 1]
                            )
                        )
                        titulo = re.findall(r'".*"', blockquote_split[j - 1])
                        if titulo:
                            data["titulo"] = (
                                titulo[0]
                                .replace("\t'", '"')
                                .replace("  ", "")
                                .replace("\n", "")
                                .replace("\r", "")
                            )

                    if j + 5 < len(blockquote_split):
                        temp = blockquote_split[j + 5].split("\n")
                        if len(temp) > 0:
                            data["pais"] = ProduccionBibliograficaExtractor._clean_text(
                                temp[0]
                            )[:-1]
                        if len(temp) > 1:
                            ano_text = ProduccionBibliograficaExtractor._clean_text(
                                temp[1]
                            )[:-1]
                            try:
                                data["ano"] = int(ano_text)
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {ano_text}"
                                )
                        if len(temp) > 2:
                            data["revista"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[2])[
                                    :-1
                                ]
                            )
                elif blockquote_split[j] == "ISSN:":
                    if j + 4 < len(blockquote_split):
                        temp = blockquote_split[j + 4].split("\n")
                        if len(temp) > 0:
                            data["issn"] = ProduccionBibliograficaExtractor._clean_text(
                                temp[0]
                            )

                        # Extraer página inicial
                        if len(temp) > 1:
                            pagina_inicial = re.findall(r"[0-9]+", temp[1])
                            if pagina_inicial:
                                try:
                                    data["pagina_inicial"] = int(pagina_inicial[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página inicial a entero: {pagina_inicial[0]}"
                                    )

                        # Extraer página final
                        if len(temp) > 2:
                            pagina_final = re.findall(r"[0-9]+", temp[2])
                            if pagina_final:
                                try:
                                    data["pagina_final"] = int(pagina_final[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página final a entero: {pagina_final[0]}"
                                    )

                        if len(temp) > 3:
                            data["volumen"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[3])
                            )
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote textos no científicos: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_traducciones(cod_rh, h3, connection):
        """
        Extrae información sobre traducciones.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para traducciones en {cod_rh}"
                )
                return

            lis = table.find_all("li")
            blockquotes = table.find_all("blockquote")

            if len(lis) != len(blockquotes):
                module_logger.warning(
                    f"Número desigual de elementos li y blockquote en traducciones: {cod_rh}"
                )

            for i in range(len(lis)):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del elemento li
                    data["chulo"] = "SI" if lis[i].find("img") else "NO"
                    li_split = lis[i].text.split("-")
                    if len(li_split) > 2:
                        data["tipo"] = ProduccionBibliograficaExtractor._clean_text(
                            li_split[2]
                        )

                    # Extraer información del blockquote
                    if i < len(blockquotes):
                        blockquote_split = re.split(
                            "(En:)|(Idioma original:)|(Idioma traducción:)|(Autor:)|(Nombre original:)|"
                            "(Palabras:)|(Areas:)|(Sectores:)",
                            blockquotes[i].text,
                        )

                        ProduccionBibliograficaExtractor._extract_blockquote_traducciones(
                            blockquote_split, data
                        )

                    # Insertar en la base de datos
                    insert_data("traducciones", data, connection)
                    module_logger.debug(f"Traducción insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando traducción {i} para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_traducciones para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_traducciones(blockquote_split, data):
        """
        Extrae información del blockquote para traducciones.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "En:":
                    if j - 1 >= 0:
                        data["coautores"] = ", ".join(
                            re.findall(
                                "[A-Z]{2,}[ [A-Z]{2,}]*", blockquote_split[j - 1]
                            )
                        )
                        nombre = re.findall(r'".*"', blockquote_split[j - 1])
                        if nombre:
                            data["nombre"] = nombre[0]

                    if j + 8 < len(blockquote_split):
                        temp = blockquote_split[j + 8].split("\n")
                        if len(temp) > 0:
                            data["pais"] = ProduccionBibliograficaExtractor._clean_text(
                                temp[0]
                            )[:-1]
                        if len(temp) > 1:
                            ano_text = ProduccionBibliograficaExtractor._clean_text(
                                temp[1]
                            )[:-1]
                            try:
                                data["ano"] = int(ano_text)
                            except (ValueError, TypeError):
                                module_logger.warning(
                                    f"No se pudo convertir el año a entero: {ano_text}"
                                )
                elif blockquote_split[j] == "Idioma original:":
                    if j + 7 < len(blockquote_split):
                        data["idioma_original"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[j + 7]
                            )
                        )
                elif blockquote_split[j] == "Idioma traducción:":
                    if j + 6 < len(blockquote_split):
                        data["idioma_traduccion"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[j + 6]
                            )
                        )
                elif blockquote_split[j] == "Autor:":
                    if j + 5 < len(blockquote_split):
                        data["autor"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 5]
                        )
                elif blockquote_split[j] == "Nombre original:":
                    if j + 4 < len(blockquote_split):
                        volumen = re.findall(r"v.[0-9]*", blockquote_split[j + 4])
                        if volumen:
                            data["volumen"] = volumen[0]
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote traducciones: {str(ex)}",
                    exc_info=True,
                )

    @staticmethod
    def extract_notas_cientificas(cod_rh, h3, connection):
        """
        Extrae información sobre notas científicas.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(
                    f"No se encontró tabla para notas científicas en {cod_rh}"
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
                        "(medio de divulgación:)|(Idioma original:)|(ISSN:)|(ed:)|(Sitio web:)|"
                        "(DOI:)|(Palabras:)|(Areas:)|(Sectores:)",
                        blockquote.text,
                    )

                    ProduccionBibliograficaExtractor._extract_blockquote_notas_cientificas(
                        blockquote_split, data
                    )

                    # Insertar en la base de datos
                    insert_data("notas_cientificas", data, connection)
                    module_logger.debug(f"Nota científica insertada para {cod_rh}")
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando nota científica para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract_notas_cientificas para {cod_rh}: {str(ex)}",
                exc_info=True,
            )

    @staticmethod
    def _extract_blockquote_notas_cientificas(blockquote_split, data):
        """
        Extrae información del blockquote para notas científicas.

        Args:
            blockquote_split (list): Lista con las partes del blockquote.
            data (dict): Diccionario donde se almacenará la información.
        """
        for j in range(len(blockquote_split)):
            try:
                if blockquote_split[j] == "medio de divulgación:":
                    if j - 1 >= 0:
                        temp = re.split(r'(".*")', blockquote_split[j - 1])
                        if len(temp) > 0:
                            data["coautores"] = ", ".join(
                                re.findall("[A-Z]{2,}[ [A-Z]{2,}]*", temp[0])
                            )
                        if len(temp) > 1:
                            data["titulo_nota"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[1])
                            )
                        if len(temp) > 2:
                            data["revista"] = (
                                ProduccionBibliograficaExtractor._clean_text(
                                    temp[2][1:]
                                )
                            )

                    if j + 9 < len(blockquote_split):
                        data["medio_divulgacion"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[j + 9]
                            )
                        )
                elif blockquote_split[j] == "Idioma original:":
                    if j + 8 < len(blockquote_split):
                        data["idioma_original"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[j + 8]
                            )
                        )
                elif blockquote_split[j] == "ISSN:":
                    if j + 7 < len(blockquote_split):
                        data["issn"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 7]
                        )
                elif blockquote_split[j] == "ed:":
                    if j + 6 < len(blockquote_split):
                        temp = blockquote_split[j + 6].split("\n")
                        if len(temp) > 0:
                            data["editorial"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[0])
                            )
                        if len(temp) > 1:
                            data["volumen"] = (
                                ProduccionBibliograficaExtractor._clean_text(temp[1])
                            )
                        if len(temp) > 2:
                            data["fasc"] = ProduccionBibliograficaExtractor._clean_text(
                                temp[2]
                            )

                        # Extraer página inicial
                        if len(temp) > 3:
                            pagina_inicial = re.findall(r"[0-9]+", temp[3])
                            if pagina_inicial:
                                try:
                                    data["pagina_inicial"] = int(pagina_inicial[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página inicial a entero: {pagina_inicial[0]}"
                                    )

                        # Extraer página final
                        if len(temp) > 4:
                            pagina_final = re.findall(r"[0-9]+", temp[4])
                            if pagina_final:
                                try:
                                    data["pagina_final"] = int(pagina_final[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir la página final a entero: {pagina_final[0]}"
                                    )

                        # Extraer año
                        if len(temp) > 5:
                            ano = re.findall(r"[0-9]+", temp[5])
                            if ano:
                                try:
                                    data["ano"] = int(ano[0])
                                except (ValueError, TypeError):
                                    module_logger.warning(
                                        f"No se pudo convertir el año a entero: {ano[0]}"
                                    )
                elif blockquote_split[j] == "Sitio web:":
                    if j + 5 < len(blockquote_split):
                        data["sitio_web"] = (
                            ProduccionBibliograficaExtractor._clean_text(
                                blockquote_split[j + 5]
                            )
                        )
                elif blockquote_split[j] == "DOI:":
                    if j + 4 < len(blockquote_split):
                        data["doi"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 4]
                        )
                elif blockquote_split[j] == "Palabras:":
                    if j + 3 < len(blockquote_split):
                        data["palabras"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 3]
                        )
                elif blockquote_split[j] == "Areas:":
                    if j + 2 < len(blockquote_split):
                        data["areas"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 2]
                        )
                elif blockquote_split[j] == "Sectores:":
                    if j + 1 < len(blockquote_split):
                        data["sectores"] = ProduccionBibliograficaExtractor._clean_text(
                            blockquote_split[j + 1]
                        )
            except Exception as ex:
                module_logger.error(
                    f"Error extrayendo datos del blockquote notas científicas: {str(ex)}",
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
def extract_articulos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_articulos"""
    return ProduccionBibliograficaExtractor.extract_articulos(cod_rh, h3, connection)


def extract_capitulos(cod_rh, h3, connection):
    """Función de compatibilidad para extract_capitulos"""
    return ProduccionBibliograficaExtractor.extract_capitulos(cod_rh, h3, connection)


def extract_libros(cod_rh, h3, connection):
    """Función de compatibilidad para extract_libros"""
    return ProduccionBibliograficaExtractor.extract_libros(cod_rh, h3, connection)


def extract_working_papers(cod_rh, h3, connection):
    """Función de compatibilidad para extract_working_papers"""
    return ProduccionBibliograficaExtractor.extract_working_papers(
        cod_rh, h3, connection
    )


def extract_otra_produccion(cod_rh, h3, connection):
    """Función de compatibilidad para extract_otra_produccion"""
    return ProduccionBibliograficaExtractor.extract_otra_produccion(
        cod_rh, h3, connection
    )


def extract_textos_no_cientificas(cod_rh, h3, connection):
    """Función de compatibilidad para extract_textos_no_cientificas"""
    return ProduccionBibliograficaExtractor.extract_textos_no_cientificas(
        cod_rh, h3, connection
    )


def extract_traducciones(cod_rh, h3, connection):
    """Función de compatibilidad para extract_traducciones"""
    return ProduccionBibliograficaExtractor.extract_traducciones(cod_rh, h3, connection)


def extract_notas_cientificas(cod_rh, h3, connection):
    """Función de compatibilidad para extract_notas_cientificas"""
    return ProduccionBibliograficaExtractor.extract_notas_cientificas(
        cod_rh, h3, connection
    )
