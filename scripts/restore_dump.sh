#!/bin/sh

# Script to set up PostgreSQL in Docker and restore a dump file
# Usage: ./restore_dump.sh [dump_file] [database_name] [dev_user] [dev_password] [clean_volume]

set -e

# Default values
CONTAINER_NAME="postgres_db"
PG_USER="postgres"
PG_PASSWORD="postgres"
DB_NAME="scrap_db"
DEV_USER="dev_user"
DEV_PASSWORD="dev_password"
DUMP_DIR="./dump"
DUMP_FILE="$DUMP_DIR/Scrap_Gruplac_24-Feb-2025.dump"
CLEAN_VOLUME="no"
VOLUME_NAME="cvlac_postgres_data"
NETWORK_NAME="cvlac_postgres_network"

# Display help
show_help() {
  echo "Usage: $0 [dump_file] [database_name] [dev_user] [dev_password] [clean_volume]"
  echo ""
  echo "Arguments:"
  echo "  dump_file       (Optional) Path to the PostgreSQL dump file (.dump)"
  echo "                  Default: $DUMP_FILE"
  echo "  database_name   (Optional) Name of the database to restore to (default: $DB_NAME)"
  echo "  dev_user        (Optional) Development user to create (default: $DEV_USER)"
  echo "  dev_password    (Optional) Password for development user (default: $DEV_PASSWORD)"
  echo "  clean_volume    (Optional) Set to 'yes' to remove existing volume (default: $CLEAN_VOLUME)"
  echo ""
  echo "Example: $0 ./dump/Scrap_Gruplac_24-Feb-2025.dump scrap_db dev_admin secure_pass123 yes"
  exit 1
}

# Parse arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  show_help
fi

# If dump file is provided, use it
if [ $# -ge 1 ] && [ -n "$1" ]; then
  DUMP_FILE="$1"
fi

# Check if dump file exists
if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: Dump file '$DUMP_FILE' not found."
  exit 1
fi

# If database name is provided, use it
if [ $# -ge 2 ] && [ -n "$2" ]; then
  DB_NAME="$2"
fi

# If dev user is provided, use it
if [ $# -ge 3 ] && [ -n "$3" ]; then
  DEV_USER="$3"
fi

# If dev password is provided, use it
if [ $# -ge 4 ] && [ -n "$4" ]; then
  DEV_PASSWORD="$4"
fi

# If clean_volume is provided, use it
if [ $# -ge 5 ] && [ -n "$5" ]; then
  CLEAN_VOLUME="$5"
fi

# Check if PostgreSQL container is already running
if docker ps | grep -q $CONTAINER_NAME; then
  echo "Stopping existing PostgreSQL container..."
  docker-compose down
fi

# Clean existing volume if requested
if [ "$CLEAN_VOLUME" = "yes" ]; then
  echo "Removing existing PostgreSQL data volume..."
  
  # Remove container if it exists
  if docker ps -a | grep -q $CONTAINER_NAME; then
    docker rm -f $CONTAINER_NAME > /dev/null 2>&1
  fi
  
  # Remove volume if it exists
  if docker volume ls | grep -q $VOLUME_NAME; then
    docker volume rm $VOLUME_NAME > /dev/null 2>&1
  fi
  
  # Remove network if it exists
  if docker network ls | grep -q $NETWORK_NAME; then
    docker network rm $NETWORK_NAME > /dev/null 2>&1
  fi
fi

# Create docker-compose.yml if it doesn't exist or needs to be updated
echo "Setting up Docker Compose configuration..."
cat > docker-compose.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: $CONTAINER_NAME
    restart: always
    environment:
      POSTGRES_USER: $PG_USER
      POSTGRES_PASSWORD: $PG_PASSWORD
      POSTGRES_DB: $DB_NAME
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./dump:/dumps
    networks:
      - postgres_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $PG_USER"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  postgres_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
EOF

echo "Creating dump directory if it doesn't exist..."
mkdir -p ./dump

echo "Starting PostgreSQL container..."
docker-compose up -d

echo "Waiting for PostgreSQL to be ready..."
wait_count=0
max_wait=30
until docker exec $CONTAINER_NAME pg_isready -U $PG_USER > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL to start..."
  sleep 2
  wait_count=$((wait_count + 1))
  if [ $wait_count -ge $max_wait ]; then
    echo "PostgreSQL failed to start properly. Checking logs:"
    docker logs $CONTAINER_NAME
    
    echo ""
    echo "It appears there may be a compatibility issue with the database volume."
    echo "Would you like to remove the existing volume and try again? (y/n): "
    read should_clean
    
    if [ "$should_clean" = "y" ] || [ "$should_clean" = "Y" ]; then
      echo "Stopping container and removing volume..."
      docker-compose down
      docker volume rm $VOLUME_NAME
      echo "Please run the script again with clean_volume=yes:"
      echo "sh restore_dump.sh $DUMP_FILE $DB_NAME $DEV_USER $DEV_PASSWORD yes"
      exit 1
    else
      echo "Restoration aborted."
      exit 1
    fi
  fi
done

# Get the base filename for the dump
DUMP_FILENAME=$(basename "$DUMP_FILE")

# Ensure the dump directory is mounted in the container
echo "Verifying container setup..."
if ! docker exec $CONTAINER_NAME test -d /dumps; then
  echo "Error: /dumps directory is not mounted in the container."
  echo "Please check the volume mapping in docker-compose.yml."
  exit 1
fi

# Copy dump file to the container's mounted volume if needed
CONTAINER_DUMP_PATH="/dumps/$DUMP_FILENAME"
case "$DUMP_FILE" in
  ./dump/*)
    # File is already in the dump directory
    echo "Using dump file already in ./dump directory"
    ;;
  *)
    # File needs to be copied
    echo "Copying dump file to the container's mounted volume..."
    cp "$DUMP_FILE" "./dump/$DUMP_FILENAME"
    ;;
esac

echo "Checking if database '$DB_NAME' exists..."
if docker exec $CONTAINER_NAME psql -U $PG_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
  printf "Database '%s' already exists. Do you want to drop and recreate it? (y/n): " $DB_NAME
  read confirm
  if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ] || [ "$confirm" = "YES" ]; then
    echo "Dropping database '$DB_NAME'..."
    docker exec $CONTAINER_NAME psql -U $PG_USER -c "DROP DATABASE $DB_NAME;"
    echo "Creating database '$DB_NAME'..."
    docker exec $CONTAINER_NAME psql -U $PG_USER -c "CREATE DATABASE $DB_NAME;"
  else
    echo "Using existing database."
  fi
else
  echo "Creating database '$DB_NAME'..."
  docker exec $CONTAINER_NAME psql -U $PG_USER -c "CREATE DATABASE $DB_NAME;"
fi

# Determine dump file format - MODIFICACIÓN AQUÍ
echo "Determining dump file format..."
if file "./dump/$DUMP_FILENAME" | grep -q "PostgreSQL custom" || [[ "$DUMP_FILENAME" == *.dump ]]; then
  echo "Detected PostgreSQL custom format dump file."
  RESTORE_COMMAND="pg_restore -U $PG_USER -d $DB_NAME -v $CONTAINER_DUMP_PATH"
else
  echo "Assuming SQL format dump file."
  RESTORE_COMMAND="psql -U $PG_USER -d $DB_NAME -f $CONTAINER_DUMP_PATH"
fi

echo "Restoring dump file to database '$DB_NAME'..."
if ! docker exec $CONTAINER_NAME sh -c "$RESTORE_COMMAND"; then
  echo "Warning: Restore encountered errors."
  echo "Some errors are normal if the dump contains statements that depend on each other."
  
  # Ask if user wants to proceed despite restore errors
  printf "Do you want to continue with user creation anyway? (y/n): "
  read continue_anyway
  if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
    echo "Restoration aborted."
    exit 1
  fi
fi

echo "Creating development user '$DEV_USER'..."
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "DROP ROLE IF EXISTS $DEV_USER;" || true
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "CREATE USER $DEV_USER WITH PASSWORD '$DEV_PASSWORD';"
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DEV_USER;"
docker exec $CONTAINER_NAME psql -U $PG_USER -c "ALTER USER $DEV_USER WITH SUPERUSER;" || true

# Grant privileges on all existing objects
echo "Granting privileges on all database objects..."
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DEV_USER;" || true
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DEV_USER;" || true
docker exec $CONTAINER_NAME psql -U $PG_USER -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DEV_USER;" || true

echo "Restoration process completed successfully!"
echo ""
echo "PostgreSQL container is now running in the background."
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo ""
echo "Administrator credentials:"
echo "  Username: $PG_USER"
echo "  Password: $PG_PASSWORD"
echo ""
echo "Development credentials:"
echo "  Username: $DEV_USER"
echo "  Password: $DEV_PASSWORD"
echo ""
echo "To stop the container, use: docker-compose down"
echo "To restart the container later, use: docker-compose up -d"