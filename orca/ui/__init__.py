"""
UI components for Orca OS.
"""

try:
    from .overlay import OrcaOverlay
    from .hotkey import HotkeyManager
    __all__ = ["OrcaOverlay", "HotkeyManager"]
except ImportError:
    # GTK not available, overlay not supported
    try:
        from .hotkey import HotkeyManager
        __all__ = ["HotkeyManager"]
    except ImportError:
        __all__ = []
