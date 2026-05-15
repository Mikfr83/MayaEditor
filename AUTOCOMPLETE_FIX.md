# Jedi Autocomplete Fix

## Problem
The Jedi autocomplete popup was not appearing when typing, even though the basic integration code was in place.

## Root Cause
The `QCompleter` was not attached to the widget. While the model was set and the signal was connected, the completer didn't know where to display the popup.

## Changes Made

### 1. Added `setWidget()` call (Critical Fix)
**File**: `MayaEditorCore/PythonTextEdit.py`  
**Line**: ~108

```python
self.completer.setWidget(self)  # Attach completer to this widget
```

Without this call, the completer has no context about where to show the popup.

### 2. Fixed Column Index
**File**: `MayaEditorCore/PythonTextEdit.py`  
**Line**: ~193

Changed from:
```python
col = self.textCursor().positionInBlock() + 1
```

To:
```python
col = self.textCursor().positionInBlock()
```

Jedi uses 0-based column indexing, while the line number is 1-based.

### 3. Added Debug Output
Added print statements to trace the autocomplete flow:
- `[PythonTextEdit] Jedi autocomplete enabled` - Confirms Jedi is available on startup
- `[Jedi] Line X, Col Y: Found N completions: [...]` - Shows what completions were found
- `[Jedi] Showing popup at ...` - Confirms popup is being triggered
- `[Jedi] Inserting completion: ...` - Shows when a completion is selected
- `[Jedi] Error getting completions: ...` - Shows any errors during completion

### 4. Added Safety Checks
Added bounds checking in `_insert_completion()` to prevent "QTextCursor::setPosition out of range" warnings:

```python
doc_length = len(doc)
start = max(0, min(start, doc_length))
end = max(0, min(end, doc_length))
```

## Testing
See `TEST_AUTOCOMPLETE.md` for detailed testing instructions.

## How It Works Now

1. **User types** a character (letter, digit, underscore, or dot)
2. **`keyPressEvent`** calls `_update_completions()`
3. **Jedi analyzes** the code at cursor position
4. **Completions populate** the `QStringListModel`
5. **Popup appears** at the cursor position via `completer.complete(rect)`
6. **User selects** a completion with arrow keys + Enter/Tab
7. **`_insert_completion`** replaces the partial word with the selected completion

## Debug Workflow

When testing in Maya, watch the Script Editor for debug output:

```
[PythonTextEdit] Jedi autocomplete enabled
[Jedi] Line 3, Col 3: Found 156 completions: ['path', 'getcwd', 'getenv', 'listdir', 'makedirs']...
[Jedi] Showing popup at PyQt6.QtCore.QRect(...)
[Jedi] Inserting completion: getcwd
```

If you don't see these messages:
- Jedi might not be installed
- `_JEDI_AVAILABLE` might be False
- An exception might be silently caught

## Future Improvements
- Add completion popup styling
- Show function signatures in the popup
- Add configurable trigger characters
- Add keyboard shortcut to manually trigger completions (Ctrl+Space)
- Remove debug prints once stable
