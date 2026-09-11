from src.bronze.ingestion import ingest_bronze
from src.bronze.quality import validate_bronze
from src.common.logger import get_logger
from src.gold.quality import validate_gold
from src.gold.risk_by_region import create_risk_by_region
from src.gold.top_receiving_addresses import (
    create_top_receiving_addresses,
)
from src.silver.quality import validate_silver
from src.silver.transformation import transform_silver

logger = get_logger(__name__)

def run_pipeline() -> None:
    logger.info("======================================")
    logger.info("Iniciando pipeline Fraud Credit")
    logger.info("======================================")

    logger.info("Etapa 1/7 - Ingestão Bronze")
    ingest_bronze()

    logger.info("Etapa 2/7 - Data Quality Bronze")
    validate_bronze()

    logger.info("Etapa 3/7 - Transformação Silver")
    transform_silver()

    logger.info("Etapa 4/7 - Data Quality Silver")
    validate_silver()

    logger.info("Etapa 5/7 - Gold risco por região")
    create_risk_by_region()

    logger.info(
        "Etapa 6/7 - Gold top receiving addresses"
    )
    create_top_receiving_addresses()

    logger.info("Etapa 7/7 - Data Quality Gold")
    validate_gold()

    logger.info("======================================")
    logger.info("Pipeline executada com sucesso.")
    logger.info("======================================")

if __name__ == "__main__":
    run_pipeline()