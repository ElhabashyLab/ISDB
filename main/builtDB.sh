#! /bin/bash
# Please adjust "tempory_directory" to the path in which the database can be built
export tempory_directory="/vol/michael_data/db_interspecies/data_prot"
# Overwrite existing out files: false, true
export overwrite=false
# Addtional data (optional): e.g. filepath: <myFile.csv> or directory: <myFiles/> 
export addtional_data=""
### Delete tempory files
delete=false
### For manually downloaded database files:
# "false" -> no manual downloaded databases
# "true" -> includes manual downloaded databases (file path need to be specified)
manualDatabases=false

export current_dir=$(pwd)

if manualDatabases; then
    ## Bat Eco-Interactions
    # no static link -> https://www.batbase.org/explore
    mv $tempory_directory/manualDownload/BatEco-InteractionRecords.csv $tempory_directory
    ## BV-BRC 
    # no static link -> https://www.bv-brc.org
    mkdir $tempory_directory/bvbrc/
    mv $tempory_directory/manualDownload/BVBRC_genome_bacteria.csv $tempory_directory/bvbrc/
    mv $tempory_directory/manualDownload/BVBRC_genome_viruses.csv $tempory_directory/bvbrc/
    mv $tempory_directory/manualDownload/BVBRC_genome_archaea.csv $tempory_directory/bvbrc/
    ## DIP [dip/*] (Have to register -> not updated automatically)
    # https://dip.doe-mbi.ucla.edu/dip/
    mkdir $tempory_directory/dip/
    mv $tempory_directory/manualDownload/DIP/Celeg20170205.txt $tempory_directory/dip/
    mv $tempory_directory/manualDownload/DIP/Ecoli20170205.txt $tempory_directory/dip/ 
    mv $tempory_directory/manualDownload/DIP/Hsapi20170205.txt $tempory_directory/dip/ 
    mv $tempory_directory/manualDownload/DIP/Rnorv20170205.txt $tempory_directory/dip/
    mv $tempory_directory/manualDownload/DIP/Dmela20170205.txt $tempory_directory/dip/ 
    mv $tempory_directory/manualDownload/DIP/Hpylo20170205.txt $tempory_directory/dip/ 
    mv $tempory_directory/manualDownload/DIP/Mmusc20170205.txt $tempory_directory/dip/ 
    mv $tempory_directory/manualDownload/DIP/Scere20170205.txt $tempory_directory/dip/
    ## GMPD
    # no static link -> https://parasites.nunn-lab.org/data/
    mkdir gmpd
    mv $tempory_directory/manualDownload/GMPD/gmpd-data-carnivores.csv $tempory_directory/gmpd  
    mv $tempory_directory/manualDownload/GMPD/gmpd-data-primates.csv $tempory_directory/gmpd
    mv $tempory_directory/manualDownload/GMPD/gmpd-data-ungulates.csv $tempory_directory/gmpd
    ## PHILM2Web
    # no static link -> https://phim2web.lailab.info/pages/index.html
    mv $tempory_directory/manualDownload/philm2web.csv $tempory_directory
    ## PHISTO
    # no static link -> https://phisto.org/search.xhtml
    mv $tempory_directory/manualDownload/phisto_data.csv $tempory_directory
    ## FGSCdb
    # no static link -> https://edelponte.shinyapps.io/FGSCdb/
    mv $tempory_directory/manualDownload/FGSCdb_data.csv $tempory_directory
fi

# ### Download files 
# bash ../utils/downloadDB.sh
# ### Clean files
python ../utils/processDB.py
# ### Build DB
python ../utils/aggregateDB.py
##
if $delete; then
    rm *_out.*
fi
