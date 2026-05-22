"""Historical CoinGecko market chart normalization helpers."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_narrative_radar.api.coingecko import COINGECKO_MARKET_CHART_ENDPOINT
from crypto_narrative_radar.config import PROCESSED_DATA_DIR, RAW_DATA_DIR


HISTORICAL_OUTPUT_COLUMNS = [
    "date",
    "timestamp_ms",
    "coingecko_id",
    "symbol",
    "name",
    "primary_narrative",
    "secondary_narratives",
    "include_in_score",
    "price_usd",
    "market_cap_usd",
    "total_volume_usd",
    "volume_to_market_cap",
    "return_1d",
    "return_7d",
    "return_30d",
    "source",
    "endpoint",
    "backfill_days",
    "interval",
    "backfilled_at_utc",
    "data_quality_flag",
]
FAILURE_COLUMNS = [
    "coingecko_id",
    "symbol",
    "name",
    "error_type",
    "status_code",
    "message",
    "attempted_at_utc",
    "attempt_count",
]
VALID_QUALITY_FLAGS = {
    "ok",
    "missing_price",
    "missing_market_cap",
    "missing_volume",
    "zero_or_negative_price",
    "zero_market_cap",
    "incomplete_lag_history",
}


def historical_raw_output_dir(
    run_date: date,
    base_dir: Path = RAW_DATA_DIR,
) -> Path:
    """Return the date-partitioned raw historical output directory."""
    return base_dir / "coingecko" / "historical" / run_date.isoformat()


def historical_processed_output_path(
    output_name: str = "token_market_history_90d.csv",
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Return the processed historical market data output path."""
    return base_dir / "historical" / output_name


def save_raw_market_chart(
    coingecko_id: str,
    response: dict[str, Any],
    run_date: date,
    backfill_days: int,
    vs_currency: str,
    interval: str,
    fetched_at_utc: str,
    base_dir: Path = RAW_DATA_DIR,
) -> Path:
    """Save one raw CoinGecko market chart response as JSON."""
    output_dir = historical_raw_output_dir(run_date, base_dir=base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{coingecko_id}_market_chart_{backfill_days}d.json"
    payload = {
        "coingecko_id": coingecko_id,
        "fetched_at_utc": fetched_at_utc,
        "endpoint": COINGECKO_MARKET_CHART_ENDPOINT,
        "params": {
            "vs_currency": vs_currency,
            "days": backfill_days,
            "interval": interval,
        },
        "response": response,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def save_failure_log(
    failures: list[dict[str, object]],
    run_date: date,
    base_dir: Path = RAW_DATA_DIR,
) -> Path:
    """Save failed token requests to a CSV failure log."""
    output_dir = historical_raw_output_dir(run_date, base_dir=base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "backfill_failures.csv"
    pd.DataFrame(failures, columns=FAILURE_COLUMNS).to_csv(output_path, index=False)
    return output_path


def build_failure_row(
    token: pd.Series | dict[str, object],
    error_type: str,
    message: str,
    attempted_at_utc: str,
    attempt_count: int,
    status_code: int | None = None,
) -> dict[str, object]:
    """Build a failure-log row without raising pipeline errors."""
    token_data = dict(token)
    return {
        "coingecko_id": token_data.get("coingecko_id", ""),
        "symbol": token_data.get("symbol", ""),
        "name": token_data.get("name", ""),
        "error_type": error_type,
        "status_code": status_code,
        "message": message,
        "attempted_at_utc": attempted_at_utc,
        "attempt_count": attempt_count,
    }


def _series_from_points(
    response: dict[str, Any],
    key: str,
    value_column: str,
) -> pd.DataFrame:
    points = response.get(key, [])
    if points is None:
        points = []
    rows = []
    for point in points:
        if not isinstance(point, list) or len(point) < 2:
            continue
        rows.append({"timestamp_ms": point[0], value_column: point[1]})
    return pd.DataFrame(rows, columns=["timestamp_ms", value_column])


def normalize_market_chart_response(
    coingecko_id: str,
    response: dict[str, Any],
    taxonomy_row: pd.Series | dict[str, object],
    backfill_days: int,
    interval: str,
    backfilled_at_utc: str,
) -> pd.DataFrame:
    """Normalize a CoinGecko market chart response to daily token-level rows."""
    price_df = _series_from_points(response, "prices", "price_usd")
    market_cap_df = _series_from_points(response, "market_caps", "market_cap_usd")
    volume_df = _series_from_points(response, "total_volumes", "total_volume_usd")

    if price_df.empty and market_cap_df.empty and volume_df.empty:
        return pd.DataFrame(columns=HISTORICAL_OUTPUT_COLUMNS)

    normalized = price_df.merge(market_cap_df, on="timestamp_ms", how="outer")
    normalized = normalized.merge(volume_df, on="timestamp_ms", how="outer")
    normalized["timestamp_ms"] = pd.to_numeric(normalized["timestamp_ms"], errors="coerce")
    normalized = normalized.dropna(subset=["timestamp_ms"]).copy()
    normalized["timestamp_ms"] = normalized["timestamp_ms"].astype("int64")
    normalized = normalized.sort_values("timestamp_ms")
    normalized["date"] = (
        pd.to_datetime(normalized["timestamp_ms"], unit="ms", utc=True)
        .dt.date.astype(str)
    )

    # If CoinGecko returns more granular data, keep the last observation per UTC date.
    normalized = normalized.groupby("date", as_index=False).tail(1).reset_index(drop=True)

    taxonomy = dict(taxonomy_row)
    normalized["coingecko_id"] = coingecko_id
    normalized["symbol"] = taxonomy.get("symbol", pd.NA)
    normalized["name"] = taxonomy.get("name", pd.NA)
    normalized["primary_narrative"] = taxonomy.get("primary_narrative", pd.NA)
    normalized["secondary_narratives"] = taxonomy.get("secondary_narratives", pd.NA)
    normalized["include_in_score"] = taxonomy.get("include_in_score", pd.NA)

    for column in ["price_usd", "market_cap_usd", "total_volume_usd"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    normalized["volume_to_market_cap"] = pd.NA
    valid_market_cap = normalized["market_cap_usd"] > 0
    normalized.loc[valid_market_cap, "volume_to_market_cap"] = (
        normalized.loc[valid_market_cap, "total_volume_usd"]
        / normalized.loc[valid_market_cap, "market_cap_usd"]
    )

    normalized["source"] = "CoinGecko"
    normalized["endpoint"] = COINGECKO_MARKET_CHART_ENDPOINT
    normalized["backfill_days"] = backfill_days
    normalized["interval"] = interval
    normalized["backfilled_at_utc"] = backfilled_at_utc

    for column in ["return_1d", "return_7d", "return_30d", "data_quality_flag"]:
        normalized[column] = pd.NA

    return normalized[HISTORICAL_OUTPUT_COLUMNS]


def normalize_historical_market_data(
    responses: dict[str, dict[str, Any]],
    taxonomy_df: pd.DataFrame,
    backfill_days: int,
    interval: str,
    backfilled_at_utc: str,
) -> pd.DataFrame:
    """Normalize successful CoinGecko responses and add calendar-lag returns."""
    frames: list[pd.DataFrame] = []
    taxonomy_by_id = taxonomy_df.set_index("coingecko_id", drop=False)

    for coingecko_id, response in responses.items():
        if coingecko_id not in taxonomy_by_id.index:
            continue
        frames.append(
            normalize_market_chart_response(
                coingecko_id=coingecko_id,
                response=response,
                taxonomy_row=taxonomy_by_id.loc[coingecko_id],
                backfill_days=backfill_days,
                interval=interval,
                backfilled_at_utc=backfilled_at_utc,
            )
        )

    if not frames:
        return pd.DataFrame(columns=HISTORICAL_OUTPUT_COLUMNS)

    historical = pd.concat(frames, ignore_index=True)
    historical = add_calendar_lag_returns(historical)
    historical["data_quality_flag"] = historical.apply(data_quality_flag, axis=1)
    return historical[HISTORICAL_OUTPUT_COLUMNS].sort_values(
        ["coingecko_id", "date"]
    ).reset_index(drop=True)


def add_calendar_lag_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add 1D, 7D, and 30D returns using exact calendar-date self-merges."""
    if df.empty:
        return df.copy()

    output = df.copy()
    output["_date_dt"] = pd.to_datetime(output["date"], errors="coerce")
    price_lookup = output[["coingecko_id", "_date_dt", "price_usd"]].copy()

    for days in [1, 7, 30]:
        lag_column = f"price_lag_{days}d"
        target_column = f"_date_minus_{days}d"
        return_column = f"return_{days}d"
        output[target_column] = output["_date_dt"] - pd.Timedelta(days=days)
        lag_lookup = price_lookup.rename(
            columns={"_date_dt": target_column, "price_usd": lag_column}
        )
        output = output.merge(
            lag_lookup,
            on=["coingecko_id", target_column],
            how="left",
        )
        valid_lag = output[lag_column].notna() & (output[lag_column] > 0)
        output[return_column] = pd.NA
        output.loc[valid_lag, return_column] = (
            output.loc[valid_lag, "price_usd"] / output.loc[valid_lag, lag_column] - 1
        )
        output = output.drop(columns=[target_column, lag_column])

    output = output.drop(columns=["_date_dt"])
    return output


def data_quality_flag(row: pd.Series) -> str:
    """Return a simple quality flag for one historical market row."""
    if pd.isna(row.get("price_usd")):
        return "missing_price"
    if row.get("price_usd") <= 0:
        return "zero_or_negative_price"
    if pd.isna(row.get("market_cap_usd")):
        return "missing_market_cap"
    if row.get("market_cap_usd") == 0:
        return "zero_market_cap"
    if pd.isna(row.get("total_volume_usd")):
        return "missing_volume"
    if any(pd.isna(row.get(column)) for column in ["return_1d", "return_7d", "return_30d"]):
        return "incomplete_lag_history"
    return "ok"


def save_processed_historical_data(
    df: pd.DataFrame,
    output_name: str = "token_market_history_90d.csv",
    base_dir: Path = PROCESSED_DATA_DIR,
) -> Path:
    """Save normalized historical token market data."""
    output_path = historical_processed_output_path(output_name, base_dir=base_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
