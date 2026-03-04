from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CanvasCourse:
    id: int
    code: str          # e.g. "CAB401"
    name: str          # e.g. "High Performance and Parallel Computing"
    start_at: datetime | None = None


@dataclass
class CanvasModuleItem:
    id: int
    module_id: int
    title: str
    type: str          # "Page", "Assignment", "File", "ExternalUrl", etc.
    url: str | None = None       # API URL for the resource
    page_url: str | None = None  # Canvas page slug (for type=Page)
    content_id: int | None = None


@dataclass
class CanvasModule:
    id: int
    course_id: int
    name: str          # e.g. "Week 2 - Different Forms of Parallel Computing"
    position: int
    unlock_at: datetime | None = None
    items: list[CanvasModuleItem] = field(default_factory=list)


@dataclass
class CanvasAssignment:
    id: int
    course_id: int
    name: str
    due_at: datetime | None = None
    points_possible: float | None = None
    description: str = ""       # HTML
    submission_types: list[str] = field(default_factory=list)


@dataclass
class CanvasPage:
    url: str           # page slug
    title: str
    body: str          # HTML content
    updated_at: datetime | None = None
