"""
Command history system for Orca OS.
Terminal-friendly history browsing.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from ...database.session import DatabaseSession
from ...database.models import Query, Result, Session as DBSession
from ...database.init_db import initialize_database

logger = logging.getLogger(__name__)
console = Console()


class HistoryManager:
    """Manages command history for Orca OS."""
    
    def __init__(self):
        """Initialize history manager."""
        initialize_database()
        self.db = DatabaseSession()
    
    def show_history(self, limit: int = 20, user_id: str = "default"):
        """Show command history in terminal."""
        with self.db.session() as session:
            queries = session.query(Query).filter_by(user_id=user_id)\
                .order_by(Query.timestamp.desc()).limit(limit).all()
            
            if not queries:
                console.print("[yellow]No command history found[/yellow]")
                return
            
            # Create history table
            table = Table(title=f"Command History (Last {len(queries)})", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=4, justify="right")
            table.add_column("Query", style="white", width=50)
            table.add_column("Time", style="dim", width=12)
            table.add_column("Status", style="green", width=10)
            
            for i, query in enumerate(queries, 1):
                # Get result status
                result = session.query(Result).filter_by(query_id=query.id).first()
                status = "✅ Success" if result and result.success else "❌ Failed" if result else "⏳ Pending"
                
                query_text = query.query_text[:47] + "..." if len(query.query_text) > 50 else query.query_text
                time_str = query.timestamp.strftime("%Y-%m-%d %H:%M")
                
                table.add_row(str(i), query_text, time_str, status)
            
            console.print(table)
            
            # Show navigation options
            console.print("\n[dim]Use 'orca --history <number>' to see details, or 'orca --history-search <term>' to search[/dim]")
    
    def show_history_details(self, history_id: int, user_id: str = "default"):
        """Show detailed history for a specific entry."""
        with self.db.session() as session:
            query = session.query(Query).filter_by(id=history_id, user_id=user_id).first()
            
            if not query:
                console.print(f"[red]History entry #{history_id} not found[/red]")
                return
            
            # Show query details
            console.print(Panel(
                f"[bold]Query:[/bold] {query.query_text}\n"
                f"[bold]Time:[/bold] {query.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"[bold]Session:[/bold] {query.session_id}",
                title="Query Details",
                border_style="cyan"
            ))
            
            # Show results
            results = session.query(Result).filter_by(query_id=query.id).all()
            
            if results:
                result_table = Table(title="Execution Results", box=box.ROUNDED)
                result_table.add_column("Command", style="cyan", width=40)
                result_table.add_column("Success", style="green", width=10)
                result_table.add_column("Exit Code", style="yellow", width=10)
                result_table.add_column("Time", style="dim", width=10)
                
                for result in results:
                    success = "✅ Yes" if result.success else "❌ No"
                    exit_code = str(result.exit_code) if result.exit_code is not None else "N/A"
                    exec_time = f"{result.execution_time:.2f}s" if result.execution_time else "N/A"
                    
                    cmd = result.command[:37] + "..." if len(result.command) > 40 else result.command
                    result_table.add_row(cmd, success, exit_code, exec_time)
                
                console.print(result_table)
                
                # Show output if available
                for result in results:
                    if result.stdout:
                        console.print(Panel(
                            result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                            title="Output",
                            border_style="green"
                        ))
                    if result.stderr:
                        console.print(Panel(
                            result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr,
                            title="Error",
                            border_style="red"
                        ))
            else:
                console.print("[yellow]No execution results found[/yellow]")
    
    def search_history(self, search_term: str, user_id: str = "default", limit: int = 20):
        """Search command history."""
        with self.db.session() as session:
            queries = session.query(Query)\
                .filter_by(user_id=user_id)\
                .filter(Query.query_text.contains(search_term))\
                .order_by(Query.timestamp.desc())\
                .limit(limit).all()
            
            if not queries:
                console.print(f"[yellow]No history found matching '{search_term}'[/yellow]")
                return
            
            table = Table(title=f"Search Results: '{search_term}'", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Query", style="white", width=50)
            table.add_column("Time", style="dim", width=12)
            
            for i, query in enumerate(queries, 1):
                query_text = query.query_text[:47] + "..." if len(query.query_text) > 50 else query.query_text
                time_str = query.timestamp.strftime("%Y-%m-%d %H:%M")
                table.add_row(str(i), query_text, time_str)
            
            console.print(table)
    
    def export_history(self, filename: Optional[str] = None, user_id: str = "default"):
        """Export history to file."""
        filename = filename or f"orca_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with self.db.session() as session:
            queries = session.query(Query).filter_by(user_id=user_id)\
                .order_by(Query.timestamp.desc()).all()
            
            with open(filename, 'w') as f:
                f.write("Orca OS Command History\n")
                f.write("=" * 80 + "\n\n")
                
                for query in queries:
                    f.write(f"Time: {query.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Query: {query.query_text}\n")
                    
                    results = session.query(Result).filter_by(query_id=query.id).all()
                    for result in results:
                        f.write(f"  Command: {result.command}\n")
                        f.write(f"  Success: {result.success}\n")
                        if result.stdout:
                            f.write(f"  Output: {result.stdout[:200]}\n")
                    f.write("\n" + "-" * 80 + "\n\n")
            
            console.print(f"[green]✅ History exported to {filename}[/green]")
    
    def clear_history(self, user_id: str = "default", confirm: bool = True):
        """Clear command history."""
        if confirm:
            if not Confirm.ask("[red]Are you sure you want to clear all history?[/red]"):
                console.print("[yellow]Cancelled[/yellow]")
                return
        
        with self.db.session() as session:
            queries = session.query(Query).filter_by(user_id=user_id).all()
            count = len(queries)
            
            for query in queries:
                session.delete(query)
            
            session.commit()
            console.print(f"[green]✅ Cleared {count} history entries[/green]")

