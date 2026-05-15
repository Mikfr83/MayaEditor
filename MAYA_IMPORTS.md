# Maya Module Discovery for Jedi

## Problem
By default, Jedi doesn't know about Maya's Python modules, so completions for `maya.cmds`, `maya.OpenMaya`, `PySide6`, etc. wouldn't work.

## Solution
We configure Jedi with a **Project** that includes Maya's `sys.path`, allowing Jedi to discover all Maya modules.

## How It Works

### 1. Project Creation
When the first completion is requested, we create a cached Jedi `Project`:

```python
_jedi_project = Project(path=".", added_sys_path=sys.path)
```

This tells Jedi to include all paths from Maya's runtime `sys.path`, which includes:
- Maya's Python site-packages
- Maya's internal modules
- Any plugins you've loaded
- Your PYTHONPATH additions

### 2. Script Creation
When getting completions, we pass the project to the Script:

```python
script = Script(source, path=filename, project=project)
```

Now Jedi can resolve imports like:
- `import maya.cmds`
- `from maya import OpenMaya`
- `from maya.api import OpenMaya as om2`
- `from PySide6.QtWidgets import QWidget`

### 3. Caching
The project is cached globally to avoid recreating it on every keystroke, improving performance.

## Testing

### Test 1: maya.cmds
```python
import maya.cmds as cmds
cmds.  # Should show: polyCube, ls, select, etc.
```

### Test 2: maya.OpenMaya (API 1.0)
```python
from maya import OpenMaya
OpenMaya.M  # Should show: MVector, MMatrix, MObject, etc.
```

### Test 3: maya.api.OpenMaya (API 2.0)
```python
from maya.api import OpenMaya as om2
om2.M  # Should show: MVector, MMatrix, MFnMesh, etc.
```

### Test 4: PySide6
```python
from PySide6.QtWidgets import QWidget
QWidget.  # Should show: show, hide, setWindowTitle, etc.
```

### Test 5: Custom modules
If you have custom modules in your PYTHONPATH:
```python
import my_custom_module
my_custom_module.  # Should show your functions/classes
```

## Debug Output

When the project is created (first completion), you'll see:
```
[Jedi] Created project with 47 sys.path entries
[Jedi] Sample paths: ['/Applications/Autodesk/maya2024/Maya.app/...', ...]
```

When completions are found:
```
[Jedi] Returned 234 completions: ['polyCube', 'polySphere', 'polyPlane', ...]...
```

## Troubleshooting

### No completions for maya.cmds
**Check**: Is `maya` in sys.path?
```python
import sys
print([p for p in sys.path if 'maya' in p.lower()])
```

### Completions are slow
**Cause**: Jedi is analyzing large modules like `maya.cmds` for the first time.
**Solution**: This only happens once. Jedi caches the analysis.

### Wrong completions
**Cause**: Jedi might be using stale cache.
**Solution**: Restart Maya to clear Jedi's cache.

### No completions for custom modules
**Check**: Are they in sys.path?
```python
import sys
print(sys.path)
```

Add your module path:
```python
import sys
sys.path.append('/path/to/your/modules')
```

## Performance Notes

- **First completion**: May take 500ms-1s while Jedi analyzes maya.cmds
- **Subsequent completions**: Should be fast (< 100ms)
- **Project is cached**: Only created once per editor session
- **Jedi caches analysis**: Maya modules analyzed once, then cached

## Limitations

### 1. No C++ API completions
Jedi can only analyze Python code. Maya's C++ bindings (exposed via shiboken) don't have Python source, so Jedi infers what it can from:
- Function signatures
- Docstrings
- Type hints (if present)

Some completions might be incomplete for:
- `maya.cmds` (partially generated from C++)
- `maya.OpenMaya` (C++ bindings)
- `maya.api.OpenMaya` (C++ bindings)

But you should still get function names, and Jedi does a good job inferring.

### 2. Dynamic maya.cmds
`maya.cmds` functions are dynamically generated based on loaded plugins. Jedi sees the base set, but plugin-specific commands might not appear until you've imported and used them.

### 3. MEL commands
Jedi only works with Python. MEL command completions are not supported.

## Future Enhancements

- [ ] Add type stubs for maya.cmds to improve completions
- [ ] Cache completion results for common modules
- [ ] Add signature hints showing function parameters
- [ ] Show docstrings on hover
- [ ] Support for MEL command completion (separate system)
