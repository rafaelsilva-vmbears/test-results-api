
import re
import json
from datetime import datetime, timedelta, timezone


def compute_passed(total, failures, skipped):
    """Calculates the number of passed tests given total,
        failures, and skipped tests. Returns None if total is None."""
    if total is None:
        return None
    f = failures or 0
    s = skipped or 0
    p = total - f - s
    return p if p >= 0 else None


def parse_brazilian_date(date_str, end_of_day=False):
    """Parses a Brazilian date string and converts it to a UTC timezone-aware datetime object."""
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    if end_of_day:
        dt = dt + timedelta(days=1) - timedelta(milliseconds=1)
    return dt.replace(tzinfo=timezone.utc)


def print_truncated_json(data, max_lines=50, title="RESULTADO", save_full=False):
    """Print JSON truncated to max_lines with indicator if content is larger."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

    if not data:
        print("Nenhum dado retornado")
        print("=" * 80 + "\n")
        return

    # Format JSON
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    lines = formatted_json.split('\n')
    total_lines = len(lines)

    # Display logic
    if total_lines <= max_lines:
        # Show all
        print(formatted_json)
    else:
        # Show truncated
        truncated = '\n'.join(lines[:max_lines])
        print(truncated)
        print(f"\n... [{total_lines - max_lines} more lines hidden]")
        print(f"Total: {total_lines} lines")

        # Save full JSON if requested
        if save_full:
            filename = f"full_output_{title.replace(' ', '_').replace('#', '')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Full JSON saved to: {filename}")

    print("=" * 80 + "\n")

def normalize_project_id(raw: str) -> str:
    """
    Normalizes the project's technical identifier (_id).

    Rules:
    - lowercase
    - stripe
    - replaces spaces and underscores with hyphens
    - collapses multiple hyphens

    Ex:
    "HomePoint Legado" -> "homepoint-legado"
    "homepoint_legado" -> "homepoint-legado"
    "homepoint__legado" -> "homepoint-legado"
    """
    if not raw:
        return ""

    value = str(raw).strip().lower()
    value = re.sub(r"[ _]+", "-", value)
    value = re.sub(r"-+", "-", value)
    value = value.strip("-")

    return value

def normalize_project_name(project_id: str) -> str:
    """
    Normalizes the human name of the project (name field).
    Derived from project_id.

    Ex:
    "homepoint-legado" -> "homepoint legado"
    """
    if not project_id:
        return ""

    name = project_id.replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip()

    return name
