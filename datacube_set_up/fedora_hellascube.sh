#!/usr/bin/env bash
#
# setup_odc_fedora.sh
# Draft provisioning script for the HellasCube Open Data Cube (ODC) environment on Fedora.
#
# What it does:
#   1. Installs system deps (PostgreSQL, PostGIS, GDAL build deps, conda if missing)
#   2. Creates/initializes the PostgreSQL role + opendatacube database
#   3. Creates a conda env (odc_env, Python 3.10) and installs datacube + friends
#   4. Writes ~/.datacube.conf
#   5. Runs `datacube system init`
#
# Usage:
#   chmod +x setup_odc_fedora.sh
#   ./setup_odc_fedora.sh
#
# Review every variable in the CONFIG section before running — this is a draft,
# not a finished, idempotent installer. Run sections manually if you'd rather
# not execute the whole thing blind.

set -euo pipefail

# ---------- CONFIG (edit these) ----------
DB_NAME="opendatacube"
DB_USER="chsap"
DB_PASSWORD="changeme"          # CHANGE THIS before running
DB_HOST="localhost"
DB_PORT="5432"
CONDA_ENV_NAME="odc_env"
PYTHON_VERSION="3.10"
PG_MAJOR_VERSION="18"           # matches your existing PG18 + PostGIS setup
# ------------------------------------------

log() { echo -e "\n\033[1;34m==>\033[0m $1"; }

log "Checking for sudo privileges..."
if ! sudo -v; then
    echo "This script needs sudo access. Exiting."
    exit 1
fi

# ---------- 1. System packages ----------
log "Installing PostgreSQL ${PG_MAJOR_VERSION}, PostGIS, and build deps via dnf..."
sudo dnf install -y \
    postgresql-server postgresql-contrib \
    postgis \
    gdal gdal-devel \
    proj proj-devel \
    geos geos-devel \
    gcc gcc-c++ make \
    git wget curl

# ---------- 2. Initialize PostgreSQL (skip if already initialized) ----------
if [ ! -d "/var/lib/pgsql/data" ]; then
    log "Initializing PostgreSQL database cluster..."
    sudo postgresql-setup --initdb
else
    log "PostgreSQL data directory already exists, skipping initdb."
fi

log "Enabling and starting postgresql.service..."
sudo systemctl enable --now postgresql

# ---------- 3. pg_hba.conf: scram-sha-256 auth ----------
PG_HBA="/var/lib/pgsql/data/pg_hba.conf"
log "Checking pg_hba.conf auth method (expects scram-sha-256)..."
if [ -f "$PG_HBA" ]; then
    sudo sed -i "s/ident$/scram-sha-256/g; s/peer$/scram-sha-256/g" "$PG_HBA"
    sudo systemctl restart postgresql
else
    echo "WARNING: $PG_HBA not found — check your PostgreSQL install path manually."
fi

# ---------- 4. Create role + database ----------
log "Creating role '${DB_USER}' and database '${DB_NAME}' (if they don't exist)..."
sudo -u postgres psql -v ON_ERROR_STOP=1 <<EOF
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}' SUPERUSER;
   END IF;
END
\$\$;

SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec

\c ${DB_NAME}
CREATE EXTENSION IF NOT EXISTS postgis;
EOF

# ---------- 5. Conda environment ----------
if ! command -v conda &> /dev/null; then
    log "conda not found — installing Miniforge..."
    wget -q "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh" -O /tmp/miniforge.sh
    bash /tmp/miniforge.sh -b -p "$HOME/miniforge3"
    source "$HOME/miniforge3/etc/profile.d/conda.sh"
    conda init bash
else
    log "conda already installed, sourcing it..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
fi

log "Creating conda env '${CONDA_ENV_NAME}' (Python ${PYTHON_VERSION})..."
conda create -y -n "$CONDA_ENV_NAME" python="$PYTHON_VERSION"
conda activate "$CONDA_ENV_NAME"

log "Installing datacube and geospatial stack via conda-forge..."
conda install -y -c conda-forge \
    datacube \
    gdal \
    rasterio \
    xarray \
    dask \
    distributed \
    boto3 \
    psycopg2 \
    stac-to-dc

# ---------- 6. GDAL env vars for S3 / COG performance ----------
log "Writing GDAL S3 performance env vars to conda activation hook..."
ACTIVATE_DIR="$HOME/miniforge3/envs/${CONDA_ENV_NAME}/etc/conda/activate.d"
mkdir -p "$ACTIVATE_DIR"
cat > "${ACTIVATE_DIR}/gdal_s3_env.sh" <<'EOG'
export GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR
export CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF,.tiff"
export GDAL_HTTP_MULTIRANGE=YES
export GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES
export VSI_CACHE=TRUE
export VSI_CACHE_SIZE=536870912
EOG

# ---------- 7. ~/.datacube.conf ----------
log "Writing ~/.datacube.conf..."
cat > "$HOME/.datacube.conf" <<EOC
[default]
db_hostname: ${DB_HOST}
db_port: ${DB_PORT}
db_database: ${DB_NAME}
db_username: ${DB_USER}
db_password: ${DB_PASSWORD}
EOC

# ---------- 8. datacube system init ----------
log "Running 'datacube system init'..."
datacube system init

log "Running 'datacube system check'..."
datacube system check

log "Done. Activate the environment with: conda activate ${CONDA_ENV_NAME}"
echo "Next steps: configure product YAML definitions and run stac-to-dc to index Sentinel-2 / Landsat / HLS data."