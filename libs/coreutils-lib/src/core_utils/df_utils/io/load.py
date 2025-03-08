from __future__ import annotations

import logging
from pathlib import Path
import typing as t

import pandas as pd
import sqlalchemy as sa

log = logging.getLogger(__name__)

__all__ = [
    "load_pqs_to_df",
    "load_pq",
    "load_csv",
    "load_json",
    "load_sql",
]


def load_pqs_to_df(
    search_dir: str = None, filetype: str = ".parquet"
) -> list[pd.DataFrame]:
    """Load data export files in search_dir into list of DataFrames.

    Params:
        search_dir (str): The directory to search for files in
        filetype (str): The file extension to filter results by

    Returns:
        (list[pandas.DataFrame]): A list of Pandas `DataFrame`s created from files in `search_dir`

    """
    if search_dir is None:
        raise ValueError("Missing a directory to search")

    if not filetype.startswith("."):
        filetype = f".{filetype}"

    files: list[Path] = []

    for f in Path(search_dir).glob(f"**/*{filetype}"):
        if f.is_file():
            files.append(f)

    dataframes: list[pd.DataFrame] = []

    if filetype == ".parquet":
        for pq in files:
            df = load_pq(pq_file=pq)

            dataframes.append(df)

    elif filetype == ".csv":
        for f in files:
            df = pd.read_csv(f)

            dataframes.append(df)

    return dataframes


def load_pq(
    pq_file: t.Union[str, Path] = None, pq_engine: str = "pyarrow"
) -> pd.DataFrame:
    """Return a DataFrame from a previously saved .parquet file.

    Params:
        pq_file (str|Path): Path to a `.parquet` file to load

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` loaded from a `.parquet` file

    """
    if pq_file is None:
        raise ValueError("Missing pq_file to load")
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if not pq_file.suffix == ".parquet":
        pq_file: Path = Path(f"{pq_file}.parquet")

    if not pq_file.exists():
        msg = FileNotFoundError(f"Could not find Parquet file at '{pq_file}'")
        # log.error(msg)
        log.error(msg)

        raise exc

    try:
        df = pd.read_parquet(pq_file, engine=pq_engine)

        return df

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading Parquet file '{pq_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)

        raise exc


def load_csv(csv_file: t.Union[str, Path] = None, delimiter: str = ",") -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Params:
        csv_file (str|Path): The path to a `.csv` file to load into a `DataFrame
        delimiter (str): The delimiter symbol the `csv_file` uses

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` with data loaded from the `csv_file`

    """
    if csv_file is None:
        raise ValueError("Missing output path")

    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)

    if csv_file.suffix != ".csv":
        new_str = str(f"{csv_file}.csv")
        csv_file: Path = Path(new_str)

    if not csv_file.exists():
        msg = FileNotFoundError(f"Could not find CSV file: '{csv_file}'.")
        log.error(msg)
        raise exc

    try:
        df = pd.read_csv(csv_file, delimiter=delimiter)

        return df

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading DataFrame from CSV file: {csv_file}. Details: {exc}"
        )
        log.error(msg)

        raise exc


def load_json(json_file: t.Union[str, Path] = None) -> pd.DataFrame:
    """Load a JSON file into a DataFrame.

    Params:
        json_file (str|Path): The path to a `.json` file to load into a `DataFrame`

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` loaded from the `json_file`

    Raises:
        Exception: If file cannot be loaded, an `Exception` is raised

    """
    if json_file is None:
        raise ValueError("Missing input file to load")

    if isinstance(json_file, str):
        json_file: Path = Path(json_file)

    if not json_file.exists():
        msg = FileNotFoundError(f"Could not find JSON file at '{json_file}'")
        log.error(msg)
        raise exc

    try:
        df = pd.read_json(json_file, orient="records")
        return df

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading JSON file '{json_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)
        raise exc


def load_sql(table_name: str, db_engine: sa.Engine):
    if not db_engine:
        log.error("Missing a SQLAlchemy Engine object")
        return
    if not table_name:
        log.error("Missing a database table name")
        return

    log.debug(f"Detected database dialect: {db_engine.dialect.name}")
    log.info(f"Reading table into DataFrame: {table_name}")
    try:
        df: pd.DataFrame = pd.read_sql_table(table_name=table_name, con=db_engine)

        return df
    except Exception as exc:
        msg = f"({type(exc)}) error"
        log.error(msg)

        raise exc
