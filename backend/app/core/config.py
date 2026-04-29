from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	app_name: str = "Guardian AI Backend"
	app_env: str = "dev"
	cors_origins: str | None = None

	database_host: str | None = None
	database_port: int | None = None
	database_name: str | None = None
	database_user: str | None = None
	database_password: str | None = None
	database_url: str | None = None

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)

	@property
	def sqlalchemy_database_uri(self) -> str:
		if self.database_url:
			return self.database_url

		if not all(
			[
				self.database_host,
				self.database_port,
				self.database_name,
				self.database_user,
				self.database_password,
			]
		):
			raise ValueError(
				"DATABASE_URL is not set. Provide DATABASE_URL or all DATABASE_* variables."
			)

		return (
			"postgresql+psycopg2://"
			f"{self.database_user}:{self.database_password}@"
			f"{self.database_host}:{self.database_port}/{self.database_name}"
		)

	@property
	def allowed_cors_origins(self) -> list[str]:
		if self.cors_origins:
			return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

		if self.app_env.lower() == "dev":
			return [
				"http://localhost:3000",
				"http://127.0.0.1:3000",
				"http://localhost:5173",
				"http://127.0.0.1:5173",
			]

		return []


@lru_cache
def get_settings() -> Settings:
	return Settings()


settings = get_settings()
