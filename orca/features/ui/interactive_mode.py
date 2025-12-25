"""
Interactive chat-like interface for Orca OS.
Terminal-friendly conversation mode.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.text import Text

from ...core.integration_layer import OrcaIntegrationLayer
from ...core.intelligent_router import IntelligentRouter
from ...database.session import DatabaseSession
from ...database.models import Query, Session as DBSession
from ...utils.config import load_config

logger = logging.getLogger(__name__)
console = Console()


class InteractiveMode:
    """Interactive chat-like interface for Orca OS."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize interactive mode."""
        self.config = load_config(config_path or "config/orca.yaml")
        self.integration = OrcaIntegrationLayer(self.config)
        self.router = IntelligentRouter(self.integration.db, self.integration.autonomy_engine)
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = None
        self._init_session()
    
    def _init_session(self):
        """Initialize conversation session."""
        from ...database.init_db import initialize_database
        initialize_database()
        
        with self.integration.db.session() as session:
            db_session = DBSession(
                session_id=f"interactive_{int(datetime.now().timestamp())}",
                user_id="default",
                started_at=datetime.now()
            )
            session.add(db_session)
            session.commit()
            self.session_id = db_session.session_id
    
    async def start(self):
        """Start interactive mode."""
        console.print(Panel(
            "[bold cyan]🐋 Orca OS - Interactive Mode[/bold cyan]\n"
            "[dim]Type your commands naturally. Type 'help' for commands, 'exit' to quit.[/dim]",
            border_style="cyan",
            title="Welcome"
        ))
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    console.print("\n[yellow]Goodbye! 👋[/yellow]")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'history':
                    self._show_conversation_history()
                    continue
                elif user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    console.print("[green]Conversation history cleared[/green]")
                    continue
                
                # Process query
                await self._process_query(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except EOFError:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                console.print(f"[red]Error: {e}[/red]")
    
    async def _process_query(self, query: str):
        """Process a user query."""
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': query,
            'timestamp': datetime.now()
        })
        
        # Show thinking indicator
        with console.status("[bold yellow]🤖 Orca is thinking...", spinner="dots"):
            # Route query
            route_info = self.router.route_query(query)
            
            # If advanced features triggered
            if route_info['route'] == 'advanced_features':
                results = await self.router.execute_routed_query(
                    query, route_info, self.integration
                )
                self._display_advanced_results(results, route_info)
            else:
                # Standard natural language processing
                result = await self.integration.process_query_with_all_features(
                    query=query,
                    user_id="default"
                )
                self._display_result(result, query)
        
        # Save to database
        self._save_to_history(query)
    
    def _display_result(self, result: Dict[str, Any], query: str):
        """Display result in chat format."""
        suggestion = result.get('suggestion')
        
        if isinstance(suggestion, dict):
            from ...core.models import CommandSuggestion
            suggestion = CommandSuggestion(**suggestion)
        
        # Create response text
        response = Text()
        response.append("💡 ", style="cyan")
        response.append(suggestion.explanation or suggestion.command, style="white")
        
        # Show command if different from explanation
        if suggestion.command and suggestion.command != suggestion.explanation:
            response.append(f"\n\n[dim]Command:[/dim] [cyan]{suggestion.command}[/cyan]")
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': suggestion.explanation or suggestion.command,
            'command': suggestion.command,
            'timestamp': datetime.now()
        })
        
        # Display in chat bubble
        console.print(Panel(
            response,
            border_style="blue",
            title="[bold blue]Orca[/bold blue]"
        ))
    
    def _display_advanced_results(self, results: Dict[str, Any], route_info: Dict[str, Any]):
        """Display advanced feature results."""
        from rich.table import Table
        
        response = Text()
        response.append("🔍 ", style="cyan")
        response.append("Analyzed your system and found:\n\n", style="white")
        
        # Summarize results
        for feature, result in results.items():
            if feature == 'predictive' and result.get('predictions'):
                response.append(f"• {len(result['predictions'])} predictions\n", style="yellow")
            elif feature == 'optimizer' and result.get('autonomous_actions'):
                response.append(f"• {len(result['autonomous_actions'])} optimizations applied\n", style="green")
            elif feature == 'autonomous_fix':
                actions = result.get('optimizations_applied', [])
                response.append(f"• Fixed {len(actions)} issues autonomously\n", style="green")
        
        console.print(Panel(
            response,
            border_style="green",
            title="[bold green]Orca[/bold green]"
        ))
    
    def _show_help(self):
        """Show help commands."""
        help_text = """
[bold]Available Commands:[/bold]

  [cyan]help[/cyan]          - Show this help message
  [cyan]history[/cyan]       - Show conversation history
  [cyan]clear[/cyan]         - Clear conversation history
  [cyan]exit[/cyan] / [cyan]quit[/cyan] - Exit interactive mode

[bold]Examples:[/bold]

  "show me disk usage"
  "my system is slow"
  "optimize my system"
  "will my disk fill up?"
        """
        console.print(Panel(help_text, title="Help", border_style="cyan"))
    
    def _show_conversation_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            console.print("[yellow]No conversation history yet[/yellow]")
            return
        
        from rich.table import Table
        
        table = Table(title="Conversation History", show_header=True)
        table.add_column("Role", style="cyan", width=10)
        table.add_column("Content", style="white", width=60)
        table.add_column("Time", style="dim", width=12)
        
        for msg in self.conversation_history[-10:]:  # Show last 10
            role = "You" if msg['role'] == 'user' else "Orca"
            content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            time = msg['timestamp'].strftime("%H:%M:%S")
            table.add_row(role, content, time)
        
        console.print(table)
    
    def _save_to_history(self, query: str):
        """Save query to database history."""
        try:
            with self.integration.db.session() as session:
                db_query = Query(
                    query_text=query,
                    user_id="default",
                    session_id=self.session_id,
                    language="en"
                )
                session.add(db_query)
                session.commit()
        except Exception as e:
            logger.error(f"Error saving to history: {e}")

