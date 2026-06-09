from typing import Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponseBase(BaseModel):
    """
    Standard base configuration for all API schemas.
    Configures Pydantic to read ORM models automatically.
    """
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(APIResponseBase, Generic[T]):
    """
    Standard envelope format for paginated queries.
    """
    items: List[T]
    total: int
    offset: int
    limit: int
