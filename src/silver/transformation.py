import pandas as pd
from src.common.logger import get_logger
from src.common.paths import BRONZE_FILE, SILVER_FILE

logger = get_logger(__name__)

VALID_REGIONS = {
    "North America",
    "South America",
    "Europe",
    "Asia",
    "Africa",
}

def transform_silver() -> None:
    logger.info("Iniciando transformação da camada Silver.")

    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo Bronze não encontrado: {BRONZE_FILE}"
        )

    df = pd.read_parquet(BRONZE_FILE)

    logger.info(
        "Bronze carregada com %s registros.",
        len(df),
    )

    # Remove metadados técnicos da Bronze.
    df = df.drop(
        columns=[
            "_source_file",
            "_ingestion_timestamp",
        ],
        errors="ignore",
    )

    # Padroniza campos textuais.
    text_columns = [
        "sending_address",
        "receiving_address",
        "transaction_type",
        "location_region",
        "purchase_pattern",
        "age_group",
        "anomaly",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].str.strip()

    # Padroniza transaction_type.
    df["transaction_type"] = (
        df["transaction_type"]
        .str.lower()
    )

    # Converte amount para número.
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    # Converte risk_score para número.
    df["risk_score"] = pd.to_numeric(
        df["risk_score"],
        errors="coerce",
    )

    # Converte timestamp Unix para datetime UTC.
    df["timestamp"] = pd.to_datetime(
        pd.to_numeric(
            df["timestamp"],
            errors="coerce",
        ),
        unit="s",
        errors="coerce",
        utc=True,
    )

    # Regiões fora do domínio conhecido passam a ser nulas.
    df.loc[
        ~df["location_region"].isin(VALID_REGIONS),
        "location_region",
    ] = pd.NA

    # Remove somente duplicidades exatas.
    df = df.drop_duplicates()

    SILVER_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        SILVER_FILE,
        index=False,
    )

    logger.info(
        "Silver gerada com %s registros.",
        len(df),
    )

    logger.info(
        "Camada Silver salva em: %s",
        SILVER_FILE,
    )

if __name__ == "__main__":
    transform_silver()