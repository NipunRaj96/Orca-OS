"""
Progress indicators for Orca OS operations.
Shows real-time progress in terminal.
"""

import asyncio
from typing import Optional, Callable
from contextlib import asynccontextmanager

from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn,
    TimeElapsedColumn, TimeRemainingColumn, TaskID
)
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()


class ProgressIndicator:
    """Shows progress for Orca operations."""
    
    def __init__(self):
        """Initialize progress indicator."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        )
    
    @asynccontextmanager
    async def thinking(self, message: str = "🤖 Orca is thinking..."):
        """Show thinking indicator."""
        with self.progress:
            task = self.progress.add_task(message, total=None)
            try:
                yield task
            finally:
                self.progress.remove_task(task)
    
    @asynccontextmanager
    async def operation(self, message: str, total: int = 100):
        """Show operation progress."""
        with self.progress:
            task = self.progress.add_task(message, total=total)
            try:
                yield task
            finally:
                self.progress.update(task, completed=total)
    
    def update(self, task: TaskID, advance: int = 1, description: Optional[str] = None):
        """Update progress."""
        self.progress.update(task, advance=advance, description=description)


class StepProgress:
    """Shows step-by-step progress for complex operations."""
    
    def __init__(self, steps: list):
        """Initialize step progress."""
        self.steps = steps
        self.current_step = 0
        self.completed_steps = []
    
    def start(self):
        """Start step progress."""
        console.print(f"[cyan]Starting operation with {len(self.steps)} steps...[/cyan]\n")
    
    def next_step(self, step_name: Optional[str] = None):
        """Move to next step."""
        if step_name:
            self.steps[self.current_step] = step_name
        
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            console.print(f"[yellow]⏳ Step {self.current_step + 1}/{len(self.steps)}:[/yellow] {step}")
            self.current_step += 1
    
    def complete_step(self, message: Optional[str] = None):
        """Mark current step as complete."""
        if self.current_step > 0:
            step = self.steps[self.current_step - 1]
            status = message or "✅ Complete"
            console.print(f"[green]   {status}[/green]\n")
            self.completed_steps.append(step)
    
    def finish(self):
        """Finish all steps."""
        console.print(f"[green]✅ All {len(self.steps)} steps completed![/green]\n")


def show_thinking(message: str = "🤖 Orca is thinking..."):
    """Simple thinking indicator."""
    return console.status(message, spinner="dots")


def show_progress_bar(message: str, total: int = 100):
    """Show a progress bar."""
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    )
    
    with progress:
        task = progress.add_task(message, total=total)
        return task, progress


def show_steps(steps: list, operation_name: str = "Operation"):
    """Show step-by-step progress."""
    console.print(f"\n[bold cyan]{operation_name}[/bold cyan]")
    console.print(f"[dim]Total steps: {len(steps)}[/dim]\n")
    
    for i, step in enumerate(steps, 1):
        console.print(f"[yellow]Step {i}/{len(steps)}:[/yellow] {step}")
        yield i
        console.print(f"[green]   ✅ Complete[/green]\n")
    
    console.print(f"[bold green]✅ {operation_name} completed![/bold green]\n")

