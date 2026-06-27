---
title: Dropdown
description: UIDropdown: scrollable selection list with keyboard navigation and list flipping
---

# UIDropdown

`UIDropdown` renders a collapsed header that expands into a scrollable item list when clicked. It supports keyboard navigation, automatic list flipping when near the bottom of the screen, and an optional scrollbar when the item count exceeds `MaxVisibleItems`.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var dropdown = new UIDropdown(new Vector2(100, 60), new Vector2(180, 30));
dropdown.Items.AddRange(new[] { "Low", "Medium", "High", "Ultra" });
dropdown.SelectedIndex = 1;
_canvas.Add(dropdown);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `position` | `Vector2` | Screen-space top-left |
| `size` | `Vector2` | Width and height of the collapsed header |

---

## Items

```csharp
dropdown.Items.Add("Option A");
dropdown.Items.AddRange(new[] { "Option B", "Option C" });
dropdown.Items.Clear();
```

`Items` is a plain `List<string>`. Modify it any time; the dropdown renders the current state when next opened.

---

## Selection

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedIndex` | `int` | `-1` | Zero-based index of the selected item; `-1` = nothing selected |
| `SelectedText` | `string?` | `null` | Text of the selected item; `null` when nothing selected |
| `IsExpanded` | `bool` | `false` | Read-only: whether the list is currently open |

```csharp
dropdown.SelectedIndex = 0;  // select first item
string? current = dropdown.SelectedText;
```

---

## Display

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MaxVisibleItems` | `int` | `5` | Max rows shown before the list scrolls; `0` = show all |

---

## Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(60,60,60)` |
| `HoverColor` | `Color` | `(80,80,80)` |
| `SelectedColor` | `Color` | `(100,150,255)` |
| `TextColor` | `Color` | White |
| `BorderColor` | `Color` | `(150,150,150)` |
| `ScrollbarColor` | `Color` | `(120,120,120)` |
| `ScrollbarWidth` | `float` | `8` |

---

## Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnSelectionChanged` | `Action<int, string?>` | Selected index or text changes |
| `OnFocusGained` | `Action` | Dropdown gains keyboard focus |
| `OnFocusLost` | `Action` | Dropdown loses keyboard focus |

```csharp
dropdown.OnSelectionChanged += (index, text) =>
{
	_settings.Quality = (QualityLevel)index;
};
```

---

## Keyboard navigation

When focused:

| Key | Action |
|-----|--------|
| Space / Enter | Open / close the list |
| Up / Down arrows | Move highlighted item |
| Enter (while open) | Confirm selection |
| Escape | Close without changing selection |

---

## List flipping

When the expanded list would extend past the bottom of the screen, the canvas automatically draws it above the header instead. `UICanvas` propagates the current `ScreenSize.Y` into `ScreenHeight` automatically via `PropagateScreenSize`.

---

## Example: graphics quality selector

```csharp
var qualityDrop = new UIDropdown(new Vector2(160, 80), new Vector2(160, 28))
{
	MaxVisibleItems  = 4,
	SelectedColor    = new Color(60, 160, 100),
	TabIndex         = 0,
};
qualityDrop.Items.AddRange(Enum.GetNames<QualityLevel>());
qualityDrop.SelectedIndex = (int)_settings.Quality;
qualityDrop.OnSelectionChanged += (i, _) => ApplyQuality((QualityLevel)i);
_canvas.Add(qualityDrop);
```

---

## Dropdown inside a scroll view

When a `UIDropdown` is placed inside a `UIScrollView` and expanded, the canvas renders the expanded list as a top-level overlay so the list is never clipped by the scroll view. This is handled automatically: no extra configuration is needed.
