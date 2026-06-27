---
title: Panel, Stack & Grid
description: UIPanel, UIStackPanel, and UIGrid: container and layout controls
---

# Panel, Stack & Grid

Three container types handle background rendering and child layout:

- **`UIPanel`**: free-form container; children are positioned relative to the panel
- **`UIStackPanel`**: auto-stacks children vertically or horizontally
- **`UIGrid`**: arranges children in a fixed-column grid

All three implement `IUIComponent` and `IAnchoredUIComponent`.

---

## UIPanel

`UIPanel` is a background surface. Children are positioned relative to the panel's top-left corner: child `Position = (0, 0)` is the panel's own top-left.

### Constructor

```csharp
var panel = new UIPanel(new Vector2(50, 50), new Vector2(300, 200));
_canvas.Add(panel);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `BackgroundColor` | `Color` | `(50,50,50,200)` | Solid background fill |
| `BorderColor` | `Color?` | `null` | Outline color; `null` = no outline |
| `BorderThickness` | `float` | `2` | Outline thickness in pixels |
| `BlocksInput` | `bool` | `false` | Consume mouse events that hit the panel area |
| `ClipChildren` | `bool` | `false` | Clip child rendering to the panel bounds |

### Nine-slice texture

```csharp
panel.BackgroundTexture       = renderer.LoadTexture("ui/panel.png");
panel.BackgroundTextureBorder = new NineSliceBorder(12, 12, 12, 12);
panel.BackgroundTextureTint   = Color.White;
```

When `BackgroundTexture` is set it replaces the solid color fill. The border outline is still drawn on top if `BorderColor` is set.

### Child management

```csharp
panel.AddChild(new UILabel("Name", new Vector2(10, 10)));
panel.RemoveChild(label);
panel.ClearChildren();

IReadOnlyList<IUIComponent> kids = panel.GetChildren();
```

### Example: settings window

```csharp
var win = new UIPanel(new Vector2(200, 100), new Vector2(400, 300))
{
	BackgroundColor = new Color(30, 30, 40, 240),
	BorderColor     = new Color(80, 80, 120),
	BlocksInput     = true,
};
win.AddChild(new UILabel("Settings", new Vector2(10, 10)) { Color = Color.White });
win.AddChild(new UICheckbox("VSync", new Vector2(10, 40)));
_canvas.Add(win);
```

---

## UIStackPanel

`UIStackPanel` positions its children one after another, separated by `Spacing`. `Size` is recalculated to fit all children on every `Render` call: you do not set a fixed size.

### Constructor

```csharp
var stack = new UIStackPanel(new Vector2(20, 60));
_canvas.Add(stack);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Orientation` | `StackOrientation` | `Vertical` | `Vertical` or `Horizontal` |
| `Spacing` | `float` | `4` | Gap between children in pixels |
| `Padding` | `float` | `0` | Interior padding on all sides |
| `BackgroundColor` | `Color?` | `null` | Optional background; `null` = transparent |
| `BlocksInput` | `bool` | `false` | Consume mouse events |
| `ClipChildren` | `bool` | `false` | Clip children to bounds |

### Child management

Same as `UIPanel`: `AddChild`, `RemoveChild`, `ClearChildren`, `GetChildren`.

### Example: vertical button list

```csharp
var menu = new UIStackPanel(new Vector2(0, 0))
{
	Spacing     = 8f,
	Padding     = 12f,
	Anchor      = UIAnchor.MiddleCenter,
	AnchorOffset = new Vector2(-60, -80),
};

foreach (var (label, action) in menuItems)
{
	var btn = new UIButton(label, Vector2.Zero, new Vector2(120, 36));
	btn.OnClick += action;
	menu.AddChild(btn);
}
_canvas.Add(menu);
```

### Example: horizontal toolbar

```csharp
var toolbar = new UIStackPanel(new Vector2(10, 10))
{
	Orientation = StackOrientation.Horizontal,
	Spacing     = 4f,
};
toolbar.AddChild(new UIButton("File",  Vector2.Zero, new Vector2(50, 28)));
toolbar.AddChild(new UIButton("Edit",  Vector2.Zero, new Vector2(50, 28)));
toolbar.AddChild(new UIButton("View",  Vector2.Zero, new Vector2(50, 28)));
_canvas.Add(toolbar);
```

---

## UIGrid

`UIGrid` lays out children left-to-right, wrapping to a new row after `Columns` cells. Every cell is the same size: determined by the largest visible child. `Size` is updated automatically on every `Render` call.

### Constructor

```csharp
var grid = new UIGrid(new Vector2(20, 80));
_canvas.Add(grid);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Columns` | `int` | `2` | Number of columns |
| `HorizontalSpacing` | `float` | `4` | Gap between columns in pixels |
| `VerticalSpacing` | `float` | `4` | Gap between rows in pixels |
| `Padding` | `float` | `0` | Interior padding on all sides |
| `BackgroundColor` | `Color?` | `null` | Optional background |
| `BlocksInput` | `bool` | `false` | Consume mouse events |
| `ClipChildren` | `bool` | `false` | Clip children to bounds |

### Child management

Same as `UIPanel`: `AddChild`, `RemoveChild`, `ClearChildren`, `GetChildren`.

### Example: item inventory grid

```csharp
var inventoryGrid = new UIGrid(new Vector2(10, 60))
{
	Columns           = 5,
	HorizontalSpacing = 4f,
	VerticalSpacing   = 4f,
	Padding           = 8f,
	BackgroundColor   = new Color(20, 20, 30, 200),
};

foreach (var item in _inventory.Items)
{
	var cell = new UIImage(item.Icon, Vector2.Zero, new Vector2(48, 48));
	cell.Tooltip = new UITooltip(item.Name);
	inventoryGrid.AddChild(cell);
}
_canvas.Add(inventoryGrid);
```

---

## Choosing the right container

| Need | Use |
|------|-----|
| Freehand child positioning | `UIPanel` |
| Vertical or horizontal auto-layout | `UIStackPanel` |
| Grid of uniform-sized items | `UIGrid` |
| Scrollable content area | [`UIScrollView`](scroll-view.md) |
