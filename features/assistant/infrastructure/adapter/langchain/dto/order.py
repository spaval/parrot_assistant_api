from langchain_core.pydantic_v1 import BaseModel, Field

class Order(BaseModel):
    """Information about an order."""

    product: str = Field(..., description="The name of the product")
    quantity: int = Field(..., description="The number of products")
    price: float = Field(..., description="The price of the product")
    color: str = Field(..., description="The color of the product")
    size: str = Field(..., description="The size of the product")
    payment_method: str = Field(..., description="The payment method")
    address: str = Field(..., description="The address of the customer")