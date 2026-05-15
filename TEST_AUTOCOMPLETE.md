# Testing Jedi Autocomplete

## Setup
1. Make sure you're on the `jedi-autocomplete` branch
2. Make sure Jedi is installed: `pip install jedi`

## Test in Maya

### Method 1: Using DebugEditor.py (Hot Reload)
In Maya's Script Editor, run:
```python
import sys
import os

# Adjust this path to your MayaEditor location
repo_path = "/Volumes/teaching/Code/MayaEditor"
debug_script = os.path.join(repo_path, "DebugEditor.py")

with open(debug_script) as f:
    exec(f.read())
```

### Method 2: Reload Plugin
In Maya's Script Editor, run:
```python
import maya.cmds as cmds
cmds.unloadPlugin("MayaEditor.py")
cmds.loadPlugin("MayaEditor.py")
cmds.MayaEditor()
```

## Test Cases

### Test 1: Basic module completion
1. Open the MayaEditor window
2. Type: `import os`
3. Press Enter
4. Type: `os.`
5. **Expected**: A popup should appear with completions like `path`, `getcwd`, `listdir`, etc.
6. Check the Script Editor output for debug messages like:
   ```
   [PythonTextEdit] Jedi autocomplete enabled
   [Jedi] Line X, Col Y: Found Z completions: ['path', 'getcwd', ...]
   [Jedi] Showing popup at ...
   ```

### Test 2: Object method completion
1. Type: `my_list = [1, 2, 3]`
2. Press Enter
3. Type: `my_list.`
4. **Expected**: Popup with list methods: `append`, `extend`, `pop`, etc.

### Test 3: Completion insertion
1. Type: `import os`
2. Press Enter
3. Type: `os.ge`
4. **Expected**: Popup shows `getcwd`, `getenv`, etc.
5. Use arrow keys to select `getcwd`
6. Press Enter or Tab
7. **Expected**: The text changes from `os.ge` to `os.getcwd`
8. Check Script Editor for: `[Jedi] Inserting completion: getcwd`

### Test 4: Maya cmds completion
1. Type: `import maya.cmds as cmds`
2. Press Enter
3. Type: `cmds.poly`
4. **Expected**: Popup with `polyCube`, `polySphere`, etc.

## Troubleshooting

### Popup not showing
- Check Script Editor for debug messages
- Verify Jedi is installed: `python -c "import jedi; print(jedi.__version__)"`
- Look for error messages in the debug output

### Completions empty
- Check if `[Jedi] Found 0 completions` appears
- This might be normal if typing in the middle of invalid syntax

### Wrong completions
- Jedi analyzes the code context, so it depends on imports and variable assignments above the cursor
