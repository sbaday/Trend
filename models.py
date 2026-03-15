from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class SignalOutput(BaseModel):
    id: Optional[int] = None
    source: str
    raw_title: str
    url: Optional[str] = None
    engagement: int = 0
    captured_at: str

class PhraseOutput(BaseModel):
    normalized_phrase: str
    confidence_score: float

class ScoringOutput(BaseModel):
    humor: int = Field(default=5, ge=1, le=10)
    identity: int = Field(default=5, ge=1, le=10)
    giftability: int = Field(default=5, ge=1, le=10)
    design_simplicity: int = Field(default=5, ge=1, le=10)
    niche: Literal[
        "Pets", "Fitness", "Gaming", "Funny", "Occupation", 
        "Hobby", "Family", "Holiday", "Aesthetic", "Politics", 
        "Crypto", "General"
    ] = "General"
    reasoning: str = ""
    final_score: float = 0.0

class EtsyListingOutput(BaseModel):
    title: str
    description: str
    tags: List[str]

class SocialContentOutput(BaseModel):
    tiktok_hook: str
    pinterest_title: str
    instagram_caption: str

class OutputResult(BaseModel):
    design_prompt: Optional[str] = None
    etsy_listing: Optional[EtsyListingOutput] = None
    social_content: Optional[SocialContentOutput] = None
    printify_draft_id: Optional[str] = None

class EmbeddingOutput(BaseModel):
    vector: List[float] = Field(default_factory=list)

class TrendContext(BaseModel):
    """Bütün pipeline boyunca trendin state'ini tutan Workflow Context nesnesi"""
    trend_id: Optional[int] = None
    signal: SignalOutput
    phrase: Optional[PhraseOutput] = None
    embedding: Optional[EmbeddingOutput] = None
    scores: Optional[ScoringOutput] = None
    outputs: OutputResult = Field(default_factory=OutputResult)
