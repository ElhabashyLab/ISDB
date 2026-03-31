#!/usr/bin/env bash
# ======================================================================
# ISDB Resource Downloader
# Description: Automated retrieval of all interspecies interaction datasets
# Author: Hadeer Elhabashy
# Version: 2.2
# ======================================================================

set -uo pipefail

# ===============================
# CONFIGURATION
# ===============================
MAX_RETRIES=3
TIMEOUT=60
# Load environment variables
set -a
source config.env
set +a


# Ensure OUT_DIRECTORY exists
mkdir -p "$OUT_DIRECTORY"

# use a subfolder for downloads (inputs)
DOWNLOAD_DIR="${OUT_DIRECTORY%/}/inputs"
mkdir -p "$DOWNLOAD_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging
LOG_FILE="${OUT_DIRECTORY%/}/download_log_$(date +%Y_%m_%d__%H).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=================================================================="
echo "### ISDB Downloader started at $(date)"
echo "### Working directory: $DOWNLOAD_DIR"
echo "=================================================================="

# ===============================
# HELPER FUNCTIONS
# ===============================

download_file() {
    local url="$1"
    local output="$2"
    local desc="${3:-$output}"

    echo "→ Downloading $desc ..."
    if wget --progress=bar:force:noscroll --tries="$MAX_RETRIES" --timeout="$TIMEOUT" -N -O "$output" "$url"; then
        echo "   ✔ $desc downloaded successfully."
    else
        echo "   ❌ Failed to download $desc after $MAX_RETRIES attempts."
        return 1
    fi
}

unzip_safely() {
    local zipfile="$1"
    local targetdir="$2"
    if [ -f "$zipfile" ]; then
        mkdir -p "$targetdir"
        unzip -o -q "$zipfile" -d "$targetdir" || echo "⚠️  Unzip failed for $zipfile"
        rm -f "$zipfile"
    else
        echo "⚠️  Zip file not found: $zipfile"
    fi
}


# ===============================
# DOWNLOAD FUNCTIONS
# ===============================

download_biogrid() {
    download_file "$BIOGRID_URL" \
                  "BIOGRID-ALL-LATEST.mitab.zip" "BioGRID" \
    || { echo "⚠️  BioGRID download failed, continuing..."; return; }
    unzip_safely "BIOGRID-ALL-LATEST.mitab.zip" "biogrid_all_latest"
}

download_web_of_life() {
    download_file "$WEB_OF_LIFE_URL" \
                  "web_of_life.zip" "Web of Life" \
    || { echo "⚠️  Web of Life download failed, continuing..."; return; }
    unzip_safely "web_of_life.zip" "web_of_life"
}

download_globi() {
    download_file "$GLOBI_URL" "globi.tsv.gz" "GloBI" \
    || { echo "⚠️  GloBI download failed, continuing..."; return; }
    gunzip -f globi.tsv.gz || echo "⚠️  Failed to extract GloBI"
}


download_hpidb() {
    echo "→ Downloading HPIDB ..."
    if curl -L -A "Mozilla/5.0" -o "hpidb.mitab.zip" \
            "$HPIDB_URL"; then
        echo "   ✔ HPIDB downloaded successfully."
        unzip_safely "hpidb.mitab.zip" "hpidb"
    else
        echo "⚠️  HPIDB download failed, continuing..."
        return 1
    fi
}

download_intact() {
    download_file "$INTACT_URL" \
                  "intact.txt" "IntAct" \
    || { echo "⚠️  IntAct download failed, continuing..."; return; }
}

download_iwdb() {
    echo "→ Downloading IWDB ..."
    bash "${SCRIPT_DIR}/downloadIWDB.sh" || echo "⚠️  IWDB download failed, continuing..."
}

download_phi_base() {
    download_file "$PHI_BASE_URL" \
                  "phi_base.csv" "PHI-base" \
    || { echo "⚠️  PHI-base download failed, continuing..."; return; }
}

download_pida() {
    mkdir -p pida
    download_file "$PIDA_URL" "pida/master.zip" "PIDA" \
    || { echo "⚠️  PIDA download failed, continuing..."; return; }
    unzip -o -q "pida/master.zip" || echo "⚠️  PIDA unzip failed"
    mv PIDA-master/pida.tsv ./pida.tsv 2>/dev/null || echo "⚠️  PIDA file not found"
    rm -rf pida PIDA-master
}

download_virhostnet() {
    download_file "$VIRHOSTNET_URL" \
                  "vir_host_net.tsv" "VirHostNet" \
    || { echo "⚠️  VirHostNet download failed, continuing..."; return; }
}

download_eid2() {
    echo "→ Downloading EID2 ..."
    if curl -L -A "Mozilla/5.0" -o "eid2.csv" \
            "$EID2_URL"; then
        echo "   ✔ EID2 downloaded successfully."
    else
        echo "⚠️  EID2 download failed, continuing..."
        return 1
    fi
}

download_siad() {
    download_file "$SIAD_URL" \
                  "siad.txt" "SIAD" \
    || { echo "⚠️  SIAD download failed, continuing..."; return; }
}

download_mint() {
    download_file "$MINT_URL" \
                  "mint.tsv" "MINT" \
    || { echo "⚠️  MINT download failed, continuing..."; return; }
}

download_viral_interactome() {
    echo "→ Downloading Viral Interactome ..."
    if curl -L -o "viral_interactome.zip" \
            "$PMC9897028_URL"; then
        echo "   ✔ Viral Interactome downloaded successfully."
    else
        echo "⚠️  Viral Interactome download failed, continuing..."
        return 1
    fi
    unzip_safely "viral_interactome.zip" "viral_interactome"
}

download_signor() {
    download_file "$SIGNOR_URL" \
                  "signor.tsv" "SIGNOR" \
    || { echo "⚠️  SIGNOR download failed, continuing..."; return; }
}


# ===============================
# MAIN WORKFLOW
# ===============================
echo "### Starting downloads ###"

cd $DOWNLOAD_DIR
download_biogrid
download_web_of_life
download_globi
download_hpidb
download_intact
download_iwdb
download_phi_base
download_pida
download_virhostnet
download_eid2
download_siad
download_mint
download_viral_interactome
download_signor
cd "$SCRIPT_DIR/../main"

echo
echo "### Checking all downloads ###"

declare -A db_files=(
    ["BioGRID"]="$BIOGRID_DIR"
    ["Web_of_Life"]="$WEB_OF_LIFE_DATABASE_DIR"
    ["GloBI"]="$GLOBI_FILE"
    ["HPIDB"]="$HPIDB_DIR"
    ["IntAct"]="$INTACT_FILE"
    ["IWDB"]="$IWDB_DIR"
    ["PHI-base"]="$PHI_BASE_FILE"
    ["PIDA"]="$PIDA_FILE"
    ["VirHostNet"]="$VIRHOSTNET_FILE"
    ["EID2"]="$EID2_FILE"
    ["SIAD"]="$SIAD_FILE"
    ["MINT"]="$MINT_FILE"
    ["Viral_Interactome"]="$PMC9897028_DIR"
    ["SIGNOR"]="$SIGNOR_FILE"
)

missing=()

for db in "${!db_files[@]}"; do
    path="${DOWNLOAD_DIR}/${db_files[$db]}"

    if [ -e "$path" ]; then
        echo "✔ $db found: $path"
    else
        echo "❌ $db missing: $path"
        missing+=("$db")
    fi
done

echo
if [ ${#missing[@]} -eq 0 ]; then
    echo "🎉 All databases downloaded successfully at $(date)"
else
    echo "⚠️  Missing databases: ${missing[*]}"
    echo "Check the log file for details: $LOG_FILE"
fi

echo "=================================================================="
echo "### ISDB Downloader finished at $(date)"
echo "=================================================================="


