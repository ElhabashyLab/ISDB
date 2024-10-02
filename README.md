# The Interacting Species Database (ISDB)
A Comprehensive Resource for Ecological Interactions at the Molecular Level.
The ISDB compiles data on species interactions from 21 resources, including scientific names, Taxon IDs, UniProt IDs, interaction types, ontology identifiers, references, and original database sources. ISDB is developed using Python and Bash scripts and is available as an open-source under the MIT License.

# Web interface
ISDB web interface can be found here (www.elhabashylab.org/ISDB) which is hosted by the German Network for Bioinformatics Infrastructure (de.NBI).
The web interface provides functionalities for batch downloads, data search, result download, and data deposition.

# How to download ISDB? 
Built versions of ISDB can be found under the directory `versions` and be downloaded either through GitHubs user-interface, the ISDB web interface, or through command line via:
```
wget https://github.com/ElhabashyLab/ISDB/tree/main/versions/ISDB_2024_09_13.<tsv/csv>.gz
```

# How to build ISDB locally? 
To rebuild ISDB locally, Please follow these steps:

1. Successful execution requires the following dependencies: Python 3.11.7, Pandas 2.0.3, NumPy 1.24.3, and Requests 2.31.0.

2. You computer should be connected to the internet.

3. Download resources. While the database automatically parses information from most sources, certain datasets must be manually downloaded by the user, with their locations specified in `updateDB.sh`. 
   ISDB parces the most of the databases automatically. However, some resources need to be manually downloaded
   - Bat Eco-Interactions (https://www.batbase.org/explore)
   - BV-BRC (https://www.bv-brc.org)
   - DIP (https://dip.doe-mbi.ucla.edu/dip/)
   - GMPD (https://parasites.nunn-lab.org/data/)
   - PHILM2Web (https://phim2web.lailab.info/pages/index.html)
   - PHISTO (https://parasites.nunn-lab.org/data/)
   - FGSCdb (https://edelponte.shinyapps.io/FGSCdb/)

4. Clone this repository and cd into it.
    ```
   git clone
   ```

5. Edit the paths to the downloaded databases in the  `main/builtDB.sh` script. Further parameters are:
   
   1. `tempory_directory`: Direction in which ISDB is build,
   2. `overwrite`: Wether to overwrite pre-existing stages,
   3. `addtional_data`: File path or directory path of additional data files. Each file should at least include two species columns,
   4. `delete`: If intermediate stages should be deleted afterwards,
   5. `manualDatabases`: Exclude or include database which could not be downloaded automatically. If 'true' the user has specify their paths in the following section.

6. Finally build ISDB database
   To compile the database locally, the main script `main/builtDB.sh` should be executed inside the `main` directory.
   ```
   cd main
   .bash /builtDB.sh
   ```
Additional parameters, such as whether to overwrite existing files, remove intermediate files, or incorporate user-provided data, can also be configured within this script. More details can be found on the documentation on GitHub.

The generated database will be available in CSV and TSV formats, with the following column descriptions:
- SerialNumber: Interaction identifier inside ISDB
- TaxId(A/B): NCBI Taxonomical identifer
- Uid(A/B): UniProt protein identifier
- ScientificName(A/B): Sientifc species name
- interactionType: Phrase describing the interaction
- ontology: Interaction identifier of the coresponding ontology
- reference: Reference as defined by data source
- database: Databank source of the interaction


# How to deposite data to the ISDB?

To submit data for inclusion in our system, please contact our [team](#authors) directly. To incorporate your own data into the database locally please follow the instruction on [*How to build ISDB locally?*](#how-to-build-isdb-locally)

# List of resources 

The database can be built automatically. However, some resources need to be downloaded manually. This includes:

| Database | #Species | #Specie Pairs | #PPIs | Interaction Type | Batch download  | Citation |
|----------|--|--|--|--|--|--|
|Bat Eco-Interactions | 3,099 | 8,101 | 0 |   :heavy_check_mark: |  X  | | 
|BioGRID | 83 | 359 | 2,228,610 | X  |  :heavy_check_mark:  |  |
|BV-BRC | 133,835 | 142,666 | 0 | X  |   X  | |cite{BVBRC,BVBRC_homepage} |
|Database of Interacting Proteins (DIP) | 210 | 423 | 73,852 |  :heavy_check_mark:  |   X  | |
|The Enhanced Infectious Diseases (EID2) | 12,486 | 18,086 | 0 |  :heavy_check_mark:  |    :heavy_check_mark:  | |
|Fusarium graminearum species complex database (FGSCdb) | 19 | 15 | 0 |  :heavy_check_mark:  |   X  |  |
|Global Biotic Interactions (GloBI) | 89,994 | 461,385 | 0 | :heavy_check_mark:  |  :heavy_check_mark:  ||
|Global Mammal Parasite Database (GMPD) | 1,558 | 5,444 | 0 | X  |  X  |  |
|Host-pathogen interactions database (HPIDB)  | 734 | 967 | 54,879 | :heavy_check_mark:  |  :heavy_check_mark:  |  |
|IntAct | 1,819 | 3,575 | 1,079,255 | :heavy_check_mark:  |  :heavy_check_mark:  | |
|Interactome | 264 | 263 | 4,154 | :heavy_check_mark:  | :heavy_check_mark:  | |
|Interaction Web Database (IWDB) | 594 | 3,449 | 0 | X  | X  | |
|MINT | 698 | 1,331 | 100,048 | :heavy_check_mark:  |  :heavy_check_mark:  |  |
|PHI-base | 539 | 1,062 | 0 | X  |  :heavy_check_mark:  |  |
|PHILM2Web | 460 | 1,506 | 0 | :heavy_check_mark:  |  X  |  |
|Pathogen-Host Interaction Search Tool (PHISTO)  | 589 | 589 | 47,920 | X  |  X  | |cite{PHISTO} |
|Protist Interaction DAtabase (PIDA) | 647 | 836 | 0 | X  |  :heavy_check_mark: |  |
|Signaling Network Open Resource (Signor) | 7 | 10 | 17,400 | :heavy_check_mark:  |  :heavy_check_mark:  | |
|Species Interactions of Australia Database (SIAD) | 3,744 | 5,049 | 0 |  :heavy_check_mark:  |  :heavy_check_mark:  |  |
|Virus / Host protein-protein interactions Network (VirHostNet)  | 332 | 494 | 47,182 |  :heavy_check_mark:  |  :heavy_check_mark:  |  |
|Web of Life database | 172 | 1,007 | 0 | X  |    :heavy_check_mark: |  |


# Cite

# Authors
- Michael Mederer
- Anupam Gautam
- Hadeer Elhabashy
