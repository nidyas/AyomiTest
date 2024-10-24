from pydantic import BaseModel

class OperationCreate(BaseModel):
    expression: str
    result: float

    class Config:
        orm_mode = True
