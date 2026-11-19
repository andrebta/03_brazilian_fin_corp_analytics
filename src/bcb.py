from datetime import date, datetime
import requests
from src.database import get_connection
import math
import pandas as pd


def fetch_sgs_series(series_id: int, start_date: date, end_date: date) -> list[dict]:
    """Fetch raw observations for one BCB SGS series and date range."""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"
    params = {
        "formato": "json",
        "dataInicial": start_date.strftime("%d/%m/%Y"),
        "dataFinal": end_date.strftime("%d/%m/%Y"),
    }

    response = requests.get(url, params=params, timeout=30)

    if response.status_code == 304:
        response = requests.get(
            url,
            params=params,
            headers={"Cache-Control": "no-cache"},
            timeout=30,
        )

    response.raise_for_status()

    if response.status_code == 304:
        raise RuntimeError(
            f"O BCB retornou HTTP 304 novamente para a série {series_id}. "
            "A extração terminou sem receber os dados."
        )

    return response.json()

def prepare_sgs_rows(series_id: int, records: list[dict]) -> list[tuple[int, date, str]]:
    """Prepare SGS observations for loading into PostgreSQL."""
    rows = []

    for record in records:
        observation_date = datetime.strptime(record["data"], "%d/%m/%Y").date()
        rows.append((series_id, observation_date, record["valor"]))

    return rows

def load_sgs_observations(rows):
    """Insert new SGS observations and update values revised by the source."""
    upsert_sql = """
        INSERT INTO raw_bcb.sgs_observations AS obs
            (series_id, observation_date, raw_value)
        VALUES (%s, %s, %s)
        ON CONFLICT (series_id, observation_date)
        DO UPDATE SET raw_value = EXCLUDED.raw_value
        WHERE obs.raw_value IS DISTINCT FROM EXCLUDED.raw_value
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(upsert_sql, rows)
            affected_rows = cur.rowcount

    return affected_rows

def validate_ipca_rows(rows):
    if not rows:
        raise ValueError("O lote do IPCA está vazio.")

    batch = pd.DataFrame(rows, columns=["series_id", "observation_date", "raw_value"])

    if not batch["series_id"].eq(433).all():
        raise ValueError("O lote contém observações de outra série além do IPCA (433).")

    months = pd.to_datetime(batch["observation_date"]).dt.to_period("M")

    if months.isna().any():
        raise ValueError("O lote contém observações sem data.")

    duplicates = months[months.duplicated()].unique()
    if len(duplicates):
        raise ValueError(f"Meses repetidos no IPCA: {duplicates.tolist()}")

    expected = pd.period_range("2000-01", months.max(), freq="M")
    missing = expected.difference(months)
    if len(missing):
        raise ValueError(f"Meses ausentes no IPCA: {missing.tolist()}")

    values = pd.to_numeric(batch["raw_value"], errors="coerce")
    invalid = ~values.map(math.isfinite)
    if invalid.any():
        invalid_records = batch.loc[invalid].to_dict("records")
        raise ValueError(f"Valores inválidos no IPCA: {invalid_records}")