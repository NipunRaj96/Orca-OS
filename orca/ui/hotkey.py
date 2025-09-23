"""
Global hotkey management for Orca OS.
"""

import asyncio
import logging
from typing import Callable, Optional
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey registration and handling."""
    
    def __init__(self):
        """Initialize hotkey manager."""
        self.callback: Optional[Callable] = None
        self.accelerator = Gtk.accelerator_parse('<Control>space')
        self.hotkey_id = None
        self.is_registered = False
    
    def register_hotkey(self, callback: Callable) -> bool:
        """Register global hotkey (Ctrl+Space) with callback."""
        try:
            self.callback = callback
            
            # Register the hotkey
            self.hotkey_id = Gtk.accelerator_map_add_entry(
                '<Control>space',
                0,  # No modifiers beyond Ctrl
                Gtk.ACCEL_VISIBLE
            )
            
            # Connect to the accelerator
            Gtk.accelerator_connect(
                '<Control>space',
                0,
                Gtk.ACCEL_VISIBLE,
                self._on_hotkey_activated
            )
            
            self.is_registered = True
            logger.info("Global hotkey Ctrl+Space registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register global hotkey: {e}")
            return False
    
    def unregister_hotkey(self) -> bool:
        """Unregister the global hotkey."""
        try:
            if self.hotkey_id:
                Gtk.accelerator_disconnect(
                    '<Control>space',
                    0,
                    Gtk.ACCEL_VISIBLE
                )
                self.hotkey_id = None
            
            self.is_registered = False
            logger.info("Global hotkey unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister global hotkey: {e}")
            return False
    
    def _on_hotkey_activated(self, accelerator, data):
        """Handle hotkey activation."""
        try:
            if self.callback:
                # Run callback in async context
                asyncio.create_task(self.callback())
            return True
        except Exception as e:
            logger.error(f"Error in hotkey callback: {e}")
            return False
    
    def is_hotkey_available(self) -> bool:
        """Check if hotkey is available for registration."""
        try:
            # Try to parse the accelerator
            Gtk.accelerator_parse('<Control>space')
            return True
        except Exception:
            return False


class X11HotkeyManager:
    """Alternative X11-based hotkey manager for better compatibility."""
    
    def __init__(self):
        """Initialize X11 hotkey manager."""
        self.callback: Optional[Callable] = None
        self.display = None
        self.root = None
        self.is_registered = False
    
    def register_hotkey(self, callback: Callable) -> bool:
        """Register hotkey using X11."""
        try:
            import Xlib
            from Xlib import X, XK
            from Xlib.error import XError
            
            self.callback = callback
            self.display = Xlib.display.Display()
            self.root = self.display.screen().root
            
            # Define the key combination (Ctrl+Space)
            ctrl_mask = X.ControlMask
            space_key = XK.string_to_keysym('space')
            space_keycode = self.display.keysym_to_keycode(space_key)
            
            # Grab the key combination
            self.root.grab_key(
                space_keycode,
                ctrl_mask,
                1,  # owner_events
                X.GrabModeAsync,
                X.GrabModeAsync
            )
            
            # Listen for key press events
            self.root.change_attributes(event_mask=X.KeyPressMask)
            
            self.is_registered = True
            logger.info("X11 global hotkey Ctrl+Space registered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register X11 hotkey: {e}")
            return False
    
    def unregister_hotkey(self) -> bool:
        """Unregister X11 hotkey."""
        try:
            if self.display and self.root:
                space_key = XK.string_to_keysym('space')
                space_keycode = self.display.keysym_to_keycode(space_key)
                ctrl_mask = X.ControlMask
                
                self.root.ungrab_key(space_keycode, ctrl_mask)
                self.display.close()
            
            self.is_registered = False
            logger.info("X11 global hotkey unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister X11 hotkey: {e}")
            return False
    
    def check_events(self):
        """Check for X11 events (to be called in main loop)."""
        try:
            if not self.display:
                return
            
            while self.display.pending_events() > 0:
                event = self.display.next_event()
                if event.type == X.KeyPress:
                    if self.callback:
                        asyncio.create_task(self.callback())
                        
        except Exception as e:
            logger.error(f"Error checking X11 events: {e}")


def create_hotkey_manager() -> HotkeyManager:
    """Create appropriate hotkey manager for the system."""
    try:
        # Try GTK first
        manager = HotkeyManager()
        if manager.is_hotkey_available():
            return manager
    except Exception:
        pass
    
    # Fallback to X11
    try:
        return X11HotkeyManager()
    except Exception as e:
        logger.error(f"Failed to create any hotkey manager: {e}")
        return None
