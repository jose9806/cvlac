from psycopg2 import OperationalError, connect
from contextlib import contextmanager
from config import ProjectLogger, project_settings


# Configuramos el logger para este módulo
logger = ProjectLogger()
module_logger = logger.get_logger(__name__)


class DatabaseConnection:
    """
    Clase para manejar las conexiones a la base de datos PostgreSQL.
    """

    _instance = None

    def __new__(cls):
        """Implementa el patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._init_connection_params()
        return cls._instance

    def _init_connection_params(self):
        """Inicializa los parámetros de conexión desde la configuración"""
        db_config = project_settings.db
        self.connection_params = {
            "user": db_config.get("user", "postgres"),
            "password": db_config.get("password", "root"),
            "host": db_config.get("host", "localhost"),
            "port": db_config.get("port", "5432"),
            "database": db_config.get("database", "cvlac_db"),
        }

        # Para debug
        masked_params = self.connection_params.copy()
        if "password" in masked_params:
            masked_params["password"] = "***"
        module_logger.debug(f"Connection parameters initialized: {masked_params}")

    def test_connection(self):
        """
        Prueba la conexión a la base de datos.

        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    module_logger.info("Database connection test successful")
                    return True
        except Exception as e:
            module_logger.error(f"Database connection test failed: {str(e)}")
            return False

    def get_connection(self):
        """
        Obtiene una conexión a la base de datos.

        Returns:
            connection: Conexión a la base de datos.

        Raises:
            OperationalError: Si no se puede establecer la conexión.
        """
        try:
            connection = connect(**self.connection_params)
            return connection
        except OperationalError as e:
            module_logger.error(f"Error connecting to database: {str(e)}")
            # Reintento con sockets TCP explícitos si falló la conexión por socket
            if (
                "socket" in str(e).lower()
                and self.connection_params.get("host", "") == ""
            ):
                modified_params = self.connection_params.copy()
                modified_params["host"] = "localhost"
                module_logger.info(
                    "Retrying connection with explicit TCP socket (localhost)"
                )
                try:
                    connection = connect(**modified_params)
                    # Actualizar parámetros si tuvo éxito
                    self.connection_params = modified_params
                    return connection
                except Exception as e2:
                    module_logger.error(f"Retry connection failed: {str(e2)}")
            raise

    @contextmanager
    def get_connection_context(self):
        """
        Proporciona un contexto para usar una conexión a la base de datos,
        manejando automáticamente el cierre de la conexión.

        Yields:
            connection: Conexión a la base de datos.

        Example:
            with db.get_connection_context() as conn:
                # Usar conn aquí
        """
        connection = None
        try:
            connection = self.get_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            module_logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()

    def execute_query(self, query, params=None, commit=True):
        """
        Ejecuta una consulta en la base de datos.

        Args:
            query (str): Consulta SQL a ejecutar.
            params (tuple, dict, optional): Parámetros para la consulta.
            commit (bool, optional): Si se debe hacer commit de los cambios.

        Returns:
            list: Resultados de la consulta si es SELECT, None en caso contrario.
        """
        with self.get_connection_context() as connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query, params)

                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    return result

                if commit:
                    connection.commit()

                return None
            except Exception as e:
                connection.rollback()
                module_logger.error(f"Error executing query: {str(e)}")
                raise


# Exportar una instancia única para usar en todo el proyecto
db = DatabaseConnection()
