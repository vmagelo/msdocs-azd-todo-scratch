from datetime import datetime
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import urljoin

from fastapi import HTTPException, Response
from starlette.requests import Request
from sqlmodel import Session, select

from .app import app, engine
from .models import (CreateUpdateTodoItem, CreateUpdateTodoList, TodoItem,
                        TodoList, TodoState)

@app.get("/lists", response_model=List[TodoList], response_model_by_alias=False)
async def get_lists(
    top: Optional[int] = None, skip: Optional[int] = None
) -> List[TodoList]:
    """
    Get all Todo lists

    Optional arguments:

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList).offset(skip).limit(top))
        return query.all()

@app.post("/lists", response_model=TodoList, response_model_by_alias=False, status_code=201)
async def create_list(body: CreateUpdateTodoList, request: Request, response: Response) -> TodoList:
    """
    Create a new Todo list
    """
    with Session(engine) as session:
        todo_list2 = TodoList(**body.dict(), createdDate=datetime.utcnow(), updatedDate=datetime.utcnow())
        session.add(todo_list2)
        session.commit()
        response.headers["Location"] = urljoin(str(request.base_url), "lists/{0}".format(str(todo_list2.id)))
        return todo_list2


@app.get("/lists/{list_id}", response_model=TodoList, response_model_by_alias=False)
async def get_list(list_id: int) -> TodoList:
    """
    Get Todo list by ID
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList).where(TodoList.id == list_id))
        todo_list2 = query.first()
        if not todo_list2:
            raise HTTPException(status_code=404, detail="Todo list not found")
        return todo_list2


@app.put("/lists/{list_id}", response_model=TodoList, response_model_by_alias=False)
async def update_list(
    list_id: int, body: CreateUpdateTodoList
) -> TodoList:
    """
    Updates a Todo list by unique identifier
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList).where(TodoList.id == list_id))
        todo_list2 = query.one()
        if not todo_list2:
            raise HTTPException(status_code=404, detail="Todo list not found")
        todo_list2.name = body.name
        todo_list2.description = body.description
        todo_list2.updatedDate = datetime.utcnow()
        session.add(todo_list2)
        session.commit()
        session.refresh(todo_list2)
        return todo_list2


@app.delete("/lists/{list_id}", response_class=Response, status_code=204)
async def delete_list(list_id: int) -> None:
    """
    Deletes a Todo list by unique identifier
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList).where(TodoList.id == list_id))
        todo_list2 = query.first()
        if not todo_list2:
            raise HTTPException(status_code=404, detail="Todo list not found")
        session.delete(todo_list2)
        session.commit()

\
@app.post("/lists/{list_id}/items", response_model=TodoItem, response_model_by_alias=False, status_code=201)
async def create_list_item(
    list_id: int, body: CreateUpdateTodoItem, request: Request, response: Response
) -> TodoItem:
    """
    Creates a new Todo item within a list
    """
    with Session(engine) as session:
        todo_item2 = TodoItem(listId=list_id, **body.dict(), createdDate=datetime.utcnow())
        session.add(todo_item2)
        session.commit()
        response.headers["Location"] = urljoin(str(request.base_url), "lists/{0}/items/{1}".format(str(list_id), str(todo_item2.id)))
        return todo_item2


@app.get("/lists/{list_id}/items", response_model=List[TodoItem], response_model_by_alias=False)
async def get_list_items(
    list_id: int,
    top: Optional[int] = None,
    skip: Optional[int] = None,
) -> List[TodoItem]:
    """
    Gets Todo items within a specified list

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """    
    with Session(engine) as session:
        query = session.exec(select(TodoItem).where(TodoItem.listId == str(list_id)).offset(skip).limit(top))
        return query.all()


@app.get("/lists/{list_id}/items/state/{state}", response_model=List[TodoItem], response_model_by_alias=False)
async def get_list_items_by_state(
    list_id: int,
    state: TodoState = ...,
    top: Optional[int] = None,
    skip: Optional[int] = None,
) -> List[TodoItem]:
    """
    Gets a list of Todo items of a specific state

    Optional arguments:

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """    
    with Session(engine) as session:
        query = (
            session.exec(
                select(TodoItem).where(TodoItem.listId == str(list_id), TodoItem.state == state.name)
                    .offset(skip)
                    .limit(top)
            )
        )
        return query.all()


@app.put("/lists/{list_id}/items/state/{state}", response_model=List[TodoItem], response_model_by_alias=False)
async def update_list_items_state(
    list_id: int,
    state: TodoState = ...,
    body: List[int] = None,
) -> List[TodoItem]:
    """
    Changes the state of the specified list items
    """
    if not body:
        raise HTTPException(status_code=400, detail="No items specified")
    results = []
    for id_ in body:
        with Session(engine) as session:
            item = session.exec(select(TodoItem).where(TodoItem.id == id_)).first()
            if not item:
                raise HTTPException(status_code=404, detail="Todo item not found")
            item.state = state
            item.updatedDate = datetime.utcnow()
            session.add(item)
            session.commit()
            session.refresh(item)
            results.append(item)
    return results


@app.get("/lists/{list_id}/items/{item_id}", response_model=TodoItem, response_model_by_alias=False)
async def get_list_item(
    list_id: int, 
    item_id: int
) -> TodoItem:
    """
    Gets a Todo item by unique identifier
    """
    with Session(engine) as session:
        item = session.exec(
            select(TodoItem).where(TodoItem.listId == str(list_id), TodoItem.id == item_id)
        ).one()
        if not item:
            raise HTTPException(status_code=404, detail="Todo item not found")
        return item


@app.put("/lists/{list_id}/items/{item_id}", response_model=TodoItem, response_model_by_alias=False)
async def update_list_item(
    list_id: int,
    item_id: int,
    body: CreateUpdateTodoItem,
) -> TodoItem:
    """
    Updates a Todo item by unique identifier
    """
    with Session(engine) as session:
        item = session.exec(
            select(TodoItem).where(TodoItem.listId == str(list_id), TodoItem.id == item_id)
        ).one()
        if not item:
            raise HTTPException(status_code=404, detail="Todo item not found")
        if body.name:
            item.name = body.name
        if body.description:
            item.description = body.description
        if body.state:
            item.state = body.state
        item.updatedDate = datetime.utcnow()
        session.commit()
        session.refresh(item)
        return item

@app.delete("/lists/{list_id}/items/{item_id}", response_class=Response, status_code=204)
async def delete_list_item(
    list_id: int, item_id: int
) -> None:
    """
    Deletes a Todo item by unique identifier
    """
    try:
        with Session(engine) as session:
            item = session.exec(
                select(TodoItem).where(TodoItem.listId == str(list_id), TodoItem.id == item_id)
            ).one()
            session.delete(item)
            session.commit()
    except:            
        raise HTTPException(status_code=404, detail="Todo item not found")

