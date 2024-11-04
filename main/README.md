# Parameter description:
Attention: Please do not change any parameter, not listed here if you are uncertain. Instead please contact [us](../README.md#authors) for help!
- `export tempory_directory="/etc/ISDB"`: \
`/etc/ISDB` describes the path in which all data during and after the building process is stored.
- `export overwrite=false`: \
If set `false` existing already processed sources will be reused, else if set on `true` each database is cleaned and processed from scratch.
- `export addtional_data=""`: \
`""` describes the path to a CSV file or a directory containing CSV files which should also be included during the aggregation process. If path is set to `""` no additional files are included.
- `delete=false`: \
If set `false` already processed intermediate files are kept, else if set on `true` intermediated files are removed. Removing of intermediated files also leads to cleaning and processing each database from scratch on the next execution. 
- `manualDatabases=false`: \
If set `false` databases which must be downloaded by the user are not considered, else if set on `true` files are moved from the path specified by the user the expected directory.
    - After the following statement the user should specify the path the manual downloaded sources: \
    `if $manualDatabases; then` 
    - For each of the following lines the User should only adjust `$tempory_directory/manualDownload/<UserFilename>` according to the name of the downloaded database: \
    `mv $tempory_directory/manualDownload/<UserFilename> $tempory_directory/<ExpectedFilename>`
- By commenting any of the following stages the User can only rerun specify ones:
    ```
    ### Download files 
    bash ../utils/downloadDB.sh
    # ### Clean files
    python ../utils/processDB.py
    # ### Build DB
    python ../utils/aggregateDB.py
    ```