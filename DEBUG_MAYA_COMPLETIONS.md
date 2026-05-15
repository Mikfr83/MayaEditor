# Debugging Maya Completions

## Key Changes

### 1. Interpreter Mode
Now using `jedi.Interpreter` which can access **live runtime objects** instead of just analyzing static code. This means:
- If you've imported `maya.cmds` in Maya's main namespace, Jedi can see it
- If you've imported modules in the editor, Jedi can access them
- Much better for REPL-style environments like Maya

### 2. Extensive Debug Output
Added verbose logging to diagnose issues:
- Shows Maya paths in sys.path
- Shows the exact line being analyzed
- Shows raw completion count
- Shows first 3 completions with their types

## Testing

### Step 1: Reload Editor
In Maya Script Editor:
```python
import sys
sys.path.append('/Volumes/teaching/Code/MayaEditor')
exec(open('/Volumes/teaching/Code/MayaEditor/DebugEditor.py').read())
```

### Step 2: Check Initialization
Look for:
```
[PythonTextEdit] Custom Jedi autocomplete enabled
[JediCompletionPopup] Initialized
[Jedi] Created project with 47 sys.path entries
[Jedi] Found 5 Maya-related paths
[Jedi] Maya paths: ['/Applications/Autodesk/maya2024/...', ...]
```

**If you see**: `WARNING: No Maya paths found in sys.path!`
- Something is wrong with Maya's Python environment
- Try: `import sys; print([p for p in sys.path if 'maya' in p.lower()])`

### Step 3: Test Basic Completion
In the editor, type:
```python
import os
os.
```

Watch console for:
```
[Jedi] Analyzing: 'os.' at col 3
[Jedi] Using Interpreter mode (runtime aware)
[Jedi] Jedi returned 234 completions
[Jedi]   - path (type: module)
[Jedi]   - getcwd (type: function)
[Jedi]   - listdir (type: function)
[Jedi] Returned 234 completions: ['path', 'getcwd', ...]...
[JediCompletionPopup] Showing 50 items at QPoint(...)
```

### Step 4: Test Maya Completions

**Important**: You need to import `maya.cmds` in Maya's **main namespace** first!

In Maya's **Script Editor** (not the MayaEditor), run:
```python
import maya.cmds as cmds
```

Now in **MayaEditor**, type:
```python
import maya.cmds as cmds
cmds.poly
```

Watch console for:
```
[Jedi] Analyzing: 'cmds.poly' at col 10
[Jedi] Using Interpreter mode (runtime aware)
[Jedi] Jedi returned 150 completions
[Jedi]   - polyCube (type: function)
[Jedi]   - polySphere (type: function)
[Jedi]   - polyPlane (type: function)
[Jedi] Returned 150 completions: ['polyCube', 'polySphere', ...]...
```

## Troubleshooting

### Issue: "WARNING: No Maya paths found in sys.path!"

**Diagnosis**: Maya's Python environment not detected
**Solution**: Check if you're running in actual Maya (not standalone Python)
```python
import sys
maya_paths = [p for p in sys.path if 'maya' in p.lower()]
if not maya_paths:
    print("ERROR: Not in Maya environment!")
else:
    print(f"OK: Found {len(maya_paths)} Maya paths")
```

### Issue: "Jedi returned 0 raw completions"

**Possible causes**:
1. **Syntax error** before cursor - Jedi can't parse
2. **Unknown module** - Not imported or not in sys.path  
3. **Wrong cursor position** - Check the "Analyzing:" line

**Debug**:
```python
# Check if module is accessible
import maya.cmds
print(dir(maya.cmds)[:10])  # Should show function names
```

### Issue: "Interpreter failed, falling back to Script"

**Cause**: Interpreter mode couldn't access namespace
**Impact**: Script mode still works but might not see runtime imports
**Debug**: Check the error message after "Interpreter failed:"

### Issue: Completions work for `os` but not `maya.cmds`

**Cause**: `maya.cmds` needs to be imported in Maya's environment first
**Solution**:
1. Import in Maya's main Script Editor: `import maya.cmds`
2. Then use in MayaEditor

**Why**: Interpreter mode accesses `__main__.__dict__`, which is Maya's main namespace.

### Issue: Very slow completions

**Cause**: First time analyzing large modules like `maya.cmds`
**Expected**: First completion: 1-2 seconds, subsequent: < 100ms
**Solution**: Wait for first completion, then it's cached

## Advanced Debugging

### Check what Jedi sees:
```python
# In MayaEditor
import jedi
source = "import maya.cmds as cmds\ncmds."
interp = jedi.Interpreter(source, namespaces=[__main__.__dict__])
comps = interp.complete(2, 5)
print([c.name for c in comps][:10])
```

### Check namespace contents:
```python
# What's in main namespace?
import __main__
maya_items = [k for k in __main__.__dict__.keys() if 'maya' in k.lower()]
print(f"Maya items in namespace: {maya_items}")
```

### Force reimport:
```python
# If modules seem stale
import sys
if 'maya.cmds' in sys.modules:
    del sys.modules['maya.cmds']
import maya.cmds
```

## Expected Behavior

### ✅ Working:
- Standard library completions (os, sys, etc.)
- Previously imported modules in the editor
- Maya modules **if imported in Maya's main namespace**
- Local variables and functions defined in the editor

### ⚠️ Limitations:
- Maya modules **not yet imported** won't show completions
- Dynamic/generated attributes might not appear
- C++ extensions without Python source (limited completions)
- Plugin-specific commands (until plugin loaded)

## Next Steps

If Maya completions still don't work after following this guide:
1. **Share the complete debug output** when typing `cmds.`
2. **Confirm Maya is imported**: `import maya.cmds; print(dir(maya.cmds)[:5])`
3. **Check Jedi version**: `import jedi; print(jedi.__version__)`
4. **Try simple test**: Does `os.` work? Then the issue is Maya-specific.
