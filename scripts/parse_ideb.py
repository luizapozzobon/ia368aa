"""Process raw data with approval rates, SAEB grades, IDEB and projections.

Source:
    https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados.
"""
import re
from pathlib import Path
from typing import List

from tqdm import tqdm

from src.assets_utils import (
    CapitalProperty,
    EducationNetwork,
    SchoolLevel,
    brazil_capitals_df_from_csv,
    ideb_capital_csv_filename,
    ideb_df_from_ods,
)
from src.utils import default_parser


def export_ideb_capital_data(
    assets_dir: Path,
    outputs_dir: Path,
    only_capitals: bool,
    school_levels: List[SchoolLevel],
    networks: List[EducationNetwork],
) -> None:
    """Export IDEB scores for each state's capital."""
    brazil_capitals_df = brazil_capitals_df_from_csv(assets_dir)
    brazil_capitals_index = brazil_capitals_df.index
    for school_level in tqdm(school_levels, position=0, desc="School levels"):
        ideb_df = ideb_df_from_ods(assets_dir, school_level)
        for network in tqdm(networks, position=1, desc="Education Networks"):
            network_list = [network.value] * len(brazil_capitals_index)
            ideb_capital_indices = list(
                zip(brazil_capitals_index, network_list)
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


def export_all_ideb_data(
    assets_dir: Path,
    outputs_dir: Path,
    only_capitals: bool,
    school_levels: List[SchoolLevel],
    networks: List[EducationNetwork],
) -> None:
    """Export IDEB scores for each state's capital."""

    def keep_year(col):
        return re.findall(r"\d+", col)

    brazil_capitals_df = brazil_capitals_df_from_csv(
        assets_dir,
        set(CapitalProperty).difference({CapitalProperty.COUNTY_CODE}),
    ).set_index(CapitalProperty.STATE_ABBREV.value)

    for school_level in tqdm(school_levels, position=0, desc="School levels"):
        ideb_df = ideb_df_from_ods(assets_dir, school_level)
        for network in tqdm(networks, position=1, desc="Education Networks"):
            ideb_network_df = ideb_df.query("Rede == @network.value")

            ideb_network_df.columns = [
                keep_year(col)[0] if keep_year(col) else col
                for col in ideb_network_df.columns
            ]

            ideb_network_df["Regiões"] = (
                ideb_network_df.reset_index()["Sigla da UF"]
                .apply(
                    lambda x: brazil_capitals_df.loc[x][
                        CapitalProperty.REGION.value
                    ]
                )
                .values
            )

            ideb_network_df.to_csv(
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

    parser.add_argument(
        "--only_capitals",
        default=False,
        type=bool,
        help="If True, export only capitals' scores, else all cities'.",
    )

    if parser.parse_args().only_capitals:
        print("Only capitals.")
        export_ideb_capital_data(**vars(parser.parse_args()))
    else:
        export_all_ideb_data(**vars(parser.parse_args()))
