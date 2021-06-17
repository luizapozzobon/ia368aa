"""Compute and export homicides per capita data."""
from functools import partial
from numbers import Real
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd

from src.assets_utils import (
    homicides_df_from_csv,
    parse_population_values,
    population_df_from_csv,
)
from src.consts import HOMICIDES_PER_CAPITA_PER_CAPITAL_FILENAME
from src.utils import default_parser


def convert_value_range(
    num: np.ndarray,
    range1: Tuple[Real, Real],
    range2: Tuple[Real, Real],
) -> np.ndarray:
    """Convert the domain of a value `num` from `range1` to `range2`."""
    ratio = (num - range1[0]) / (range1[1] - range1[0])
    return range2[0] + ratio * (range2[1] - range2[0])


def generate_year_to_pop_fn(
    population: pd.Series,
) -> Callable[[np.ndarray], np.ndarray]:
    """Return a function that linearly interpolates year to population."""

    # Available anchors that we'll use to interpolate intermediate years.
    years = np.array(population.index)

    # Generate funclist that linearly interpolates
    funclist = []
    for year_lb, year_ub in zip(years[:-1], years[1:]):
        pop_lb, pop_ub = population[[year_lb, year_ub]]
        funclist.append(
            partial(
                convert_value_range,
                range1=(year_lb, year_ub),
                range2=(pop_lb, pop_ub),
            )
        )

    def piecewise_fn(year_req: np.ndarray) -> np.ndarray:
        """Return the interpolated population for the requested years."""
        years = np.expand_dims(population.index, -1)

        assert np.logical_and(
            min(years) <= year_req, year_req <= max(years)
        ).all(), f"At least one requested year in {year_req} is out of range."

        condlist = np.logical_and(years[:-1] <= year_req, year_req <= years[1:])

        return np.piecewise(year_req, condlist, funclist)

    return piecewise_fn


def export_homicides_per_capita(assets_dir: Path, outputs_dir: Path) -> None:
    """Plot the population trend for all capitals from 1980 to 2020."""
    population_df = population_df_from_csv(assets_dir)
    homicides_df = homicides_df_from_csv(assets_dir)
    homicides_df.columns = homicides_df.columns.astype(np.int64)
    homicides_per_capita_dict: Dict[str, List[Real]] = {}
    for county_code, population_per_year in population_df.iterrows():
        population_per_year = parse_population_values(
            population_per_year, min_year=2000
        )

        # Create function that estimates population for current county.
        year_to_pop_fn = generate_year_to_pop_fn(population_per_year)

        # Retrieve absolute number of homicides.
        homicides_per_year = homicides_df.loc[county_code]

        # Estimate population in the years we have homicide data for.
        homicide_years = np.array(homicides_per_year.index, dtype=np.int64)
        homicide_years_population = year_to_pop_fn(homicide_years)

        # Compute average number of homicides per person for each year.
        homicides_per_capita = homicides_per_year / homicide_years_population

        homicides_per_capita_dict[county_code] = homicides_per_capita

    homicides_per_capita_df = pd.DataFrame.from_dict(
        homicides_per_capita_dict, orient="index"
    )
    homicides_per_capita_df.index.name = homicides_df.index.name
    homicides_per_capita_df.to_pickle(
        outputs_dir / HOMICIDES_PER_CAPITA_PER_CAPITAL_FILENAME
    )


if __name__ == "__main__":
    parser = default_parser()
    export_homicides_per_capita(**vars(parser.parse_args()))
