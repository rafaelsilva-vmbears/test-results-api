"""
This module provides a utility function for validating and
converting date ranges from string inputs to datetime objects.
It ensures the dates are in the correct format and that t
he start date is not later than the end date.
"""


from typing import Tuple
from datetime import datetime, timedelta
from fastapi import Query, HTTPException


def validate_date_range(
    start_date: str = Query(...,
                            description="Data inicial no formato dd/mm/yyyy"),
    end_date: str = Query(..., description="Data final no formato dd/mm/yyyy")
) -> Tuple[datetime, datetime]:
    """Dependência para validar e converter datas"""

    try:
        start_dt = datetime.strptime(start_date, "%d/%m/%Y")
        end_date_dt = datetime.strptime(end_date, "%d/%m/%Y")
        # Usar o início do próximo dia para incluir todo o último dia
        end_dt = end_date_dt + timedelta(days=1)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use dd/mm/yyyy") from e

    if start_dt > end_date_dt:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date.")

    return start_dt, end_dt
