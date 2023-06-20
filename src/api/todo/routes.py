from datetime import datetime
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import urljoin

from beanie import PydanticObjectId
from fastapi import HTTPException, Response
from starlette.requests import Request
from sqlmodel import Session, select

from .app import app, engine
from .models import (CreateUpdateTodoItem, CreateUpdateTodoList, TodoItem,
                     TodoList, TodoState)
from .models2 import (CreateUpdateTodoItem2, CreateUpdateTodoList2, TodoItem2,
                        TodoList2, TodoState2)

@app.get("/lists", response_model=List[TodoList2], response_model_by_alias=False)
async def get_lists2(
    top: Optional[int] = None, skip: Optional[int] = None
) -> List[TodoList2]:
    """
    Get all Todo lists

    Optional arguments:

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList2).offset(skip).limit(top))
        return query.all()


@app.get("/oldlists", response_model=List[TodoList], response_model_by_alias=False)
async def get_lists(
    top: Optional[int] = None, skip: Optional[int] = None
) -> List[TodoList]:
    """
    Get all Todo lists

    Optional arguments:

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """
    query = TodoList.all().skip(skip).limit(top)
    return await query.to_list()


@app.post("/lists", response_model=TodoList2, response_model_by_alias=False, status_code=201)
async def create_list2(body: CreateUpdateTodoList2, request: Request, response: Response) -> TodoList2:
    """
    Create a new Todo list
    """
    with Session(engine) as session:
        todo_list2 = TodoList2(**body.dict(), createdDate=datetime.utcnow(), updatedDate=datetime.utcnow())
        session.add(todo_list2)
        session.commit()
        response.headers["Location"] = urljoin(str(request.base_url), "lists/{0}".format(str(todo_list2.id)))
        return todo_list2

@app.post("/oldlists", response_model=TodoList, response_model_by_alias=False, status_code=201)
async def create_list(body: CreateUpdateTodoList, request: Request, response: Response) -> TodoList:
    """
    Create a new Todo list
    """
    todo_list = await TodoList(**body.dict(), createdDate=datetime.utcnow()).save()
    response.headers["Location"] = urljoin(str(request.base_url), "lists/{0}".format(str(todo_list.id)))
    return todo_list

@app.get("/lists/{list_id}", response_model=TodoList2, response_model_by_alias=False)
async def get_list2(list_id: int) -> TodoList2:
    """
    Get Todo list by ID
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList2).where(TodoList2.id == list_id))
        todo_list2 = query.first()
        if not todo_list2:
            raise HTTPException(status_code=404, detail="Todo list not found")
        return todo_list2

@app.get("/oldlists/{list_id}", response_model=TodoList, response_model_by_alias=False)
async def get_list(list_id: PydanticObjectId) -> TodoList:
    """
    Get Todo list by ID
    """
    todo_list = await TodoList.get(document_id=list_id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo list not found")
    return todo_list

@app.put("/lists/{list_id}", response_model=TodoList2, response_model_by_alias=False)
async def update_list2(
    list_id: int, body: CreateUpdateTodoList2
) -> TodoList2:
    """
    Updates a Todo list by unique identifier
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList2).where(TodoList2.id == list_id))
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

@app.put("/oldlists/{list_id}", response_model=TodoList, response_model_by_alias=False)
async def update_list(
    list_id: PydanticObjectId, body: CreateUpdateTodoList
) -> TodoList:
    """
    Updates a Todo list by unique identifier
    """
    todo_list = await TodoList.get(document_id=list_id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo list not found")
    await todo_list.update({"$set": body.dict(exclude_unset=True)})
    todo_list.updatedDate = datetime.utcnow()
    return await todo_list.save()

@app.delete("/lists/{list_id}", response_class=Response, status_code=204)
async def delete_list2(list_id: int) -> None:
    """
    Deletes a Todo list by unique identifier
    """
    with Session(engine) as session:
        query = session.exec(select(TodoList2).where(TodoList2.id == list_id))
        todo_list2 = query.first()
        if not todo_list2:
            raise HTTPException(status_code=404, detail="Todo list not found")
        session.delete(todo_list2)
        session.commit()

@app.delete("/oldlists/{list_id}", response_class=Response, status_code=204)
async def delete_list(list_id: PydanticObjectId) -> None:
    """
    Deletes a Todo list by unique identifier
    """
    todo_list = await TodoList.get(document_id=list_id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo list not found")
    await todo_list.delete()

@app.post("/lists/{list_id}/items", response_model=TodoItem2, response_model_by_alias=False, status_code=201)
async def create_list_item2(
    list_id: int, body: CreateUpdateTodoItem2, request: Request, response: Response
) -> TodoItem2:
    """
    Creates a new Todo item within a list
    """
    with Session(engine) as session:
        todo_item2 = TodoItem2(listId=list_id, **body.dict(), createdDate=datetime.utcnow())
        session.add(todo_item2)
        session.commit()
        response.headers["Location"] = urljoin(str(request.base_url), "lists/{0}/items/{1}".format(str(list_id), str(todo_item2.id)))
        return todo_item2

@app.post("/oldlists/{list_id}/items", response_model=TodoItem, response_model_by_alias=False, status_code=201)
async def create_list_item(
    list_id: PydanticObjectId, body: CreateUpdateTodoItem, request: Request, response: Response
) -> TodoItem:
    """
    Creates a new Todo item within a list
    """
    item = TodoItem(listId=list_id, **body.dict(), createdDate=datetime.utcnow())
    response.headers["Location"] = urljoin(str(request.base_url), "lists/{0}/items/{1}".format(str(list_id), str(item.id)))
    return await item.save()

@app.get("/lists/{list_id}/items", response_model=List[TodoItem2], response_model_by_alias=False)
async def get_list_items2(
    list_id: int,
    top: Optional[int] = None,
    skip: Optional[int] = None,
) -> List[TodoItem2]:
    """
    Gets Todo items within a specified list

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """    
    with Session(engine) as session:
        query = session.exec(select(TodoItem2).where(TodoItem2.listId == str(list_id)).offset(skip).limit(top))
        return query.all()


@app.get("/oldlists/{list_id}/items", response_model=List[TodoItem], response_model_by_alias=False)
async def get_list_items(
    list_id: PydanticObjectId,
    top: Optional[int] = None,
    skip: Optional[int] = None,
) -> List[TodoItem]:
    """
    Gets Todo items within the specified list

    Optional arguments:

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """
    query = TodoItem.find(TodoItem.listId == list_id).skip(skip).limit(top)
    return await query.to_list()



@app.get("/lists/{list_id}/items/state/{state}", response_model=List[TodoItem2], response_model_by_alias=False)
async def get_list_items_by_state2(
    list_id: int,
    state: TodoState2 = ...,
    top: Optional[int] = None,
    skip: Optional[int] = None,
) -> List[TodoItem2]:
    """
    Gets a list of Todo items of a specific state

    Optional arguments:

    - **top**: Number of lists to return
    - **skip**: Number of lists to skip
    """    
    with Session(engine) as session:
        query = (
            session.exec(
                select(TodoItem2).where(TodoItem2.listId == str(list_id), TodoItem2.state == state.name)
                    .offset(skip)
                    .limit(top)
            )
        )
        return query.all()

@app.get("/oldlists/{list_id}/items/state/{state}", response_model=List[TodoItem], response_model_by_alias=False)
async def get_list_items_by_state(
    list_id: PydanticObjectId,
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
    query = (
        TodoItem.find(TodoItem.listId == list_id, TodoItem.state == state)
        .skip(skip)
        .limit(top)
    )
    return await query.to_list()


@app.put("/lists/{list_id}/items/state/{state}", response_model=List[TodoItem2], response_model_by_alias=False)
async def update_list_items_state2(
    list_id: int,
    state: TodoState2 = ...,
    body: List[int] = None,
) -> List[TodoItem2]:
    """
    Changes the state of the specified list items
    """
    if not body:
        raise HTTPException(status_code=400, detail="No items specified")
    results = []
    for id_ in body:
        with Session(engine) as session:
            item = session.exec(select(TodoItem2).where(TodoItem2.id == id_)).first()
            if not item:
                raise HTTPException(status_code=404, detail="Todo item not found")
            item.state = state
            item.updatedDate = datetime.utcnow()
            session.add(item)
            session.commit()
            session.refresh(item)
            results.append(item)
    return results

@app.put("/oldlists/{list_id}/items/state/{state}", response_model=List[TodoItem], response_model_by_alias=False)
async def update_list_items_state(
    list_id: PydanticObjectId,
    state: TodoState = ...,
    body: List[str] = None,
) -> List[TodoItem]:
    """
    Changes the state of the specified list items
    """
    if not body:
        raise HTTPException(status_code=400, detail="No items specified")
    results = []    
    for id_ in body:
        item = await TodoItem.get(document_id=id_)
        if not item:
            raise HTTPException(status_code=404, detail="Todo item not found")
        item.state = state
        item.updatedDate = datetime.utcnow()
        results.append(await item.save())
    return results


@app.get("/lists/{list_id}/items/{item_id}", response_model=TodoItem2, response_model_by_alias=False)
async def get_list_item2(
    list_id: int, 
    item_id: int
) -> TodoItem2:
    """
    Gets a Todo item by unique identifier
    """
    with Session(engine) as session:
        item = session.exec(
            select(TodoItem2).where(TodoItem2.listId == str(list_id), TodoItem2.id == item_id)
        ).one()
        if not item:
            raise HTTPException(status_code=404, detail="Todo item not found")
        return item

@app.get("/oldlists/{list_id}/items/{item_id}", response_model=TodoItem, response_model_by_alias=False)
async def get_list_item(
    list_id: PydanticObjectId, item_id: PydanticObjectId
) -> TodoItem:
    """
    Gets a Todo item by unique identifier
    """
    item = await TodoItem.find_one(TodoItem.listId == list_id, TodoItem.id == item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Todo item not found")
    return item


@app.put("/lists/{list_id}/items/{item_id}", response_model=TodoItem2, response_model_by_alias=False)
async def update_list_item2(
    list_id: int,
    item_id: int,
    body: CreateUpdateTodoItem2,
) -> TodoItem2:
    """
    Updates a Todo item by unique identifier
    """
    with Session(engine) as session:
        item = session.exec(
            select(TodoItem2).where(TodoItem2.listId == str(list_id), TodoItem2.id == item_id)
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

@app.put("/oldlists/{list_id}/items/{item_id}", response_model=TodoItem, response_model_by_alias=False)
async def update_list_item(
    list_id: PydanticObjectId,
    item_id: PydanticObjectId,
    body: CreateUpdateTodoItem,
) -> TodoItem:
    """
    Updates a Todo item by unique identifier
    """
    item = await TodoItem.find_one(TodoItem.listId == list_id, TodoItem.id == item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Todo item not found")
    await item.update({"$set": body.dict(exclude_unset=True)})
    item.updatedDate = datetime.utcnow()
    return await item.save()

@app.delete("/lists/{list_id}/items/{item_id}", response_class=Response, status_code=204)
async def delete_list_item2(
    list_id: int, item_id: int
) -> None:
    """
    Deletes a Todo item by unique identifier
    """
    try:
        with Session(engine) as session:
            item = session.exec(
                select(TodoItem2).where(TodoItem2.listId == str(list_id), TodoItem2.id == item_id)
            ).one()
            session.delete(item)
            session.commit()
    except:            
        raise HTTPException(status_code=404, detail="Todo item not found")

@app.delete("/oldlists/{list_id}/items/{item_id}", response_class=Response, status_code=204)
async def delete_list_item(
    list_id: PydanticObjectId, item_id: PydanticObjectId
) -> None:
    """
    Deletes a Todo item by unique identifier
    """
    todo_item = await TodoItem.find_one(TodoItem.id == item_id)
    if not todo_item:
        raise HTTPException(status_code=404, detail="Todo item not found")
    await todo_item.delete()
