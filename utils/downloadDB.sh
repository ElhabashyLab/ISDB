#! /bin/bash

cd $tempory_directory

# Download files
echo "### Downloading files ###"
# Biogrid [biogrid_all_latest] # TODO sometimes failes
wget -N -v "https://downloads.thebiogrid.org/Download/BioGRID/Latest-Release/BIOGRID-ALL-LATEST.tab3.zip" 
if [ $? -eq 0 ]; then
    echo "Download successful. Proceeding with unzip."
    # Unzip the file
    unzip biogrid_latest_tab3.zip -d biogird_all_latest
    rm biogrid_latest.tab3.zip
else
    echo "Download failed. Using static file. Please try again later"
    rm biogrid_latest.tab3.zip
fi
# web of life [web_of_life/*]
wget -N -O web_of_life.zip "https://www.web-of-life.es/map_download_fast2.php?format=csv&networks=A_HP_001,A_HP_002,A_HP_003,A_HP_004,A_HP_005,A_HP_006,A_HP_007,A_HP_008,A_HP_009,A_HP_010,A_HP_011,A_HP_012,A_HP_013,A_HP_014,A_HP_015,A_HP_016,A_HP_017,A_HP_018,A_HP_019,A_HP_020,A_HP_021,A_HP_022,A_HP_023,A_HP_024,A_HP_025,A_HP_026,A_HP_027,A_HP_028,A_HP_029,A_HP_030,A_HP_031,A_HP_032,A_HP_033,A_HP_034,A_HP_035,A_HP_036,A_HP_037,A_HP_038,A_HP_039,A_HP_040,A_HP_041,A_HP_042,A_HP_043,A_HP_044,A_HP_045,A_HP_046,A_HP_047,A_HP_048,A_HP_049,A_HP_050,A_HP_051,A_PH_004,A_PH_005,A_PH_006,A_PH_007,FW_001,FW_002,FW_003,FW_004,FW_005,FW_006,FW_007,FW_008,FW_009,FW_010,FW_011,FW_012_01,FW_012_02,FW_013_01,FW_013_02,FW_013_03,FW_013_04,FW_013_05,FW_014_01,FW_014_02,FW_014_03,FW_014_04,FW_015_01,FW_015_02,FW_015_03,FW_015_04,FW_016_01,FW_017_01,FW_017_02,FW_017_03,FW_017_04,FW_017_05,FW_017_06,M_AF_001,M_AF_002_01,M_AF_002_02,M_AF_002_03,M_AF_002_04,M_AF_002_05,M_AF_002_06,M_AF_002_07,M_AF_002_08,M_AF_002_09,M_AF_002_10,M_AF_002_11,M_AF_002_12,M_AF_002_13,M_AF_002_14,M_AF_002_15,M_AF_002_16,M_PA_001,M_PA_002,M_PA_003,M_PA_004,M_PA_005,M_PL_001,M_PL_002,M_PL_003,M_PL_004,M_PL_005,M_PL_006,M_PL_007,M_PL_008,M_PL_009,M_PL_010,M_PL_011,M_PL_012,M_PL_013,M_PL_014,M_PL_015,M_PL_016,M_PL_017,M_PL_018,M_PL_019,M_PL_020,M_PL_021,M_PL_022,M_PL_023,M_PL_024,M_PL_025,M_PL_026,M_PL_027,M_PL_028,M_PL_029,M_PL_030,M_PL_031,M_PL_032,M_PL_033,M_PL_034,M_PL_035,M_PL_036,M_PL_037,M_PL_038,M_PL_039,M_PL_040,M_PL_041,M_PL_042,M_PL_043,M_PL_044,M_PL_045,M_PL_046,M_PL_047,M_PL_048,M_PL_049,M_PL_050,M_PL_051,M_PL_052,M_PL_053,M_PL_054,M_PL_055,M_PL_056,M_PL_057,M_PL_058,M_PL_059,M_PL_060_01,M_PL_060_02,M_PL_060_03,M_PL_060_04,M_PL_060_05,M_PL_060_06,M_PL_060_07,M_PL_060_08,M_PL_060_09,M_PL_060_10,M_PL_060_11,M_PL_060_12,M_PL_060_13,M_PL_060_14,M_PL_060_15,M_PL_060_16,M_PL_060_17,M_PL_060_18,M_PL_060_19,M_PL_060_20,M_PL_060_21,M_PL_060_22,M_PL_060_23,M_PL_060_24,M_PL_061_01,M_PL_061_02,M_PL_061_03,M_PL_061_04,M_PL_061_05,M_PL_061_06,M_PL_061_07,M_PL_061_08,M_PL_061_09,M_PL_061_10,M_PL_061_11,M_PL_061_12,M_PL_061_13,M_PL_061_14,M_PL_061_15,M_PL_061_16,M_PL_061_17,M_PL_061_18,M_PL_061_19,M_PL_061_20,M_PL_061_21,M_PL_061_22,M_PL_061_23,M_PL_061_24,M_PL_061_25,M_PL_061_26,M_PL_061_27,M_PL_061_28,M_PL_061_29,M_PL_061_30,M_PL_061_31,M_PL_061_32,M_PL_061_33,M_PL_061_34,M_PL_061_35,M_PL_061_36,M_PL_061_37,M_PL_061_38,M_PL_061_39,M_PL_061_40,M_PL_061_41,M_PL_061_42,M_PL_061_43,M_PL_061_44,M_PL_061_45,M_PL_061_46,M_PL_061_47,M_PL_061_48,M_PL_062,M_PL_063,M_PL_064,M_PL_065,M_PL_066,M_PL_067,M_PL_068,M_PL_069_01,M_PL_069_02,M_PL_069_03,M_PL_070,M_PL_071,M_PL_072_01,M_PL_072_02,M_PL_072_03,M_PL_072_04,M_PL_072_05,M_PL_072_06,M_PL_072_07,M_PL_072_08,M_PL_072_09,M_PL_072_10,M_PL_072_11,M_PL_072_12,M_PL_073,M_PL_074_01,M_PL_074_02,M_PL_074_03,M_PL_074_04,M_PL_074_05,M_PL_074_06,M_PL_074_07,M_PL_074_08,M_PL_074_09,M_PL_074_10,M_PL_074_11,M_PL_074_12,M_PL_074_13,M_PL_074_14,M_PL_074_15,M_PL_074_16,M_SD_001,M_SD_002,M_SD_003,M_SD_004,M_SD_005,M_SD_006,M_SD_007,M_SD_008,M_SD_009,M_SD_010,M_SD_011,M_SD_012,M_SD_013,M_SD_014,M_SD_015,M_SD_016,M_SD_017,M_SD_018,M_SD_019,M_SD_020,M_SD_021,M_SD_022,M_SD_023,M_SD_024,M_SD_025,M_SD_026,M_SD_027,M_SD_028,M_SD_029,M_SD_030,M_SD_031,M_SD_032,M_SD_033,M_SD_034&species=yes&type=All&data=All&speciesrange=from%200%20to%20999999&interactionsrange=from%200%20to%20999999&searchbox=undefined&checked=false"
unzip web_of_life.zip -d web_of_life
rm web_of_life.zip
# GloBI [globi.tsv]
wget -N -O globi.tsv.gz "https://zenodo.org/record/8284068/files/interactions.tsv.gz"
gunzip globi.tsv.gz
# HPIDB [hpidb] # OPTIONAL check interlog prediction
wget -N -O hpidb.mitab.zip "https://hpidb.igbb.msstate.edu/download_hpidata.php?type=1&file=hpidb2.mitab.zip"
unzip hpidb.mitab.zip -d hpidb 
rm hpidb.mitab.zip
#"https://hpidb.igbb.msstate.edu/hpi30_interologs.html"
# IntAct [intact.txt]
wget -N -O intact.txt "https://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/intact.txt"
# IWDB [iwdb/*]
bash "${current_dir}/../utils/downloadIWDB.sh"
# PHI-base [phi_base,csv]
wget -N -O phi_base.csv "https://raw.githubusercontent.com/PHI-base/data/master/releases/phi-base_current.csv"
# PIDA [pida.tsv] (static version)
wget -N -P pida "https://github.com/ramalok/PIDA/archive/refs/heads/master.zip"
unzip pida/master.zip
mv PIDA-master/pida.tsv ./
rm -r pida
rm -r PIDA-master
# VirHostNet [vir_host_net.tsv]https://www.bv-brc.org
wget -N -O vir_host_net.tsv "http://virhostnet.prabi.fr:9090/psicquic/webservices/current/search/query/*"
# EID2 [eid2.csv] (static)
wget -N -O eid2.csv "https://figshare.com/ndownloader/files/2196534"
# SIAD [siad.txt] (dollar limited)
wget -N -O siad.txt "https://www.discoverlife.org/siad/data/source/biodiversity.org.au:dataexport/interactions.txt"
# MINT [mint.tsv]
wget -N -O mint.tsv "http://www.ebi.ac.uk/Tools/webservices/psicquic/mint/webservices/current/search/query/*"
# viral interactome [viral_interactome/*] (static)
wget -N -O viral_interactome.zip "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9897028/bin/msad012_supplementary_data.zip"
unzip viral_interactome.zip -d viral_interactome
rm viral_interactome.zip
# Signor [signor.tsv]
wget -N -O signor.tsv "https://signor.uniroma2.it/releases/getLatestRelease.php"