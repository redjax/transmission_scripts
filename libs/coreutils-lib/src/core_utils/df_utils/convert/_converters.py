from __future__ import annotations

import logging
from pathlib import Path
import typing as t

import pandas as pd

log = logging.getLogger(__name__)

from ..io.save import save_csv, save_json, save_pq
from ..io.load import load_csv, load_json, load_pq, load_pqs_to_df, load_sql

__all__ = [
    "convert_csv_to_pq",
    "convert_pq_to_csv",
    "convert_df_col_dtypes",
    "convert_df_datetimes_to_timestamp",
]


def convert_csv_to_pq(
    csv_file: t.Union[str, Path] = None,
    pq_file: t.Union[str, Path] = None,
    dedupe: bool = False,
) -> bool:
    """Read a CSV file into a DataFrame, then write the DataFrame to a Parquet file.

    Params:
        csv_file (str|Path): Path to a CSV file to read from
        pq_file (str|Path): Path to a Parquet file to write to
        dedupe (bool): Whether to run .drop_duplicates() on the DataFrame

    Returns:
        (bool): `True` if `csv_file` is converted to `pq_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised instead of returning
            a bool value

    """
    if csv_file is None:
        raise ValueError("Missing a CSV input file to read from")
    if pq_file is None:
        raise ValueError("Missing a Parquet file to save to")

    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if not csv_file.exists():
        raise FileNotFoundError(f"Could not find input CSV file at path: {csv_file}")

    try:
        df = load_csv(csv_file=csv_file)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading CSV file '{csv_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)

        raise exc

    try:
        success = save_pq(df=df, pq_file=pq_file, dedupe=dedupe)

        return success

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception writing DataFrame to file: {pq_file}. Details: {exc}"
        )
        log.error(msg)

        raise exc


def convert_pq_to_csv(
    pq_file: t.Union[str, Path] = None,
    csv_file: t.Union[str, Path] = None,
    dedupe: bool = False,
) -> bool:
    """Read a Parquet file into a DataFrame, then write the DataFrame to a CSV file.

    Params:
        pq_file (str|Path): Path to a Parquet file to read from
        csv_file (str|Path): Path to a CSV file to write to
        dedupe (bool): Whether to run .drop_duplicates() on the DataFrame

    Returns:
        (bool): `True` if `pq_file` is converted to `csv_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised instead of returning
            a bool value

    """
    if csv_file is None:
        raise ValueError("Missing a CSV file to save to")
    if pq_file is None:
        raise ValueError("Missing an input Parquet file to read from")

    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if not pq_file.exists():
        raise FileNotFoundError(f"Could not find input Parquet file at path: {pq_file}")

    try:
        df = load_pq(pq_file=pq_file)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading Parquet file '{pq_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)

        raise exc

    try:
        success = save_csv(df=df, csv_file=csv_file, columns=df.columns, dedupe=dedupe)

        return success

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception writing DataFrame to file: {csv_file}. Details: {exc}"
        )
        log.error(msg)

        raise exc


def convert_df_col_dtypes(df: pd.DataFrame, dtype_mapping: dict) -> pd.DataFrame:
    """Converts the specified columns in a DataFrame to the given data types.

    Params:
        df (pd.DataFrame): The input DataFrame.
        dtype_mapping (dict): A dictionary where keys are column names and values are the target data types.

    Returns:
        pd.DataFrame: The DataFrame with converted column types.

    """
    try:
        return df.astype(dtype_mapping)
    except KeyError as e:
        raise ValueError(f"Column not found: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid data type conversion: {e}")


def convert_df_datetimes_to_timestamp(df: pd.DataFrame):
    """Convert all datetime columns in the DataFrame to Unix timestamps (integers).

    Params:
    - df (pandas.DataFrame): The DataFrame to be processed.

    Returns:
    - pandas.DataFrame: The DataFrame with all datetime columns converted to timestamps.

    """
    # Iterate over each column in the DataFrame
    for column in df.columns:
        # Check if the column contains datetime-like data
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            # Convert datetime to Unix timestamp (number of seconds since epoch)
            df[column] = df[column].apply(
                lambda x: int(x.timestamp()) if pd.notnull(x) else None
            )

    return df
