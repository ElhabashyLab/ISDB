# General
- **`builtDB.sh`** main script for execution of the pipeline. For execution please see [here](../README.md#building-isdb-locally).
- **`config.env`** config file in which to adjust parameters
## Parameter description
Attention: Please do not change any parameter, not listed here if you are uncertain. Instead please contact [us](../README.md#authors) for help!

1. **`OUT_DIRECTORY`** — Directory in which ISDB is built.  
2. Decide which steps to (re)run
    1. **`DOWNLOAD`** — Whether to download files from scratch (`true` / `false`).  
    2. **`PROCESS`** — Whether to process downloaded files (`true` / `false`).  
    3. **`AGGREGATE`** — Whether to summon processed files (`true` / `false`).  
3. **`OVERWRITE`** — Whether to overwrite existing stages (`true` / `false`).  
3. **`ADDITIONAL_DATA`** — Path to an additional data file or directory containing multiple files. Each file must include at least two species columns. Please make sure [columns](../README.md#how-to-build-isdb-locally) are correctly named.
4. **`DELETE`** — Whether to delete intermediate files after build (`true` / `false`).  
5. **`MANUAL_DATABASES`** — Include databases that cannot be downloaded automatically  (`true` / `false`). If true, paths must be specified. 
6. **`SOURCE_DIR`** — Directory where manual downloaded files are stored.
7. File and directory names for manual downloaded databases. Names should match the ones of your downloaded files otherwise files won't be found.
    1. **`BATECO_FILE`**
    1. **`PHISTO_FILE`**
    1. **`PHILM2WEB_FILE`**
    1. **`FGSCDB_FILE`**
    1. **`BVBRC_DIR`**
    1. **`DIP_DIR`**
    1. **`GMPD_DIR`**
8. File and directory names for automatic downloaded databases. Names should **only** be **adjusted** if **names change**. 
    1. **`GLOBI_FILE`**
    1. **`INTACT_FILE`**
    1. **`PHI_BASE_FILE`**
    1. **`EID2_FILE`**
    1. **`SIAD_FILE`**
    1. **`MINT_FILE`**
    1. **`SIGNOR_FILE`**
    1. **`HIPIDB_DIR`**
    1. **`BIOGRID_DIR`**
    1. **`WEB_OF_LIFE_DATABASE_DIR`**
    1. **`HPIDB_DIR`**
    1. **`IWDB_DIR`**
    1. **`PMC9897028_DIR`**
9. URLs from which databases are downloaded. URLs should **only** be **adjusted** if **names change**. 
    1. **`BIOGRID_URL`**
    1. **`WEB_OF_LIFE_URL`**
    1. **`GLOBI_URL`**
    1. **`HPIDB_URL`**
    1. **`INTACT_URL`**
    1. **`PHI_BASE_URL`**
    1. **`PIDA_URL`**
    1. **`VIRHOSTNET_URL`**
    1. **`EID2_URL`**
    1. **`SIAD_URL`**
    1. **`MINT_URL`**
    1. **`PMC9897028_URL`**
