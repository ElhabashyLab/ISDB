#!/bin/bash
set -e

# Change to the temporary directory
cd "$tempory_directory"

# Function to download and unzip files
download_and_unzip() {
    local url="$1"
    local output="$2"
    echo "Downloading $output..."
    if wget -N -O "$output" "$url"; then
        echo "Download successful. Proceeding with unzip."
        unzip "$output" -d "${output%.*}"
        rm "$output"
    else
        echo "Download failed for $output."
    fi
}

# Download files
echo "### Downloading files ###"

# Define URLs and output files
declare -A urls=(
    ["biogrid"]="https://downloads.thebiogrid.org/Download/BioGRID/Latest-Release/BIOGRID-ALL-LATEST.tab3.zip"
    ["web_of_life"]="https://www.web-of-life.es/map_download_fast2.php?format=csv&networks=..."
    ["globi"]="https://zenodo.org/record/8284068/files/interactions.tsv.gz"
    ["hpidb"]="https://hpidb.igbb.msstate.edu/download_hpidata.php?type=1&file=hpidb2.mitab.zip"
    ["intact"]="https://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/intact.txt"
    ["phi_base"]="https://raw.githubusercontent.com/PHI-base/data/master/releases/phi-base_current.csv"
    ["pida"]="https://github.com/ramalok/PIDA/archive/refs/heads/master.zip"
    ["vir_host_net"]="http://virhostnet.prabi.fr:9090/psicquic/webservices/current/search/query/*"
    ["eid2"]="https://figshare.com/ndownloader/files/2196534"
    ["siad"]="https://www.discoverlife.org/siad/data/source/biodiversity.org.au:dataexport/interactions.txt"
    ["mint"]="http://www.ebi.ac.uk/Tools/webservices/psicquic/mint/webservices/current/search/query/*"
    ["viral_interactome"]="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9897028/bin/msad012_supplementary_data.zip"
    ["signor"]="https://signor.uniroma2.it/releases/getLatestRelease.php"
)

# Download all files
for file in "${!urls[@]}"; do
    case "$file" in
        "biogrid")
            download_and_unzip "${urls[$file]}" "biogrid_all_latest.tab3.zip"
            ;;
        "web_of_life")
            download_and_unzip "${urls[$file]}" "web_of_life.zip"
            ;;
        "globi")
            wget -N -O globi.tsv.gz "${urls[$file]}"
            gunzip globi.tsv.gz
            ;;
        "hpidb")
            download_and_unzip "${urls[$file]}" "hpidb.mitab.zip"
            ;;
        "intact")
            wget -N -O intact.txt "${urls[$file]}"
            ;;
        "phi_base")
            wget -N -O phi_base.csv "${urls[$file]}"
            ;;
        "pida")
            wget -N -P pida "${urls[$file]}"
            unzip pida/master.zip
            mv PIDA-master/pida.tsv ./
            rm -r pida PIDA-master
            ;;
        "vir_host_net")
            wget -N -O vir_host_net.tsv "${urls[$file]}"
            ;;
        "eid2")
            wget -N -O eid2.csv "${urls[$file]}"
            ;;
        "siad")
            wget -N -O siad.txt "${urls[$file]}"
            ;;
        "mint")
            wget -N -O mint.tsv "${urls[$file]}"
            ;;
        "viral_interactome")
            download_and_unzip "${urls[$file]}" "viral_interactome.zip"
            ;;
        "signor")
            wget -N -O signor.tsv "${urls[$file]}"
            ;;
    esac
done

echo "### Download complete ###"
