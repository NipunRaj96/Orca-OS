"""
Analytics dashboard for displaying user behavior insights.
Terminal-friendly visualizations and reports.
"""

import logging
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.layout import Layout
from rich.text import Text

from .engine import AnalyticsEngine
from .patterns import PatternRecognizer

logger = logging.getLogger(__name__)
console = Console()


class AnalyticsDashboard:
    """Terminal-friendly analytics dashboard."""
    
    def __init__(self, user_id: str = "default"):
        """Initialize analytics dashboard."""
        self.engine = AnalyticsEngine(user_id)
        self.patterns = PatternRecognizer(user_id)
        self.user_id = user_id
    
    def show_usage_stats(self, days: int = 30):
        """Display usage statistics."""
        console.print(f"\n[bold cyan]📊 Usage Statistics (Last {days} days)[/bold cyan]\n")
        
        with console.status("[bold green]Analyzing usage...") as status:
            stats = self.engine.get_usage_stats(days)
        
        if not stats:
            console.print("[yellow]No usage data available[/yellow]")
            return
        
        # Main stats table
        stats_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric", style="cyan", width=25)
        stats_table.add_column("Value", style="white", justify="right")
        
        stats_table.add_row("Total Queries", f"{stats['total_queries']:,}")
        stats_table.add_row("Successful Commands", f"{stats['successful_commands']:,}")
        stats_table.add_row("Failed Commands", f"{stats['failed_commands']:,}")
        stats_table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
        stats_table.add_row("Avg Execution Time", f"{stats['avg_execution_time']:.2f}s")
        
        console.print(stats_table)
        
        # Hour distribution
        if stats.get('hour_distribution'):
            console.print("\n[bold]⏰ Activity by Hour:[/bold]")
            hour_table = Table(box=box.SIMPLE, show_header=False)
            hour_table.add_column("Hour", style="dim", width=8)
            hour_table.add_column("Count", style="cyan", justify="right", width=10)
            hour_table.add_column("Bar", style="green", width=30)
            
            sorted_hours = sorted(stats['hour_distribution'].items())
            max_count = max(stats['hour_distribution'].values()) if stats['hour_distribution'] else 1
            
            for hour, count in sorted_hours:
                bar_length = int((count / max_count) * 30)
                bar = "█" * bar_length
                hour_table.add_row(f"{hour:02d}:00", str(count), bar)
            
            console.print(hour_table)
    
    def show_productivity_metrics(self):
        """Display productivity metrics."""
        console.print("\n[bold cyan]📈 Productivity Metrics[/bold cyan]\n")
        
        with console.status("[bold green]Calculating productivity...") as status:
            metrics = self.engine.get_productivity_metrics()
        
        if not metrics:
            console.print("[yellow]No productivity data available[/yellow]")
            return
        
        metrics_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        metrics_table.add_column("Metric", style="cyan", width=30)
        metrics_table.add_column("Value", style="white")
        
        metrics_table.add_row("Today's Queries", str(metrics.get('today_queries', 0)))
        metrics_table.add_row("This Week's Queries", str(metrics.get('week_queries', 0)))
        metrics_table.add_row("Avg Daily Queries", f"{metrics.get('avg_daily_queries', 0):.1f}")
        
        if metrics.get('peak_hours'):
            peak_str = ", ".join([f"{h}:00" for h in metrics['peak_hours']])
            metrics_table.add_row("Peak Hours", peak_str)
        
        if metrics.get('most_productive_day'):
            metrics_table.add_row("Most Productive Day", metrics['most_productive_day'])
        
        console.print(metrics_table)
    
    def show_command_frequency(self, limit: int = 10):
        """Display most frequently used commands."""
        console.print(f"\n[bold cyan]🔥 Top {limit} Commands[/bold cyan]\n")
        
        with console.status("[bold green]Analyzing commands...") as status:
            commands = self.engine.get_command_frequency(limit)
        
        if not commands:
            console.print("[yellow]No command data available[/yellow]")
            return
        
        cmd_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        cmd_table.add_column("#", style="dim", width=3, justify="right")
        cmd_table.add_column("Command", style="white", width=40)
        cmd_table.add_column("Count", style="cyan", justify="right", width=8)
        cmd_table.add_column("Avg Time", style="yellow", justify="right", width=10)
        cmd_table.add_column("Success Rate", style="green", justify="right", width=12)
        
        for i, cmd_data in enumerate(commands, 1):
            cmd_table.add_row(
                str(i),
                cmd_data['command'][:40],
                str(cmd_data['count']),
                f"{cmd_data['avg_time']:.2f}s",
                f"{cmd_data['success_rate']:.1f}%"
            )
        
        console.print(cmd_table)
    
    def show_patterns(self):
        """Display identified patterns."""
        console.print("\n[bold cyan]🔍 Usage Patterns[/bold cyan]\n")
        
        with console.status("[bold green]Identifying patterns...") as status:
            command_patterns = self.patterns.identify_command_patterns()
            time_patterns = self.patterns.identify_time_patterns()
        
        all_patterns = command_patterns + time_patterns
        
        if not all_patterns:
            console.print("[yellow]No patterns identified yet. Keep using Orca to discover patterns![/yellow]")
            return
        
        patterns_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        patterns_table.add_column("Type", style="cyan", width=20)
        patterns_table.add_column("Pattern", style="white", width=50)
        patterns_table.add_column("Frequency", style="yellow", justify="right", width=10)
        patterns_table.add_column("Confidence", style="green", justify="right", width=12)
        
        for pattern in all_patterns[:10]:
            patterns_table.add_row(
                pattern['type'].replace('_', ' ').title(),
                pattern['pattern'],
                str(pattern['frequency']),
                f"{pattern['confidence']:.1f}%"
            )
        
        console.print(patterns_table)
    
    def show_insights(self):
        """Display actionable insights."""
        console.print("\n[bold cyan]💡 Insights & Recommendations[/bold cyan]\n")
        
        with console.status("[bold green]Generating insights...") as status:
            insights = self.patterns.generate_insights()
        
        if not insights:
            console.print("[yellow]No insights available yet. Keep using Orca![/yellow]")
            return
        
        for insight in insights:
            priority_color = {
                'high': 'red',
                'medium': 'yellow',
                'low': 'green'
            }.get(insight.get('priority', 'medium'), 'white')
            
            panel = Panel(
                f"[bold]{insight['message']}[/bold]\n\n[dim]{insight.get('suggestion', '')}[/dim]",
                title=f"[{priority_color}]{insight['title']}[/{priority_color}]",
                border_style=priority_color,
                box=box.ROUNDED
            )
            console.print(panel)
    
    def show_trends(self, days: int = 7):
        """Display usage trends."""
        console.print(f"\n[bold cyan]📉 Trends (Last {days} days)[/bold cyan]\n")
        
        with console.status("[bold green]Analyzing trends...") as status:
            trends = self.engine.get_trends(days)
        
        if not trends or not trends.get('dates'):
            console.print("[yellow]No trend data available[/yellow]")
            return
        
        # Create trend visualization
        dates = trends['dates']
        counts = trends['query_counts']
        success_rates = trends['success_rates']
        
        if not dates:
            console.print("[yellow]No trend data available[/yellow]")
            return
        
        trend_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        trend_table.add_column("Date", style="cyan", width=12)
        trend_table.add_column("Queries", style="white", justify="right", width=10)
        trend_table.add_column("Query Bar", style="green", width=20)
        trend_table.add_column("Success Rate", style="yellow", justify="right", width=12)
        trend_table.add_column("Success Bar", style="blue", width=20)
        
        max_count = max(counts) if counts else 1
        max_success = max(success_rates) if success_rates else 100
        
        for date, count, success in zip(dates, counts, success_rates):
            count_bar_length = int((count / max_count) * 20)
            count_bar = "█" * count_bar_length
            
            success_bar_length = int((success / max_success) * 20)
            success_bar = "█" * success_bar_length
            
            trend_table.add_row(
                date,
                str(count),
                count_bar,
                f"{success:.1f}%",
                success_bar
            )
        
        console.print(trend_table)
    
    def show_full_dashboard(self, days: int = 30):
        """Display complete analytics dashboard."""
        console.print("\n[bold blue]╔═══════════════════════════════════════════════════════════╗[/bold blue]")
        console.print("[bold blue]║[/bold blue]  [bold white]🐋 Orca OS - Analytics Dashboard[/bold white]  [bold blue]║[/bold blue]")
        console.print("[bold blue]╚═══════════════════════════════════════════════════════════╝[/bold blue]\n")
        
        # Usage stats
        self.show_usage_stats(days)
        
        # Productivity metrics
        self.show_productivity_metrics()
        
        # Command frequency
        self.show_command_frequency(10)
        
        # Patterns
        self.show_patterns()
        
        # Trends
        self.show_trends(7)
        
        # Insights
        self.show_insights()
        
        console.print("\n[dim]Use 'orca \"show my usage patterns\"' for more details[/dim]\n")

