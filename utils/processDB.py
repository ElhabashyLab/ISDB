"""
Script for processing data from each database.

Please do not change code here.
Changes should only be done it file paths
if users know what they are doing.
"""

import pandas as pd
import numpy as np
from dotenv import load_dotenv
import re
import sys
import os
import requests
import yaml

sys.path.insert(1, "./")
from uniprot_api import uniprot_request
from helper import *
from helper_processDB import *


def check_and_process_db(
    dir: str,
    name: str,
    process_func: callable,
    overwrite: bool,
    tmp_dir: str,
    uniprot: uniprot_request,
) -> str:
    """
    Executues cleaning process of a database
    """
    exception = None
    try:
        file_exists(dir, tmp_dir, overwrite)
        print(f"# Processing {name}")
        if not check_out_exists(name.lower(), tmp_dir) or overwrite:
            process_func(dir, name, tmp_dir, uniprot)
    except Exception as e:
        exception = f"# {name}\n"
        exception += str(e)
    return exception


def main():
    print("### Processing data ###")
    uniprot = uniprot_request()
    exceptions = []
    # load environment variables from config.env
    load_dotenv("config.env")
    overwrite = True if os.getenv("OVERWRITE") == "true" else False
    out_directory = os.getenv("OUT_DIRECTORY")

    for env, name in env2name.items():
        func_name = f"clean_{name.lower()}"
        dir = os.getenv(env)

        # Get the function object from globals()
        func: callable = globals()[func_name]

        # Run functions
        exception = check_and_process_db(
            dir, name, func, overwrite, out_directory, uniprot
        )
        if exception is not None:
            exceptions.append(exception)

    if exceptions:
        with open("stderr.txt", "w") as f:
            f.write("\n".join(exceptions))


if __name__ == "__main__":
    main()
