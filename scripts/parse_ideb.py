"""Process raw data with approval rates, SAEB grades, IDEB and projections.

Source:
    https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados.
"""
import re
from pathlib import Path
from typing import List

from src.assets_utils import (
    EducationNetwork,
    SchoolLevel,
    brazil_capitals_df_from_csv,
    ideb_capital_csv_filename,
    ideb_df_from_ods,
)
from src.utils import default_parser


def export_ideb_data(
    assets_dir: Path,
    outputs_dir: Path,
    school_levels: List[SchoolLevel],
    networks: List[EducationNetwork],
) -> None:
    """Export IDEB scores for each state's capital."""
    for school_level in school_levels:
        ideb_df = ideb_df_from_ods(assets_dir, school_level)
        brazil_capitals_df = brazil_capitals_df_from_csv(assets_dir)
        brazil_capitals_series = brazil_capitals_df.squeeze()
        for network in networks:
            network_list = [network.value] * len(brazil_capitals_series)
            ideb_capital_indices = list(
                zip(brazil_capitals_series, network_list)
            )

            # Ignore missing indices by only keeping the intersection.
            ideb_capital_indices = ideb_df.index.intersection(
                ideb_capital_indices
            )

            ideb_capital_df = ideb_df.loc[ideb_capital_indices]
            ideb_capital_df.index = ideb_capital_df.index.droplevel("Rede")
            ideb_capital_df.columns = [
                re.findall(r"\d+", col)[0] for col in ideb_capital_df.columns
            ]

            ideb_capital_df.to_csv(
                outputs_dir / ideb_capital_csv_filename(school_level, network)
            )


if __name__ == "__main__":
    parser = default_parser()
    parser.add_argument(
        "--school_levels",
        nargs="+",
        default=[SchoolLevel.HIGH],
        type=SchoolLevel,
        choices=list(SchoolLevel),
        help="School levels we wish to export data for.",
    )
    parser.add_argument(
        "--networks",
        nargs="+",
        default=[EducationNetwork.PUBLIC],
        type=EducationNetwork,
        choices=list(EducationNetwork),
        help="Type of education network results we wish to export data for.",
    )
    export_ideb_data(**vars(parser.parse_args()))
