#!/bin/sh

# Script para diagnosticar problemas en la base de datos CvLAC
# Usage: ./diagnostic_cvlac_db.sh [database_name] [user] [password] [container_name]

set -e

# Default values
CONTAINER_NAME=${4:-"postgres_db"}
PG_USER=${2:-"postgres"}
PG_PASSWORD=${3:-"postgres"}
DB_NAME=${1:-"cvlac_db"}
SCRIPT_DIR=$(dirname "$0")
OUTPUT_FILE="${SCRIPT_DIR}/cvlac_db_diagnostic_$(date +%Y%m%d_%H%M%S).log"

# Display help
show_help() {
  echo "Usage: $0 [database_name] [user] [password] [container_name]"
  echo ""
  echo "Arguments:"
  echo "  database_name   (Optional) Name of the CvLAC database to diagnose (default: cvlac_db)"
  echo "  user            (Optional) PostgreSQL user (default: postgres)"
  echo "  password        (Optional) PostgreSQL password (default: postgres)"
  echo "  container_name  (Optional) Docker container name (default: postgres_db)"
  echo ""
  echo "Example: $0 cvlac_db postgres postgres postgres_db"
  exit 1
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  show_help
fi

echo "Diagnostic for CvLAC database: $DB_NAME"
echo "Using container: $CONTAINER_NAME"
echo "Diagnostic log will be saved to: $OUTPUT_FILE"

# Check if PostgreSQL container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
  echo "Error: PostgreSQL container '$CONTAINER_NAME' is not running."
  echo "Start the container with: docker-compose up -d"
  exit 1
fi

# Check if database exists
echo "Checking if database '$DB_NAME' exists..."
if ! docker exec $CONTAINER_NAME psql -U $PG_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
  echo "Error: Database '$DB_NAME' does not exist."
  exit 1
fi

# Create output file
touch "$OUTPUT_FILE"
echo "# Diagnóstico de la base de datos CvLAC - $(date)" >> "$OUTPUT_FILE"
echo "## Información básica" >> "$OUTPUT_FILE"
echo "- Base de datos: $DB_NAME" >> "$OUTPUT_FILE"
echo "- Usuario: $PG_USER" >> "$OUTPUT_FILE"
echo "- Contenedor: $CONTAINER_NAME" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Run diagnostic queries
echo "Running diagnostics..."

echo "## Listado de tablas" >> "$OUTPUT_FILE"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "\dt" >> "$OUTPUT_FILE" 2>&1
echo "" >> "$OUTPUT_FILE"

echo "## Propietarios de tablas" >> "$OUTPUT_FILE"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" >> "$OUTPUT_FILE" 2>&1
echo "" >> "$OUTPUT_FILE"

echo "## Schemas disponibles" >> "$OUTPUT_FILE"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SELECT nspname FROM pg_catalog.pg_namespace;" >> "$OUTPUT_FILE" 2>&1
echo "" >> "$OUTPUT_FILE"

echo "## Search path actual" >> "$OUTPUT_FILE"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SHOW search_path;" >> "$OUTPUT_FILE" 2>&1
echo "" >> "$OUTPUT_FILE"

# Check specific tables that have issues - compatible with sh
problem_tables="identificacion formacion_academica experiencia areas_actuacion idioma lineas_investigacion reconocimientos trabajos_dirigidos jurados"

echo "## Información detallada de tablas con problemas reportados" >> "$OUTPUT_FILE"
for table in $problem_tables; do
    echo "### Tabla: $table" >> "$OUTPUT_FILE"
    
    # Check if table exists
    exists=$(docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -t -c "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table');")
    
    if echo "$exists" | grep -q "t"; then
        echo "- Estado: Tabla existe" >> "$OUTPUT_FILE"
        
        # Get table definition
        echo "- Definición:" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "\d $table" >> "$OUTPUT_FILE" 2>&1
        echo '```' >> "$OUTPUT_FILE"
        
        # Get column info
        echo "- Columnas:" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'public' AND table_name = '$table' ORDER BY ordinal_position;" >> "$OUTPUT_FILE" 2>&1
        echo '```' >> "$OUTPUT_FILE"
        
        # Check permissions
        echo "- Permisos:" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SELECT grantee, privilege_type FROM information_schema.table_privileges WHERE table_schema = 'public' AND table_name = '$table';" >> "$OUTPUT_FILE" 2>&1
        echo '```' >> "$OUTPUT_FILE"
        
        # Try select statement
        echo "- Prueba de SELECT:" >> "$OUTPUT_FILE"
        echo '```' >> "$OUTPUT_FILE"
        docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SELECT COUNT(*) FROM $table;" >> "$OUTPUT_FILE" 2>&1
        echo '```' >> "$OUTPUT_FILE"
    else
        echo "- Estado: Tabla no existe" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
done

echo "## Tests de Transacciones" >> "$OUTPUT_FILE"
echo "### Test de inserción con ROLLBACK (para no afectar datos reales)" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "
BEGIN;
DO \$\$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'identificacion') THEN
        INSERT INTO identificacion (cvlac_id, nombre_completo, nombre_citaciones) 
        VALUES ('TEST_DIAG', 'USUARIO DIAGNÓSTICO', 'DIAGNOSTICO, USUARIO')
        ON CONFLICT (cvlac_id) DO NOTHING;
        RAISE NOTICE 'Inserción de prueba realizada';
    ELSE
        RAISE NOTICE 'La tabla identificacion no existe';
    END IF;
END;
\$\$;
ROLLBACK;
" >> "$OUTPUT_FILE" 2>&1
echo '```' >> "$OUTPUT_FILE"

echo "## Diagnóstico de configuración PostgreSQL" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "SHOW ALL;" >> "$OUTPUT_FILE" 2>&1
echo '```' >> "$OUTPUT_FILE"

echo "Diagnostics completed. Results saved to $OUTPUT_FILE"
echo ""
echo "Posibles soluciones basadas en problemas comunes:"
echo "1. Si las tablas existen pero no son accesibles: ejecute fix_cvlac_db.sh"
echo "2. Si las tablas no existen: ejecute setup_cvlac_db.sh"
echo "3. Si hay problemas de permisos: verifique el usuario de conexión"
echo "4. Si hay inconsistencias entre schemas: asegúrese de que search_path incluya 'public'"
echo ""
echo "Revise el archivo de diagnóstico para más detalles: $OUTPUT_FILE"

exit 0