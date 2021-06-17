"""Inspect population trends for every capital in Brazil."""
from pathlib import Path

import matplotlib.pyplot as plt

from src.assets_utils import (
    CapitalProperty,
    brazil_capitals_df_from_csv,
    parse_population_values,
    population_df_from_csv,
)
from src.utils import default_parser


def plot_population_trend(assets_dir: Path, outputs_dir: Path):
    """Plot the population trend for all capitals from 1980 to 2020."""
    population_df = population_df_from_csv(assets_dir)
    brazil_capitals_df = brazil_capitals_df_from_csv(
        assets_dir, usecols={CapitalProperty.NAME}
    )
    fig, ax = plt.subplots(figsize=(10, 10))
    for county_code, population in population_df.iterrows():
        capital_name = brazil_capitals_df.loc[county_code].squeeze()
        population_values = parse_population_values(population)
        ax.plot(
            population_values.index,
            population_values,
            label=capital_name,
        )
    ax.legend()
    fig.savefig(outputs_dir / "population_trends.pdf")


if __name__ == "__main__":
    parser = default_parser()
    plot_population_trend(**vars(parser.parse_args()))
