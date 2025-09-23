#!/usr/bin/env python3
"""
Orca OS Plugin System
Extensible plugin architecture for community extensions
"""

import asyncio
import json
import importlib
import sys
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import inspect

# Add orca-core to path
sys.path.insert(0, '/opt/orca-os')

from orca.llm.manager import LLMManager
from orca.core.models import UserQuery, SystemContext
from orca.utils.config import load_config


@dataclass
class PluginInfo:
    """Plugin information and metadata."""
    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str]
    enabled: bool
    load_time: float
    functions: List[str]


@dataclass
class PluginFunction:
    """Plugin function definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    return_type: str
    ai_enhanced: bool


class OrcaPluginSystem:
    """Plugin system for Orca OS extensions."""
    
    def __init__(self):
        """Initialize the plugin system."""
        self.config = load_config('/opt/orca-os/config/orca.yaml')
        self.llm_manager = LLMManager(self.config.llm.dict())
        self.plugins = {}
        self.plugin_functions = {}
        self.plugin_directory = Path('/opt/orca-os/plugins')
        self.plugin_directory.mkdir(exist_ok=True)
        
    async def load_plugin(self, plugin_path: str) -> Dict[str, Any]:
        """Load a plugin from file."""
        try:
            plugin_name = Path(plugin_path).stem
            
            # Load plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # Get plugin metadata
            metadata = getattr(plugin_module, 'PLUGIN_METADATA', {})
            plugin_info = PluginInfo(
                name=metadata.get('name', plugin_name),
                version=metadata.get('version', '1.0.0'),
                description=metadata.get('description', 'No description'),
                author=metadata.get('author', 'Unknown'),
                category=metadata.get('category', 'general'),
                dependencies=metadata.get('dependencies', []),
                enabled=True,
                load_time=0.0,
                functions=[]
            )
            
            # Register plugin functions
            functions = await self._register_plugin_functions(plugin_module, plugin_name)
            plugin_info.functions = [func.name for func in functions]
            
            # Store plugin
            self.plugins[plugin_name] = {
                'info': plugin_info,
                'module': plugin_module,
                'functions': functions
            }
            
            return {
                "status": "success",
                "plugin": plugin_info.name,
                "functions": len(functions),
                "message": f"Plugin '{plugin_info.name}' loaded successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load plugin: {str(e)}"
            }
    
    async def _register_plugin_functions(self, plugin_module, plugin_name: str) -> List[PluginFunction]:
        """Register functions from a plugin module."""
        functions = []
        
        try:
            # Find all callable functions in the module
            for name, obj in inspect.getmembers(plugin_module):
                if inspect.isfunction(obj) and not name.startswith('_'):
                    # Get function metadata
                    doc = inspect.getdoc(obj) or "No description"
                    sig = inspect.signature(obj)
                    
                    # Check if function is AI-enhanced
                    ai_enhanced = hasattr(obj, '__ai_enhanced__') or 'ai' in name.lower()
                    
                    # Create function definition
                    func_def = PluginFunction(
                        name=name,
                        description=doc,
                        parameters={param.name: str(param.annotation) for param in sig.parameters.values()},
                        return_type=str(sig.return_annotation),
                        ai_enhanced=ai_enhanced
                    )
                    
                    functions.append(func_def)
                    
                    # Register function
                    full_name = f"{plugin_name}.{name}"
                    self.plugin_functions[full_name] = {
                        'function': obj,
                        'plugin': plugin_name,
                        'definition': func_def
                    }
            
        except Exception as e:
            print(f"Error registering plugin functions: {e}")
        
        return functions
    
    async def call_plugin_function(self, function_name: str, *args, **kwargs) -> Any:
        """Call a plugin function."""
        try:
            if function_name not in self.plugin_functions:
                return {"error": f"Function '{function_name}' not found"}
            
            func_info = self.plugin_functions[function_name]
            func = func_info['function']
            
            # Check if function is AI-enhanced
            if func_info['definition'].ai_enhanced:
                # Add AI context to function call
                ai_context = await self._get_ai_context()
                kwargs['ai_context'] = ai_context
            
            # Call the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            return result
            
        except Exception as e:
            return {"error": f"Function call failed: {str(e)}"}
    
    async def _get_ai_context(self) -> Dict[str, Any]:
        """Get AI context for plugin functions."""
        try:
            # Get current system state
            system_context = SystemContext(
                processes=[],
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                disk_usage=psutil.disk_usage('/').percent
            )
            
            return {
                "llm_manager": self.llm_manager,
                "system_context": system_context,
                "config": self.config
            }
            
        except Exception as e:
            return {"error": f"Failed to get AI context: {str(e)}"}
    
    async def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        plugins = []
        
        for plugin_name, plugin_data in self.plugins.items():
            plugin_info = plugin_data['info']
            plugins.append({
                "name": plugin_info.name,
                "version": plugin_info.version,
                "description": plugin_info.description,
                "author": plugin_info.author,
                "category": plugin_info.category,
                "enabled": plugin_info.enabled,
                "functions": plugin_info.functions
            })
        
        return plugins
    
    async def list_functions(self) -> List[Dict[str, Any]]:
        """List all available plugin functions."""
        functions = []
        
        for func_name, func_info in self.plugin_functions.items():
            func_def = func_info['definition']
            functions.append({
                "name": func_name,
                "description": func_def.description,
                "parameters": func_def.parameters,
                "return_type": func_def.return_type,
                "ai_enhanced": func_def.ai_enhanced,
                "plugin": func_info['plugin']
            })
        
        return functions
    
    async def enable_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Enable a plugin."""
        try:
            if plugin_name not in self.plugins:
                return {"status": "error", "message": f"Plugin '{plugin_name}' not found"}
            
            self.plugins[plugin_name]['info'].enabled = True
            
            return {
                "status": "success",
                "message": f"Plugin '{plugin_name}' enabled"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def disable_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Disable a plugin."""
        try:
            if plugin_name not in self.plugins:
                return {"status": "error", "message": f"Plugin '{plugin_name}' not found"}
            
            self.plugins[plugin_name]['info'].enabled = False
            
            return {
                "status": "success",
                "message": f"Plugin '{plugin_name}' disabled"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def unload_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Unload a plugin."""
        try:
            if plugin_name not in self.plugins:
                return {"status": "error", "message": f"Plugin '{plugin_name}' not found"}
            
            # Remove plugin functions
            functions_to_remove = [name for name in self.plugin_functions if name.startswith(f"{plugin_name}.")]
            for func_name in functions_to_remove:
                del self.plugin_functions[func_name]
            
            # Remove plugin
            del self.plugins[plugin_name]
            
            return {
                "status": "success",
                "message": f"Plugin '{plugin_name}' unloaded"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def create_plugin_template(self, plugin_name: str, category: str = "general") -> Dict[str, Any]:
        """Create a plugin template."""
        try:
            plugin_file = self.plugin_directory / f"{plugin_name}.py"
            
            template = f'''#!/usr/bin/env python3
"""
{plugin_name.title()} Plugin for Orca OS
Generated plugin template
"""

import asyncio
from typing import Dict, Any, Optional

# Plugin metadata
PLUGIN_METADATA = {{
    "name": "{plugin_name}",
    "version": "1.0.0",
    "description": "A plugin for {plugin_name}",
    "author": "Your Name",
    "category": "{category}",
    "dependencies": []
}}

async def hello_world(name: str = "World") -> str:
    """Say hello to someone.
    
    Args:
        name: Name to greet
        
    Returns:
        Greeting message
    """
    return f"Hello, {{name}}! This is the {plugin_name} plugin."

def simple_function(value: int) -> int:
    """A simple function that doubles a value.
    
    Args:
        value: Input value
        
    Returns:
        Doubled value
    """
    return value * 2

@ai_enhanced
async def ai_function(query: str, ai_context: Dict[str, Any] = None) -> str:
    """An AI-enhanced function.
    
    Args:
        query: Query string
        ai_context: AI context from Orca OS
        
    Returns:
        AI-generated response
    """
    if ai_context and 'llm_manager' in ai_context:
        # Use Orca's AI capabilities
        from orca.core.models import UserQuery, SystemContext
        
        user_query = UserQuery(query=query)
        system_context = ai_context.get('system_context', SystemContext(
            processes=[],
            memory_usage=0,
            cpu_usage=0,
            disk_usage=0
        ))
        
        suggestion = await ai_context['llm_manager'].generate_suggestion(user_query, system_context)
        return suggestion.explanation or "No response generated"
    
    return f"AI-enhanced response for: {{query}}"

def ai_enhanced(func):
    """Decorator to mark functions as AI-enhanced."""
    func.__ai_enhanced__ = True
    return func

# Plugin initialization
async def initialize():
    """Initialize the plugin."""
    print(f"Initializing {plugin_name} plugin...")
    return True

async def cleanup():
    """Cleanup the plugin."""
    print(f"Cleaning up {plugin_name} plugin...")
    return True
'''
            
            with open(plugin_file, 'w') as f:
                f.write(template)
            
            # Make file executable
            plugin_file.chmod(0o755)
            
            return {
                "status": "success",
                "message": f"Plugin template created: {plugin_file}",
                "file_path": str(plugin_file)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_plugin_analytics(self) -> Dict[str, Any]:
        """Get plugin usage analytics."""
        try:
            total_plugins = len(self.plugins)
            enabled_plugins = len([p for p in self.plugins.values() if p['info'].enabled])
            total_functions = len(self.plugin_functions)
            ai_functions = len([f for f in self.plugin_functions.values() if f['definition'].ai_enhanced])
            
            # Categorize plugins
            categories = {}
            for plugin_data in self.plugins.values():
                category = plugin_data['info'].category
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
            
            return {
                "total_plugins": total_plugins,
                "enabled_plugins": enabled_plugins,
                "total_functions": total_functions,
                "ai_functions": ai_functions,
                "categories": categories,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get analytics: {str(e)}"}


async def main():
    """Main entry point for Plugin System."""
    plugin_system = OrcaPluginSystem()
    
    print("🐋 Orca OS Plugin System")
    print("=" * 50)
    
    # List plugins
    plugins = await plugin_system.list_plugins()
    print(f"Loaded Plugins: {len(plugins)}")
    for plugin in plugins:
        print(f"  • {plugin['name']} v{plugin['version']} - {plugin['description']}")
    
    # List functions
    functions = await plugin_system.list_functions()
    print(f"\nAvailable Functions: {len(functions)}")
    for func in functions[:5]:  # Show first 5
        print(f"  • {func['name']} - {func['description']}")
    
    # Get analytics
    analytics = await plugin_system.get_plugin_analytics()
    if "error" not in analytics:
        print(f"\nAnalytics:")
        print(f"  Total Plugins: {analytics['total_plugins']}")
        print(f"  Enabled Plugins: {analytics['enabled_plugins']}")
        print(f"  Total Functions: {analytics['total_functions']}")
        print(f"  AI Functions: {analytics['ai_functions']}")


if __name__ == "__main__":
    asyncio.run(main())
