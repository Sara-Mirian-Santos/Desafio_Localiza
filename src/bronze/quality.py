import json
import pandas as pd
from src.common.logger import get_logger
from src.common.paths import BRONZE_FILE, BRONZE_REPORT

logger = get_logger(__name__)

EXPECTED_COLUMNS = {
    "timestamp",
    "sending_address",
    "receiving_address",
    "amount",
    "transaction_type",
    "location_region",
    "ip_prefix",
    "login_frequency",
    "session_duration",
    "purchase_pattern",
    "age_group",
    "risk_score",
    "anomaly",
}

VALID_REGIONS = {
    "North America",
    "South America",
    "Europe",
    "Asia",
    "Africa",
}

SOURCE_COLUMNS = list(EXPECTED_COLUMNS)

def validate_bronze() -> dict:
    logger.info("Iniciando validação da camada Bronze.")

    if not BRONZE_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo Bronze não encontrado: {BRONZE_FILE}"
        )

    df = pd.read_parquet(BRONZE_FILE)

    total_records = len(df)

    logger.info(
        "Validando %s registros.",
        total_records,
    )

    # -------------------------
    # Validação de schema
    # -------------------------

    columns = set(df.columns)

    missing_columns = sorted(
        EXPECTED_COLUMNS - columns
    )

    extra_columns = sorted(
        columns - EXPECTED_COLUMNS
    )

    # As duas colunas técnicas que criamos são esperadas na Bronze.
    allowed_technical_columns = {
        "_source_file",
        "_ingestion_timestamp",
    }

    unexpected_columns = sorted(
        set(extra_columns) - allowed_technical_columns
    )

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing_columns}"
        )

    # -------------------------
    # Duplicidades
    # -------------------------

    duplicate_rows = int(
        df[SOURCE_COLUMNS].duplicated().sum()
    )

    # -------------------------
    # Amount
    # -------------------------

    amount_numeric = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    invalid_amount = (
        amount_numeric.isna()
        & df["amount"].notna()
    )

    invalid_amount_count = int(
        invalid_amount.sum()
    )

    # -------------------------
    # Risk score
    # -------------------------

    risk_numeric = pd.to_numeric(
        df["risk_score"],
        errors="coerce",
    )

    invalid_risk_score = (
        risk_numeric.isna()
        & df["risk_score"].notna()
    )

    invalid_risk_score_count = int(
        invalid_risk_score.sum()
    )

    # -------------------------
    # Região
    # -------------------------

    invalid_region = (
        df["location_region"].notna()
        & ~df["location_region"].isin(
            VALID_REGIONS
        )
    )

    invalid_region_count = int(
        invalid_region.sum()
    )

    # -------------------------
    # Timestamp
    # -------------------------

    timestamp_numeric = pd.to_numeric(
        df["timestamp"],
        errors="coerce",
    )

    invalid_timestamp = (
        timestamp_numeric.isna()
        & df["timestamp"].notna()
    )

    invalid_timestamp_count = int(
        invalid_timestamp.sum()
    )

    # -------------------------
    # Campos obrigatórios
    # -------------------------

    missing_receiving_address = (
        df["receiving_address"].isna()
        | df["receiving_address"].str.strip().eq("")
    )

    missing_receiving_address_count = int(
        missing_receiving_address.sum()
    )

    missing_transaction_type = (
        df["transaction_type"].isna()
        | df["transaction_type"].str.strip().eq("")
    )

    missing_transaction_type_count = int(
        missing_transaction_type.sum()
    )

    # -------------------------
    # Erro por registro
    # -------------------------

    records_with_errors_mask = (
        df[SOURCE_COLUMNS].duplicated(keep=False)
        | invalid_amount
        | invalid_risk_score
        | invalid_region
        | invalid_timestamp
        | missing_receiving_address
        | missing_transaction_type
    )

    records_with_errors = int(
        records_with_errors_mask.sum()
    )

    if total_records > 0:
        error_rate_percentage = round(
            records_with_errors
            / total_records
            * 100,
            2,
        )

        conformity_percentage = round(
            (
                total_records
                - records_with_errors
            )
            / total_records
            * 100,
            2,
        )
    else:
        error_rate_percentage = 0.0
        conformity_percentage = 0.0

    # -------------------------
    # Relatório
    # -------------------------

    report = {
        "layer": "bronze",
        "total_records": total_records,
        "records_with_errors": records_with_errors,
        "error_rate_percentage": error_rate_percentage,
        "conformity_percentage": conformity_percentage,
        "schema": {
            "missing_columns": missing_columns,
            "unexpected_columns": unexpected_columns,
        },
        "errors": {
            "duplicate_rows": duplicate_rows,
            "invalid_amount": invalid_amount_count,
            "invalid_risk_score": invalid_risk_score_count,
            "invalid_location_region": invalid_region_count,
            "invalid_timestamp": invalid_timestamp_count,
            "missing_receiving_address": (
                missing_receiving_address_count
            ),
            "missing_transaction_type": (
                missing_transaction_type_count
            ),
        },
    }

    BRONZE_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        BRONZE_REPORT,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Data Quality Bronze concluído."
    )

    logger.info(
        "Registros com erro: %s",
        records_with_errors,
    )

    logger.info(
        "Conformidade: %s%%",
        conformity_percentage,
    )

    logger.info(
        "Relatório salvo em: %s",
        BRONZE_REPORT,
    )

    return report

if __name__ == "__main__":
    validate_bronze()