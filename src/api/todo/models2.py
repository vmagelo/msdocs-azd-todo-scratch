from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def keyvault_name_as_attr(name: str) -> str:
    return name.replace("-", "_").upper()

class Settings():
    def __init__(self, *args, **kwargs):
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

    AZURE_COSMOS_CONNECTION_STRING: str = ""
    AZURE_COSMOS_DATABASE_NAME: str = "Todo"
    AZURE_KEY_VAULT_ENDPOINT: Optional[str] = None
    APPLICATIONINSIGHTS_CONNECTION_STRING: Optional[str] = None
    APPLICATIONINSIGHTS_ROLENAME: Optional[str] = "API"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

class TodoList2(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    createdDate: Optional[datetime] = Field(default=None)
    updatedDate: Optional[datetime] = Field(default=None)

class CreateUpdateTodoList2(BaseModel):
    name: str
    description: Optional[str] = None

class TodoState2(Enum):
    TODO = "todo"
    INPROGRESS = "inprogress"
    DONE = "done"

class TodoItem2(SQLModel, table=True):
    listId: PydanticObjectId
    name: str
    description: Optional[str] = None
    state: Optional[TodoState2] = None
    dueDate: Optional[datetime] = None
    completedDate: Optional[datetime] = None
    createdDate: Optional[datetime] = None
    updatedDate: Optional[datetime] = None

class CreateUpdateTodoItem2(SQLModel):
    name: str
    description: Optional[str] = None
    state: Optional[TodoState2] = None
    dueDate: Optional[datetime] = None
    completedDate: Optional[datetime] = None
