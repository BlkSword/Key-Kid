from pydantic import BaseModel, Field


class DetectionCandidate(BaseModel):
    name: str
    score: float = Field(ge=0, le=1)
    decoded: str | None = None

class BreakResult(BaseModel):
    algorithm: str
    plaintext: str
    key: str | None = None
    confidence: float = Field(ge=0, le=1)

class FactorResult(BaseModel):
    n: str
    factors: list[str]
