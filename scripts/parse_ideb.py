"""Process raw data with approval rates, SAEB grades, IDEB and projections.

Source:
    https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados.
"""
import argparse
from enum import Enum
from pathlib import Path

import pandas as pd

from src.consts import (
    BRAZILIAN_CAPITALS_FILENAME,
    IDEB_INFO_PER_COUNTY_FILENAME,
)


class EducationNetwork(Enum):
    """Types of education networks in the raw IDEB data."""

    PUBLIC = "Pública"
    STATE = "Estadual"
    COUNTY = "Municipal"

    def __str__(self) -> str:
        return str(self.value)


def export_ideb_data(
    assets_dir: Path, outputs_dir: Path, network: EducationNetwork
) -> None:
    """Export IDEB scores for each state's capital."""
    ideb_df = pd.read_excel(
        assets_dir / IDEB_INFO_PER_COUNTY_FILENAME,
        engine="odf",
        index_col=[0, 1],
        usecols="B,D,CG:CN",
        skipfooter=3,
        skiprows=lambda r: r <= 9 and r != 6,  # Keep 7th row to use as a header
    )
    brazil_info_series = pd.read_csv(
        assets_dir / BRAZILIAN_CAPITALS_FILENAME,
        usecols=[0],
        squeeze=True,
    )
    network_list = [network.value] * len(brazil_info_series)
    ideb_capital_indices = list(zip(brazil_info_series, network_list))
    ideb_capital_df = ideb_df.loc[ideb_capital_indices]
    ideb_capital_df.index = ideb_capital_df.index.droplevel("Rede")
    ideb_capital_df.to_csv(
        outputs_dir / f"ideb_capitals_{network.name.lower()}.csv"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--assets_dir",
        default="assets",
        type=Path,
        help="Directory to look for required assets.",
    )
    parser.add_argument(
        "--outputs_dir",
        default="outputs",
        type=Path,
        help="Directory to export processed data.",
    )
    parser.add_argument(
        "--network",
        default=EducationNetwork.PUBLIC,
        type=EducationNetwork,
        choices=list(EducationNetwork),
        help="Type of education network results we wish to export data for.",
    )
    export_ideb_data(**vars(parser.parse_args()))
