# Custom Popup Solution

## Problem Summary

QCompleter was causing crashes in Maya with these symptoms:
- ✗ Crash after typing second character
- ✗ Popup parent was `None`
- ✗ Model showed 0 items despite being populated with completions
- ✗ `QTimer.singleShot` may have caused threading issues

## Solution: Custom JediCompletionPopup

Replaced `QCompleter` with a custom `QListWidget`-based popup that gives us full control.

## New Files

### `JediCompleter.py`
A standalone module with:
- **`JediCompletionPopup`**: Custom QListWidget popup widget
- **`get_jedi_completions()`**: Helper function to get completions from Jedi

## How It Works

### 1. Initialization
```python
self._jedi_popup = JediCompletionPopup(self)
self._jedi_popup.completion_selected.connect(self._insert_completion)
```

### 2. On Keystroke
When you type a character:
1. `keyPressEvent` processes the key normally
2. If it's alphanumeric, `_`, or `.`, we call `_update_completions()`
3. Get completions from Jedi using `get_jedi_completions()`
4. Show popup with `self._jedi_popup.show_completions(self, completions)`

### 3. Popup Display
The popup:
- Positions itself below the cursor using `mapToGlobal()`
- Limits to 50 items for performance
- Has white background with blue border
- Auto-sizes based on content

### 4. Navigation
When popup is visible:
- **Up/Down**: Navigate items
- **Enter/Tab**: Select current item
- **Escape**: Hide popup
- **Other keys**: Hide popup and send to editor

### 5. Selection
When you select an item:
1. `completion_selected` signal emits the text
2. `_insert_completion()` replaces the current word
3. Popup hides automatically

## Benefits

✅ **No crashes**: Direct control, no threading issues  
✅ **Simple**: Fewer moving parts than QCompleter  
✅ **Predictable**: We control exactly when it shows/hides  
✅ **Maya-compatible**: Works in Maya's Qt environment  
✅ **Debuggable**: Clear flow, easy to trace  

## Testing

1. **Reload editor** in Maya
2. **Type**: `import os`
3. **Press Enter**
4. **Type**: `os.` 
5. **Expected**: White popup with blue border appears below cursor
6. **Type more**: Popup updates as you type
7. **Use arrows**: Navigate completions
8. **Press Enter**: Insert selected completion

## Debug Output

You should see:
```
[PythonTextEdit] Custom Jedi autocomplete enabled
[JediCompletionPopup] Initialized
[Jedi] Line 2, Col 3: Found 454 completions
[JediCompletionPopup] Showing 50 items at QPoint(...)
```

## Customization

### Styling
Edit the `setStyleSheet()` in `JediCompletionPopup.__init__()`:
```python
self.setStyleSheet("""
    QListWidget {
        background-color: #ffffff;  /* Change background */
        border: 2px solid #4a90d9;   /* Change border */
        font-size: 12px;             /* Change font size */
    }
""")
```

### Size Limits
Edit in `JediCompletionPopup.__init__()`:
```python
self.setMinimumWidth(200)   # Minimum width
self.setMaximumWidth(400)   # Maximum width
self.setMaximumHeight(300)  # Maximum height
```

### Item Limit
Edit in `show_completions()`:
```python
for comp in completions[:50]:  # Change 50 to different number
```

## Known Limitations

1. **No fuzzy filtering**: Shows all completions from Jedi as-is
2. **No signature hints**: Just shows completion names (future enhancement)
3. **No icons**: Could add icons for functions, classes, etc.
4. **Fixed position**: Always below cursor (could be smarter about screen edges)

## Future Enhancements

- [ ] Add function signatures as tooltips
- [ ] Add icons for different completion types (function, class, variable)
- [ ] Add fuzzy filtering to narrow results as you type
- [ ] Smart positioning to avoid going off-screen
- [ ] Show docstrings on hover
- [ ] Ctrl+Space to manually trigger completions
