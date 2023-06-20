from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import BaseSettings, BaseModel

def keyvault_name_as_attr(name: str) -> str:
    return name.replace("-", "_").upper()

class Settings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load secrets from keyvault
        if self.AZURE_KEY_VAULT_ENDPOINT:
            credential = DefaultAzureCredential()
            keyvault_client = SecretClient(self.AZURE_KEY_VAULT_ENDPOINT, credential)
            for secret in keyvault_client.list_properties_of_secrets():
                setattr(
                    self,
                    keyvault_name_as_attr(secret.name),
                    keyvault_client.get_secret(secret.name).value,
                )

    AZURE_POSTGRESQL_CONNECTION_STRING: str = ""
    AZURE_POSTGRESQL_DATABASE_NAME: str = "Todo"
    AZURE_KEY_VAULT_ENDPOINT: Optional[str] = None
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = None
    APPLICATIONINSIGHTS_ROLENAME: Optional[str] = "API"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class TodoList(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    createdDate: Optional[datetime] = Field(default=None)
    updatedDate: Optional[datetime] = Field(default=None)

class CreateUpdateTodoList(BaseModel):
    name: str
    description: Optional[str] = None

class TodoState(Enum):
    TODO = "todo"
    INPROGRESS = "inprogress"
    DONE = "done"

class TodoItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    listId: int = Field(default=None, foreign_key="todolist.id")
    name: str
    description: Optional[str] = None
    state: Optional[TodoState] = None
    dueDate: Optional[datetime] = None
    completedDate: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None

class CreateUpdateTodoItem(BaseModel):
    name: str
    description: Optional[str] = None
    state: Optional[TodoState] = None
    dueDate: Optional[datetime] = None
    completedDate: Optional[datetime] = None
