from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.config import get_settings
from app.core.logging_config import setup_logging


router = APIRouter()

logger = setup_logging(get_settings().log_level)


class ItemCreate(BaseModel):
    """
    Schema for creating a new item.
    """
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemUpdate(BaseModel):
    """
    Schema for updating an existing item.
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None

class ItemResponse(BaseModel):
    """
    Schema for item response.
    """
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ItemsListResponse(BaseModel):
    """
    Schema for the response containing a list of items.
    """
    message: str
    items: List[ItemResponse]

items = []
next_id = 0

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create Item", tags=["Items"])
def create_item(item: ItemCreate):
    """
    Create a new item with the provided details.
    """
    logger.info(f"Create item request: name={item.name}, price={item.price}, tax={item.tax}")
    if item.price < 0:
            logger.warning(f"Error while creating item: name={item.name}, price={item.price}, tax={item.tax} - Price must be a positive value")
            raise HTTPException(status_code=400, detail="Price must be a positive value")
    if item.tax is not None and item.tax < 0:
            logger.warning(f"Error while creating item: name={item.name}, price={item.price}, tax={item.tax} - Tax must be a positive value")
            raise HTTPException(status_code=400, detail="Tax must be a positive value")
    global next_id
    next_id += 1
    item_id = next_id
        
    new_item = ItemResponse(id=item_id, **item.model_dump())
    items.append(new_item)
    logger.info(f"Item created: id={item_id}")
    return new_item
    


@router.get("/items", response_model=ItemsListResponse, status_code=status.HTTP_200_OK, summary="Get All Items", tags=["Items"])
def list_items():
    """
    Return all items with a custom message.
    """
    logger.info(f"List items request: total_items={len(items)}")
    return {
        "message": "Items retrieved successfully",
        "items": items,
    }

@router.get("/items/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK, summary="Get Item by ID", tags=["Items"])
def get_item(item_id: int):
    """
    Retrieve an item by its ID.
    """
    logger.info(f"Get item request: item_id={item_id}")
    if item_id <= 0:
        logger.warning(f"Error while retrieving item: item_id={item_id} - Item ID must be a positive integer")    
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")

    for item in items:
        if item.id == item_id:
            logger.info(f"Item found: {item}")
            return  item 
    logger.warning(f"Error while retrieving item: item_id={item_id} - Item not found")
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/items/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK, summary="Update Item by ID", tags=["Items"])
def update_item(item_id: int, updated_item: ItemUpdate):
    """
    Update an existing item by its ID.
    
    """
    if item_id <= 0:
        logger.warning(f"Error while updating item: item_id={item_id} - Item ID must be a positive integer")
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")

    for index, item in enumerate(items):
        if item.id == item_id:
            patch_data = updated_item.model_dump(exclude_unset=True)

            if "price" in patch_data and patch_data["price"] is not None and patch_data["price"] < 0:
                logger.warning(f"Error while updating item: item_id={item_id} - Price must be a positive value")
                raise HTTPException(status_code=400, detail="Price must be a positive value")

            if "tax" in patch_data and patch_data["tax"] is not None and patch_data["tax"] < 0:
                logger.warning(f"Error while updating item: item_id={item_id} - Tax must be a positive value")
                raise HTTPException(status_code=400, detail="Tax must be a positive value")

            merged_data = item.model_dump()
            merged_data.update(patch_data)
            merged_data["id"] = item_id

            updated_item_response = ItemResponse(**merged_data)
            items[index] = updated_item_response
            logger.info(f"Item updated: item_id={item_id}")
            return updated_item_response
    logger.warning(f"Error while updating item: item_id={item_id} - Item not found")
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Item by ID", tags=["Items"])
def delete_item(item_id: int):
    """
    Delete an item by its ID.
    """
    if item_id <= 0:
        logger.warning(f"Error while deleting item: item_id={item_id} - Item ID must be a positive integer")
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer")

    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            logger.info(f"Item deleted: item_id={item_id}")
            return
    logger.warning(f"Error while deleting item: item_id={item_id} - Item not found")
    raise HTTPException(status_code=404, detail="Item not found")
