"""Find interesting correlations between data."""
from math import ceil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

from src.assets_utils import (
    EducationNetwork,
    SchoolLevel,
    ideb_capital_csv_filename,
    ideb_capital_df_from_csv,
)
from src.consts import HOMICIDES_PER_CAPITA_PER_CAPITAL_FILENAME
from src.utils import default_parser


def plot_linear_regression_ideb_vs_homicides(
    ax: mpl.axes.Axes,
    ideb_for_year: pd.Series,
    homicides_for_year: pd.Series,
    ideb_year: int,
    homicide_year: int,
) -> None:
    """Plot linear regression between IDEB scores and homicides on `ax`."""
    x, y = ideb_for_year, homicides_for_year
    res = linregress(x, y)

    # Plot the raw data points.
    ax.scatter(x, y, alpha=0.7)

    # Plot best fit line.
    x_lb, x_ub = ax.get_xlim()
    uniform_xs = np.linspace(x_lb, x_ub, num=10)
    ax.plot(
        uniform_xs,
        res.intercept + res.slope * uniform_xs,
        linestyle="-.",
        linewidth=1,
        color="r",
        label=rf"$y = {res.slope:.1f} \pm {res.stderr:.1f} \cdot x + "
        rf"{res.intercept:.1f} \pm {res.intercept_stderr:.1f}$",
    )
    ax.set_xlabel(f"IDEB {ideb_year}")
    ax.set_ylabel(f"Homicides per 100,000 for {homicide_year}")
    ax.annotate(
        f"$R^2 = {res.rvalue:.3f}$",
        xy=(0.03, 0.9),
        xycoords="axes fraction",
    )
    ax.legend(loc="upper right")


def correlate_ideb_with_homicides(
    outputs_dir: Path,
    school_level: SchoolLevel = SchoolLevel.MIDDLE,
    network: EducationNetwork = EducationNetwork.PUBLIC,
) -> None:
    """Correlate IDEB data for `school_level` and `network` with homicides."""
    homicides_per_capita_df = pd.read_pickle(
        outputs_dir / HOMICIDES_PER_CAPITA_PER_CAPITAL_FILENAME
    )
    ideb_capital_df = ideb_capital_df_from_csv(
        outputs_dir, school_level, network
    )
    ideb_capital_df.columns = ideb_capital_df.columns.astype(np.int64)
    for ideb_year in ideb_capital_df:
        ideb_capital_for_year = ideb_capital_df[ideb_year]
        ideb_capital_for_year.dropna(inplace=True)

        homicides_per_capita_from_years = homicides_per_capita_df.loc[
            ideb_capital_for_year.index, ideb_year:
        ]

        num_plots = homicides_per_capita_from_years.shape[1]

        if not num_plots:
            continue

        nrows = ceil(num_plots / 2)
        fig, axes = plt.subplots(
            nrows=nrows, ncols=2, figsize=(10, nrows * 3), squeeze=False
        )
        for idx, homicide_year in enumerate(homicides_per_capita_from_years):
            ax = axes[idx // 2, idx % 2]
            homicides_per_capita_for_year = homicides_per_capita_from_years[
                homicide_year
            ]
            plot_linear_regression_ideb_vs_homicides(
                ax,
                ideb_capital_for_year,
                homicides_per_capita_for_year * 1e5,
                ideb_year,
                homicide_year,
            )
        fig.tight_layout()
        fig.savefig(
            outputs_dir
            / "correlation_ideb_{}_{}_{}_vs_homicide.pdf".format(
                ideb_year,
                school_level.name.lower(),
                network.name.lower(),
            )
        )
        plt.close(fig)


def correlate(assets_dir: Path, outputs_dir: Path) -> None:
    """Plot correlations between relevant data."""
    for school_level in SchoolLevel:
        for network in EducationNetwork:
            ideb_filepath = outputs_dir / ideb_capital_csv_filename(
                school_level, network
            )
            if ideb_filepath.is_file():
                correlate_ideb_with_homicides(
                    outputs_dir, school_level, network
                )


if __name__ == "__main__":
    parser = default_parser()
    correlate(**vars(parser.parse_args()))
