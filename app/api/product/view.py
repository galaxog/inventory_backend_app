import logging

from fastapi import APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app import models
from app.api.product.schemas import (
    ProductCreateRequest,
    ProductCreateResponse,
    UpdateProductInventoryRequest
)
from app.api.product.exceptions import (
    ProductAlreadyExistsException,
    ProductNotFoundException,
    InvalidInventoryUpdateException
)

logger = logging.getLogger("api")
router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def create_product(validated_data: ProductCreateRequest):
    """
    Create a new product. if there isn't a matching one already existing in the DB
    :param validated_data: ProductCreateRequest
    """

    # Check if product with the same name already exists
    existing_product = models.Product.query.filter(
        models.Product.name == validated_data.name
    ).one_or_none()

    if existing_product is not None:
        logger.error("Product creation failed: Product with name '%s' already exists.", validated_data.name)
        raise ProductAlreadyExistsException(
            description=f"Product with name '{validated_data.name}' already exists."
        )

    # Create new product
    new_product = models.Product(
        name=validated_data.name,
        description=validated_data.description,
        price=validated_data.price,
        inventory=validated_data.inventory,
    )

    # Add to the database session and commit
    models.db.session.add(new_product)
    models.db.session.commit()

    logger.info("Created new product with ID %s", new_product.id)

    response_data = ProductCreateResponse(
        id=new_product.id,
        name=new_product.name,
        description=new_product.description,
        price=new_product.price,
        inventory=new_product.inventory,
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(response_data),
    )

@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Retrieve a product by its ID.
    :param product_id: ID of the product to retrieve
    """

    product = models.Product.query.filter(
        models.Product.id == product_id
    ).one_or_none()

    if product is None:
        logger.error("Product retrieval failed: Product with ID '%s' not found.", product_id)
        raise ProductNotFoundException(
            description=f"Product with ID '{product_id}' not found."
        )

    response_data = ProductCreateResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        inventory=product.inventory,
    )

    logger.info("Retrieved product with ID %s", product.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(response_data),
    )

@router.post("/{product_id}/update_inventory")
async def update_product_inventory(
    product_id: int, validated_data: UpdateProductInventoryRequest
):
    """
    Update the inventory of a product.
    :param product_id: ID of the product to update
    :param validated_data: UpdateProductInventoryRequest
    """

    product = models.Product.query.filter(
        models.Product.id == product_id
    ).one_or_none()

    if product is None:
        logger.error("Inventory update failed: Product with ID '%s' not found.", product_id)
        raise ProductNotFoundException(
            description=f"Product with ID '{product_id}' not found."
        )

    try:
        product.update_inventory(
            quantity=validated_data.quantity,
            type=validated_data.type,
            reason_code=validated_data.reason_code,
        )
        logger.info("Updated inventory for product ID %s", product.id)
    except ValueError as e:
        logger.error("Inventory update failed for product ID %s: %s", product.id, str(e))
        raise InvalidInventoryUpdateException(description=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Inventory updated successfully."},
    )
