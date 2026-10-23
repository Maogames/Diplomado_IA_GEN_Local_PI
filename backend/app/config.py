from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

SECRETO_POR_DEFECTO = "solo-para-desarrollo-cambiar-antes-de-desplegar"


class Settings(BaseSettings):
    """Configuración leída de variables de entorno con prefijo LAB_ (o del archivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LAB_", extra="ignore")

    entorno: str = "desarrollo"  # desarrollo | pruebas | produccion
    nombre_app: str = "API de Inventario y Préstamos del Laboratorio"

    # SQLite sirve para desarrollar sin Docker; en el servidor se usa PostgreSQL:
    # postgresql+psycopg://usuario:clave@localhost:5432/laboratorio
    database_url: str = "sqlite:///./laboratorio.db"
    crear_tablas_al_iniciar: bool = True

    jwt_secreto: str = SECRETO_POR_DEFECTO
    jwt_algoritmo: str = "HS256"
    token_minutos: int = 120

    # PBKDF2-SHA256. 600 000 iteraciones es la recomendación actual de OWASP.
    iteraciones_hash: int = 600_000
    max_intentos_login: int = 5
    minutos_bloqueo_login: int = 10

    cors_origenes: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    zona_horaria: str = "America/Bogota"
    dias_max_prestamo: int = 15
    max_elementos_por_prestamo: int = 10


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.entorno == "produccion" and s.jwt_secreto == SECRETO_POR_DEFECTO:
        raise RuntimeError("LAB_JWT_SECRETO debe definirse en producción.")
    return s
