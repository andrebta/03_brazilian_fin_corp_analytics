from datetime import date, datetime

import requests

from src.database import get_connection


def fetch_sgs_series(series_id: int, start_date: date, end_date: date) -> list[dict]:
    """Fetch raw observations for one BCB SGS series and date range."""
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"
    params = {
        "formato": "json",
        "dataInicial": start_date.strftime("%d/%m/%Y"),
        "dataFinal": end_date.strftime("%d/%m/%Y"),
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
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