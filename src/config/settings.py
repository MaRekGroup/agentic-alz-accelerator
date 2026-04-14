"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field

_ENV_FILE = ".env"
_BASE_CONFIG = {"env_file": _ENV_FILE, "env_file_encoding": "utf-8", "extra": "ignore"}


class AzureAISettings(BaseSettings):
    project_connection_string: str = Field(alias="AZURE_AI_PROJECT_CONNECTION_STRING")
    openai_endpoint: str = Field(alias="AZURE_OPENAI_ENDPOINT")
    openai_deployment: str = Field(default="gpt-4o", alias="AZURE_OPENAI_DEPLOYMENT")
    openai_api_version: str = Field(
        default="2025-01-01-preview", alias="AZURE_OPENAI_API_VERSION"
    )

    model_config = _BASE_CONFIG


class AzureSettings(BaseSettings):
    subscription_id: str = Field(alias="AZURE_SUBSCRIPTION_ID")
    tenant_id: str = Field(default="", alias="AZURE_TENANT_ID")
    management_group_prefix: str = Field(
        default="alz", alias="AZURE_MANAGEMENT_GROUP_PREFIX"
    )

    model_config = _BASE_CONFIG


class IaCSettings(BaseSettings):
    framework: str = Field(default="bicep", alias="IAC_FRAMEWORK")
    terraform_state_storage_account: str = Field(
        default="", alias="TERRAFORM_STATE_STORAGE_ACCOUNT"
    )
    terraform_state_container: str = Field(
        default="tfstate", alias="TERRAFORM_STATE_CONTAINER"
    )

    model_config = _BASE_CONFIG


class MonitorSettings(BaseSettings):
    interval_minutes: int = Field(default=30, alias="MONITOR_INTERVAL_MINUTES")
    drift_check_interval_minutes: int = Field(
        default=60, alias="DRIFT_CHECK_INTERVAL_MINUTES"
    )
    auto_remediate: bool = Field(default=False, alias="AUTO_REMEDIATE")

    model_config = _BASE_CONFIG


class NotificationSettings(BaseSettings):
    webhook_url: str = Field(default="", alias="NOTIFICATION_WEBHOOK_URL")
    email: str = Field(default="", alias="NOTIFICATION_EMAIL")

    model_config = _BASE_CONFIG


class Settings(BaseSettings):
    ai: AzureAISettings = Field(default_factory=AzureAISettings)
    azure: AzureSettings = Field(default_factory=AzureSettings)
    iac: IaCSettings = Field(default_factory=IaCSettings)
    monitor: MonitorSettings = Field(default_factory=MonitorSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)

    model_config = _BASE_CONFIG
