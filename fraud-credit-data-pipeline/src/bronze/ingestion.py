from datetime import datetime, timezone
import pandas as pd
from src.common.logger import get_logger
from src.common.paths import BRONZE_FILE, LANDING_FILE

logger = get_logger(__name__)

def ingest_bronze() -> None:
    logger.info("Iniciando ingestão da camada Bronze.")

    if not LANDING_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {LANDING_FILE}"
        )

    df = pd.read_csv(
        LANDING_FILE,
        dtype=str,
    )

    logger.info(
        "Arquivo carregado com %s registros e %s colunas.",
        len(df),
        len(df.columns),
    )

    df["_source_file"] = LANDING_FILE.name
    df["_ingestion_timestamp"] = datetime.now(timezone.utc)

    BRONZE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        BRONZE_FILE,
        index=False,
    )

    logger.info(
        "Camada Bronze salva em: %s",
        BRONZE_FILE,
    )

if __name__ == "__main__":
    ingest_bronze()