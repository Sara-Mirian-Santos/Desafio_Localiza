import pandas as pd
from src.common.logger import get_logger
from src.common.paths import GOLD_ADDRESS_FILE, SILVER_FILE

logger = get_logger(__name__)

def build_top_receiving_addresses(
    df: pd.DataFrame,
) -> pd.DataFrame:

    sales = df.loc[
        df["transaction_type"].eq("sale")
    ].copy()

    sales = sales.dropna(
        subset=[
            "receiving_address",
            "timestamp",
        ]
    )

    # Guardamos a ordem original para desempate determinístico.
    sales["_row_order"] = range(len(sales))

    # Primeiro: pega a venda mais recente por receiving_address.
    latest_sales = (
        sales
        .sort_values(
            by=[
                "receiving_address",
                "timestamp",
                "_row_order",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .drop_duplicates(
            subset=["receiving_address"],
            keep="first",
        )
    )

    # Só depois de escolher a venda mais recente
    # removemos casos em que amount não pode ser usado no ranking.
    latest_sales = latest_sales.dropna(
        subset=["amount"]
    )

    # Agora ordenamos pelos maiores valores.
    result = (
        latest_sales
        .sort_values(
            by=[
                "amount",
                "receiving_address",
            ],
            ascending=[
                False,
                True,
            ],
        )
        .head(3)
        [
            [
                "receiving_address",
                "amount",
                "timestamp",
            ]
        ]
        .reset_index(drop=True)
    )

    return result

def create_top_receiving_addresses() -> None:
    logger.info(
        "Iniciando criação da Gold: top receiving addresses."
    )

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo Silver não encontrado: {SILVER_FILE}"
        )

    df = pd.read_parquet(
        SILVER_FILE
    )

    result = build_top_receiving_addresses(
        df
    )

    GOLD_ADDRESS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_parquet(
        GOLD_ADDRESS_FILE,
        index=False,
    )

    logger.info(
        "Gold top receiving addresses gerada com %s registros.",
        len(result),
    )

    logger.info(
        "Arquivo salvo em: %s",
        GOLD_ADDRESS_FILE,
    )

    logger.info(
        "\n%s",
        result.to_string(index=False),
    )

if __name__ == "__main__":
    create_top_receiving_addresses()