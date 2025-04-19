from config import ProjectLogger
from extractors.utils import get_table, get_text_next_tag, get_href, insert_data

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class IdentificacionExtractor:
    """
    Clase para extraer información de identificación del investigador.
    """

    @staticmethod
    def extract(cod_rh, html, connection):
        """
        Extrae información de identificación del investigador.

        Args:
            cod_rh (str): Código del investigador.
            html (BeautifulSoup): Documento HTML completo.
            connection: Conexión a la base de datos.

        Returns:
            str: Nombre completo del investigador o None si no se pudo extraer.
        """
        try:
            data = {"cvlac_id": cod_rh}

            # Obtener la tabla de datos generales
            table = get_table(html, {"name": "datos_generales"})

            if not table:
                module_logger.warning(
                    f"No se encontró tabla de datos generales para {cod_rh}"
                )
                return None

            # Extraer categoría
            categoria = get_text_next_tag(table, "Categoría", "td")
            if categoria:
                data["categoria"] = " ".join(categoria.split())

            # Extraer nombre completo
            nombre_completo = get_text_next_tag(table, "Nombre", "td")
            if nombre_completo:
                data["nombre_completo"] = IdentificacionExtractor._clean_text(
                    nombre_completo
                ).replace("\xa0", " ")
            else:
                module_logger.warning(f"No se encontró nombre completo para {cod_rh}")
                return None

            # Extraer nombre en citaciones
            nombre_citaciones = get_text_next_tag(table, "Nombre en citaciones", "td")
            if nombre_citaciones:
                data["nombre_citaciones"] = nombre_citaciones

            # Extraer nacionalidad
            nacionalidad = get_text_next_tag(table, "Nacionalidad", "td")
            if nacionalidad:
                data["nacionalidad"] = nacionalidad

            # Extraer género
            genero = get_text_next_tag(table, "Sexo", "td")
            if genero:
                data["genero"] = genero

            # Extraer código ORCID
            codigo_orcid = get_href(table, "Código ORCID")
            if codigo_orcid:
                data["codigo_orcid"] = codigo_orcid

            # Extraer author ID SCOPUS
            author_id_scopus = get_href(table, "Author ID SCOPUS")
            if author_id_scopus:
                data["author_id_scopus"] = author_id_scopus

            # Verificar si es par evaluador reconocido
            message_text = table.find("b")
            if (
                message_text
                and message_text.text == "Par evaluador reconocido por Minciencias."
            ):
                data["reconocido_colciencias"] = "Sí"

            # Insertar en la base de datos y retornar nombre completo
            insert_data("identificacion", data, connection)
            module_logger.debug(f"Identificación insertada para {cod_rh}")

            return data["nombre_completo"]
        except Exception as ex:
            module_logger.error(
                f"Error general en extract para {cod_rh}: {str(ex)}", exc_info=True
            )
            return None

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
def extract(cod_rh, html, connection):
    """Función de compatibilidad para extract"""
    return IdentificacionExtractor.extract(cod_rh, html, connection)
