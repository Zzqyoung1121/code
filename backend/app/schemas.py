from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ClassOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class StudentOut(BaseModel):
    id: int
    class_id: int
    name: str
    student_number: Optional[str]

    class Config:
        from_attributes = True


class HomeworkTaskCreate(BaseModel):
    class_id: int
    subject: str
    due_date: Optional[date] = None
    notes: Optional[str] = None


class HomeworkTaskOut(BaseModel):
    id: int
    class_id: int
    subject: str
    due_date: Optional[date]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UploadImageOut(BaseModel):
    id: int
    class_id: int
    filename: str
    storage_path: str

    class Config:
        from_attributes = True


class OcrRecognizeRequest(BaseModel):
    class_id: int
    image_id: int
    recognized_text: Optional[str] = None


class OcrCandidate(BaseModel):
    student_id: int
    name: str
    score: float


class OcrRecognizeResponse(BaseModel):
    image_id: int
    recognized_text: str
    candidates: List[OcrCandidate]


class SubmissionConfirm(BaseModel):
    task_id: int
    student_id: int
    image_id: Optional[int] = None
    status: str = Field(..., pattern="^(submitted|missing|pending)$")
    source: str = "manual"


class SubmissionOut(BaseModel):
    id: int
    task_id: int
    student_id: int
    image_id: Optional[int]
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HomeworkReportEntry(BaseModel):
    student_id: int
    name: str
    student_number: Optional[str]
    status: str
    image_id: Optional[int]


class HomeworkReport(BaseModel):
    task_id: int
    subject: str
    totals: dict
    entries: List[HomeworkReportEntry]
