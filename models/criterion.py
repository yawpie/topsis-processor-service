from pydantic import BaseModel

class CriterionBody(BaseModel):
    name: str
    weight: float
    type: str

class Criterion:
    def __init__(self, name: str, weight: float, type: str):
        self.name = name
        self.weight = weight
        self.type = type