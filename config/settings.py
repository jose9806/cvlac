import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Configuración por defecto
DEFAULT_CONFIG = {
    "db": {
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "scrap"),
    },
    "logging": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "dir": os.getenv("LOG_DIR", "logs"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
    },
    "scraper": {
        "user_agent": os.getenv(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        ),
        "timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "retry_delay": int(os.getenv("RETRY_DELAY", "5")),
        "verify_ssl": os.getenv("VERIFY_SSL", "False").lower() in ("true", "1", "yes"),
        "remove_existing_data": os.getenv("REMOVE_EXISTING_DATA", "True").lower()
        in ("true", "1", "yes"),
        "update_if_exists": os.getenv("UPDATE_IF_EXISTS", "True").lower()
        in ("true", "1", "yes"),
    },
}


class Settings:
    """
    Clase para manejar la configuración del proyecto
    """

    _instance = None
    _config = {}

    def __new__(cls):
        """Implementa patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._config = DEFAULT_CONFIG.copy()
            cls._instance._load_config_file()
        return cls._instance

    def _load_config_file(self):
        """Carga configuración desde archivo config.json si existe"""
        config_file = BASE_DIR / "config.json"
        custom_config = None

        # Intentar cargar desde config.json
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    custom_config = json.load(f)
            except Exception as e:
                print(f"Error loading config.json: {e}")

        # Intentar cargar desde db_config.json (para mantener compatibilidad)
        if not custom_config:
            db_config_file = BASE_DIR / "db_config.json"
            if db_config_file.exists():
                try:
                    with open(db_config_file, "r") as f:
                        db_config = json.load(f)
                        # Integrar solo la configuración de DB desde el archivo
                        # de configuración anterior
                        custom_config = {"db": db_config}
                except Exception as e:
                    print(f"Error loading db_config.json: {e}")

        # Actualizar la configuración con valores personalizados
        if custom_config:
            self._update_config(self._config, custom_config)

    def _update_config(self, target, source):
        """Actualiza configuración de manera recursiva"""
        for key, value in source.items():
            if (
                isinstance(value, dict)
                and key in target
                and isinstance(target[key], dict)
            ):
                self._update_config(target[key], value)
            else:
                target[key] = value

    @property
    def db(self):
        """Obtiene configuración de base de datos"""
        return self._config.get("db", {})

    @property
    def logging(self):
        """Obtiene configuración de logging"""
        return self._config.get("logging", {})

    @property
    def scraper(self):
        """Obtiene configuración del scraper"""
        return self._config.get("scraper", {})

    def to_dict(self):
        """Retorna toda la configuración como diccionario"""
        return self._config.copy()

    def save_config(self):
        """Guarda la configuración actual en config.json"""
        config_file = BASE_DIR / "config.json"
        try:
            with open(config_file, "w") as f:
                json.dump(self._config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config.json: {e}")
            return False

    def __getattr__(self, name):
        """Manejo de acceso a atributos no definidos explícitamente"""
        if name in self._config:
            return self._config[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


# Exponer una instancia única para su uso en todo el proyecto
project_settings = Settings()
