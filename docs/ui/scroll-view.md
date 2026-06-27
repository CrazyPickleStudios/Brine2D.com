---
title: Scroll View
description: UIScrollView: scrollable container with vertical and horizontal scrollbars
---

# UIScrollView

`UIScrollView` clips its children to a visible viewport and provides scrollbars to navigate content that exceeds the view size. Content can scroll vertically, horizontally, or both.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var sv = new UIScrollView(new Vector2(20, 60), new Vector2(400, 300));
_canvas.Add(sv);
```

---

## Content size

You must tell the scroll view how large the content actually is. The scroll view does not measure its children: set `ContentHeight` and/or `ContentWidth` manually.

```csharp
sv.ContentHeight = 800f;  // content is taller than the 300px view
sv.ContentWidth  = 400f;  // same as view width = no horizontal scrolling
```

---

## Scrollbars

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ShowVerticalScrollbar` | `bool` | `true` | Show the vertical scrollbar |
| `ShowHorizontalScrollbar` | `bool` | `false` | Show the horizontal scrollbar |
| `ScrollbarWidth` | `float` | `10` | Scrollbar track width in pixels |
| `MinScrollbarThumbSize` | `float` | `10` | Minimum thumb height/width in pixels |
| `ScrollSpeed` | `float` | `20` | Pixels scrolled per mouse wheel tick |

---

## Scroll offset

```csharp
// Read current position
Vector2 offset = sv.ScrollOffset; // (0,0) = top-left

// Jump to a position
sv.ScrollOffset = new Vector2(0, 200);
```

`ScrollOffset` is automatically clamped to `[0, ContentWidth - Size.X]` × `[0, ContentHeight - Size.Y]`.

---

## Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(40,40,40)` |
| `BorderColor` | `Color` | `(80,80,80)` |
| `ScrollbarTrackColor` | `Color` | `(30,30,30)` |
| `ScrollbarColor` | `Color` | `(100,100,100)` |
| `ScrollbarHoverColor` | `Color` | `(120,120,120)` |
| `FocusColor` | `Color` | `(120,180,255)` |

---

## Nine-slice background

```csharp
sv.BackgroundTexture       = renderer.LoadTexture("ui/scrollview_bg.png");
sv.BackgroundTextureBorder = new NineSliceBorder(8, 8, 8, 8);
sv.BackgroundTextureTint   = Color.White;
```

---

## Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnScrollChanged` | `Action<Vector2>` | `ScrollOffset` changes |
| `OnFocusGained` | `Action` | Gains keyboard focus |
| `OnFocusLost` | `Action` | Loses keyboard focus |

---

## Child management

```csharp
sv.AddChild(component);
sv.RemoveChild(component);
sv.ClearChildren();

IReadOnlyList<IUIComponent> kids = sv.GetChildren();
```

Child `Position` is relative to the scroll view's top-left. The canvas applies `ScrollOffset` when hit-testing and rendering.

---

## Keyboard scrolling

When the scroll view has focus, the arrow keys and Page Up/Down scroll the content. Set `TabIndex` to make it focusable via Tab.

---

## Example: settings list

```csharp
var settingsScroll = new UIScrollView(new Vector2(20, 60), new Vector2(460, 340))
{
	ContentHeight = 600f,
	ScrollSpeed   = 30f,
	BackgroundColor = new Color(25, 25, 35, 230),
};

float y = 8f;
foreach (var setting in _settings.All)
{
	var row = BuildSettingRow(setting); // returns IUIComponent
	row.Position = new Vector2(8, y);
	settingsScroll.AddChild(row);
	y += row.Size.Y + 6f;
}

settingsScroll.ContentHeight = y + 8f; // fit to content
_canvas.Add(settingsScroll);
```

---

## Dropdowns inside a scroll view

When a `UIDropdown` inside a scroll view is opened, the canvas renders the expanded list as a top-level overlay so the list is never clipped by the scroll view. No extra configuration is needed.

---

## Choosing content size

Because `UIScrollView` does not auto-measure its children, the typical pattern is to track the total layout height/width as you add children and set `ContentHeight`/`ContentWidth` afterward:

```csharp
float totalHeight = padding;
foreach (var row in rows)
{
	sv.AddChild(row);
	totalHeight += row.Size.Y + spacing;
}
sv.ContentHeight = totalHeight + padding;
```
