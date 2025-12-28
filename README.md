# The Interacting Species Database (ISDB)
A Comprehensive Resource for Ecological Interactions at the Molecular Level.
The ISDB compiles data on species interactions from 21 resources, including scientific names, Taxon IDs, UniProt IDs, interaction types, ontology identifiers, references, and original database sources. ISDB is developed using Python and Bash scripts and is available as an open-source under the MIT License.
#![Figure description](mainFigure_04_04_25.svg)

<p align="center">
  <img src="mainFigure_04_04_25.svg" alt="Figure description" width=\linewidth>
</p>
<p align="center"><em>Figure 1.  (A) Flowchart outlining the key steps in ISDB creation, including data retrieval, standardization, taxonomy annotation, and aggregation. (B–D) Ring diagrams illustrating (B) the proportional distribution of species by superkingdom, (C) the classification of species interactions according to superkingdom, and (D) the predominant interaction types categorized by keywords. (E) Example of an ecological network depicting interconnected species within ISDB.</em></p>

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
 
    Before downloading, **please update the path where the resources will be stored** in the `downloadDB.sh` script.
    Set the directory by editing the following variable:
    ```bash
    DATA_DIR="<path where the resources will be stored>"
    ```
    
    To download the required databases, then run the provided script:
    
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

   
   a.`tempory_directory`: Direction in which ISDB is build,
   b. `overwrite`: Wether to overwrite pre-existing stages,
   c. `addtional_data`: File path or directory path of additional data files. Each file should at least include two species columns,
   d. `delete`: If intermediate stages should be deleted afterwards,
   e. `manualDatabases`: Exclude or include database which could not be downloaded automatically. If 'true' the user has specify their paths in the following section.



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
| Database | #Species | #Species Pairs | #PPIs | Interaction Type | Batch Download | Database Type | 
|----------|-----------|----------------|-------|-----------------|----------------|---------------|
| [BioGRID](https://thebiogrid.org/) | 86 | 260 | 1,905,211 | ✔ | ✔ | M |
| [IntAct](https://www.ebi.ac.uk/intact/home) | 1,806 | 2,855 | 942,611 | ✔ | ✔ | M | 
| [MINT](https://mint.bio.uniroma2.it/) | 697 | 1,018 | 79,223 | ✔ | ✔ | M | 
| [DIP](https://dip.doe-mbi.ucla.edu/dip/Main.cgi) | 193 | 270 | 39,422 | ✔ | ✔ | M | 
| [Signor](https://signor.uniroma2.it/) | 7 | 7 | 14,959 | ✔ | ✔ | M | 
| [VirHostNet](https://virhostnet.prabi.fr/) | 331 | 465 | 41,422 | ✔ | ✔ | HP/M |
| [PHISTO](https://www.phisto.org/) | 589 | 528 | 25,405 | ✔ | X | HP/M |
| [Interactomics](https://doi.org/10.1093/molbev/msad012) | 294 | 293 | 3,958 | ✔ | ✔ | HP/M | 
| [BV-BRC](https://www.bv-brc.org/) | 136,861 | 146,797 | 0 | X | X | HP |
| [EID2](https://eid2.liverpool.ac.uk/) | 12,428 | 17,927 | 0 | ✔ | ✔ | HP | 
| [GMPD](https://parasites.nunn-lab.org/) | 1,562 | 5,525 | 0 | X | X | HP | 
| [PHILM2Web](http://philm2web.live) | 411 | 1,167 | 0 | ✔ | X | HP | 
| [PHI-base](http://www.phi-base.org/) | 538 | 1,061 | 0 | X | ✔ | HP | 
| [HPIDB](https://hpidb.igbb.msstate.edu/) | 620 | 788 | 0 | ✔ | ✔ | HP | 
| [GloBI](https://www.globalbioticinteractions.org/) | 87,958 | 436,911 | 0 | ✔ | ✔ | E | 
| [Bat Eco-Interactions](https://www.batbase.org/db) | 3,094 | 8,080 | 0 | ✔ | X | E |
| [SIAD](https://www.discoverlife.org/siad/) | 3,732 | 5,028 | 0 | ✔ | ✔ | E |
| [IWDB](https://iwdb.nceas.ucsb.edu/resources.html) | 593 | 3,440 | 0 | X | ✔ | E |
| [Web of Life database](https://www.web-of-life.es/map.php) | 172 | 1,050 | 0 | X | ✔ | E | 
| [PIDA](https://github.com/ramalok/PIDA) | 598 | 757 | 0 | X | ✔ | E | 
| [FGSCdb](https://fgsc.netlify.app/) | 19 | 15 | 0 | ✔ | X | E | 



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
