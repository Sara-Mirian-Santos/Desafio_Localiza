import pandas as pd
from src.gold.risk_by_region import build_risk_by_region
from src.gold.top_receiving_addresses import (
    build_top_receiving_addresses,
)

def test_risk_by_region_orders_by_average_desc():
    df = pd.DataFrame(
        {
            "location_region": [
                "Europe",
                "Europe",
                "Asia",
                "Asia",
            ],
            "risk_score": [
                50.0,
                70.0,
                80.0,
                100.0,
            ],
        }
    )

    result = build_risk_by_region(df)

    assert len(result) == 2

    assert result.iloc[0]["location_region"] == "Asia"
    assert result.iloc[0]["average_risk_score"] == 90.0

    assert result.iloc[1]["location_region"] == "Europe"
    assert result.iloc[1]["average_risk_score"] == 60.0


def test_risk_by_region_ignores_null_values():
    df = pd.DataFrame(
        {
            "location_region": [
                "Europe",
                "Europe",
                None,
            ],
            "risk_score": [
                50.0,
                None,
                100.0,
            ],
        }
    )

    result = build_risk_by_region(df)

    assert len(result) == 1

    assert result.iloc[0]["location_region"] == "Europe"
    assert result.iloc[0]["average_risk_score"] == 50.0


def test_top_receiving_addresses_uses_latest_sale():
    df = pd.DataFrame(
        {
            "receiving_address": [
                "A",
                "A",
                "B",
                "C",
                "D",
            ],
            "transaction_type": [
                "sale",
                "sale",
                "sale",
                "sale",
                "sale",
            ],
            "amount": [
                1000.0,
                10.0,
                500.0,
                400.0,
                300.0,
            ],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-02-01",
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-01",
                ],
                utc=True,
            ),
        }
    )

    result = build_top_receiving_addresses(df)

    assert len(result) == 3

    assert "A" not in result["receiving_address"].tolist()

    assert result["receiving_address"].tolist() == [
        "B",
        "C",
        "D",
    ]


def test_top_receiving_addresses_filters_sale_before_latest():
    df = pd.DataFrame(
        {
            "receiving_address": [
                "A",
                "A",
                "B",
                "C",
            ],
            "transaction_type": [
                "sale",
                "transfer",
                "sale",
                "sale",
            ],
            "amount": [
                1000.0,
                9999.0,
                500.0,
                400.0,
            ],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-03-01",
                    "2024-01-01",
                    "2024-01-01",
                ],
                utc=True,
            ),
        }
    )

    result = build_top_receiving_addresses(df)

    row_a = result.loc[
        result["receiving_address"].eq("A")
    ].iloc[0]

    assert row_a["amount"] == 1000.0

    assert row_a["timestamp"] == pd.Timestamp(
        "2024-01-01",
        tz="UTC",
    )


def test_latest_sale_with_null_amount_does_not_use_older_sale():
    df = pd.DataFrame(
        {
            "receiving_address": [
                "A",
                "A",
                "B",
                "C",
                "D",
            ],
            "transaction_type": [
                "sale",
                "sale",
                "sale",
                "sale",
                "sale",
            ],
            "amount": [
                9000.0,
                None,
                800.0,
                700.0,
                600.0,
            ],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-02-01",
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-01",
                ],
                utc=True,
            ),
        }
    )

    result = build_top_receiving_addresses(df)

    assert "A" not in result["receiving_address"].tolist()

    assert result["receiving_address"].tolist() == [
        "B",
        "C",
        "D",
    ]


def test_top_receiving_addresses_returns_only_three():
    df = pd.DataFrame(
        {
            "receiving_address": [
                "A",
                "B",
                "C",
                "D",
                "E",
            ],
            "transaction_type": [
                "sale",
                "sale",
                "sale",
                "sale",
                "sale",
            ],
            "amount": [
                100.0,
                500.0,
                400.0,
                300.0,
                200.0,
            ],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-01",
                ],
                utc=True,
            ),
        }
    )

    result = build_top_receiving_addresses(df)

    assert len(result) == 3

    assert result["receiving_address"].tolist() == [
        "B",
        "C",
        "D",
    ]