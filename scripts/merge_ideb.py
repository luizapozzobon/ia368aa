"""Merge parsed ideb data.

Source:
    https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados.
"""
from pathlib import Path
from typing import List

import pandas as pd

from src.assets_utils import (
    EducationNetwork,
    SchoolLevel,
    ideb_capital_df_from_csv,
    ideb_merged_to_csv,
)
from src.utils import default_parser


def merge_ideb_data(
    assets_dir: Path,
    outputs_dir: Path,
    school_levels: List[SchoolLevel],
    networks: List[EducationNetwork],
):
    """Merge ideb data."""
    for level in school_levels:
        dfs = []
        for network in networks:
            df = ideb_capital_df_from_csv(outputs_dir, level, network)
            melted = df.reset_index().melt(
                id_vars=[
                    "Código do Município",
                    "Sigla da UF",
                    "Regiões",
                    "Nome do Município",
                    "Rede",
                ],
                value_vars=[col for col in df.columns if col.isnumeric()],
                var_name="Ano",
                value_name="IDEB",
            )
            dfs.append(melted)

        ideb = pd.concat(dfs).reset_index(drop=True)

        ideb_merged_to_csv(ideb, outputs_dir, level)


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
    merge_ideb_data(**vars(parser.parse_args()))
