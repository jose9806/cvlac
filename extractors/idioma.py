from config import ProjectLogger
from extractors.utils import insert_data
from datetime import datetime

# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class IdiomaExtractor:
    """
    Clase para extraer información relacionada con idiomas del investigador.
    """

    @staticmethod
    def extract(cod_rh, h3, connection):
        """
        Extrae información sobre idiomas.

        Args:
            cod_rh (str): Código del investigador.
            h3 (BeautifulSoup): Elemento HTML que contiene la información.
            connection: Conexión a la base de datos.
        """
        try:
            table = h3.parent.parent.parent

            if not table:
                module_logger.warning(f"No se encontró tabla para idiomas en {cod_rh}")
                return

            for tr in table.find_all("tr"):
                try:
                    data = {"cvlac_id": cod_rh}

                    # Extraer información del idioma
                    info_language = [a for a in tr.strings]

                    # Verificar que la estructura sea correcta y que haya información
                    if len(info_language) == 11 and info_language[1] != "\xa0":
                        data["idioma"] = info_language[1].replace("\xa0", "")
                        data["habla"] = info_language[3]
                        data["escribe"] = info_language[5]
                        data["lee"] = info_language[7]
                        data["entiende"] = info_language[9]

                        # Insertar en la base de datos
                        insert_data("idioma", data, connection)
                        module_logger.debug(
                            f"Idioma {data['idioma']} insertado para {cod_rh}"
                        )
                except Exception as ex:
                    module_logger.error(
                        f"Error procesando idioma para {cod_rh}: {str(ex)}",
                        exc_info=True,
                    )
        except Exception as ex:
            module_logger.error(
                f"Error general en extract para {cod_rh}: {str(ex)}", exc_info=True
            )


# Función de compatibilidad para el código existente
def extract(cod_rh, h3, connection):
    """Función de compatibilidad para extract"""
    return IdiomaExtractor.extract(cod_rh, h3, connection)
