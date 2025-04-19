import logging
import os
import sys
import json
import threading
from functools import wraps
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class ProjectLogger:
    """
    Una clase de logging escalable y reutilizable para todo el proyecto.
    Implementa un patrón singleton para asegurar la consistencia en todo el proyecto.
    """

    # Niveles de log estándar
    CRITICAL = logging.CRITICAL  # 50
    ERROR = logging.ERROR        # 40
    WARNING = logging.WARNING    # 30
    INFO = logging.INFO          # 20
    DEBUG = logging.DEBUG        # 10

    # Implementación del patrón singleton
    _instance = None
    _lock = threading.Lock()

    # Configuraciones por defecto
    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_LOG_DIR = "logs"

    def __new__(cls, *args, **kwargs):
        """Implementa el patrón singleton para asegurar una única instancia."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProjectLogger, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, log_level=None, log_format=None, date_format=None, log_dir=None):
        """
        Inicializa el logger con opciones de configuración.

        Args:
            log_level (int, optional): Nivel de log por defecto. Por defecto es INFO.
            log_format (str, optional): Formato para las entradas de log. 
            date_format (str, optional): Formato para las marcas de tiempo.
            log_dir (str, optional): Directorio para almacenar los archivos de log.
        """
        # Evita la reinicialización del singleton
        if self._initialized:
            return

        # Configuración por defecto
        self.log_level = log_level or self.DEFAULT_LOG_LEVEL
        self.log_format = log_format or self.DEFAULT_LOG_FORMAT
        self.date_format = date_format or self.DEFAULT_DATE_FORMAT
        self.log_dir = log_dir or self.DEFAULT_LOG_DIR

        # Almacena los loggers
        self._loggers = {}
        
        # Crea el directorio de logs si no existe
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Configura el logger raíz
        self._setup_root_logger()
        
        self._initialized = True
    
    def _setup_root_logger(self):
        """Configura el logger raíz con la configuración básica."""
        logging.basicConfig(
            level=self.log_level,
            format=self.log_format,
            datefmt=self.date_format,
            stream=sys.stdout
        )
        
        self._root_logger = logging.getLogger()
    
    def get_logger(self, name, log_to_file=True, log_to_console=True, log_level=None,
                  max_bytes=10485760, backup_count=5, file_log_level=None,
                  console_log_level=None, propagate=True):
        """
        Obtiene un logger para un módulo o componente específico.
        
        Args:
            name (str): Nombre del logger, típicamente __name__ del módulo llamante.
            log_to_file (bool, optional): Si se debe registrar en un archivo. Por defecto True.
            log_to_console (bool, optional): Si se debe registrar en consola. Por defecto True.
            log_level (int, optional): Nivel de log para este logger.
            max_bytes (int, optional): Tamaño máximo de archivo antes de rotación. Por defecto 10MB.
            backup_count (int, optional): Número de archivos de respaldo a mantener. Por defecto 5.
            file_log_level (int, optional): Nivel de log para el manejador de archivo.
            console_log_level (int, optional): Nivel de log para el manejador de consola.
            propagate (bool, optional): Si se propagan logs al padre. Por defecto True.
            
        Returns:
            logging.Logger: Objeto logger configurado.
        """
        # Verifica si ya creamos este logger
        if name in self._loggers:
            return self._loggers[name]
        
        # Crea un nuevo logger
        logger = logging.getLogger(name)
        
        # Establece el nivel del logger
        logger.setLevel(log_level or self.log_level)
        
        # Establece la propagación
        logger.propagate = propagate
        
        # Añade manejadores
        if log_to_file:
            file_handler = self._create_file_handler(
                name, 
                max_bytes=max_bytes, 
                backup_count=backup_count,
                log_level=file_log_level or log_level or self.log_level
            )
            logger.addHandler(file_handler)
            
        if log_to_console:
            console_handler = self._create_console_handler(
                log_level=console_log_level or log_level or self.log_level
            )
            logger.addHandler(console_handler)
        
        # Almacena el logger
        self._loggers[name] = logger
        
        return logger
    
    def _create_file_handler(self, name, max_bytes=10485760, backup_count=5, log_level=None):
        """
        Crea un manejador de archivo para registrar en archivos.
        
        Args:
            name (str): Nombre para el archivo de log.
            max_bytes (int, optional): Tamaño máximo de archivo antes de rotación. Por defecto 10MB.
            backup_count (int, optional): Número de archivos de respaldo. Por defecto 5.
            log_level (int, optional): Nivel de log para este manejador.
            
        Returns:
            logging.Handler: Manejador de archivo configurado.
        """
        log_file = os.path.join(self.log_dir, f"{name}.log")
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        handler.setLevel(log_level or self.log_level)
        
        formatter = logging.Formatter(self.log_format, self.date_format)
        handler.setFormatter(formatter)
        
        return handler
    
    def _create_console_handler(self, log_level=None):
        """
        Crea un manejador de consola para registrar en stdout.
        
        Args:
            log_level (int, optional): Nivel de log para este manejador.
            
        Returns:
            logging.Handler: Manejador de consola configurado.
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level or self.log_level)
        
        formatter = logging.Formatter(self.log_format, self.date_format)
        handler.setFormatter(formatter)
        
        return handler
    
    def create_timed_rotating_handler(self, name, when='midnight', interval=1, 
                                     backup_count=30, log_level=None):
        """
        Crea un manejador de archivo con rotación basada en tiempo.
        
        Args:
            name (str): Nombre para el archivo de log.
            when (str, optional): Cuándo rotar logs (S, M, H, D, midnight). Por defecto 'midnight'.
            interval (int, optional): Intervalo para rotación. Por defecto 1.
            backup_count (int, optional): Número de archivos de respaldo. Por defecto 30.
            log_level (int, optional): Nivel de log para este manejador.
            
        Returns:
            logging.Handler: Manejador de archivo con rotación por tiempo configurado.
        """
        log_file = os.path.join(self.log_dir, f"{name}.log")
        
        handler = TimedRotatingFileHandler(
            log_file,
            when=when,
            interval=interval,
            backupCount=backup_count
        )
        
        handler.setLevel(log_level or self.log_level)
        
        formatter = logging.Formatter(self.log_format, self.date_format)
        handler.setFormatter(formatter)
        
        return handler
    
    def create_json_handler(self, name, max_bytes=10485760, backup_count=5, log_level=None):
        """
        Crea un manejador que genera logs en formato JSON.
        
        Args:
            name (str): Nombre para el archivo de log.
            max_bytes (int, optional): Tamaño máximo de archivo antes de rotación. Por defecto 10MB.
            backup_count (int, optional): Número de archivos de respaldo. Por defecto 5.
            log_level (int, optional): Nivel de log para este manejador.
            
        Returns:
            logging.Handler: Manejador JSON configurado.
        """
        log_file = os.path.join(self.log_dir, f"{name}_json.log")
        
        handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        handler.setLevel(log_level or self.log_level)
        
        # Crear un formateador JSON
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': self.formatTime(record, self.datefmt),
                    'name': record.name,
                    'level': record.levelname,
                    'message': record.getMessage()
                }
                
                # Añadir información de excepción si está disponible
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)
                
                # Añadir atributos extra
                for attr, value in record.__dict__.items():
                    if attr not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 
                                   'filename', 'funcName', 'id', 'levelname', 'levelno',
                                   'lineno', 'module', 'msecs', 'message', 'msg', 'name',
                                   'pathname', 'process', 'processName', 'relativeCreated',
                                   'stack_info', 'thread', 'threadName']:
                        log_record[attr] = value
                
                return json.dumps(log_record)
        
        formatter = JsonFormatter(datefmt=self.date_format)
        handler.setFormatter(formatter)
        
        return handler
    
    def add_handler_to_logger(self, logger_name, handler):
        """
        Añade un manejador personalizado a un logger existente.
        
        Args:
            logger_name (str): Nombre del logger a modificar.
            handler (logging.Handler): Manejador a añadir.
            
        Returns:
            logging.Logger: Objeto logger modificado.
        """
        if logger_name in self._loggers:
            logger = self._loggers[logger_name]
            logger.addHandler(handler)
            return logger
        else:
            raise ValueError(f"Logger '{logger_name}' no encontrado.")
    
    def set_log_level(self, level, logger_name=None):
        """
        Establece el nivel de log para un logger específico o todos los loggers.
        
        Args:
            level (int): Nuevo nivel de log.
            logger_name (str, optional): Logger a modificar. Si es None, modifica todos.
        """
        if logger_name:
            if logger_name in self._loggers:
                self._loggers[logger_name].setLevel(level)
            else:
                raise ValueError(f"Logger '{logger_name}' no encontrado.")
        else:
            # Establece el nivel por defecto para futuros loggers
            self.log_level = level
            
            # Actualiza todos los loggers existentes
            for logger in self._loggers.values():
                logger.setLevel(level)
    
    def log_exception(self, logger_name=None, exc_info=None, level=None):
        """
        Registra una excepción con traza de pila.
        
        Args:
            logger_name (str, optional): Logger a usar. Por defecto usa el logger raíz.
            exc_info (tuple, optional): Información de excepción de sys.exc_info().
            level (int, optional): Nivel de log a usar. Por defecto ERROR.
        """
        logger = self._loggers.get(logger_name, self._root_logger)
        
        if exc_info is None:
            exc_info = sys.exc_info()
            
        level = level or logging.ERROR
        
        logger.log(level, "Se ha producido una excepción", exc_info=exc_info)
    
    def function_logger(self, logger_name=None, log_args=False, log_return=False):
        """
        Decorador para registrar entrada y salida de funciones.
        
        Args:
            logger_name (str, optional): Logger a usar. Si es None, usa el nombre del módulo.
            log_args (bool, optional): Si se registran los argumentos de la función. Por defecto False.
            log_return (bool, optional): Si se registran los valores de retorno. Por defecto False.
            
        Returns:
            callable: Función decoradora.
        """
        def decorator(func):
            # Usa el nombre del módulo si no se proporciona logger_name
            nonlocal logger_name
            if logger_name is None:
                logger_name = func.__module__
            
            # Obtiene o crea el logger
            if logger_name in self._loggers:
                logger = self._loggers[logger_name]
            else:
                logger = self.get_logger(logger_name)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Registra la entrada de la función
                if log_args:
                    logger.debug(f"Entrando a {func.__name__} con args: {args}, kwargs: {kwargs}")
                else:
                    logger.debug(f"Entrando a {func.__name__}")
                
                # Llama a la función
                try:
                    result = func(*args, **kwargs)
                    
                    # Registra la salida de la función
                    if log_return:
                        logger.debug(f"Saliendo de {func.__name__} con resultado: {result}")
                    else:
                        logger.debug(f"Saliendo de {func.__name__}")
                    
                    return result
                except Exception as e:
                    # Registra la excepción
                    logger.error(f"Excepción en {func.__name__}: {str(e)}", exc_info=True)
                    raise
            
            return wrapper
        
        return decorator
    
    def create_context_logger(self, name, **context):
        """
        Crea un logger que añade contexto a todos los mensajes de log.
        
        Args:
            name (str): Nombre del logger.
            **context: Contexto adicional para añadir a todos los mensajes.
            
        Returns:
            logging.LoggerAdapter: Adaptador de logger con contexto.
        """
        logger = self.get_logger(name)
        return logging.LoggerAdapter(logger, context)
    
    def configure_from_dict(self, config):
        """
        Configura el logging desde un diccionario.
        
        Args:
            config (dict): Diccionario con opciones de configuración.
        """
        # Actualiza los valores por defecto a nivel de clase
        if 'log_level' in config:
            self.log_level = config['log_level']
        if 'log_format' in config:
            self.log_format = config['log_format']
        if 'date_format' in config:
            self.date_format = config['date_format']
        if 'log_dir' in config:
            self.log_dir = config['log_dir']
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
        
        # Configura loggers individuales
        if 'loggers' in config:
            for logger_name, logger_config in config['loggers'].items():
                self.get_logger(logger_name, **logger_config)
    
    def configure_from_file(self, file_path):
        """
        Configura el logging desde un archivo de configuración JSON.
        
        Args:
            file_path (str): Ruta al archivo de configuración.
        """
        with open(file_path, 'r') as f:
            config = json.load(f)
        
        self.configure_from_dict(config)


# Ejemplo de configuración JSON para usar con configure_from_file
"""
{
    "log_level": 20,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "log_dir": "logs",
    "loggers": {
        "app": {
            "log_to_file": true,
            "log_to_console": true,
            "log_level": 10,
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "database": {
            "log_to_file": true,
            "log_level": 20
        }
    }
}
"""