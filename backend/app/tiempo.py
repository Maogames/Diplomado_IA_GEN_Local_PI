from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from .config import get_settings


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def hoy_local() -> date:
    """Fecha actual en la zona horaria del laboratorio (por defecto America/Bogota)."""
    return datetime.now(ZoneInfo(get_settings().zona_horaria)).date()
