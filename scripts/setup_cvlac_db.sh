#!/bin/sh

# Script to set up the CvLAC database structure
# Usage: ./setup_cvlac_db.sh [database_name] [user] [password] [container_name]

set -e

# Default values
CONTAINER_NAME=${4:-"postgres_db"}
PG_USER=${2:-"postgres"}
PG_PASSWORD=${3:-"postgres"}
DB_NAME=${1:-"cvlac_db"}
SCRIPT_DIR=$(dirname "$0")
ROOT_DIR=$(dirname "$SCRIPT_DIR")
SQL_FILE="$ROOT_DIR/sql/cvlac_db.sql"

# Display help
show_help() {
  echo "Usage: $0 [database_name] [user] [password] [container_name]"
  echo ""
  echo "Arguments:"
  echo "  database_name   (Optional) Name of the CvLAC database to create (default: cvlac_db)"
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

echo "Setting up CvLAC database: $DB_NAME"
echo "Using container: $CONTAINER_NAME"
echo "Using schema file: $SQL_FILE"

# Check if PostgreSQL container is running
if ! docker ps | grep -q $CONTAINER_NAME; then
  echo "Error: PostgreSQL container '$CONTAINER_NAME' is not running."
  echo "Start the container with: docker-compose up -d"
  exit 1
fi

# Check if SQL schema file exists
if [ ! -f "$SQL_FILE" ]; then
  echo "Error: SQL schema file '$SQL_FILE' not found."
  echo "Make sure cvlac_db.sql exists in the root directory of the project."
  exit 1
fi

# Check if database exists, if not create it
echo "Checking if database '$DB_NAME' exists..."
if ! docker exec $CONTAINER_NAME psql -U $PG_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
  echo "Creating database '$DB_NAME'..."
  docker exec $CONTAINER_NAME psql -U $PG_USER -c "CREATE DATABASE $DB_NAME;"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to create database '$DB_NAME'."
    exit 1
  fi
else
  echo "Database '$DB_NAME' already exists."
  
  # Ask if user wants to drop and recreate the database
  printf "Do you want to drop and recreate the database? This will delete all existing data. (y/n): "
  read confirm
  if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ] || [ "$confirm" = "YES" ]; then
    echo "Dropping database '$DB_NAME'..."
    docker exec $CONTAINER_NAME psql -U $PG_USER -c "DROP DATABASE $DB_NAME;"
    echo "Creating database '$DB_NAME'..."
    docker exec $CONTAINER_NAME psql -U $PG_USER -c "CREATE DATABASE $DB_NAME;"
    if [ $? -ne 0 ]; then
      echo "Error: Failed to recreate database '$DB_NAME'."
      exit 1
    fi
  else
    echo "Using existing database. Schema will be applied on top of existing data."
    echo "Note: This may cause conflicts if tables already exist."
  fi
fi

# Copy SQL file to the container
echo "Copying SQL schema file to container..."
docker cp "$SQL_FILE" $CONTAINER_NAME:/tmp/cvlac_db.sql

# Apply the schema to the database
echo "Applying CvLAC schema to database '$DB_NAME'..."
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -f /tmp/cvlac_db.sql
SCHEMA_RESULT=$?

if [ $SCHEMA_RESULT -ne 0 ]; then
  echo "Warning: Schema application encountered some issues."
  echo "Some warnings may be normal. Verifying table creation..."
fi

# Verify if tables were created successfully
echo "Checking key tables in the database..."
TABLE_COUNT=$(docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "Found $TABLE_COUNT tables in the database."

# Check a few critical tables
for table in identificacion formacion_academica experiencia lineas_investigacion areas_actuacion idioma articulos_publicados eventos_cientificos reconocimientos; do
  if docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "\d $table" > /dev/null 2>&1; then
    echo "Table '$table' created successfully."
  else
    echo "Warning: Table '$table' may not have been created properly."
  fi
done

echo "CvLAC database setup completed."
echo ""
echo "Database details:"
echo "  Name: $DB_NAME"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  User: $PG_USER"
echo ""
echo "To use the CvLAC database with your scraper, update your configuration:"
echo "1. Edit config/db_config.json or config/config.json to point to this database"
echo "2. Set the 'database' field to '$DB_NAME'"
echo ""
echo "To integrate CvLAC with GrupLAC data:"
echo "  python scripts/integrate_cvlac_gruplac.py --config config/integration.json"
echo ""

exit 0