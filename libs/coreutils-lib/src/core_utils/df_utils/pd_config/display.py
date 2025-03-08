from __future__ import annotations

import logging
from pathlib import Path
import typing as t

import pandas as pd

log = logging.getLogger(__name__)

__all__ = ["set_pandas_display_opts"]


def set_pandas_display_opts(
    max_rows: int | None = 60,
    max_columns: int | None = 20,
    max_colwidth: int | None = 50,
    max_width: int | None = None,
) -> None:
    """Set Pandas display options.

    Params:
        max_rows (int|None): Max number of rows to show in a dataframe. None=infinite
        max_columns (int|None): Max number of columns to show in a dataframe. Truncated columns appear as: |...|. None=infinite
        max_colwidth (int|None): Number of characters before truncating text. None=infinite
        max_width (int|None): Maximum width of the entire console display in characters. If None, Pandas adjusts display automatically.
    """
    log.debug(
        f"""Pandas options:
max_rows: {max_rows}
max_columns: {max_columns}
max_colwidth: {max_colwidth}
max_width: {max_width}
"""
    )
    pd.set_option("display.max_rows", max_rows)
    pd.set_option("display.max_columns", max_columns)
    pd.set_option("display.max_colwidth", max_colwidth)
    pd.set_option("display.width", max_width)
