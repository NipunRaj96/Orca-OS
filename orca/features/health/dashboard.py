"""
Health Dashboard for Orca OS.
Terminal-friendly health score display.
"""

import logging
from typing import Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich import box

from .score_engine import HealthScoreEngine
from .monitor import HealthMonitor

logger = logging.getLogger(__name__)
console = Console()


class HealthDashboard:
    """Displays system health in terminal."""
    
    def __init__(self):
        """Initialize health dashboard."""
        self.score_engine = HealthScoreEngine()
        self.monitor = HealthMonitor()
    
    def show_health_score(self, show_trend: bool = False):
        """Display health score in terminal."""
        try:
            # Get current health
            health_data = self.score_engine.calculate_overall_score()
            
            # Overall score panel
            score = health_data['overall_score']
            status = health_data['status']
            emoji = health_data['status_emoji']
            
            console.print(Panel(
                f"[bold white]{score:.1f}/100[/bold white]",
                title=f"{emoji} Overall Health Score: {status.upper()}",
                border_style="green" if score >= 75 else "yellow" if score >= 60 else "red"
            ))
            
            # Breakdown table
            breakdown_table = Table(title="Score Breakdown", box=box.ROUNDED)
            breakdown_table.add_column("Category", style="cyan", width=15)
            breakdown_table.add_column("Score", style="white", width=10, justify="right")
            breakdown_table.add_column("Weight", style="yellow", width=10)
            breakdown_table.add_column("Status", style="green", width=12)
            
            breakdown = health_data['breakdown']
            for category, data in breakdown.items():
                cat_score = data['score']
                weight = data['weight'] * 100
                
                # Status based on score
                if cat_score >= 80:
                    status_text = "[green]✅ Good[/green]"
                elif cat_score >= 60:
                    status_text = "[yellow]⚠️  Fair[/yellow]"
                else:
                    status_text = "[red]❌ Poor[/red]"
                
                breakdown_table.add_row(
                    category.capitalize(),
                    f"{cat_score:.1f}",
                    f"{weight:.0f}%",
                    status_text
                )
            
            console.print(breakdown_table)
            
            # Visual progress bars
            console.print("\n[bold]Score Visualization:[/bold]")
            for category, data in breakdown.items():
                score = data['score']
                self._show_score_bar(category.capitalize(), score)
            
            # Recommendations
            recommendations = health_data.get('recommendations', [])
            if recommendations:
                console.print("\n[bold yellow]💡 Recommendations:[/bold yellow]")
                for rec in recommendations:
                    console.print(f"   • {rec}")
            
            # Show trend if requested
            if show_trend:
                self._show_trend()
            
        except Exception as e:
            logger.error(f"Error showing health score: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    def _show_score_bar(self, label: str, score: float):
        """Show a score progress bar."""
        progress = Progress(
            TextColumn(f"[cyan]{label:15}[/cyan]"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        )
        
        with progress:
            task = progress.add_task(label, total=100)
            progress.update(task, completed=score)
    
    def _show_trend(self):
        """Show health trend."""
        try:
            trend = self.monitor.get_health_trend(24)
            
            if 'error' in trend:
                console.print(f"\n[yellow]{trend['error']}[/yellow]")
                return
            
            trend_table = Table(title="24-Hour Trend", box=box.ROUNDED)
            trend_table.add_column("Metric", style="cyan")
            trend_table.add_column("Value", style="white")
            
            trend_table.add_row("Average Score", f"{trend['average_score']:.1f}")
            trend_table.add_row("Min Score", f"{trend['min_score']:.1f}")
            trend_table.add_row("Max Score", f"{trend['max_score']:.1f}")
            trend_table.add_row("Trend", trend['trend'].capitalize())
            trend_table.add_row("Change", f"{trend['change']:+.1f}")
            
            console.print(trend_table)
        except Exception as e:
            logger.error(f"Error showing trend: {e}")
    
    def show_detailed_breakdown(self):
        """Show detailed breakdown of health scores."""
        health_data = self.score_engine.calculate_overall_score()
        breakdown = health_data['breakdown']
        
        for category, data in breakdown.items():
            details = data['details']
            
            detail_table = Table(title=f"{category.capitalize()} Details", box=box.ROUNDED)
            detail_table.add_column("Metric", style="cyan")
            detail_table.add_column("Value", style="white")
            
            for key, value in details.items():
                detail_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(detail_table)
            console.print()  # Empty line between categories

