---
title: Menus
description: UIMenuBar and UIContextMenu: horizontal menu bar and right-click context menus
---

# Menus

Brine2D provides two menu types:

- **`UIMenuBar`**: horizontal strip at the top of the screen with dropdown submenus
- **`UIContextMenu`**: right-click overlay that closes on selection, outside click, or Escape

---

## UIMenuBar

`UIMenuBar` renders a horizontal title strip. Clicking a title opens a dropdown (`UIMenuBarMenu`) rendered as a canvas-managed overlay. Only one menu can be open at a time.

Implements `IUIComponent` and `IAnchoredUIComponent`. Defaults to `ZOrder = 100`.

### Setup

```csharp
var menuBar = new UIMenuBar
{
	Position = new Vector2(0, 0),
	Size     = new Vector2(1280, 28), // typically full screen width × BarHeight
};
_canvas.Add(menuBar);
```

When added to the canvas via `Add`, the canvas registers it internally and routes input to it while a submenu is open.

### Adding menus and items

```csharp
// Fluent API
menuBar.AddMenu("File")
	.Add("New",   onClick: () => NewFile())
	.Add("Open",  onClick: () => OpenFile())
	.AddSeparator()
	.Add("Save",  onClick: () => SaveFile())
	.Add("Exit",  onClick: () => Application.Exit());

menuBar.AddMenu("Edit")
	.Add("Undo",  onClick: () => Undo())
	.Add("Redo",  onClick: () => Redo(), enabled: false);
```

Each `.Add(label)` call returns the `UIMenuBarMenu` for further chaining. `.AddSeparator()` inserts a horizontal divider line.

### UIMenuBarMenu events

```csharp
var fileMenu = menuBar.AddMenu("View");
fileMenu.OnItemSelected += (index, label) => Debug.Log($"Selected: {label}");
```

### Appearance properties

| Property | Type | Default |
|----------|------|---------|
| `BarHeight` | `float` | `28` |
| `TitlePadding` | `float` | `12` |
| `SubmenuWidth` | `float` | `180` |
| `ItemHeight` | `float` | `28` |
| `SeparatorHeight` | `float` | `8` |
| `ItemTextPadding` | `float` | `10` |
| `Font` | `IFont?` | `null` |

### Color properties

| Property | Type | Default |
|----------|------|---------|
| `BarColor` | `Color` | `(45,45,48)` |
| `BarBorderColor` | `Color` | `(68,68,68)` |
| `TitleTextColor` | `Color` | White |
| `TitleHoverColor` | `Color` | `(65,65,80)` |
| `TitleActiveColor` | `Color` | `(55,95,175)` |
| `SubmenuBackgroundColor` | `Color` | `(45,45,48,250)` |
| `SubmenuBorderColor` | `Color` | `(90,90,100)` |
| `ItemHoverColor` | `Color` | `(55,95,175)` |
| `ItemTextColor` | `Color` | White |
| `ItemDisabledColor` | `Color` | `(110,110,110)` |
| `SeparatorColor` | `Color` | `(90,90,100)` |

### State

```csharp
bool open   = menuBar.IsOpen;
int  index  = menuBar.OpenMenuIndex; // -1 = closed
IReadOnlyList<UIMenuBarMenu> menus = menuBar.Menus;
```

### Disabling items after creation

```csharp
var editMenu = menuBar.AddMenu("Edit");
editMenu.Add("Undo", onClick: () => Undo());

// Later: disable Undo when nothing can be undone
var undoItem = editMenu.Items[0]; // UIMenuItem
undoItem.Enabled = false;
```

---

## UIContextMenu

`UIContextMenu` is shown via `UICanvas.ShowContextMenu`. The canvas positions and manages it; it closes automatically on selection, outside click, or Escape.

### Building the menu

```csharp
var menu = new UIContextMenu();
menu.AddItem("Cut",    () => Cut());
menu.AddItem("Copy",   () => Copy());
menu.AddItem("Paste",  () => Paste());
menu.AddSeparator();
menu.AddItem("Delete", () => Delete(), enabled: false);
```

### Showing the menu

```csharp
// Call from inside a right-click or OnRightClick handler
_canvas.ShowContextMenu(menu, mousePosition);
```

### Events

```csharp
menu.OnItemSelected += (index, label) => Debug.Log($"Clicked: {label}");
menu.OnClosed       += () => Debug.Log("Menu closed");
```

### Appearance properties

| Property | Type | Default |
|----------|------|---------|
| `Width` | `float` | `160` |
| `ItemHeight` | `float` | `28` |
| `SeparatorHeight` | `float` | `8` |
| `TextPadding` | `float` | `10` |
| `Font` | `IFont?` | `null` |

### Color properties

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(45,45,45,245)` |
| `BorderColor` | `Color` | `(160,160,160)` |
| `HoverColor` | `Color` | `(80,120,200)` |
| `TextColor` | `Color` | White |
| `DisabledTextColor` | `Color` | `(110,110,110)` |
| `SeparatorColor` | `Color` | `(100,100,100,200)` |

### Example: tree-view right click

```csharp
treeView.OnRightClick += (node, mousePos) =>
{
	var ctx = new UIContextMenu { Width = 140f };
	ctx.AddItem("Rename",   () => BeginRename(node));
	ctx.AddItem("Duplicate",() => Duplicate(node));
	ctx.AddSeparator();
	ctx.AddItem("Delete",   () => Delete(node));
	_canvas.ShowContextMenu(ctx, mousePos);
};
```

---

## UIMenuItem

`UIMenuItem` represents a single item in a dropdown:

| Property | Type | Description |
|----------|------|-------------|
| `Label` | `string` | Display text |
| `Enabled` | `bool` | When `false`, item is dimmed and cannot be clicked |
| `IsSeparator` | `bool` | Read-only: separator items are created via `AddSeparator()` |
| `OnClick` | `Action?` | Per-item click callback |

Items can also be created and added manually:

```csharp
var item = new UIMenuItem("Save As…", enabled: true, onClick: () => SaveAs());
fileMenu.Add(item);
```
