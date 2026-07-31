import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class RawExperienceRound(BaseModel):
    roundNumber: int
    type: Optional[str] = None
    description: str
    cleared: Optional[bool] = None

class RawRecord(BaseModel):
    """
    Base representation of a scraped record before transformation/classification.
    Mapped heavily to what raw_scraped_data expects.
    """
    sourceId: int
    sourcePriority: int
    sourceUrl: str
    recordType: Literal['question', 'experience']
    
    # Common extracted
    companySlug: str
    problemSummary: Optional[str] = None
    experienceText: Optional[str] = None
    leetcodeUrl: Optional[str] = None
    
    # Optional / Extracted if structured source
    roundType: Optional[str] = None
    difficulty: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    
    # Experience specifics
    role: Optional[str] = None
    outcome: Optional[str] = None
    interviewDate: Optional[str] = None
    roundsCount: Optional[int] = None
    rounds: List[RawExperienceRound] = Field(default_factory=list)
    
    cautionSource: bool = False

    # Pipeline Meta
    status: Literal['pending', 'deduped', 'clean', 'classified', 'promoted', 'duplicate', 'error'] = 'pending'
    errorType: Optional[Literal['retryable', 'permanent']] = None
    errorMessage: Optional[str] = None
    promotedQuestionId: Optional[str] = None  # MongoDB ObjectId string
    scrapedAt: datetime = Field(default_factory=datetime.utcnow)
