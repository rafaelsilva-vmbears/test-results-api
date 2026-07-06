"""
This module provides a utility dependency for validating and
converting date ranges or run limits from string inputs.
It ensures that either dates OR last_runs are provided, but not both.
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
from fastapi import Query, HTTPException
from dataclasses import dataclass

@dataclass
class MetricsFilter:
    """Filter configuration for metrics queries."""
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None
    last_runs: Optional[int] = None


def get_metrics_filters(
    start_date: Optional[str] = Query(
        None, description="Data inicial no formato dd/mm/yyyy"),
    end_date: Optional[str] = Query(
        None, description="Data final no formato dd/mm/yyyy"),
    last_runs: Optional[int] = Query(
        None, description="Filtra métricas das últimas X execuções. Não pode ser usado com start_date/end_date", ge=1)
) -> MetricsFilter:
    """Dependency to validate and resolve either a date range or a limit of last runs."""

    # Rule: Must provide either dates OR last_runs
    if (start_date or end_date) and last_runs:
        raise HTTPException(
            status_code=400,
            detail="You must provide either 'start_date' and 'end_date' OR 'last_runs', not both."
        )

    if not start_date and not end_date and not last_runs:
        raise HTTPException(
            status_code=400,
            detail="You must provide either 'start_date' and 'end_date' OR 'last_runs'."
        )

    # If last_runs is provided
    if last_runs:
        return MetricsFilter(last_runs=last_runs)

    # If dates are provided
    if not start_date or not end_date:
        raise HTTPException(
            status_code=400,
            detail="Both 'start_date' and 'end_date' must be provided together."
        )

    try:
        start_dt = datetime.strptime(start_date, "%d/%m/%Y")
        end_date_dt = datetime.strptime(end_date, "%d/%m/%Y")
        # Usar o início do próximo dia para incluir todo o último dia
        end_dt = end_date_dt + timedelta(days=1)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use dd/mm/yyyy"
        ) from e

    if start_dt > end_date_dt:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date."
        )

    return MetricsFilter(start_dt=start_dt, end_dt=end_dt)
