"""
Command Line Interface for Orca OS.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .core.daemon import OrcaDaemon
from .core.models import CommandAction, CommandRisk, UserQuery
from .llm.manager import LLMManager
from .security.validator import CommandValidator
from .utils.config import load_config

console = Console()


@click.command()
@click.argument('query', required=False)
@click.option('--dry-run', is_flag=True, help='Show command without executing')
@click.option('--explain', is_flag=True, help='Show detailed explanation')
@click.option('--config', '-c', help='Path to config file')
@click.option('--daemon', is_flag=True, help='Start daemon mode')
@click.option('--overlay', is_flag=True, help='Start global overlay (Ctrl+Space)')
@click.option('--host', default='localhost', help='Daemon host')
@click.option('--port', default=8080, help='Daemon port')
@click.version_option()
def main(query: Optional[str], dry_run: bool, explain: bool, config: Optional[str], daemon: bool, overlay: bool, host: str, port: int):
    """Orca OS - AI-Powered Linux Wrapper"""
    if daemon:
        asyncio.run(_start_daemon(host, port))
    elif overlay:
        asyncio.run(_start_overlay(host, port))
    elif query:
        asyncio.run(_handle_query(query, dry_run, explain, config))
    else:
        # Show help if no arguments
        click.echo("Orca OS - AI-Powered Linux Wrapper")
        click.echo("")
        click.echo("Usage:")
        click.echo("  orca 'query'              # Process a query")
        click.echo("  orca --daemon             # Start daemon")
        click.echo("  orca --overlay            # Start global overlay")
        click.echo("")
        click.echo("Examples:")
        click.echo("  orca 'show me disk usage' --dry-run")
        click.echo("  orca --daemon --port 8080")
        click.echo("  orca --overlay")


# Additional commands can be added here if needed


async def _handle_query(query: str, dry_run: bool, explain: bool, config_path: Optional[str]):
    """Handle a user query."""
    try:
        # Load configuration
        if config_path:
            config = load_config(config_path)
        else:
            config = load_config("config/orca.yaml")
        
        # Initialize components
        llm_manager = LLMManager(config.llm)
        validator = CommandValidator(config.policy)
        
        # Create user query
        user_query = UserQuery(query=query)
        
        # Get system context
        from .core.context import ContextProvider
        from .core.executor import CommandExecutor
        context_provider = ContextProvider()
        context = await context_provider.get_context()
        
        # Regular query handling
        # Generate suggestion
        console.print(f"[blue]🤖 Processing:[/blue] {query}")
        
        suggestion = await llm_manager.generate_suggestion(
            query=user_query,
            context=context
        )
        
        # Validate suggestion
        validation_result = validator.validate(suggestion)
        
        # Display suggestion
        _display_suggestion(suggestion, validation_result, explain)
        
        if dry_run or validation_result.action == CommandAction.DRY_RUN:
            console.print("[yellow]🔍 Dry run mode - command not executed[/yellow]")
            return
        
        # Handle execution - ALWAYS require user confirmation
        if validation_result.action == CommandAction.EXECUTE:
            console.print("[yellow]⚠️  WARNING: This command will be executed on your system[/yellow]")
            console.print(f"[red]Command:[/red] {suggestion.command}")
            console.print(f"[red]Risk Level:[/red] {suggestion.risk_level.value}")
            
            if suggestion.risk_level in [CommandRisk.HIGH, CommandRisk.CRITICAL]:
                console.print("[red]⚠️  HIGH RISK COMMAND - This could potentially harm your system![/red]")
                if not click.confirm("Are you sure you want to execute this HIGH RISK command?"):
                    console.print("[yellow]High risk command cancelled by user[/yellow]")
                    return
            
            if click.confirm("Execute this command?"):
                await _execute_command(suggestion, config)
            else:
                console.print("[yellow]Command cancelled by user[/yellow]")
        elif validation_result.action == CommandAction.CLARIFY:
            console.print("[yellow]⚠️  Command needs clarification[/yellow]")
            console.print("Please refine your request for better results.")
        else:
            console.print("[red]❌ Command blocked by policy[/red]")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _display_suggestion(suggestion, validation_result, explain: bool):
    """Display command suggestion with formatting."""
    # Create a table for the suggestion
    table = Table(title="Orca Suggestion")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Command", suggestion.command)
    table.add_row("Confidence", f"{suggestion.confidence:.2%}")
    table.add_row("Action", suggestion.action.value)
    table.add_row("Risk Level", suggestion.risk_level.value)
    
    if explain and suggestion.explanation:
        table.add_row("Explanation", suggestion.explanation)
    
    console.print(table)
    
    # Show validation result
    if validation_result.action != suggestion.action:
        console.print(f"[yellow]Policy Override:[/yellow] {validation_result.action.value}")


async def _execute_command(suggestion, config):
    """Execute the suggested command."""
    from .core.executor import CommandExecutor
    
    executor = CommandExecutor(config.executor)
    
    console.print("[blue]🚀 Executing command...[/blue]")
    
    result = await executor.execute(suggestion)
    
    if result.success:
        console.print("[green]✅ Command executed successfully[/green]")
        if result.stdout:
            console.print(Panel(result.stdout, title="Output"))
    else:
        console.print(f"[red]❌ Command failed (exit code: {result.exit_code})[/red]")
        if result.stderr:
            console.print(Panel(result.stderr, title="Error", style="red"))


async def _start_daemon(host: str, port: int):
    """Start the Orca daemon."""
    console.print(f"[blue]🚀 Starting Orca daemon on {host}:{port}[/blue]")
    
    daemon = OrcaDaemon(host=host, port=port)
    await daemon.start()


async def _start_overlay(host: str, port: int):
    """Start the global overlay."""
    console.print(f"[blue]🖥️  Starting Orca overlay (Ctrl+Space)[/blue]")
    console.print(f"[blue]   Connecting to daemon at {host}:{port}[/blue]")
    
    try:
        from .ui.overlay import OrcaOverlay
        
        overlay = OrcaOverlay(daemon_host=host, daemon_port=port)
        overlay.run()
        
    except ImportError as e:
        console.print(f"[red]❌ Failed to import overlay: {e}[/red]")
        console.print(f"[yellow]💡 Make sure GTK dependencies are installed:[/yellow]")
        console.print(f"   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
        console.print(f"   # or equivalent for your distribution")
    except Exception as e:
        console.print(f"[red]❌ Failed to start overlay: {e}[/red]")
        console.print(f"[yellow]💡 Make sure the daemon is running:[/yellow]")
        console.print(f"   orca --daemon")


async def _show_status():
    """Show system status."""
    # This would check daemon status, LLM availability, etc.
    console.print("[blue]📊 Orca System Status[/blue]")
    console.print("Daemon: [green]Running[/green]")
    console.print("LLM: [green]Available[/green]")
    console.print("Policy Engine: [green]Active[/green]")


async def _show_history(limit: int):
    """Show command history."""
    console.print(f"[blue]📜 Recent Commands (last {limit})[/blue]")
    # This would query the audit log
    console.print("History feature coming soon...")


if __name__ == "__main__":
    main()
