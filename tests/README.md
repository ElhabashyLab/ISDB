# Instruction on how to run the tests
1) Clone GitHub repository:
```
clone https://github.com/ElhabashyLab/ISDB.git
cd ISDB/tests/
```
2) Install ``requirements.txt``:

e.g. via conda:
```
conda create --name <my-env>
conda activate <my-env>
pip install -r requirements.txt
```
e.g. only via pip:
```
pip install -r requirements.txt
```
3) Run tests:
    - ``test_uniprot_api.py``: 
    ```
    python -m unittest test_uniprot_api.py
    ```
    - ``test_processDB.py``
    ```
    python -m unittest test_processDB.py
    ```
    - ``test_aggregateDB.py``:
    ```
    python -m unittest test_aggregateDB.py
    ```
