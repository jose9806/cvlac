# cvlac
# CvLAC Scraper

Un scraper robusto para extraer y gestionar información de perfiles CvLAC (Currículum Vitae Latinoamericano y del Caribe) de investigadores registrados en Scienti Minciencias.

## Características

- **Extracción completa**: Captura todos los datos relevantes de los perfiles CvLAC
- **Procesamiento paralelo**: Capacidad para ejecutarse en múltiples procesos
- **Verificación de duplicados**: Sistema para evitar duplicados en la base de datos
- **Generación de reportes**: Reportes detallados de cada extracción
- **Configuración flexible**: Mediante archivos JSON y variables de entorno
- **Manejo de errores robusto**: Registro detallado y manejo de errores

## Requisitos

- Python 3.8 o superior
- PostgreSQL
- Dependencias de Python (ver `requirements.txt`)

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/cvlac-scraper.git
   cd cvlac-scraper
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**:
   - Crear un archivo `config.json` (puedes copiar desde `config.json.example`)
   - O crear archivo `.env` (puedes copiar desde `.env.example`)

5. **Probar la conexión a la base de datos**:
   ```bash
   python main.py --test_db
   ```

## Configuración

### Archivo config.json

```json
{
  "db": {
    "user": "postgres",
    "password": "tu_contraseña",
    "host": "localhost",
    "port": "5432",
    "database": "scrap"
  },
  "scraper": {
    "remove_existing_data": false,
    "update_if_exists": true,
    "timeout": 30,
    "max_retries": 3
  }
}
```

### Variables de entorno (.env)

```
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=scrap
REMOVE_EXISTING_DATA=false
UPDATE_IF_EXISTS=true
```

## Uso

### Modos de ejecución

1. **Extraer un CvLAC específico**:
   ```bash
   python main.py --cod_rh 0000123456
   ```

2. **Procesar un rango de IDs**:
   ```bash
   python main.py --range_start 1000000 --range_end 1100000 --step 1000
   ```

3. **Procesamiento en paralelo**:
   ```bash
   python main.py --multiprocess --workers 8
   ```

### Opciones importantes

- `--update_only`: No elimina datos existentes, solo actualiza o añade nuevos
- `--validate_only`: Solo verifica duplicados, sin insertar ni actualizar
- `--test_db`: Prueba la conexión a la base de datos y sale
- `--report_dir RUTA`: Especifica directorio personalizado para reportes

### Ejemplo de uso completo

```bash
python main.py --update_only --multiprocess --workers 4 --range_start 1000000 --range_end 2000000 --step 10000
```

## Estructura del Proyecto

```
cvlac-scraper/
├── config/               # Configuración del proyecto
│   ├── __init__.py
│   └── logger.py         # Configuración de logging
├── db/                   # Módulo de conexión a base de datos
│   ├── __init__.py
│   └── connection.py     # Clase de conexión a PostgreSQL
├── extractors/           # Módulos de extracción por sección
│   ├── __init__.py
│   ├── utils.py          # Utilidades comunes de extracción
│   ├── identificacion.py # Extractor de datos de identificación
│   ├── formacion.py      # Extractor de datos de formación
│   └── ...               # Otros extractores específicos
├── validators/           # Validación de datos
│   ├── __init__.py
│   └── data_validator.py # Validador de datos y generador de reportes
├── temp/                 # Directorio para archivos temporales
│   └── reports/          # Reportes de extracción generados
├── logs/                 # Logs del sistema
├── .env.example          # Plantilla para variables de entorno
├── config.json.example   # Plantilla de configuración
├── main.py               # Punto de entrada principal
├── settings.py           # Gestión de configuración
└── requirements.txt      # Dependencias del proyecto
```

## Descripción de Componentes

### Módulos Principales

- **`main.py`**: Punto de entrada que coordina todas las operaciones. Implementa el procesamiento paralelo y maneja los argumentos de línea de comandos.

- **`settings.py`**: Gestiona la configuración del proyecto desde archivos JSON y variables de entorno. Implementa un patrón Singleton para mantener configuración coherente.

- **`db/connection.py`**: Maneja conexiones a la base de datos PostgreSQL, implementando reconexión automática y manejo de errores.

- **`validators/data_validator.py`**: Sistema para validación de datos, prevención de duplicados y generación de reportes detallados.

### Extractores

Cada extractor se especializa en una sección específica del perfil CvLAC:

- **`identificacion.py`**: Datos personales del investigador
- **`formacion.py`**: Formación académica y complementaria
- **`experiencia.py`**: Experiencia profesional
- **`proyectos.py`**: Proyectos de investigación
- **`produccion_bibliografica.py`**: Artículos, libros y otras publicaciones
- **`produccion_tec.py`**: Productos tecnológicos e innovaciones
- Y muchos otros para categorías específicas

### Utilidades y Soporte

- **`config/logger.py`**: Sistema de logging configurable
- **`extractors/utils.py`**: Funciones comunes utilizadas por todos los extractores

## Sistema de Reportes

Los reportes se generan en la carpeta `temp/reports` y vienen en varios formatos:

1. **Reportes JSON** con estadísticas detalladas
2. **Reportes CSV** con resumen de operaciones por tabla
3. **Reportes de errores** cuando ocurren problemas

Ejemplo de reporte generado:
```
REPORTE FINAL DE EXTRACCIÓN
=========================

Fecha de finalización: 2025-04-19T15:30:45.123456
Total de reportes generados: 143

Reportes individuales:
- temp/reports/extraction_report_0000123456_20250419_153024.json
- temp/reports/extraction_report_0000123457_20250419_153032.json
...
```

## Prevención de Borrado de Datos

Para garantizar que nunca se borren datos existentes:

1. **Usar siempre `--update_only`**
2. **Configurar `remove_existing_data: false` en config.json**
3. **Establecer `REMOVE_EXISTING_DATA=false` en .env**

## Mantenimiento y Desarrollo

### Añadir un nuevo extractor

1. Crear un nuevo archivo en `extractors/` con clase y funciones necesarias
2. Registrar la función de extracción en el diccionario `EXTRACTORS` en `main.py`
3. Añadir la importación correspondiente

### Depuración

El sistema mantiene logs detallados en la carpeta `logs/`. Para aumentar el nivel de detalle:

```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## restauración de la base de datos a partir de un dump usando el script de bash
comando para restaurar el dump de la base de datos desde su versión inicialrestore_dump.sh:
```bash
sh restore_dump.sh ./dump/Scrap_Gruplac_24-Feb-2025.dump scrap_db dev_user dev_password yes
```