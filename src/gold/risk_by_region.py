import pandas as pd
from src.common.logger import get_logger
from src.common.paths import GOLD_RISK_FILE, SILVER_FILE

logger = get_logger(__name__)

def build_risk_by_region(df: pd.DataFrame) -> pd.DataFrame:
    valid = df.dropna(
        subset=[
            "location_region",
            "risk_score",
        ]
    )

    result = (
        valid
        .groupby(
            "location_region",
            as_index=False,
        )
        .agg(
            average_risk_score=(
                "risk_score",
                "mean",
            )
        )
        .sort_values(
            by=[
                "average_risk_score",
                "location_region",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .reset_index(drop=True)
    )

    result["average_risk_score"] = (
        result["average_risk_score"]
        .round(2)
    )

    return result

def create_risk_by_region() -> None:
    logger.info(
        "Iniciando criação da Gold: risco médio por região."
    )

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo Silver não encontrado: {SILVER_FILE}"
        )

    df = pd.read_parquet(
        SILVER_FILE
    )

    result = build_risk_by_region(
        df
    )

    GOLD_RISK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_parquet(
        GOLD_RISK_FILE,
        index=False,
    )

    logger.info(
        "Gold risco por região gerada com %s registros.",
        len(result),
    )

    logger.info(
        "Arquivo salvo em: %s",
        GOLD_RISK_FILE,
    )

    logger.info(
        "\n%s",
        result.to_string(index=False),
    )

if __name__ == "__main__":
    create_risk_by_region()