import csv
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Class, HomeworkTask, Student, Submission, UploadImage
from .ocr_client import OcrConfigError, recognize_text
from .schemas import (
    ClassCreate,
    ClassOut,
    HomeworkReport,
    HomeworkReportEntry,
    HomeworkTaskCreate,
    HomeworkTaskOut,
    OcrRecognizeRequest,
    OcrRecognizeResponse,
    SubmissionConfirm,
    SubmissionOut,
    StudentOut,
    UploadImageOut,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Homework OCR Tracker")

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "images")


def _ensure_image_dir():
    os.makedirs(IMAGE_DIR, exist_ok=True)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


@app.post("/classes", response_model=ClassOut)
def create_class(payload: ClassCreate, db: Session = Depends(get_db)):
    existing = db.query(Class).filter(Class.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Class name already exists")
    class_item = Class(name=payload.name)
    db.add(class_item)
    db.commit()
    db.refresh(class_item)
    return class_item


@app.post("/students/import", response_model=List[StudentOut])
def import_students(
    class_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="Class not found")
    if not file.filename.endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV or TXT files are supported")
    content = file.file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(content)
    students = []
    for row in reader:
        name = (row.get("name") or row.get("姓名") or "").strip()
        student_number = (row.get("student_number") or row.get("学号") or "").strip() or None
        if not name:
            continue
        existing = (
            db.query(Student)
            .filter(Student.class_id == class_id, Student.name == name)
            .first()
        )
        if existing:
            continue
        student = Student(class_id=class_id, name=name, student_number=student_number)
        db.add(student)
        students.append(student)
    db.commit()
    for student in students:
        db.refresh(student)
    return students


@app.post("/homework_tasks", response_model=HomeworkTaskOut)
def create_homework_task(payload: HomeworkTaskCreate, db: Session = Depends(get_db)):
    class_item = db.query(Class).filter(Class.id == payload.class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="Class not found")
    task = HomeworkTask(
        class_id=payload.class_id,
        subject=payload.subject,
        due_date=payload.due_date,
        notes=payload.notes,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.post("/images/upload", response_model=UploadImageOut)
def upload_image(
    class_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    class_item = db.query(Class).filter(Class.id == class_id).first()
    if not class_item:
        raise HTTPException(status_code=404, detail="Class not found")
    _ensure_image_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename = f"{timestamp}_{file.filename}"
    storage_path = os.path.join(IMAGE_DIR, filename)
    with open(storage_path, "wb") as buffer:
        buffer.write(file.file.read())
    image = UploadImage(
        class_id=class_id,
        filename=file.filename,
        storage_path=storage_path,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@app.post("/ocr/recognize", response_model=OcrRecognizeResponse)
def recognize_name(payload: OcrRecognizeRequest, db: Session = Depends(get_db)):
    image = db.query(UploadImage).filter(UploadImage.id == payload.image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    recognized_text = (payload.recognized_text or "").strip()
    if not recognized_text:
        try:
            recognized_text = recognize_text(image.storage_path) or ""
        except OcrConfigError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=500, detail="OCR service failed") from error
    if not recognized_text:
        raise HTTPException(status_code=400, detail="recognized_text is required when OCR is demo mode")

    students = db.query(Student).filter(Student.class_id == payload.class_id).all()
    candidates = []
    for student in students:
        score = _similarity(recognized_text, student.name)
        candidates.append({
            "student_id": student.id,
            "name": student.name,
            "score": round(score, 3),
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    top_candidates = candidates[:5]

    image.ocr_text = recognized_text
    image.ocr_confidence = int(top_candidates[0]["score"] * 100) if top_candidates else 0
    db.commit()

    return OcrRecognizeResponse(
        image_id=image.id,
        recognized_text=recognized_text,
        candidates=top_candidates,
    )


@app.post("/submissions/confirm", response_model=SubmissionOut)
def confirm_submission(payload: SubmissionConfirm, db: Session = Depends(get_db)):
    task = db.query(HomeworkTask).filter(HomeworkTask.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    submission = (
        db.query(Submission)
        .filter(Submission.task_id == payload.task_id, Submission.student_id == payload.student_id)
        .first()
    )
    if submission:
        submission.status = payload.status
        submission.image_id = payload.image_id
        submission.source = payload.source
        submission.updated_at = datetime.utcnow()
    else:
        submission = Submission(
            task_id=payload.task_id,
            student_id=payload.student_id,
            image_id=payload.image_id,
            status=payload.status,
            source=payload.source,
        )
        db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@app.get("/reports/homework/{task_id}", response_model=HomeworkReport)
def homework_report(task_id: int, db: Session = Depends(get_db)):
    task = db.query(HomeworkTask).filter(HomeworkTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    students = db.query(Student).filter(Student.class_id == task.class_id).all()
    submissions = (
        db.query(Submission)
        .filter(Submission.task_id == task_id)
        .all()
    )
    submission_map = {s.student_id: s for s in submissions}

    entries = []
    totals = {"submitted": 0, "missing": 0, "pending": 0}
    for student in students:
        submission = submission_map.get(student.id)
        status = submission.status if submission else "pending"
        if status not in totals:
            totals[status] = 0
        totals[status] += 1
        entries.append(
            HomeworkReportEntry(
                student_id=student.id,
                name=student.name,
                student_number=student.student_number,
                status=status,
                image_id=submission.image_id if submission else None,
            )
        )

    return HomeworkReport(
        task_id=task.id,
        subject=task.subject,
        totals=totals,
        entries=entries,
    )


@app.get("/")
def root():
    return JSONResponse({"status": "ok", "message": "Homework OCR Tracker API"})
