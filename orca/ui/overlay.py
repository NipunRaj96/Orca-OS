"""
Global overlay window for Orca OS.
"""

import asyncio
import logging
from typing import Optional, Callable
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import httpx
import json

from .hotkey import create_hotkey_manager

logger = logging.getLogger(__name__)


class OrcaOverlay:
    """Global overlay window that appears on Ctrl+Space."""
    
    def __init__(self, daemon_host: str = "localhost", daemon_port: int = 8080):
        """Initialize overlay."""
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.daemon_url = f"http://{daemon_host}:{daemon_port}"
        
        # UI components
        self.window: Optional[Gtk.Window] = None
        self.entry: Optional[Gtk.Entry] = None
        self.suggestion_box: Optional[Gtk.Box] = None
        self.status_label: Optional[Gtk.Label] = None
        
        # State
        self.is_visible = False
        self.current_suggestion = None
        self.hotkey_manager = None
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=10.0)
        
        self._setup_ui()
        self._setup_hotkey()
    
    def _setup_ui(self):
        """Setup the overlay UI."""
        # Create main window
        self.window = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.window.set_title("Orca OS")
        self.window.set_default_size(600, 400)
        self.window.set_resizable(True)
        self.window.set_decorated(False)
        self.window.set_skip_taskbar_hint(True)
        self.window.set_skip_pager_hint(True)
        self.window.set_keep_above(True)
        
        # Center the window
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        # Create main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_left(20)
        main_box.set_margin_right(20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='large' weight='bold'>🐋 Orca OS</span>")
        title_label.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(title_label, False, False, 0)
        
        # Input entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Ask Orca anything... (e.g., 'show me disk usage')")
        self.entry.set_hexpand(True)
        self.entry.connect("activate", self._on_entry_activate)
        self.entry.connect("key-press-event", self._on_key_press)
        main_box.pack_start(self.entry, False, False, 0)
        
        # Suggestion area
        self.suggestion_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.pack_start(self.suggestion_box, True, True, 0)
        
        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.set_markup("<span color='gray'>Press Ctrl+Space to toggle, Enter to execute, Esc to close</span>")
        main_box.pack_start(self.status_label, False, False, 0)
        
        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)
        
        execute_btn = Gtk.Button.new_with_label("Execute")
        execute_btn.connect("clicked", self._on_execute_clicked)
        button_box.pack_start(execute_btn, False, False, 0)
        
        dry_run_btn = Gtk.Button.new_with_label("Dry Run")
        dry_run_btn.connect("clicked", self._on_dry_run_clicked)
        button_box.pack_start(dry_run_btn, False, False, 0)
        
        close_btn = Gtk.Button.new_with_label("Close")
        close_btn.connect("clicked", self._on_close_clicked)
        button_box.pack_start(close_btn, False, False, 0)
        
        main_box.pack_start(button_box, False, False, 0)
        
        self.window.add(main_box)
        
        # Connect window events
        self.window.connect("key-press-event", self._on_window_key_press)
        self.window.connect("delete-event", self._on_window_delete)
        
        # Initially hidden
        self.window.hide()
    
    def _setup_hotkey(self):
        """Setup global hotkey."""
        self.hotkey_manager = create_hotkey_manager()
        if self.hotkey_manager:
            self.hotkey_manager.register_hotkey(self._on_hotkey_triggered)
        else:
            logger.error("Failed to create hotkey manager")
    
    async def _on_hotkey_triggered(self):
        """Handle global hotkey activation."""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def show(self):
        """Show the overlay."""
        if not self.is_visible:
            self.window.show_all()
            self.window.present()
            self.entry.grab_focus()
            self.is_visible = True
            logger.info("Orca overlay shown")
    
    def hide(self):
        """Hide the overlay."""
        if self.is_visible:
            self.window.hide()
            self.is_visible = False
            self._clear_suggestions()
            logger.info("Orca overlay hidden")
    
    def _on_entry_activate(self, entry):
        """Handle Enter key in entry."""
        query = entry.get_text().strip()
        if query:
            asyncio.create_task(self._process_query(query))
    
    def _on_key_press(self, widget, event):
        """Handle key press in entry."""
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False
    
    def _on_window_key_press(self, widget, event):
        """Handle key press in window."""
        if event.keyval == Gdk.KEY_Escape:
            self.hide()
            return True
        return False
    
    def _on_window_delete(self, widget, event):
        """Handle window delete event."""
        self.hide()
        return True
    
    def _on_execute_clicked(self, button):
        """Handle execute button click."""
        query = self.entry.get_text().strip()
        if query:
            asyncio.create_task(self._process_query(query, execute=True))
    
    def _on_dry_run_clicked(self, button):
        """Handle dry run button click."""
        query = self.entry.get_text().strip()
        if query:
            asyncio.create_task(self._process_query(query, execute=False))
    
    def _on_close_clicked(self, button):
        """Handle close button click."""
        self.hide()
    
    async def _process_query(self, query: str, execute: bool = False):
        """Process user query."""
        try:
            self._show_status("🤖 Processing...", "blue")
            self._clear_suggestions()
            
            # Send query to daemon
            response = await self.client.post(
                f"{self.daemon_url}/query",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestion = data.get("suggestion", {})
                
                self.current_suggestion = suggestion
                self._display_suggestion(suggestion)
                
                if execute and suggestion.get("action") == "execute":
                    await self._execute_command(suggestion)
                else:
                    self._show_status("✅ Suggestion ready - click Execute or Dry Run", "green")
            else:
                self._show_status(f"❌ Error: {response.status_code}", "red")
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            self._show_status(f"❌ Error: {str(e)}", "red")
    
    def _display_suggestion(self, suggestion: dict):
        """Display command suggestion."""
        self._clear_suggestions()
        
        # Command
        command_label = Gtk.Label()
        command_label.set_markup(f"<b>Command:</b> {suggestion.get('command', 'N/A')}")
        command_label.set_halign(Gtk.Align.START)
        command_label.set_selectable(True)
        self.suggestion_box.pack_start(command_label, False, False, 0)
        
        # Confidence
        confidence = suggestion.get('confidence', 0)
        confidence_label = Gtk.Label()
        confidence_label.set_markup(f"<b>Confidence:</b> {confidence:.1%}")
        confidence_label.set_halign(Gtk.Align.START)
        self.suggestion_box.pack_start(confidence_label, False, False, 0)
        
        # Action
        action = suggestion.get('action', 'N/A')
        action_label = Gtk.Label()
        action_label.set_markup(f"<b>Action:</b> {action}")
        action_label.set_halign(Gtk.Align.START)
        self.suggestion_box.pack_start(action_label, False, False, 0)
        
        # Risk Level
        risk_level = suggestion.get('risk_level', 'N/A')
        risk_label = Gtk.Label()
        risk_color = "green" if risk_level == "safe" else "orange" if risk_level == "moderate" else "red"
        risk_label.set_markup(f"<b>Risk Level:</b> <span color='{risk_color}'>{risk_level}</span>")
        risk_label.set_halign(Gtk.Align.START)
        self.suggestion_box.pack_start(risk_label, False, False, 0)
        
        # Explanation
        explanation = suggestion.get('explanation')
        if explanation:
            exp_label = Gtk.Label()
            exp_label.set_markup(f"<b>Explanation:</b> {explanation}")
            exp_label.set_halign(Gtk.Align.START)
            exp_label.set_line_wrap(True)
            exp_label.set_max_width_chars(80)
            self.suggestion_box.pack_start(exp_label, False, False, 0)
        
        self.suggestion_box.show_all()
    
    def _clear_suggestions(self):
        """Clear suggestion display."""
        for child in self.suggestion_box.get_children():
            self.suggestion_box.remove(child)
    
    def _show_status(self, message: str, color: str = "black"):
        """Show status message."""
        self.status_label.set_markup(f"<span color='{color}'>{message}</span>")
    
    async def _execute_command(self, suggestion: dict):
        """Execute the suggested command."""
        try:
            self._show_status("🚀 Executing command...", "blue")
            
            response = await self.client.post(
                f"{self.daemon_url}/execute",
                json=suggestion
            )
            
            if response.status_code == 200:
                result = response.json().get("result", {})
                if result.get("success"):
                    self._show_status("✅ Command executed successfully", "green")
                    # Show output if available
                    stdout = result.get("stdout", "")
                    if stdout:
                        self._display_output(stdout)
                else:
                    self._show_status(f"❌ Command failed: {result.get('stderr', 'Unknown error')}", "red")
            else:
                self._show_status(f"❌ Execution error: {response.status_code}", "red")
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            self._show_status(f"❌ Execution error: {str(e)}", "red")
    
    def _display_output(self, output: str):
        """Display command output."""
        output_label = Gtk.Label()
        output_label.set_text(f"Output:\n{output}")
        output_label.set_halign(Gtk.Align.START)
        output_label.set_selectable(True)
        output_label.set_line_wrap(True)
        output_label.set_max_width_chars(80)
        self.suggestion_box.pack_start(output_label, False, False, 0)
        self.suggestion_box.show_all()
    
    def run(self):
        """Run the overlay main loop."""
        try:
            # Start GTK main loop
            Gtk.main()
        except KeyboardInterrupt:
            logger.info("Overlay stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        if self.hotkey_manager:
            self.hotkey_manager.unregister_hotkey()
        
        if self.client:
            asyncio.create_task(self.client.aclose())
        
        if self.window:
            self.window.destroy()
