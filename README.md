# The Interacting Species Database (ISDB)
A Comprehensive Resource for Ecological Interactions at the Molecular Level.
The ISDB compiles data on species interactions from 21 resources, including scientific names, Taxon IDs, UniProt IDs, interaction types, ontology identifiers, references, and original database sources. ISDB is developed using Python and Bash scripts and is available as an open-source under the MIT License.

# Web interface
ISDB web interface can be found here (www.elhabashylab.org/isdb) which is hosted by the German Network for Bioinformatics Infrastructure (de.NBI).
The web interface provides functionalities for batch downloads, data search, result download, and data deposition.

# How to download ISDB? 
Built versions of ISDB can be found under the directory `versions` and be downloaded either through GitHubs user-interface, the ISDB web interface, or through command line via:
```
wget https://github.com/ElhabashyLab/ISDB/tree/main/versions/ISDB_2024_09_13.<tsv/csv>.gz
```


# How to build ISDB locally? 
To build and run **ISDB** locally, please follow these steps:

1. **Ensure internet connectivity**
     
   Make sure your computer is connected to the internet.

3. **Clone the repository and navigate into it**
   
   ```bash
   git clone https://github.com/ElhabashyLab/ISDB.git
   cd ISDB
   ```
   
4. **Set up the Python environment**
   
   ISDB requires Python 3.11.7 or more
   If your local Python version differs, we recommend creating a dedicated Conda environment:
    ```bash
   conda create --name isdb_env python=3.11.7
   conda activate isdb_env
   ```

5. **Install Dependencies**
   
   ISDB depends on the following Python packages:
   * biopython 1.79
   * click 8.1.3
   * matplotlib 3.6.3
   * pandas 1.5.3
   * requests 2.28.2
   * numpy==1.23.5
     
   You can install all required dependencies with:
   ```bash
     pip install -r requirements.txt
   ```

 6. **Download Resources**
    
    To download the required databases, run the provided script:
    
    ```bash
    bash downloadDB.sh
    ```

    ISDB automatically parses most of the databases. However, a few resources must be downloaded manually from their respective websites:
   
    - Bat Eco-Interactions (https://www.batbase.org/explore)
    - BV-BRC (https://www.bv-brc.org)
    - DIP (https://dip.doe-mbi.ucla.edu/dip/)
    - GMPD (https://parasites.nunn-lab.org/data/)
    - PHILM2Web (https://phim2web.lailab.info/pages/index.html)
    - PHISTO (https://www.phisto.org/browse.xhtml)
    - FGSCdb (https://edelponte.shinyapps.io/FGSCdb/)


  7. **Edit Build Parameters**
   
     After downloading the required databases, edit the paths and parameters in the `main/buildDB.sh` script.  
     The following parameters can be customized:

     a. **`temporary_directory`** — Directory in which ISDB is built.  
     b. **`overwrite`** — Whether to overwrite pre-existing stages (`true` / `false`).  
     c. **`additional_data`** — File or directory path containing additional data files.  
        Each file must include at least **two species columns**.  
     d. **`delete`** — Whether intermediate stages should be deleted after the build (`true` / `false`).  
     e. **`manualDatabases`** — Include or exclude databases that cannot be downloaded automatically.  
        If set to `true`, the user must specify their paths in the section below.

   
   1. `tempory_directory`: Direction in which ISDB is build,
   2. `overwrite`: Wether to overwrite pre-existing stages,
   3. `addtional_data`: File path or directory path of additional data files. Each file should at least include two species columns,
   4. `delete`: If intermediate stages should be deleted afterwards,
   5. `manualDatabases`: Exclude or include database which could not be downloaded automatically. If 'true' the user has specify their paths in the following section.


8. **Build the ISDB Database**  

   To compile the ISDB database locally, execute the main build script from within the `main` directory:

   ```bash
   cd main
   bash buildDB.sh
   ```

   
Additional parameters, such as whether to overwrite existing files, remove intermediate files, or incorporate user-provided data, can also be configured within this script. More details can be found on the documentation on GitHub.

The generated database will be available in CSV and TSV formats, with the following column descriptions:
- `Serial Number`: Interaction identifier inside ISDB
- `Taxonomy ID (A/B)`: NCBI Taxonomical identifer
- `Organism (A/B)`: Sientifc species name
- `UniProt ID (A/B)`: UniProt protein identifier
- `Protein Name (A/B)`: UniProt protein name 
- `Interaction Type`: Phrase describing the interaction
- `Ontology ID`: Interaction identifier of the coresponding ontology
- `Reference`: Reference as defined by data source
- `Database`: Databank source of the interaction


# How to deposite data to the ISDB?

To submit data for inclusion in our system, please contact our [team](#authors) directly. To incorporate your own data into the database locally please follow the instruction on [*How to build ISDB locally?*](#how-to-build-isdb-locally)

# List of resources 

The database can be built automatically. However, some resources need to be downloaded manually. This includes:

| Database | #Species | #Specie Pairs | #PPIs | Interaction Type | Batch download  |
|----------|--|--|--|--|--|
| [Bat Eco-Interactions](https://www.batbase.org/)| 3,099 | 8,101 | 0 |   :heavy_check_mark: |  X  | 
|[BioGRID](https://thebiogrid.org/) | 83 | 359 | 2,228,610 | X  |  :heavy_check_mark:  | 
|[BV-BRC](https://www.bv-brc.org/) | 133,835 | 142,666 | 0 | X  |   X  | 
|[Database of Interacting Proteins (DIP)](https://dip.doe-mbi.ucla.edu/dip/Main.cgi) | 210 | 423 | 73,852 |  :heavy_check_mark:  |   X  | 
|[The Enhanced Infectious Diseases (EID2)](https://eid2.liverpool.ac.uk/) | 12,486 | 18,086 | 0 |  :heavy_check_mark:  |  :heavy_check_mark: | 
|[Fusarium graminearum species complex database (FGSCdb)](https://emdelponte.github.io/FGSC/#:~:text=FGSCdb%20is%20a%20database%20of,and%20panicle%20blight%20in%20rice.) | 19 | 15 | 0 |  :heavy_check_mark:  |   X  |  
|[Global Biotic Interactions (GloBI)](https://www.globalbioticinteractions.org/) | 89,994 | 461,385 | 0 | :heavy_check_mark:  |  :heavy_check_mark:  |
|[Global Mammal Parasite Database (GMPD)](https://parasites.nunn-lab.org/data/) | 1,558 | 5,444 | 0 | X  |  X  |  
|[Host-pathogen interactions database (HPIDB)](https://hpidb.igbb.msstate.edu/)  | 734 | 967 | 54,879 | :heavy_check_mark:  |  :heavy_check_mark:  |  
|[IntAct](https://www.ebi.ac.uk/intact/home) | 1,819 | 3,575 | 1,079,255 | :heavy_check_mark:  |  :heavy_check_mark:  | 
|[Interactome](https://pubmed.ncbi.nlm.nih.gov/36649176/) | 264 | 263 | 4,154 | :heavy_check_mark:  | :heavy_check_mark:  | 
|[Interaction Web Database (IWDB)](https://iwdb.nceas.ucsb.edu/whoweare.html) | 594 | 3,449 | 0 | X  | X  | 
|[MINT](https://mint.bio.uniroma2.it/) | 698 | 1,331 | 100,048 | :heavy_check_mark:  |  :heavy_check_mark:  |  
|[PHI-base](http://www.phi-base.org/) | 539 | 1,062 | 0 | X  |  :heavy_check_mark:  |  
|[PHILM2Web](http://philm2web.live/) | 460 | 1,506 | 0 | :heavy_check_mark:  |  X  |  
|[Pathogen-Host Interaction Search Tool (PHISTO)](https://www.phisto.org/browse.xhtml)  | 589 | 589 | 47,920 | X  |  X  | |cite{PHISTO} |
|[Protist Interaction DAtabase (PIDA)](https://github.com/ramalok/PIDA) | 647 | 836 | 0 | X  |  :heavy_check_mark: |  
|[Signaling Network Open Resource (Signor)](https://signor.uniroma2.it/) | 7 | 10 | 17,400 | :heavy_check_mark:  |  :heavy_check_mark:  | 
|[Species Interactions of Australia Database (SIAD)](https://www.discoverlife.org/siad/) | 3,744 | 5,049 | 0 |  :heavy_check_mark:  |  :heavy_check_mark:  |  
|[Virus / Host protein-protein interactions Network (VirHostNet)](https://virhostnet.prabi.fr/)  | 332 | 494 | 47,182 |  :heavy_check_mark:  |  :heavy_check_mark:  |  
|[Web of Life database](https://www.web-of-life.es/) | 172 | 1,007 | 0 | X  |    :heavy_check_mark: |  




# Cite
Mederer, M., Gautam, A., Kohlbacher, O., Lupas, A., Elhabashy, H. Interacting Species Database (ISDB): A Comprehensive Resource for Ecological Interactions at the Molecular Level. Manuscript in preparation.

# Authors
- Michael Mederer
- Anupam Gautam
- Hadeer Elhabashy

# Contact
If you have any questions or inquiries, please feel free to contact Hadeer Elhabashy at (Elhabashylab [@] gmail.com))

# License
- The **ISDB code** in this repository is licensed under the [MIT License](./LICENSE).
  
Shield: [![CC BY 4.0][cc-by-shield]][cc-by]
- This **ISDB database** in the versions/ folder is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
