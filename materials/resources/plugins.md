holaneu: but how plugins are treated in common best practice?
I expected to have tools possible to add as plugins from more locations

GitHub Copilot: Great question! In Python, **plugins** are typically handled differently from standard modules. The best practices for plugin systems focus on **discoverability, extensibility, and decoupling**. Here’s how it’s commonly done:

---

### 1. **Use Entry Points (Recommended for Plugins)**
- **Entry points** (via [setuptools entry_points](https://setuptools.pypa.io/en/latest/userguide/entry_point.html)) allow plugins to be registered and discovered dynamically, even if they are installed from other packages or locations.
- This is how many frameworks (like pytest, Flask, etc.) support plugins.

**Example:**
- Each plugin package defines an entry point in its `setup.py`:
    ```python
    entry_points={
        'myapp.tools': [
            'save_to_file2 = app.tools.save_to_file:save_to_file2',
            'user_files_folder_path2 = app.tools.user_files_folder_path:user_files_folder_path2',
        ],
    }
    ```
- Your app discovers plugins using `importlib.metadata.entry_points()` (Python 3.10+):
    ```python
    from importlib.metadata import entry_points

    for ep in entry_points(group='myapp.tools'):
        tool_func = ep.load()
        # Register or use tool_func
    ```

---

### 2. **Plugin Folder with Dynamic Import**
- Place plugins in a specific folder (or folders).
- Dynamically import all modules in those folders at runtime.
- Optionally, require plugins to register themselves (e.g., by calling a registration function).

**Example:**
```python
import os, importlib

plugin_folder = "plugins"
for fname in os.listdir(plugin_folder):
    if fname.endswith(".py"):
        modulename = f"{plugin_folder}.{fname[:-3]}"
        importlib.import_module(modulename)
```
- Each plugin could register itself with a central registry.

---

### 3. **Use a Plugin Registry**
- Maintain a registry (a dict or list) of available tools.
- Plugins register themselves with the registry when imported.

**Example:**
```python
# In app/tools/registry.py
TOOLS = {}

def register_tool(name, func):
    TOOLS[name] = func

# In each plugin
from app.tools.registry import register_tool

def my_tool(...):
    ...
register_tool("my_tool", my_tool)
```
- Your app can now discover all registered tools via `TOOLS`.

---

### 4. **Summary Table**

| Approach         | Best for...         | Pros                        | Cons                        |
|------------------|---------------------|-----------------------------|-----------------------------|
| Entry Points     | Real plugins        | Works across packages, robust | Requires packaging, setup   |
| Dynamic Import   | Local plugins       | Simple, no packaging needed | Harder to manage, less safe |
| Registry Pattern | Both                | Explicit, easy to extend    | Needs manual registration   |

---

**For a real plugin system, entry points are the best practice.**  
For simple modularity within your own codebase, dynamic import or a registry is often enough.

---

**If you want to support plugins from multiple locations,**  
- Use entry points for external plugins.
- Use dynamic import/registry for local plugins.

Let me know if you want a code example for a specific approach!