#!/usr/bin/env bash
# ======================================================================
# ISDB Resource Downloader
# Description: Automated retrieval of all interspecies interaction within IWDB
# Author: Hadeer Elhabashy
# Version: 2.2
# ======================================================================

set -euo pipefail

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

# Allow external path argument, otherwise use default
DATA_DIR="${1:-/vol/webapps/isdb_resourcesDB}"
IWDB_DIR="${DATA_DIR}/iwdb"

mkdir -p "${IWDB_DIR}"

echo "ISDB IWDB download started"
echo "Target directory: ${IWDB_DIR}"

# ----------------------------------------------------------------------
# Generic download function
# ----------------------------------------------------------------------

download_file() {
    local url="$1"
    local outfile="$2"

    echo "Downloading: ${outfile}"
    wget -N -O "${outfile}" "${url}"
}

# ----------------------------------------------------------------------
# Host–Parasite
# ----------------------------------------------------------------------

download_file \
"http://www.ecologia.ib.usp.br/iwdb/data/host_parasite/excel_matrices/canadian_fish_excel.zip" \
"${IWDB_DIR}/host_parasite.zip"

unzip -o "${IWDB_DIR}/host_parasite.zip" -d "${IWDB_DIR}"
rm -f "${IWDB_DIR}/host_parasite.zip"

# ----------------------------------------------------------------------
# Ant–Plant
# ----------------------------------------------------------------------

ANT_BASE="http://www.ecologia.ib.usp.br/iwdb/data/ant_plant/excel_matrices"

download_file "${ANT_BASE}/bluthgen_2004.xls" "${IWDB_DIR}/bluthgen_2004.xls"
download_file "${ANT_BASE}/davidson_et_al_1989.xls" "${IWDB_DIR}/davidson_et_al_1989.xls"
download_file "${ANT_BASE}/davidson&fisher_1991.xls" "${IWDB_DIR}/davidson_fisher_1991.xls"
download_file "${ANT_BASE}/fonseca&ganade.xls" "${IWDB_DIR}/fonseca_ganade.xls"


# ----------------------------------------------------------------------
# Plant–Herbivore
# ----------------------------------------------------------------------

HERB_BASE="http://www.ecologia.ib.usp.br/iwdb/data/plant_herbivore/excel_matrices"

download_file "${HERB_BASE}/joern_1979_marathon.xls" "${IWDB_DIR}/joern_1979_marathon.xls"
download_file "${HERB_BASE}/joern_1979_altuda.xls" "${IWDB_DIR}/joern_1979_altuda.xls"
download_file "${HERB_BASE}/leather_1991_britain.xls" "${IWDB_DIR}/leather_1991_britain.xls"
download_file "${HERB_BASE}/leather_1991_finland.xls" "${IWDB_DIR}/leather_1991_finland.xls"


# ----------------------------------------------------------------------
# Plant–Pollinator
# ----------------------------------------------------------------------

POLL_BASE="http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel"

download_file "${POLL_BASE}/arroyo_I.xls" "${IWDB_DIR}/arroyo_I.xls"
download_file "${POLL_BASE}/arroyo_II.xls" "${IWDB_DIR}/arroyo_II.xls"
download_file "${POLL_BASE}/arroyo_III.xls" "${IWDB_DIR}/arroyo_III.xls"
download_file "${POLL_BASE}/barret&helenurm_1987.xls" "${IWDB_DIR}/barret_helenurm_1987.xls"
download_file "${POLL_BASE}/clements_1923.xls" "${IWDB_DIR}/clements_1923.xls"
download_file "${POLL_BASE}/dupont_et_al_2003.xls" "${IWDB_DIR}/dupont_et_al_2003.xls"
download_file "${POLL_BASE}/elberling&olesen_1999.xls" "${IWDB_DIR}/elberling_olesen_1999.xls"
download_file "${POLL_BASE}/hocking_1968.xls" "${IWDB_DIR}/hocking_1968.xls"

# ----------------------------------------------------------------------
# Seed Dispersal
# ----------------------------------------------------------------------

SEED_BASE="http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices"

download_file "${SEED_BASE}/beehler_1983.xls" "${IWDB_DIR}/beehler_1983.xls"
download_file "${SEED_BASE}/poulin_1999.xls" "${IWDB_DIR}/poulin_1999.xls"
download_file "${SEED_BASE}/schleuning-et-al-2010.xls" "${IWDB_DIR}/schleuning_2010.xls"
download_file "${SEED_BASE}/snow&snow_1971.xls" "${IWDB_DIR}/snow_snow_1971.xls"
download_file "${SEED_BASE}/snow&snow_1988.xls" "${IWDB_DIR}/snow_snow_1988.xls"
download_file "${SEED_BASE}/sorensen_1981.xls" "${IWDB_DIR}/sorensen_1981.xls"


# ----------------------------------------------------------------------
# Predator–Prey
# ----------------------------------------------------------------------

PRED_BASE="http://www.ecologia.ib.usp.br/iwdb/data/predator_prey/excel_matrices"

download_file "${PRED_BASE}/carpinteria.xls" "${IWDB_DIR}/carpinteria.xls"

download_file \
"${PRED_BASE}/thoms_towns_excel.zip" \
"${IWDB_DIR}/predator_prey.zip"

TMP_DIR=$(mktemp -d)

unzip -o "${IWDB_DIR}/predator_prey.zip" -d "${TMP_DIR}"
mv "${TMP_DIR}"/* "${IWDB_DIR}/"

rm -rf "${TMP_DIR}"
rm -f "${IWDB_DIR}/predator_prey.zip"

# ----------------------------------------------------------------------
# Finished
# ----------------------------------------------------------------------

echo "IWDB datasets downloaded successfully."
