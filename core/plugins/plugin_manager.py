"""Plugin system for Mimir"""
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Callable, Any
import logging

class PluginManager:
    """Manages Mimir plugins"""
    
    def __init__(self, plugin_dir=None):
        if plugin_dir is None:
            plugin_dir = Path.home() / ".mimir" / "plugins"
        self.plugin_dir = plugin_dir
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
    
    def discover_plugins(self):
        """Discover and load all plugins in the plugin directory"""
        self.plugins = {}
        
        if not self.plugin_dir.exists():
            self.logger.info(f"Plugin directory {self.plugin_dir} does not exist")
            return
        
        for plugin_path in self.plugin_dir.glob("*.py"):
            try:
                # Skip empty or invalid files
                if plugin_path.stat().st_size == 0:
                    self.logger.warning(f"Skipping empty plugin: {plugin_path}")
                    continue
                
                spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
                if spec is None or spec.loader is None:
                    self.logger.warning(f"Invalid plugin spec: {plugin_path}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'setup'):
                    plugin_info = module.setup()
                    self.plugins[plugin_info['name']] = {
                        'module': module,
                        'info': plugin_info,
                        'enabled': True,
                        'path': plugin_path
                    }
                    self.logger.info(f"✅ Loaded plugin: {plugin_info['name']} v{plugin_info['version']}")
                    
                    # Register hooks
                    for hook in plugin_info.get('hooks', []):
                        if hasattr(module, hook):
                            self.register_hook(hook, getattr(module, hook))
                else:
                    self.logger.warning(f"Plugin {plugin_path} has no setup() function")
                    
            except SyntaxError as e:
                self.logger.error(f"❌ Syntax error in plugin {plugin_path}: {e}")
                self.logger.info(f"   Fix the plugin file and restart Mimir")
            except ImportError as e:
                self.logger.error(f"❌ Import error in plugin {plugin_path}: {e}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load plugin {plugin_path}: {e}")
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def run_hook(self, hook_name: str, *args, **kwargs):
        """Run all callbacks for a hook"""
        results = []
        for callback in self.hooks.get(hook_name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error in hook {hook_name}: {e}")
        return results
    
    def enable_plugin(self, name: str):
        """Enable a plugin"""
        if name in self.plugins:
            self.plugins[name]['enabled'] = True
            if hasattr(self.plugins[name]['module'], 'on_enable'):
                self.plugins[name]['module'].on_enable()
    
    def disable_plugin(self, name: str):
        """Disable a plugin"""
        if name in self.plugins:
            self.plugins[name]['enabled'] = False
            if hasattr(self.plugins[name]['module'], 'on_disable'):
                self.plugins[name]['module'].on_disable()
    
    def get_plugins(self) -> Dict[str, Any]:
        """Get all plugins info"""
        return {name: p['info'] for name, p in self.plugins.items()}

