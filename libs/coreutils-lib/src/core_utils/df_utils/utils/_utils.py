from __future__ import annotations

import logging
from pathlib import Path
import typing as t

import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "hide_df_index",
    "rename_df_cols",
    "sort_df_by_col",
    "get_oldest_newest",
]


def hide_df_index(df: pd.DataFrame) -> pd.DataFrame:
    """Hide the Pandas index when previewing, i.e. with .head().

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to hide the index.

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` with the index hidden

    """
    ## Create index of empty strings for each row in the dataframe
    blank_index = [""] * len(df)
    ## Set the dataframe's index to the list of empty strings
    df.index = blank_index

    return df


def rename_df_cols(
    df: pd.DataFrame = None, col_rename_map: dict[str, str] = None
) -> pd.DataFrame:
    """Return a DataFrame with columns renamed based on input col_rename_map.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` with columns to rename
            col_rename_map (dict[str, str]): A Python `dict` defining existing column names and the value
            they should be renamed to.

    Returns:
        (pandas.DataFrame): A renamed Pandas `DataFrame`.

    """
    if col_rename_map is None:
        msg = ValueError("No col_rename_map passed")
        log.warning(msg)

        return df

    if df is None or df.empty:
        msg = ValueError("Missing DataFrame, or DataFrame is empty")
        log.error(msg)

        raise ValueError(msg)

    try:
        df = df.rename(columns=col_rename_map)

        return df
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception renaming DataFrame columns. Details: {exc}"
        )
        log.error(msg)

        raise exc


def sort_df_by_col(df: pd.DataFrame, col_name: str, order: str = "asc") -> pd.DataFrame:
    """Sorts a Pandas DataFrame by a specified column in ascending or descending order.

    Params:
        df (pd.DataFrame): The DataFrame to sort.
        col_name (str): The column name to sort by.
        order (str): The sorting order, "asc" for ascending (default) or "desc" for descending.

    Returns:
        pd.DataFrame: The sorted DataFrame.

    """
    if col_name not in df.columns:
        raise ValueError(f"Column '{col_name}' not found in DataFrame.")
    if order not in ["asc", "desc"]:
        raise ValueError("Order must be 'asc' or 'desc'.")

    ## Set ascending=True if order="asc" else False
    ascending = order == "asc"

    return df.sort_values(by=col_name, ascending=ascending)


def get_oldest_newest(
    df: pd.DataFrame = None, date_col: str = None, filter_cols: list[str] | None = None
) -> t.Union[pd.Series, pd.DataFrame]:
    """Get the oldest and newest rows in a DataFrame.

    Params:
        df (pd.DataFrame): Pandas DataFrame to work on
        date_col (str): Name of the column to sort by
        filter_cols (list[str]): List of column names to return with the oldest/newest record.

    Returns:
        (pandas.Series|pandas.DataFrame): A Pandas `DataFrame` or `Series` containing oldest & newest records
        in the input `DataFrame`.

    """
    if df is None or df.empty:
        raise ValueError("Missing or empty DataFrame")
    if date_col is None:
        raise ValueError("Missing name of date column to sort by")

    try:
        min_date = df[date_col].min()
        oldest = df.loc[df[date_col] == min_date]

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting min date value from column [{date_col}]. Details: {exc}"
        )
        log.error(msg)

        raise exc

    try:
        max_date = df[date_col].max()
        newest = df.loc[df[date_col] == max_date]

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting max date value from column [{date_col}]. Details: {exc}"
        )
        log.error(msg)

        raise exc

    if filter_cols is not None:
        try:
            oldest = oldest[filter_cols]
            newest = newest[filter_cols]
        except Exception as exc:
            msg = Exception(f"Unhandled exception filtering columns. Details: {exc}")
            log.error(msg)

            raise exc

    return oldest, newest
