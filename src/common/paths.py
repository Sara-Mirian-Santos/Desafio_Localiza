from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

LANDING_FILE = DATA_DIR / "landing" / "df_fraud_credit.csv"

BRONZE_FILE = DATA_DIR / "bronze" / "fraud_credit.parquet"

SILVER_FILE = DATA_DIR / "silver" / "fraud_credit.parquet"

GOLD_RISK_FILE = DATA_DIR / "gold" / "risk_by_region.parquet"

GOLD_ADDRESS_FILE = (
    DATA_DIR / "gold" / "top_receiving_addresses.parquet"
)

BRONZE_REPORT = (
    REPORTS_DIR / "bronze" / "data_quality.json"
)

SILVER_REPORT = (
    REPORTS_DIR / "silver" / "data_quality.json"
)

GOLD_REPORT = (
    REPORTS_DIR / "gold" / "data_quality.json"
)