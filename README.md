# The Interacting Species Database (ISDB)
This database gathers available information about possible species interactions from 21 resources.

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
|--|--|--|--|--|--|--|

BV-BRC
- Bat Eco-Interactions
- BioGRID
- Database of Interacting Proteins (DIP) 
- EID2 (host-pathogen)
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
