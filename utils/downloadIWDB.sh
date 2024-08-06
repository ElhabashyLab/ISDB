#!/bin/bash

cd $tempory_directory
# IWDB [iwdb/*]
# Download files with appropriate names under iwdb directory
# Host pathogen
wget -N -O iwdb.zip "http://www.ecologia.ib.usp.br/iwdb/data/host_parasite/excel_matrices/canadian_fish_excel.zip"
unzip iwdb.zip -d iwdb
rm iwdb.zip

# plant ants
wget -N -O "iwdb/bluthgen_2004.xls" "http://www.ecologia.ib.usp.br/iwdb/data/ant_plant/excel_matrices/bluthgen_2004.xls"
wget -N -O "iwdb/davidson_et_al_1989.xls" "http://www.ecologia.ib.usp.br/iwdb/data/ant_plant/excel_matrices/davidson_et_al_1989.xls"
wget -N -O "iwdb/davidson_fisher_1991.xls" "http://www.ecologia.ib.usp.br/iwdb/data/ant_plant/excel_matrices/davidson&fisher_1991.xls"
wget -N -O "iwdb/fonseca_ganade.xls" "http://www.ecologia.ib.usp.br/iwdb/data/ant_plant/excel_matrices/fonseca&ganade.xls"

# plant herbivore
wget -N -O "iwdb/joern_1979_marathon.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_herbivore/excel_matrices/joern_1979_marathon.xls"
wget -N -O "iwdb/joern_1979_altuda.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_herbivore/excel_matrices/joern_1979_altuda.xls"
wget -N -O "iwdb/leather_1991_britain.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_herbivore/excel_matrices/leather_1991_britain.xls"
wget -N -O "iwdb/leather_1991_finland.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_herbivore/excel_matrices/leather_1991_finland.xls"

# Download files for plant pollinator category under iwdb directory
wget -N -O "iwdb/arroyo_I.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/arroyo_I.xls"
wget -N -O "iwdb/arroyo_II.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/arroyo_II.xls"
wget -N -O "iwdb/arroyo_III.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/arroyo_III.xls"
wget -N -O "iwdb/barret&helenurm_1987.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/barret&helenurm_1987.xls"
wget -N -O "iwdb/clements_1923.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/clements_1923.xls"
wget -N -O "iwdb/dupont_et_al_2003.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/dupont_et_al_2003.xls"
wget -N -O "iwdb/elberling&olesen_1999.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/elberling&olesen_1999.xls"
wget -N -O "iwdb/hocking_1968.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/hocking_1968.xls"
wget -N -O "iwdb/kaiser-bunbury_2009.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/kaiser-bunbury_2009.xls"
wget -N -O "iwdb/Kaiser_Bunbury_et_al_2017.xlsx" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/Kaiser_Bunbury_et_al_2017.xlsx"
wget -N -O "iwdb/kato_et_al_1990.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/kato_et_al_1990.xls"
wget -N -O "iwdb/kevan_1970.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/kevan_1970.xls"
wget -N -O "iwdb/inouye_1988.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/inouye_1988.xls"
wget -N -O "iwdb/mcmullen_1993.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/mcmullen_1993.xls"
wget -N -O "iwdb/medan_et_al_2002.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/medan_et_al_2002.xls"
wget -N -O "iwdb/memmott_1999.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/memmott_1999.xls"
wget -N -O "iwdb/mosquin_1967.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/mosquin_1967.xls"
wget -N -O "iwdb/motten_1982.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/motten_1982.xls"
wget -N -O "iwdb/olesen_aigrettes.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/olesen_aigrettes.xls"
wget -N -O "iwdb/olesen_flores.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/olesen_flores.xls"
wget -N -O "iwdb/ollerton_et_al_2003.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/ollerton_et_al_2003.xls"
wget -N -O "iwdb/ramirez_1992.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/ramirez_1992.xls"
wget -N -O "iwdb/robertson_1929.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/robertson_1929.xls"
wget -N -O "iwdb/schemske_et_al_1978.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/schemske_et_al_1978.xls"
wget -N -O "iwdb/small_1976.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/small_1976.xls"
wget -N -O "iwdb/vazquez_2002.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/vazquez_2002.xls"
wget -N -O "iwdb/vizentin-bugoni_et_al_2016_complementary.xls" "http://www.ecologia.ib.usp.br/iwdb/data/plant_pollinator/excel/vizentin-bugoni_et_al_2016_complementary.xls"

# Download files for seed disperser category under iwdb directory
wget -N -O "iwdb/beehler_1983.xls" "http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices/beehler_1983.xls"
wget -N -O "iwdb/poulin_1999.xls" "http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices/poulin_1999.xls"
wget -N -O "iwdb/schleuning-et-al-2010.xls" "http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices/schleuning-et-al-2010.xls"
wget -N -O "iwdb/snow&snow_1971.xls" "http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices/snow&snow_1971.xls"
wget -N -O "iwdb/snow&snow_1988.xls" "http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices/snow&snow_1988.xls"
wget -N -O "iwdb/sorensen_1981.xls" "http://www.ecologia.ib.usp.br/iwdb/data/seed_dispersal/excel_matrices/sorensen_1981.xls"

# predator prey
wget -N -O "iwdb/carpinteria.xls" "http://www.ecologia.ib.usp.br/iwdb/data/predator_prey/excel_matrices/carpinteria.xls"
wget -N -O "iwdb_tmp.zip" "http://www.ecologia.ib.usp.br/iwdb/data/predator_prey/excel_matrices/thoms_towns_excel.zip"

# Unzip files
unzip -o iwdb_tmp.zip -d iwdb_tmp
mv iwdb_tmp/* iwdb
rm -R iwdb_tmp
rm iwdb_tmp.zip
