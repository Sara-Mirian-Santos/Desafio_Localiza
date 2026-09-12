import json
import pandas as pd
from src.common.logger import get_logger

from src.common.paths import (
    GOLD_ADDRESS_FILE,
    GOLD_REPORT,
    GOLD_RISK_FILE,
    SILVER_FILE,
)

logger = get_logger(__name__)

def validate_gold() -> dict:
    logger.info("Iniciando validação da camada Gold.")

    required_files = [
        SILVER_FILE,
        GOLD_RISK_FILE,
        GOLD_ADDRESS_FILE,
    ]

    for file_path in required_files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {file_path}"
            )

    silver = pd.read_parquet(SILVER_FILE)

    risk_by_region = pd.read_parquet(
        GOLD_RISK_FILE
    )

    top_addresses = pd.read_parquet(
        GOLD_ADDRESS_FILE
    )

    # --------------------------------
    # GOLD 1 - risco médio por região
    # --------------------------------

    risk_expected_columns = {
        "location_region",
        "average_risk_score",
    }

    risk_columns_ok = (
        set(risk_by_region.columns)
        == risk_expected_columns
    )

    risk_null_values = int(
        risk_by_region[
            [
                "location_region",
                "average_risk_score",
            ]
        ]
        .isna()
        .sum()
        .sum()
    )

    risk_score_numeric = (
        pd.api.types.is_numeric_dtype(
            risk_by_region[
                "average_risk_score"
            ]
        )
    )

    risk_sorted_desc = (
        risk_by_region[
            "average_risk_score"
        ]
        .is_monotonic_decreasing
    )

    risk_unique_regions = (
        risk_by_region[
            "location_region"
        ]
        .is_unique
    )

    # --------------------------------
    # GOLD 2 - top receiving address
    # --------------------------------

    address_expected_columns = {
        "receiving_address",
        "amount",
        "timestamp",
    }

    address_columns_ok = (
        set(top_addresses.columns)
        == address_expected_columns
    )

    top_3_count = len(top_addresses) == 3

    unique_addresses = (
        top_addresses[
            "receiving_address"
        ]
        .is_unique
    )

    address_null_values = int(
        top_addresses[
            [
                "receiving_address",
                "amount",
                "timestamp",
            ]
        ]
        .isna()
        .sum()
        .sum()
    )

    amount_numeric = (
        pd.api.types.is_numeric_dtype(
            top_addresses["amount"]
        )
    )

    amount_sorted_desc = (
        top_addresses["amount"]
        .is_monotonic_decreasing
    )

    # --------------------------------
    # Validação da regra "latest sale"
    # --------------------------------

    sales = silver.loc[
        silver["transaction_type"].eq(
            "sale"
        )
    ].copy()

    sales = sales.dropna(
        subset=[
            "receiving_address",
            "timestamp",
        ]
    )

    latest_sale_validation = True

    for _, row in top_addresses.iterrows():
        address = row["receiving_address"]
        gold_timestamp = row["timestamp"]

        address_sales = sales.loc[
            sales["receiving_address"].eq(
                address
            )
        ]

        expected_timestamp = (
            address_sales[
                "timestamp"
            ]
            .max()
        )

        if gold_timestamp != expected_timestamp:
            latest_sale_validation = False
            break

    # --------------------------------
    # Checks
    # --------------------------------

    checks = {
        "risk_columns_ok": risk_columns_ok,
        "risk_no_null_values": (
            risk_null_values == 0
        ),
        "risk_score_numeric": bool(
            risk_score_numeric
        ),
        "risk_sorted_desc": bool(
            risk_sorted_desc
        ),
        "risk_unique_regions": bool(
            risk_unique_regions
        ),
        "address_columns_ok": (
            address_columns_ok
        ),
        "address_top_3_count": (
            top_3_count
        ),
        "address_unique": (
            unique_addresses
        ),
        "address_no_null_values": (
            address_null_values == 0
        ),
        "amount_numeric": bool(
            amount_numeric
        ),
        "amount_sorted_desc": bool(
            amount_sorted_desc
        ),
        "latest_sale_rule": (
            latest_sale_validation
        ),
    }

    failed_checks = [
        check
        for check, passed in checks.items()
        if not passed
    ]

    report = {
        "layer": "gold",
        "status": (
            "PASSED"
            if not failed_checks
            else "FAILED"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "datasets": {
            "risk_by_region": {
                "total_records": len(
                    risk_by_region
                ),
                "null_values": (
                    risk_null_values
                ),
            },
            "top_receiving_addresses": {
                "total_records": len(
                    top_addresses
                ),
                "null_values": (
                    address_null_values
                ),
            },
        },
    }

    GOLD_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        GOLD_REPORT,
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
        "Data Quality Gold concluído."
    )

    logger.info(
        "Status: %s",
        report["status"],
    )

    logger.info(
        "Relatório salvo em: %s",
        GOLD_REPORT,
    )

    if failed_checks:
        raise ValueError(
            f"Falha nas validações Gold: {failed_checks}"
        )

    return report

if __name__ == "__main__":
    validate_gold()