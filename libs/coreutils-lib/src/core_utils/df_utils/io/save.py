from __future__ import annotations

import logging
from pathlib import Path
import typing as t

import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "save_pq",
    "save_csv",
    "save_json",
]


def save_pq(
    df: pd.DataFrame = None,
    pq_file: t.Union[str, Path] = None,
    dedupe: bool = False,
    pq_engine: str = "pyarrow",
) -> bool:
    """Save DataFrame to a .parquet file.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to save
        pq_file (str|Path): The path to a `.parquet` file where the `DataFrame` should be saved
        dedupe (bool): If `True`, deduplicate the `DataFrame` before saving

    Returns:
        (bool): `True` if `DataFrame` is saved to `pq_file` successfully
        (bool): `False` if `DataFrame` is not saved to `pq_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised

    """
    if df is None or df.empty:
        msg = ValueError("DataFrame is None or empty")
        log.warning(msg)

        return False

    if pq_file is None:
        raise ValueError("Missing output path")
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if pq_file.suffix != ".parquet":
        new_str = str(f"{pq_file}.parquet")
        pq_file: Path = Path(new_str)

    if not pq_file.parent.exists():
        try:
            pq_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory: {pq_file.parent}. Details: {exc}"
            )
            log.error(msg)

            return False

    try:
        if dedupe:
            df = df.drop_duplicates()

        output = df.to_parquet(path=pq_file, engine=pq_engine)

        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to Parquet file: {pq_file}. Details: {exc}"
        )
        log.error(msg)
        raise exc


def save_csv(
    df: pd.DataFrame = None,
    csv_file: t.Union[str, Path] = None,
    columns: list[str] = None,
    dedupe: bool = False,
) -> bool:
    """Save DataFrame to a .csv file.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to save
        csv_file (str|Path): The path to a `.csv` file where the `DataFrame` should be saved
        columns (list[str]): A list of string values representing column names for the `.csv` file
        dedupe (bool): If `True`, deduplicate the `DataFrame` before saving

    Returns:
        (bool): `True` if `DataFrame` is saved to `csv_file` successfully
        (bool): `False` if `DataFrame` is not saved to `csv_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised

    """
    if df is None or df.empty:
        msg = ValueError("DataFrame is None or empty")

        return False

    if csv_file is None:
        raise ValueError("Missing output path")
    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)

    if csv_file.suffix != ".csv":
        new_str = str(f"{csv_file}.csv")
        csv_file: Path = Path(new_str)

    if not csv_file.parent.exists():
        try:
            csv_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory: {csv_file.parent}. Details: {exc}"
            )
            log.error(msg)

            return False

    if columns is None:
        columns = df.columns

    try:
        if dedupe:
            df = df.drop_duplicates()

        if columns is not None:
            output = df.to_csv(csv_file, columns=columns)
        else:
            output = df.to_csv(csv_file)

        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to Parquet file: {csv_file}. Details: {exc}"
        )
        log.error(msg)
        raise exc


def save_json(
    df: pd.DataFrame = None,
    json_file: t.Union[str, Path] = None,
    indent: int | None = None,
) -> bool:
    """Save DataFrame to a .json file.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to save
        json_file (str|Path): The path to a `.json` file where the `DataFrame` should be saved

    Returns:
        (bool): `True` if `DataFrame` is saved to `json_file` successfully
        (bool): `False` if `DataFrame` is not saved to `json_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised

    """
    if df is None or df.empty:
        msg = ValueError("DataFrame is None or empty")
        log.warning(msg)

        return False

    if json_file is None:
        raise ValueError("Missing output path")
    if isinstance(json_file, str):
        json_file: Path = Path(json_file)

    if json_file.suffix != ".json":
        new_str = str(f"{json_file}.json")
        json_file: Path = Path(new_str)

    if not json_file.parent.exists():
        try:
            json_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory: {json_file.parent}. Details: {exc}"
            )
            log.error(msg)

            return False

    try:
        df.to_json(json_file, orient="records", indent=indent)
        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to JSON file: {json_file}. Details: {exc}"
        )
        log.error(msg)
        raise exc
