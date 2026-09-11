import json
import pandas as pd
from src.common.logger import get_logger
from src.common.paths import SILVER_FILE, SILVER_REPORT

logger = get_logger(__name__)

VALID_REGIONS = {
    "North America",
    "South America",
    "Europe",
    "Asia",
    "Africa",
}

def validate_silver() -> dict:
    logger.info("Iniciando validação da camada Silver.")

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo Silver não encontrado: {SILVER_FILE}"
        )

    df = pd.read_parquet(SILVER_FILE)

    total_records = len(df)

    logger.info(
        "Validando %s registros.",
        total_records,
    )

    # -------------------------
    # Duplicidades
    # -------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    # -------------------------
    # Nulos resultantes da limpeza
    # -------------------------

    null_amount = int(
        df["amount"].isna().sum()
    )

    null_risk_score = int(
        df["risk_score"].isna().sum()
    )

    null_location_region = int(
        df["location_region"].isna().sum()
    )

    null_timestamp = int(
        df["timestamp"].isna().sum()
    )

    # -------------------------
    # Domínio de região
    # -------------------------

    invalid_region = int(
        (
            df["location_region"].notna()
            & ~df["location_region"].isin(VALID_REGIONS)
        ).sum()
    )

    # -------------------------
    # Tipos esperados
    # -------------------------

    amount_is_numeric = pd.api.types.is_numeric_dtype(
        df["amount"]
    )

    risk_score_is_numeric = pd.api.types.is_numeric_dtype(
        df["risk_score"]
    )

    timestamp_is_datetime = (
        pd.api.types.is_datetime64_any_dtype(
            df["timestamp"]
        )
    )

    # -------------------------
    # Verifica strings inválidas remanescentes
    # -------------------------

    invalid_amount_text = int(
        df["amount"]
        .astype("string")
        .str.lower()
        .isin(["none", "null", "nan"])
        .sum()
    )

    invalid_risk_text = int(
        df["risk_score"]
        .astype("string")
        .str.lower()
        .isin(["none", "null", "nan"])
        .sum()
    )

    # -------------------------
    # Status das regras
    # -------------------------

    checks = {
        "no_duplicate_rows": duplicate_rows == 0,
        "amount_numeric": bool(amount_is_numeric),
        "risk_score_numeric": bool(risk_score_is_numeric),
        "timestamp_datetime": bool(timestamp_is_datetime),
        "valid_location_region_domain": invalid_region == 0,
        "no_invalid_amount_text": invalid_amount_text == 0,
        "no_invalid_risk_score_text": invalid_risk_text == 0,
    }

    failed_checks = [
        check
        for check, passed in checks.items()
        if not passed
    ]

    report = {
        "layer": "silver",
        "total_records": total_records,
        "status": (
            "PASSED"
            if not failed_checks
            else "FAILED"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "null_values": {
            "amount": null_amount,
            "risk_score": null_risk_score,
            "location_region": null_location_region,
            "timestamp": null_timestamp,
        },
        "errors": {
            "duplicate_rows": duplicate_rows,
            "invalid_location_region": invalid_region,
            "invalid_amount_text": invalid_amount_text,
            "invalid_risk_score_text": invalid_risk_text,
        },
    }

    SILVER_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        SILVER_REPORT,
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
        "Data Quality Silver concluído."
    )

    logger.info(
        "Status: %s",
        report["status"],
    )

    logger.info(
        "Relatório salvo em: %s",
        SILVER_REPORT,
    )

    if failed_checks:
        raise ValueError(
            f"Falha nas validações Silver: {failed_checks}"
        )

    return report

if __name__ == "__main__":
    validate_silver()