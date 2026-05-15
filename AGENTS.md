# AGENTS.md — MayaEditor

## What this is
A Maya plugin (Python 3 / PySide6) replacing the built-in Script Editor.
Plugin entry: `plug-ins/MayaEditor.py` → registers `cmds.MayaEditor()` command.
Core logic: `plug-ins/MayaEditorCore/` (package re-exports from `EditorDialog.py`).

## Maya-specific constraints
- Maya/PySide6 imports (`maya.cmds`, `PySide6`, `shiboken6`) have no stubs — mypy is configured with `follow_imports=skip` and `ignore_missing_imports=True` in `mypy.ini`.
- `EditorStandalone.py` requires `maya.standalone.initialize()` before `import maya.cmds` — the import order matters.
- The `.qrc` resource file must be compiled with `pyside6-rcc` → `.rcc`.
- Sentinel `maya_useNewAPI = True` at module level enables Maya Python 2 API.

## Dev workflow
- **Hot-reload**: Run `DebugEditor.py` inside Maya's script editor — it deletes stale `MayaEditorCore` submodules from `sys.modules` and re-imports.
- **Reload plugin** from Maya Script Editor: `cmds.unloadPlugin("MayaEditor.py"); cmds.loadPlugin("MayaEditor.py")`
- **Re-open editor**: `cmds.MayaEditor()`

## No test infrastructure
No test framework, no Makefile, no CI. `TODO.md` lists "add tests" as a pending task.

## Install
`python3 installEditor.py` — writes `MayaEditor.mod` into the Maya modules folder.
Manual alternative: edit `MayaEditor.mod` to point at the repo root.

## Plugin structure
```
plug-ins/
  MayaEditor.py          # Maya MPxCommand plugin, auto-loads UI via evalDeferred
  MayaEditorCore/        # All editor logic
    __init__.py          # re-exports EditorDialog
    EditorDialog.py      # Main dialog (MayaQWidgetDockableMixin), owns all sub-widgets
    PythonTextEdit.py    # Python editor with Jedi code model
    MelTextEdit.py       # MEL editor
    ...
  icons/                 # QRC resource icons
  ui/                    # Qt Designer .ui files
```
