"""
File Management CLI for Orca OS.
Terminal-friendly file organization commands.
"""

import logging
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from .analyzer import FileAnalyzer
from .organizer import FileOrganizer

logger = logging.getLogger(__name__)
console = Console()


class FileManagementCLI:
    """CLI interface for file management."""
    
    def __init__(self):
        """Initialize file management CLI."""
        self.analyzer = FileAnalyzer()
        self.organizer = FileOrganizer()
    
    def analyze_directory(self, directory: str):
        """Analyze and display directory contents."""
        console.print(f"[cyan]📊 Analyzing directory: {directory}[/cyan]\n")
        
        analysis = self.analyzer.analyze_directory(directory)
        
        if 'error' in analysis:
            console.print(f"[red]Error: {analysis['error']}[/red]")
            return
        
        # Summary table
        summary_table = Table(title="Directory Analysis", box=box.ROUNDED)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Total Files", str(analysis['total_files']))
        summary_table.add_row("Total Size", f"{analysis['total_size_mb']} MB")
        summary_table.add_row("Categories", str(len(analysis['categories'])))
        summary_table.add_row("File Types", str(len(analysis['file_types'])))
        summary_table.add_row("Duplicates", str(len(analysis['duplicates'])))
        
        console.print(summary_table)
        
        # Categories breakdown
        if analysis['categories']:
            console.print("\n[bold]Categories:[/bold]")
            cat_table = Table(box=box.SIMPLE)
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Files", style="white", justify="right")
            cat_table.add_column("Size (MB)", style="yellow", justify="right")
            
            for category, files in analysis['categories'].items():
                total_size = sum(f.get('size_mb', 0) for f in files)
                cat_table.add_row(category.capitalize(), str(len(files)), f"{total_size:.2f}")
            
            console.print(cat_table)
        
        # Suggestions
        suggestions = analysis.get('organization_suggestions', [])
        if suggestions:
            console.print("\n[bold yellow]💡 Organization Suggestions:[/bold yellow]")
            for suggestion in suggestions:
                console.print(f"   • {suggestion}")
    
    def organize_directory(
        self,
        directory: str,
        strategy: str = 'category',
        preview: bool = True
    ):
        """Organize directory with preview option."""
        console.print(f"[cyan]🗂️  Organizing directory: {directory}[/cyan]")
        console.print(f"[dim]Strategy: {strategy}[/dim]\n")
        
        # Preview first
        if preview:
            console.print("[yellow]📋 Preview (dry-run):[/yellow]")
            preview_result = self.organizer.preview_organization(directory, strategy)
            
            if 'error' in preview_result:
                console.print(f"[red]Error: {preview_result['error']}[/red]")
                return
            
            # Show what will happen
            actions = preview_result.get('actions', [])
            folders = [a for a in actions if a['action'] == 'create_folder']
            moves = [a for a in actions if a['action'] == 'move']
            
            console.print(f"[cyan]Will create {len(folders)} folders[/cyan]")
            console.print(f"[cyan]Will move {len(moves)} files[/cyan]\n")
            
            # Show folder structure
            if folders:
                console.print("[bold]Folders to create:[/bold]")
                for folder in folders[:10]:  # Show first 10
                    console.print(f"   📁 {folder['path']}")
                if len(folders) > 10:
                    console.print(f"   ... and {len(folders) - 10} more")
            
            # Ask for confirmation (skip in non-interactive mode)
            import sys
            if sys.stdin.isatty():  # Only ask if terminal is interactive
                if not Confirm.ask("\n[bold yellow]Proceed with organization?[/bold yellow]"):
                    console.print("[yellow]Cancelled[/yellow]")
                    return
            else:
                console.print("[cyan]Proceeding with organization...[/cyan]")
        
        # Perform organization
        console.print("\n[green]🔄 Organizing files...[/green]")
        result = self.organizer.organize_directory(directory, strategy, dry_run=False)
        
        if 'error' in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return
        
        # Show results
        console.print(f"\n[green]✅ {result['summary']}[/green]")
        
        # Show actions summary
        actions = result.get('actions', [])
        successful = [a for a in actions if a.get('success', False)]
        failed = [a for a in actions if 'error' in a]
        
        if successful:
            console.print(f"[green]   ✅ {len(successful)} files moved successfully[/green]")
        if failed:
            console.print(f"[red]   ❌ {len(failed)} files failed to move[/red]")
            for fail in failed[:5]:
                console.print(f"      [dim]{fail.get('error', 'Unknown error')}[/dim]")

