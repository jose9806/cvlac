# CvLAC Scraper

Este proyecto es un sistema de extracción de datos (scraper) para perfiles de investigadores en la plataforma CvLAC (Currículum Vitae Latinoamericano y del Caribe). Permite recopilar información detallada sobre investigadores, incluyendo sus datos personales, formación académica, experiencia profesional, producción bibliográfica, proyectos de investigación, y más, almacenándola en una base de datos PostgreSQL para su posterior análisis.

## Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
- [Uso del Scraper](#uso-del-scraper)
- [Argumentos de main.py](#argumentos-de-mainpy)
- [Scripts Auxiliares](#scripts-auxiliares)
- [Integración con GrupLAC](#integración-con-gruplac)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Solución de Problemas](#solución-de-problemas)
- [Contribución](#contribución)

## Requisitos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Docker y Docker Compose (recomendado para configuración de BD)
- Librerías Python (ver `requirements.txt`)

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/cvlac-scraper.git
cd cvlac-scraper
```

2. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar la base de datos (ver siguiente sección).

## Configuración de la Base de Datos

### Utilizando Docker (recomendado)

El proyecto incluye una configuración de Docker Compose para levantar fácilmente una instancia de PostgreSQL:

```bash
docker-compose up -d postgres
```

### Configuración del esquema de base de datos

Existen dos formas de configurar el esquema de la base de datos:

#### 1. Script automático para crear el esquema

```bash
./scripts/setup_cvlac_db.sh [database_name] [user] [password] [container_name]
```

Ejemplo:
```bash
./scripts/setup_cvlac_db.sh cvlac_db postgres postgres postgres_db
```

#### 2. Restaurar desde un dump existente

```bash
./scripts/restore_dump.sh [dump_file] [database_name] [dev_user] [dev_password] [clean_volume]
```

Ejemplo:
```bash
./scripts/restore_dump.sh ./dump/Scrap_CvLAC_20240420.dump cvlac_db dev_user dev_password yes
```

### Configuración de la conexión a la base de datos

Edita el archivo `config/config.json` o crea un archivo de entorno `.env` en la raíz del proyecto con las credenciales de la base de datos:

```json
{
  "db": {
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432",
    "database": "cvlac_db"
  }
}
```

## Uso del Scraper

El script principal `main.py` permite extraer información de CvLAC de varias formas:

### Extraer un perfil específico

```bash
python main.py --cod_rh 0000123456
```

### Extraer un rango de perfiles

```bash
python main.py --range_start 1000000 --range_end 1010000 --step 1000
```

### Extraer con multiprocesamiento (más rápido)

```bash
python main.py --multiprocess --workers 8 --range_start 1000000 --range_end 1010000
```

## Argumentos de main.py

El script principal admite los siguientes argumentos:

| Argumento | Tipo | Valor predeterminado | Descripción |
|-----------|------|----------------------|-------------|
| `--cod_rh` | string | - | Código CvLAC específico del investigador a extraer |
| `--multiprocess` | bandera | false | Activar el modo de multiprocesamiento |
| `--workers` | int | 64 | Número de procesos paralelos a utilizar (con --multiprocess) |
| `--range_start` | int | 0 | ID inicial para el procesamiento en rango |
| `--range_end` | int | 2000000 | ID final para el procesamiento en rango |
| `--step` | int | 31250 | Tamaño del paso para el procesamiento en rango |
| `--test_db` | bandera | false | Probar la conexión a la base de datos y salir |
| `--update_only` | bandera | false | Solo actualizar registros sin eliminar datos existentes |
| `--validate_only` | bandera | false | Solo validar sin actualizar ni insertar nuevos registros |
| `--report_dir` | string | - | Directorio para almacenar los reportes de extracción |
| `--session-id` | string | - | ID de sesión para agrupar reportes (opcional) |

### Modos de ejecución

El script tiene tres modos de ejecución principales:

1. **Modo Individual**: Extrae datos de un solo investigador
   ```bash
   python main.py --cod_rh 0000123456
   ```

2. **Modo Rango**: Extrae datos de un rango de códigos CvLAC
   ```bash
   python main.py --range_start 1000000 --range_end 1100000 --step 1000
   ```

3. **Modo Multiproceso**: Utiliza múltiples procesos para extraer datos más rápidamente
   ```bash
   python main.py --multiprocess --workers 8 --range_start 1000000 --range_end 1100000
   ```

## Scripts Auxiliares

### setup_cvlac_db.sh

Este script configura la estructura de la base de datos CvLAC.

```bash
./scripts/setup_cvlac_db.sh [database_name] [user] [password] [container_name]
```

**Argumentos**:
- `database_name`: Nombre de la base de datos a crear (default: cvlac_db)
- `user`: Usuario de PostgreSQL (default: postgres)
- `password`: Contraseña de PostgreSQL (default: postgres)
- `container_name`: Nombre del contenedor Docker (default: postgres_db)

### restore_dump.sh

Este script restaura un dump en la base de datos PostgreSQL dentro de Docker.

```bash
./scripts/restore_dump.sh [dump_file] [database_name] [dev_user] [dev_password] [clean_volume]
```

**Argumentos**:
- `dump_file`: Ruta al archivo de dump (.dump)
- `database_name`: Nombre de la base de datos a restaurar (default: scrap_db)
- `dev_user`: Usuario de desarrollo a crear (default: dev_user)
- `dev_password`: Contraseña para el usuario de desarrollo (default: dev_password)
- `clean_volume`: "yes" para eliminar el volumen existente antes de restaurar (default: no)

### diagnostic_cvlac.sh

Este script diagnostica problemas en la base de datos CvLAC.

```bash
./scripts/diagnostic_cvlac_db.sh [database_name] [user] [password] [container_name]
```

**Argumentos**:
- `database_name`: Nombre de la base de datos a diagnosticar (default: cvlac_db)
- `user`: Usuario de PostgreSQL (default: postgres)
- `password`: Contraseña de PostgreSQL (default: postgres)
- `container_name`: Nombre del contenedor Docker (default: postgres_db)

## Integración con GrupLAC

El proyecto incluye un script para integrar datos de CvLAC con datos de GrupLAC:

```bash
python scripts/integrate_cvlac_gruplac.py --config config/integration.json
```

### Argumentos de integrate_cvlac_gruplac.py

| Argumento | Descripción |
|-----------|-------------|
| `--config` | Ruta al archivo de configuración (default: config/integration.json) |
| `--backup-only` | Solo realizar respaldo sin integración |
| `--tables` | Lista de tablas específicas a procesar, separadas por comas |

## Estructura del Proyecto

```
cvlac-scraper/
├── config/                 # Configuración del proyecto
│   ├── __init__.py
│   ├── connection.py       # Conexión a la base de datos
│   ├── integration.json    # Configuración para integración GrupLAC
│   ├── logger.py           # Configuración de logging
│   └── settings.py         # Configuración general
├── extractors/             # Módulos de extracción para diferentes secciones de CvLAC
│   ├── __init__.py
│   ├── actividades_evaluador.py
│   ├── actividades_formacion.py
│   ├── apropiacion_social.py
│   ├── ...
│   └── utils.py            # Utilidades para extractores
├── scripts/                # Scripts auxiliares
│   ├── diagnostic_cvlac.sh
│   ├── integrate_cvlac_gruplac.py
│   ├── restore_dump.sh
│   └── setup_cvlac_db.sh
├── sql/                    # Definiciones SQL
│   └── cvlac_db.sql        # Esquema de la base de datos
├── validators/             # Validadores de datos
│   ├── __init__.py
│   └── data_validator.py   # Validación y limpieza de datos
├── docker-compose.yml      # Configuración Docker Compose
├── main.py                 # Script principal
└── requirements.txt        # Dependencias del proyecto
```

## Solución de Problemas

Si encuentras problemas con la base de datos, puedes ejecutar el script de diagnóstico:

```bash
./scripts/diagnostic_cvlac.sh
```

Los errores comunes incluyen:
- Problemas de conexión a la base de datos: Verifica que PostgreSQL esté en ejecución
- Errores de permisos: Verifica las credenciales en la configuración
- Esquema incompleto: Ejecuta el script setup_cvlac_db.sh para asegurar que todas las tablas existan

