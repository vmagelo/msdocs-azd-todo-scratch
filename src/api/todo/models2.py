from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel
from beanie import PydanticObjectId

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import BaseSettings

def keyvault_name_as_attr(name: str) -> str:
    return name.replace("-", "_").upper()

class TodoList2(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    createdDate: Optional[datetime] = Field(default=None)
    updatedDate: Optional[datetime] = Field(default=None)

class CreateUpdateTodoList2(SQLModel):
    name: str
    description: Optional[str] = None

class TodoState2(Enum):
    TODO = "todo"
    INPROGRESS = "inprogress"
    DONE = "done"

class TodoItem2(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    listId: str  # PydanticObjectId
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
