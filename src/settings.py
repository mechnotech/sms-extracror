from pathlib import Path

from pydantic_settings import BaseSettings

base_dir = Path(__file__).parent.parent.absolute()


class Settings(BaseSettings):
    dev_mode: bool = False
    log_level: str = 'DEBUG'

    db_postgres_host: str
    db_postgres_port: int = 5432
    db_postgres_user: str
    db_postgres_pass: str
    db_postgres_name: str
    db_postgres_schema: str


    @property
    def psycopg_dsn(self) -> dict:
        return dict(
                    host=self.db_postgres_host,
                    user=self.db_postgres_user,
                    password=self.db_postgres_pass,
                    dbname=self.db_postgres_name,
                    port=self.db_postgres_port
        )


    @property
    def psg_connection_string(self) -> str:
        return (
            'postgresql://{}:{}@{}:{}/{}'.format(
                self.db_postgres_user,
                self.db_postgres_pass,
                self.db_postgres_host,
                self.db_postgres_port,
                self.db_postgres_name,

            )
        )

    def apsg_connection_string(self) -> str:
        return (
            'postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
                self.db_postgres_user,
                self.db_postgres_pass,
                self.db_postgres_host,
                self.db_postgres_port,
                self.db_postgres_name,

            )
        )

    class Config:
        env_file = f'{base_dir}/.env'
        extra = 'allow'


config = Settings()
