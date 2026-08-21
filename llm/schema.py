from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    billing = "billing"
    bug = "bug"
    feature = "feature"
    other = "other"


class Urgency(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"


class SuggestedTeam(str, Enum):
    billing_support = "billing-support"
    engineering = "engineering"
    product = "product"
    general_support = "general-support"


class TriageResult(BaseModel):
    category: Category
    urgency: Urgency
    suggested_team: SuggestedTeam
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
