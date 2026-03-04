from canvasapi import Canvas
from canvasapi.course import Course
from datetime import datetime
from rich.console import Console
from .models import CanvasCourse, CanvasModule, CanvasModuleItem, CanvasAssignment, CanvasPage

console = Console()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class CanvasClient:
    def __init__(self, api_url: str, access_token: str):
        self._canvas = Canvas(api_url, access_token)

    def get_courses(self) -> list[CanvasCourse]:
        courses = self._canvas.get_courses(enrollment_type="student", state=["available"])
        result = []
        for c in courses:
            code = getattr(c, "course_code", "") or ""
            name = getattr(c, "name", "") or ""
            start = _parse_dt(getattr(c, "start_at", None))
            result.append(CanvasCourse(id=c.id, code=code, name=name, start_at=start))
        return result

    def get_course(self, course_code: str) -> CanvasCourse | None:
        for course in self.get_courses():
            if course.code.upper() == course_code.upper():
                return course
        return None

    def get_modules(self, course: CanvasCourse) -> list[CanvasModule]:
        raw_course: Course = self._canvas.get_course(course.id)
        modules = raw_course.get_modules(include=["items"])
        result = []
        for m in modules:
            unlock_at = _parse_dt(getattr(m, "unlock_at", None))
            module = CanvasModule(
                id=m.id,
                course_id=course.id,
                name=m.name,
                position=m.position,
                unlock_at=unlock_at,
            )
            for item in getattr(m, "items", []):
                module.items.append(CanvasModuleItem(
                    id=item["id"],
                    module_id=m.id,
                    title=item["title"],
                    type=item["type"],
                    url=item.get("url"),
                    page_url=item.get("page_url"),
                    content_id=item.get("content_id"),
                ))
            result.append(module)
        return result

    def get_assignments(self, course: CanvasCourse) -> list[CanvasAssignment]:
        raw_course: Course = self._canvas.get_course(course.id)
        assignments = raw_course.get_assignments()
        result = []
        for a in assignments:
            result.append(CanvasAssignment(
                id=a.id,
                course_id=course.id,
                name=a.name,
                due_at=_parse_dt(getattr(a, "due_at", None)),
                points_possible=getattr(a, "points_possible", None),
                description=getattr(a, "description", "") or "",
                submission_types=getattr(a, "submission_types", []),
            ))
        return result

    def get_page(self, course: CanvasCourse, page_url: str) -> CanvasPage | None:
        try:
            raw_course: Course = self._canvas.get_course(course.id)
            page = raw_course.get_page(page_url)
            return CanvasPage(
                url=page.url,
                title=page.title,
                body=getattr(page, "body", "") or "",
                updated_at=_parse_dt(getattr(page, "updated_at", None)),
            )
        except Exception as e:
            console.print(f"[yellow]Warning: could not fetch page '{page_url}': {e}[/yellow]")
            return None
