"""Utility methods to process assets datasets."""
from enum import Enum
from pathlib import Path
from typing import Set

import numpy as np
import pandas as pd

from src.consts import (
    BRAZILIAN_CAPITALS_FILENAME,
    HOMICIDES_PER_CAPITAL_FILENAME,
    IDEB_CAPITALS_FILENAME_FORMAT,
    IDEB_SCHOOL_FILENAME_FORMAT,
    POPULATION_PER_CAPITAL_FILENAME,
)


def population_df_from_csv(assets_dir: Path) -> pd.DataFrame:
    """Retrieve population dataframe from csv file."""
    population_df = pd.read_csv(
        assets_dir / POPULATION_PER_CAPITAL_FILENAME,
        index_col=0,
        na_values="...",
    )
    population_df.drop("Capital", axis=1, inplace=True)
    return population_df


def parse_population_values(
    population: pd.Series,
    min_year: int = 1872,
    max_year: int = 2020,
) -> pd.Series:
    """Parse population values after `year` (inclusive).

    Args:
        population: Series with population per year, where year is the str index
            of the series and population is represented as str with '.' as the
            thousands separator.
        min_year: The minimum year after which we wish to include population
            data.
        max_year: The maximum year after which we wish to include population
            data.

    Returns:
        A series with the parsed series of integer population values for
        relevant years.

    Raises:
        KeyError: If either min_year or max_year are not a valid year in the
            dataset.
    """
    # Keep only relevant years from series.
    population.index = population.index.astype(np.int64)
    population = population.loc[min_year:max_year]

    # Drop any remaining NaN values.
    population = population.dropna()

    # Cast series values to integers using pt_BR locale.
    cast_population = population.apply(
        lambda obj: int(str(obj).replace(".", ""))
    )
    return cast_population


class CapitalProperty(Enum):
    """Available properties for each capital in the csv dataset."""

    COUNTY_CODE = "Código"
    NAME = "Capitais"
    STATE = "Estados"
    STATE_ABBREV = "Siglas dos Estados"
    REGION = "Regiões"


def brazil_capitals_df_from_csv(
    assets_dir: Path, usecols: Set[CapitalProperty] = None
) -> pd.DataFrame:
    """Retrieve Brazilian capitals info dataframe from csv file."""
    if usecols is not None:
        assert CapitalProperty.COUNTY_CODE not in usecols, (
            "The county code property is always used as an index, so it's "
            "added to usecols by default."
        )
    else:
        usecols = set()

    usecol_names = [col.value for col in usecols]
    usecol_names = [CapitalProperty.COUNTY_CODE.value] + usecol_names

    brazil_capitals_df = pd.read_csv(
        assets_dir / BRAZILIAN_CAPITALS_FILENAME,
        usecols=usecol_names,
        index_col=0,
    )
    return brazil_capitals_df


def homicides_df_from_csv(assets_dir: Path) -> pd.DataFrame:
    """Retrieve capitals number of homicides dataframe from csv file."""
    homicides_df = pd.read_csv(
        assets_dir / HOMICIDES_PER_CAPITAL_FILENAME,
        index_col=1,
    )
    homicides_df.drop(["Sigla", "Município"], axis=1, inplace=True)
    return homicides_df


class SchoolLevel(Enum):
    """Different school levels for raw IDEB data."""

    ELEMENTARY = "anos_iniciais"
    MIDDLE = "anos_finais"
    HIGH = "ensino_medio"

    def __str__(self) -> str:
        return str(self.value)


class EducationNetwork(Enum):
    """Types of education networks in the raw IDEB data."""

    PUBLIC = "Pública"
    FEDERAL = "Federal"
    STATE = "Estadual"
    COUNTY = "Municipal"

    def __str__(self) -> str:
        return str(self.value)


def ideb_column_range(school_level: SchoolLevel) -> str:
    """Return the respective column range for IDEB data."""
    if school_level is SchoolLevel.ELEMENTARY:
        return "CG:CN"
    if school_level is SchoolLevel.MIDDLE:
        return "BY:CF"
    if school_level is SchoolLevel.HIGH:
        return "W:X"
    raise NotImplementedError(
        f"No column range specified for school level {school_level.name}."
    )


def ideb_df_from_ods(
    assets_dir: Path, school_level: SchoolLevel
) -> pd.DataFrame:
    """Return IDEB data for all counties and the given `school_level`."""
    ideb_df = pd.read_excel(
        assets_dir / IDEB_SCHOOL_FILENAME_FORMAT.format(school_level.value),
        engine="odf",
        index_col=[0, 1],
        usecols="A,B,C,D," + ideb_column_range(school_level),
        skipfooter=3,
        skiprows=lambda r: r <= 9 and r != 6,  # Keep 7th row as header.
    )
    return ideb_df


def ideb_capital_csv_filename(
    school_level: SchoolLevel, network: EducationNetwork
) -> Path:
    """Return the IDEB capital csv filename."""
    return Path(
        IDEB_CAPITALS_FILENAME_FORMAT.format(
            school_level.name.lower(), network.name.lower()
        )
    )


def ideb_capital_df_from_csv(
    outputs_dir: Path, school_level: SchoolLevel, network: EducationNetwork
) -> pd.DataFrame:
    """Return IDEB data for Brazilian capitals."""
    ideb_capital_df = pd.read_csv(
        outputs_dir / ideb_capital_csv_filename(school_level, network),
        index_col=0,
        na_values="-",
    )
    return ideb_capital_df


def ideb_merged_to_csv(
    ideb_merged: pd.DataFrame, outputs_dir: Path, school_level: SchoolLevel
):
    """Save totally parsed ideb file."""
    ideb_merged.to_csv(
        outputs_dir / f"ideb_merged_{school_level.name.lower()}.csv"
    )
