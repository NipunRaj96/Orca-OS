"""
Command templates for Orca OS.
Pre-built command templates with variables.
"""

import logging
from typing import List, Dict, Any, Optional
import re

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

logger = logging.getLogger(__name__)
console = Console()


class TemplateManager:
    """Manages command templates for Orca OS."""
    
    def __init__(self):
        """Initialize template manager."""
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load default templates."""
        return {
            'disk-usage': {
                'name': 'Check Disk Usage',
                'query': 'show me disk usage',
                'description': 'Check current disk usage',
                'category': 'system',
                'variables': []
            },
            'memory-usage': {
                'name': 'Check Memory Usage',
                'query': 'show me memory usage',
                'description': 'Check current memory usage',
                'category': 'system',
                'variables': []
            },
            'system-info': {
                'name': 'System Information',
                'query': 'show me system information',
                'description': 'Get comprehensive system information',
                'category': 'system',
                'variables': []
            },
            'optimize-system': {
                'name': 'Optimize System',
                'query': 'optimize my system',
                'description': 'Run system optimization',
                'category': 'maintenance',
                'variables': []
            },
            'clean-temp': {
                'name': 'Clean Temporary Files',
                'query': 'clean temporary files',
                'description': 'Remove temporary files',
                'category': 'maintenance',
                'variables': []
            },
            'process-kill': {
                'name': 'Kill Process',
                'query': 'kill process {process_name}',
                'description': 'Kill a specific process',
                'category': 'process',
                'variables': ['process_name']
            },
            'file-search': {
                'name': 'Search Files',
                'query': 'find files named {filename} in {directory}',
                'description': 'Search for files',
                'category': 'files',
                'variables': ['filename', 'directory']
            },
            'network-test': {
                'name': 'Test Network',
                'query': 'test my network connection',
                'description': 'Test network connectivity and speed',
                'category': 'network',
                'variables': []
            },
            'backup-files': {
                'name': 'Backup Files',
                'query': 'backup {source} to {destination}',
                'description': 'Backup files from source to destination',
                'category': 'backup',
                'variables': ['source', 'destination']
            },
            'monitor-system': {
                'name': 'Monitor System',
                'query': 'monitor system for {duration}',
                'description': 'Monitor system resources',
                'category': 'monitoring',
                'variables': ['duration']
            }
        }
    
    def list_templates(self, category: Optional[str] = None):
        """List all available templates."""
        templates = self.templates
        
        if category:
            templates = {k: v for k, v in templates.items() if v.get('category') == category}
        
        if not templates:
            console.print(f"[yellow]No templates found{' in category: ' + category if category else ''}[/yellow]")
            return
        
        table = Table(title="Command Templates", box=box.ROUNDED)
        table.add_column("ID", style="cyan", width=20)
        table.add_column("Name", style="white", width=25)
        table.add_column("Query", style="green", width=40)
        table.add_column("Category", style="yellow", width=15)
        
        for template_id, template in templates.items():
            query = template['query'][:37] + "..." if len(template['query']) > 40 else template['query']
            table.add_row(
                template_id,
                template['name'],
                query,
                template.get('category', 'default')
            )
        
        console.print(table)
    
    def show_template(self, template_id: str):
        """Show template details."""
        template = self.templates.get(template_id)
        
        if not template:
            console.print(f"[red]Template '{template_id}' not found[/red]")
            return
        
        variables = template.get('variables', [])
        variable_text = ", ".join(variables) if variables else "None"
        
        console.print(Panel(
            f"[bold]Name:[/bold] {template['name']}\n"
            f"[bold]Query:[/bold] {template['query']}\n"
            f"[bold]Description:[/bold] {template.get('description', 'N/A')}\n"
            f"[bold]Category:[/bold] {template.get('category', 'default')}\n"
            f"[bold]Variables:[/bold] {variable_text}",
            title=f"Template: {template_id}",
            border_style="cyan"
        ))
    
    def get_template_query(self, template_id: str, variables: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Get template query with variables filled in."""
        template = self.templates.get(template_id)
        
        if not template:
            return None
        
        query = template['query']
        required_vars = template.get('variables', [])
        
        # Fill in variables
        if variables:
            for var_name, var_value in variables.items():
                query = query.replace(f"{{{var_name}}}", var_value)
        
        # Check if all variables are filled
        missing_vars = re.findall(r'\{(\w+)\}', query)
        if missing_vars:
            # Prompt for missing variables
            for var_name in missing_vars:
                if var_name not in (variables or {}):
                    value = Prompt.ask(f"Enter value for [cyan]{var_name}[/cyan]")
                    query = query.replace(f"{{{var_name}}}", value)
        
        return query
    
    def show_categories(self):
        """Show all template categories."""
        categories = set(t.get('category', 'default') for t in self.templates.values())
        
        table = Table(title="Template Categories", box=box.ROUNDED)
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Count", style="green", width=10)
        
        for category in sorted(categories):
            count = sum(1 for t in self.templates.values() if t.get('category') == category)
            table.add_row(category, str(count))
        
        console.print(table)
    
    def add_template(self, template_id: str, name: str, query: str, 
                     category: str = "custom", description: Optional[str] = None):
        """Add a custom template."""
        variables = re.findall(r'\{(\w+)\}', query)
        
        self.templates[template_id] = {
            'name': name,
            'query': query,
            'description': description or f"Custom template: {name}",
            'category': category,
            'variables': variables
        }
        
        console.print(f"[green]✅ Added template '{template_id}'[/green]")
    
    def remove_template(self, template_id: str):
        """Remove a template (only custom templates)."""
        if template_id in self.templates:
            # Only allow removing custom templates
            if self.templates[template_id].get('category') == 'custom':
                del self.templates[template_id]
                console.print(f"[green]✅ Removed template '{template_id}'[/green]")
            else:
                console.print(f"[yellow]Cannot remove default template '{template_id}'[/yellow]")
        else:
            console.print(f"[red]Template '{template_id}' not found[/red]")

