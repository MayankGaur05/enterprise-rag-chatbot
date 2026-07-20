from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ItemsListResponse(BaseModel):
    message: str
    items: List[ItemResponse]

items = []
next_id = 0

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create Item", tags=["Items"])
def create_item(item: ItemCreate):
    """
    Create a new item with the provided details.
    """
    if item.price < 0:
            raise HTTPException(status_code=400, detail="Price must be a positive value")
    if item.tax is not None and item.tax < 0:
            raise HTTPException(status_code=400, detail="Tax must be a positive value")
    global next_id
    next_id += 1
    item_id = next_id
        
    new_item = ItemResponse(id=item_id, **item.model_dump())
    items.append(new_item)
    return new_item
    


@router.get("/items", response_model=ItemsListResponse, status_code=status.HTTP_200_OK, summary="Get All Items", tags=["Items"])
def list_items():
    """
    Return all items with a custom message.
    """
    return {
        "message": "Items retrieved successfully",
        "items": items,
    }

@router.get("/items/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK, summary="Get Item by ID", tags=["Items"])
def get_item(item_id: int):
    """
    Retrieve an item by its ID.
    """
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")

    for item in items:
        if item.id == item_id:
            return  item 
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/items/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK, summary="Update Item by ID", tags=["Items"])
def update_item(item_id: int, updated_item: ItemUpdate):
    """
    Update an existing item by its ID.
    
    """
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")

    for index, item in enumerate(items):
        if item.id == item_id:
            updated_item_data = updated_item.model_dump()
            updated_item_response = ItemResponse(id=item_id, **updated_item_data)
            items[index] = updated_item_response
            return updated_item_response
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Item by ID", tags=["Items"])
def delete_item(item_id: int):
    """
    Delete an item by its ID.
    """
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")

    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            return
    raise HTTPException(status_code=404, detail="Item not found")
