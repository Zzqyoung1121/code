from datetime import datetime
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", back_populates="class_ref")
    homework_tasks = relationship("HomeworkTask", back_populates="class_ref")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    student_number = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    class_ref = relationship("Class", back_populates="students")
    submissions = relationship("Submission", back_populates="student")


class HomeworkTask(Base):
    __tablename__ = "homework_tasks"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    due_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    class_ref = relationship("Class", back_populates="homework_tasks")
    submissions = relationship("Submission", back_populates="task")


class UploadImage(Base):
    __tablename__ = "upload_images"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(255), nullable=False)
    ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("homework_tasks.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    image_id = Column(Integer, ForeignKey("upload_images.id"), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="pending")
    source = Column(String(30), nullable=False, default="ocr")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("HomeworkTask", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")
