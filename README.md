# The Interacting Species Database (ISDB)
A Comprehensive Resource for Ecological Interactions at the Molecular Level.
The ISDB compiles data on species interactions from 21 resources, including scientific names, Taxon IDs, UniProt IDs, interaction types, ontology identifiers, references, and original database sources.

#Web interface
ISDB web server is hosted by the German Network for Bioinformatics Infrastructure (de.NBI) and is accessible at \homepage[]. It provides functionalities for batch downloads, data search, result download, and data deposition.

#Open-source code
ISDB is developed using Python and Bash scripts and is available as an open-source project on GitHub under the MIT License \github.
 It includes both pre-built versions of the database in CSV and TSV format and the code needed to create a database.

#Execution 
Users can compile the database locally by executing the following command: 

> bash updateDB.sh} 

Successful execution requires the following dependencies: Python 3.11.7, Pandas 2.0.3, NumPy 1.24.3, and Requests 2.31.0. While the database automatically parses information from most sources, certain datasets must be manually downloaded by the user, with their locations specified in \texttt{updateDB.sh}. Additional parameters, such as whether to overwrite existing files, remove intermediate files, or incorporate user-provided data, can also be configured within this script. More details can be found on the documentation on GitHub.

# Download ISDB


# Rebuilding the ISDB
The database can be built automatically. 
To rebuild the ISDB, Please follow these steps:

1. You computer should be connect to the internet.

2. Download resources
   ISDB parces the most of the databases automatically. However, some resources need to be manually downloaded
   - Bat Eco-Interactions (https://www.batbase.org/explore)
   - BV-BRC (https://www.bv-brc.org)
   - DIP (https://dip.doe-mbi.ucla.edu/dip/)
   - GMPD (https://parasites.nunn-lab.org/data/)
   - PHILM2Web (https://phim2web.lailab.info/pages/index.html)
   - PHISTO (https://parasites.nunn-lab.org/data/)
   - FGSCdb (https://edelponte.shinyapps.io/FGSCdb/)

3. Clone this repository and cd into it.
    ```
   git clone
   ```

5. Edit the paths to the database in the  ~main/builtDB.sh script.

6. Finally build the ISDB database
   To build the database the main script *main/builtDB.sh* should be executed inside the *main* directory.
   ```
   cd main
   .bash /builtDB.sh
   ```
# Column description
- SerialNumber: Interaction identifier inside ISDB
- TaxId(A/B): NCBI Taxonomical identifer
- Uid(A/B): UniProt protein identifier
- ScientificName(A/B): Sientifc species name
- interactionType: Phrase describing the interaction
- ontology: Interaction identifier of the coresponding ontology
- reference: Reference as defined by data source
- database: Databank source of the interaction

# List of resources 

The database can be built automatically. However, some resources need to be downloaded manually. This includes:

| Database | #Species | #Specie Pairs | #PPIs | Interaction Type | Batch download  | Citation |
|----------|--|--|--|--|--|--|
|Bat Eco-Interactions | 3,099 | 8,101 | 0 |   :heavy_check_mark: |  X  | |cite{BEI} | 
|BioGRID | 83 | 359 | 2,228,610 | X  |  :heavy_check_mark:  |   |cite{biogrid} |
|BV-BRC | 133,835 | 142,666 | 0 | X  |   X  | |cite{BVBRC,BVBRC_homepage} |
|DIP | 210 | 423 | 73,852 |  :heavy_check_mark:  |   X  | |cite{DIP} |
|EID2 | 12,486 | 18,086 | 0 |  :heavy_check_mark:  |    :heavy_check_mark:  | |cite{EID2} |
|FGSCdb | 19 | 15 | 0 |  :heavy_check_mark:  |   X  | |cite{FGSCdb} |
|GloBI | 89,994 | 461,385 | 0 | :heavy_check_mark:  |  :heavy_check_mark:  | |cite{GloBI} |
|GMPD | 1,558 | 5,444 | 0 | X  |  X  | |cite{global_mammal_parasite, global_mammal_parasite_2} |
|HPIDB | 734 | 967 | 54,879 | :heavy_check_mark:  |  :heavy_check_mark:  | |cite{HPIDB, HPIDB_2} |
|IntAct | 1,819 | 3,575 | 1,079,255 | :heavy_check_mark:  |  :heavy_check_mark:  | |cite{intact} |
|Interactome | 264 | 263 | 4,154 | :heavy_check_mark:  | :heavy_check_mark:  | |cite{Interactome} |
|IWDB | 594 | 3,449 | 0 | X  | X  | :heavy_check_mark: | |cite{IWDB} |
|MINT | 698 | 1,331 | 100,048 | :heavy_check_mark:  |  :heavy_check_mark:  | |cite{MINT} |
|PHI-base | 539 | 1,062 | 0 | X  |  :heavy_check_mark:  | |cite{phi_base} |
|PHILM2Web | 460 | 1,506 | 0 | :heavy_check_mark:  |  X  | |cite{hilm2web} |
|PHISTO | 589 | 589 | 47,920 | X  |  X  | |cite{PHISTO} |
|PIDA | 647 | 836 | 0 | X  |  :heavy_check_mark: | |cite{PIDA} |
|Signor | 7 | 10 | 17,400 | :heavy_check_mark:  |  :heavy_check_mark:  | |cite{SIGNOR} |
|SIAD | 3,744 | 5,049 | 0 |  :heavy_check_mark:  |  :heavy_check_mark:  | |cite{SIAD} |
|VirHostNet | 332 | 494 | 47,182 |  :heavy_check_mark:  |  :heavy_check_mark:  | |cite{VirHostNet} |
|Web of Life database | 172 | 1,007 | 0 | X  |    :heavy_check_mark: | |cite{WOF, WOF_hompage} |


BV-BRC
- Bat Eco-Interactions
- BioGRID
- Database of Interacting Proteins (DIP) 
- The Enhanced Infectious Diseases (EID2)
- Fusarium graminearum species complex database (FGSCdb)
- Global Biotic Interactions (GloBI)
- Global Mammal Parasite Database (GMPD) 
- Host-pathogen interactions database (HPIDB) 
- IntAct 
- Interactome of co-evolving viruses with humans (https://doi.org/10.1093/molbev/msad012)
- Interaction Web Database (IWDB) 
- MINT
- Species Interactions of Australia Database (SIAD)
- Signaling Network Open Resource (Signor)
- PHI-base
- Pathogen-Host Interaction Search Tool (PHISTO) 
- PHILM2Web
- Protist Interaction DAtabase (PIDA)
- Virus / Host protein-protein interactions Network (VirHostNet) 
- Web of Life database

# Cite
- Contact:
- ```
   Reference
   ```
