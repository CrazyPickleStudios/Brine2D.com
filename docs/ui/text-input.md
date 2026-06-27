---
title: Text Input & Area
description: UITextInput and UITextArea: single-line and multi-line editable text fields
---

# Text Input & Area

Brine2D provides two editable text controls:

- **`UITextInput`**: single-line field with horizontal scrolling
- **`UITextArea`**: multi-line editor with vertical scrolling

Both support text selection, clipboard operations, undo/redo, character filtering, and read-only mode. Both implement `IUIComponent` and `IAnchoredUIComponent`.

---

## UITextInput

### Constructor

```csharp
var input = new UITextInput(new Vector2(100, 50), new Vector2(240, 32));
_canvas.Add(input);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Current text value |
| `Placeholder` | `string` | `"Enter text..."` | Shown when empty |
| `MaxLength` | `int` | `0` | Max character count; `0` = unlimited |
| `CursorPosition` | `int` | `0` | Cursor position as a character index |
| `Font` | `IFont?` | `null` | Custom font |
| `IsFocused` | `bool` | `false` | Read-only: whether the field has input focus |
| `ReadOnly` | `bool` | `false` | Display only; navigation and Ctrl+C still work |
| `IsPassword` | `bool` | `false` | Masks text with `MaskChar` |
| `MaskChar` | `char` | `'●'` | Password mask character |
| `CharacterFilter` | `Func<char, bool>?` | `null` | Accept only characters where delegate returns `true` |
| `CursorHeight` | `float` | `16` | Height of the cursor bar and selection highlight in pixels |
| `UndoStackLimit` | `int` | `100` | Max undo steps; `0` = unlimited |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `TextColor` | `Color` | White |
| `PlaceholderColor` | `Color` | `(150,150,150)` |
| `BackgroundColor` | `Color` | `(40,40,40)` |
| `FocusedBackgroundColor` | `Color` | `(50,50,50)` |
| `BorderColor` | `Color` | `(100,100,100)` |
| `FocusedBorderColor` | `Color` | `(120,180,255)` |
| `SelectionColor` | `Color` | `(80,120,200,180)` |

### Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnTextChanged` | `Action<string>` | Text changes on any keystroke or paste |
| `OnSubmit` | `Action<string>` | Enter key pressed |
| `OnFocusGained` | `Action` | Field gains keyboard focus |
| `OnFocusLost` | `Action` | Field loses keyboard focus |

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| Arrow keys | Move cursor |
| Shift + Arrow | Extend selection |
| Ctrl + A | Select all |
| Ctrl + C / X / V | Copy / cut / paste |
| Ctrl + Z / Y | Undo / redo |
| Home / End | Jump to start / end of line |
| Backspace / Delete | Delete character |
| Enter | Fire `OnSubmit` |

### Example: username field

```csharp
var usernameInput = new UITextInput(new Vector2(120, 100), new Vector2(200, 30))
{
	Placeholder          = "Username",
	MaxLength            = 24,
	FocusedBorderColor   = new Color(100, 200, 255),
	TabIndex             = 0,
};
usernameInput.OnSubmit += text => Login(text);
_canvas.Add(usernameInput);
```

### Example: password field

```csharp
var passwordInput = new UITextInput(new Vector2(120, 140), new Vector2(200, 30))
{
	Placeholder = "Password",
	IsPassword  = true,
	TabIndex    = 1,
};
```

### Example: numeric only

```csharp
var portInput = new UITextInput(new Vector2(120, 180), new Vector2(80, 30))
{
	Placeholder     = "Port",
	CharacterFilter = c => char.IsDigit(c),
	MaxLength       = 5,
	TabIndex        = 2,
};
```

---

## UITextArea

### Constructor

```csharp
var area = new UITextArea(new Vector2(20, 60), new Vector2(400, 200));
_canvas.Add(area);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Current text (`'\n'` as line separator) |
| `Placeholder` | `string` | `"Enter text..."` | Shown when empty and unfocused |
| `MaxLength` | `int` | `0` | Max character count; `0` = unlimited |
| `CursorPosition` | `int` | `0` | Cursor as a character index into `Text` |
| `Font` | `IFont?` | `null` | Custom font |
| `LineHeight` | `float` | `20` | Pixel height of each text line |
| `IsFocused` | `bool` | `false` | Read-only |
| `ReadOnly` | `bool` | `false` | Display only |
| `TabInsertsTab` | `bool` | `false` | When `true`, Tab inserts `'\t'` instead of advancing focus |
| `CharacterFilter` | `Func<char, bool>?` | `null` | Per-character acceptance filter |
| `UndoStackLimit` | `int` | `100` | Max undo steps |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `TextColor` | `Color` | White |
| `PlaceholderColor` | `Color` | `(150,150,150)` |
| `BackgroundColor` | `Color` | `(40,40,40)` |
| `FocusedBackgroundColor` | `Color` | `(50,50,50)` |
| `BorderColor` | `Color` | `(100,100,100)` |
| `FocusedBorderColor` | `Color` | `(120,180,255)` |
| `SelectionColor` | `Color` | `(80,120,200,180)` |

### Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnTextChanged` | `Action<string>` | Text changes |
| `OnFocusGained` | `Action` | Area gains keyboard focus |
| `OnFocusLost` | `Action` | Area loses keyboard focus |

!!! note
	`UITextArea` does not have an `OnSubmit` event: Enter inserts a new line. Use `OnFocusLost` or a separate submit button if you need to detect "done editing".

### Example: console / log input

```csharp
var consoleInput = new UITextArea(new Vector2(10, 400), new Vector2(780, 120))
{
	Placeholder    = "Enter command…",
	TabInsertsTab  = true,
	LineHeight     = 18f,
	FocusedBorderColor = new Color(0, 200, 100),
};
consoleInput.OnTextChanged += text => _livePreview.Text = text;
```

---

## Choosing between the two

| Scenario | Use |
|----------|-----|
| Single line (name, search, port number) | `UITextInput` |
| Submit on Enter | `UITextInput` with `OnSubmit` |
| Password field | `UITextInput` with `IsPassword = true` |
| Multi-line notes, scripts, config | `UITextArea` |
| In-game chat or console | `UITextArea` |
