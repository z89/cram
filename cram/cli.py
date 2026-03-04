import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="cram", help="Canvas → Notion sync tool")
console = Console()


def _get_canvas():
    from .config import CANVAS_API_URL, CANVAS_ACCESS_TOKEN
    from .canvas.client import CanvasClient
    return CanvasClient(CANVAS_API_URL, CANVAS_ACCESS_TOKEN)


@app.command()
def courses():
    """List all available Canvas courses."""
    client = _get_canvas()
    console.print("[bold]Fetching courses from Canvas...[/bold]")
    course_list = client.get_courses()

    table = Table(title="Canvas Courses")
    table.add_column("ID", style="dim")
    table.add_column("Code", style="cyan")
    table.add_column("Name")
    table.add_column("Start Date", style="dim")

    for c in course_list:
        start = c.start_at.strftime("%Y-%m-%d") if c.start_at else "-"
        table.add_row(str(c.id), c.code, c.name, start)

    console.print(table)


@app.command()
def inspect(
    course_code: str = typer.Argument(..., help="Course code e.g. CAB401"),
):
    """Inspect Canvas modules and assignments for a course (dry run, no Notion writes)."""
    client = _get_canvas()

    course = client.get_course(course_code)
    if not course:
        console.print(f"[red]Course '{course_code}' not found.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold cyan]{course.code}: {course.name}[/bold cyan]")

    modules = client.get_modules(course)
    console.print(f"\n[bold]Modules ({len(modules)})[/bold]")
    for m in modules:
        date = m.unlock_at.strftime("%b %d %Y") if m.unlock_at else "no date"
        console.print(f"  [green]{m.position}.[/green] {m.name} [dim]({date})[/dim]")
        for item in m.items:
            console.print(f"       [dim]{item.type}[/dim]  {item.title}")

    assignments = client.get_assignments(course)
    console.print(f"\n[bold]Assignments ({len(assignments)})[/bold]")
    for a in assignments:
        due = a.due_at.strftime("%b %d %Y") if a.due_at else "no due date"
        pts = f"{a.points_possible:.0f}pts" if a.points_possible else "-"
        console.print(f"  [yellow]{a.name}[/yellow]  [dim]{due}  {pts}[/dim]")


@app.command()
def sync(
    course_code: str = typer.Argument(..., help="Course code e.g. CAB401"),
    debug: bool = typer.Option(False, "--debug", help="Write to debug Notion page instead of real university page"),
):
    """Sync a Canvas course into Notion."""
    console.print(f"[bold]Syncing {course_code}...[/bold]" + (" [yellow](debug mode)[/yellow]" if debug else ""))
    console.print("[dim]Sync engine not yet implemented — coming in Phase 2.[/dim]")


@app.command()
def daemon(
    interval: int = typer.Option(30, "--interval", help="Sync interval in minutes"),
):
    """Run cram as a background daemon, syncing all courses on a schedule."""
    console.print(f"[bold]Starting daemon (interval: {interval}m)...[/bold]")
    console.print("[dim]Daemon mode not yet implemented — coming in Phase 5.[/dim]")
