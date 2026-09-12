from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.bronze.ingestion import ingest_bronze
from src.bronze.quality import validate_bronze
from src.gold.quality import validate_gold
from src.gold.risk_by_region import create_risk_by_region
from src.gold.top_receiving_addresses import (
    create_top_receiving_addresses,
)
from src.silver.quality import validate_silver
from src.silver.transformation import transform_silver


with DAG(
    dag_id="fraud_credit_medallion",
    description="Pipeline Medalhão para processamento de fraude de crédito",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fraud", "credit", "medallion"],
) as dag:

    bronze_ingestion = PythonOperator(
        task_id="bronze_ingestion",
        python_callable=ingest_bronze,
    )

    bronze_quality = PythonOperator(
        task_id="bronze_quality",
        python_callable=validate_bronze,
    )

    silver_transformation = PythonOperator(
        task_id="silver_transformation",
        python_callable=transform_silver,
    )

    silver_quality = PythonOperator(
        task_id="silver_quality",
        python_callable=validate_silver,
    )

    gold_risk_by_region = PythonOperator(
        task_id="gold_risk_by_region",
        python_callable=create_risk_by_region,
    )

    gold_top_receiving_addresses = PythonOperator(
        task_id="gold_top_receiving_addresses",
        python_callable=create_top_receiving_addresses,
    )

    gold_quality = PythonOperator(
        task_id="gold_quality",
        python_callable=validate_gold,
    )

    bronze_ingestion >> bronze_quality
    bronze_quality >> silver_transformation
    silver_transformation >> silver_quality

    silver_quality >> [
        gold_risk_by_region,
        gold_top_receiving_addresses,
    ]

    [
        gold_risk_by_region,
        gold_top_receiving_addresses,
    ] >> gold_quality