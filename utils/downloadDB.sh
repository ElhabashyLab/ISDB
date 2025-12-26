#!/usr/bin/env bash
# ======================================================================
# ISDB Resource Downloader
# Description: Automated retrieval of all interspecies interaction datasets
# Author: Hadeer Elhabashy
# Version: 2.2
# ======================================================================

set -euo pipefail

# ===============================
# CONFIGURATION
# ===============================
DATA_DIR="/media/elhabashy/Elements/interspecies_ev/isdb"

# the path to the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MAX_RETRIES=3
TIMEOUT=60

mkdir -p "$DATA_DIR"
LOG_FILE="${DATA_DIR%/}/download_log_$(date +%Y%m%d_%H%M).log"
cd "$DATA_DIR" || exit 1
current_dir="$(pwd)"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "=================================================================="
echo "### ISDB Downloader started at $(date)"
echo "### Working directory: $DATA_DIR"
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
    download_file "https://downloads.thebiogrid.org/Download/BioGRID/Latest-Release/BIOGRID-ALL-LATEST.mitab.zip" \
                  "BIOGRID-ALL-LATEST.mitab.zip" "BioGRID" \
    || { echo "⚠️  BioGRID download failed, continuing..."; return; }
    unzip_safely "BIOGRID-ALL-LATEST.mitab.zip" "biogrid_all_latest"
}

download_web_of_life() {
    download_file "https://www.web-of-life.es/map_download_fast2.php?format=csv&networks=A_HP_001,A_HP_002,A_HP_003,A_HP_004,A_HP_005,A_HP_006" \
                  "web_of_life.zip" "Web of Life" \
    || { echo "⚠️  Web of Life download failed, continuing..."; return; }
    #unzip_safely "web_of_life.zip" "web_of_life"
}

download_globi() {
    download_file "https://zenodo.org/record/8284068/files/interactions.tsv.gz" "globi.tsv.gz" "GloBI" \
    || { echo "⚠️  GloBI download failed, continuing..."; return; }
    gunzip -f globi.tsv.gz || echo "⚠️  Failed to extract GloBI"
}


download_hpidb() {
    echo "→ Downloading HPIDB ..."
    if curl -L -A "Mozilla/5.0" -o "hpidb.mitab.zip" \
            "http://hpidb.igbb.msstate.edu/downloads/hpidb2.mitab.zip"; then
        echo "   ✔ HPIDB downloaded successfully."
        unzip_safely "hpidb.mitab.zip" "hpidb"
    else
        echo "⚠️  HPIDB download failed, continuing..."
        return 1
    fi
}

download_intact() {
    download_file "https://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/intact.txt" \
                  "intact.txt" "IntAct" \
    || { echo "⚠️  IntAct download failed, continuing..."; return; }
}

download_iwdb() {
    echo "→ Downloading IWDB ..."
    bash "${SCRIPT_DIR}/../utils/downloadIWDB.sh" || echo "⚠️  IWDB download failed, continuing..."
}

download_phi_base() {
    download_file "https://raw.githubusercontent.com/PHI-base/data/master/releases/phi-base_current.csv" \
                  "phi_base.csv" "PHI-base" \
    || { echo "⚠️  PHI-base download failed, continuing..."; return; }
}

download_pida() {
    mkdir -p pida
    download_file "https://github.com/ramalok/PIDA/archive/refs/heads/master.zip" "pida/master.zip" "PIDA" \
    || { echo "⚠️  PIDA download failed, continuing..."; return; }
    unzip -o -q "pida/master.zip" || echo "⚠️  PIDA unzip failed"
    mv PIDA-master/pida.tsv ./pida.tsv 2>/dev/null || echo "⚠️  PIDA file not found"
    rm -rf pida PIDA-master
}

download_virhostnet() {
    download_file "http://virhostnet.prabi.fr:9090/psicquic/webservices/current/search/query/*" \
                  "vir_host_net.tsv" "VirHostNet" \
    || { echo "⚠️  VirHostNet download failed, continuing..."; return; }
}



download_eid2() {
    echo "→ Downloading EID2 ..."
    if curl -L -A "Mozilla/5.0" -o "eid2.csv" \
            "https://figshare.com/ndownloader/files/2196534"; then
        echo "   ✔ EID2 downloaded successfully."
    else
        echo "⚠️  EID2 download failed, continuing..."
        return 1
    fi
}

download_siad() {
    download_file "https://www.discoverlife.org/siad/data/source/biodiversity.org.au:dataexport/interactions.txt" \
                  "siad.txt" "SIAD" \
    || { echo "⚠️  SIAD download failed, continuing..."; return; }
}

download_mint() {
    download_file "http://www.ebi.ac.uk/Tools/webservices/psicquic/mint/webservices/current/search/query/*" \
                  "mint.tsv" "MINT" \
    || { echo "⚠️  MINT download failed, continuing..."; return; }
}



download_viral_interactome() {
    echo "→ Downloading Viral Interactome ..."
    if curl -L -o "viral_interactome.zip" \
            "https://pmc.ncbi.nlm.nih.gov/articles/instance/9897028/bin/msad012_supplementary_data.zip"; then
        echo "   ✔ Viral Interactome downloaded successfully."
    else
        echo "⚠️  Viral Interactome download failed, continuing..."
        return 1
    fi
    unzip_safely "viral_interactome.zip" "viral_interactome"
}


# ===============================
# MAIN WORKFLOW
# ===============================
echo "### Starting downloads ###"

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

echo
echo "### Checking all downloads ###"

declare -A db_files=(
    ["BioGRID"]="biogrid_all_latest"
    ["Web_of_Life"]="web_of_life"
    ["GloBI"]="globi.tsv"
    ["HPIDB"]="hpidb"
    ["IntAct"]="intact.txt"
    ["IWDB"]="iwdb"
    ["PHI-base"]="phi_base.csv"
    ["PIDA"]="pida.tsv"
    ["VirHostNet"]="vir_host_net.tsv"
    ["EID2"]="eid2.csv"
    ["SIAD"]="siad.txt"
    ["MINT"]="mint.tsv"
    ["Viral_Interactome"]="viral_interactome"
    ["SIGNOR"]="signor.tsv"
)

missing=()
for db in "${!db_files[@]}"; do
    if [ -e "${db_files[$db]}" ]; then
        echo "✔ $db found."
    else
        echo "❌ $db missing!"
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

                                                                                                                                                         258,0-1       Bot

