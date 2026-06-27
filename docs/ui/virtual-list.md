---
title: Virtual List
description: UIVirtualList<T>: high-performance virtualized scrolling list
---

# UIVirtualList\<T\>

`UIVirtualList<T>` renders only the rows currently visible in the viewport, making it practical for thousands of items. It supports single-item selection, a vertical scrollbar, alternating row colors, hover highlighting, and a custom per-row renderer delegate.

`UIVirtualList<T>` extends `UIVirtualListBase` which implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var list = new UIVirtualList<string>(new Vector2(20, 60), new Vector2(320, 280));
_canvas.Add(list);
```

---

## Data binding

```csharp
list.SetItems(new[] { "Alpha", "Beta", "Gamma", "Delta" });

// Or from an existing collection
list.SetItems(_players.AsReadOnly());
```

`SetItems` resets the scroll position and selection.

---

## Custom row renderer

Supply a delegate that receives the renderer, the item, row bounds, and state flags:

```csharp
list.RowRenderer = (renderer, item, x, y, width, height, selected, hovered) =>
{
	var bgColor = selected ? new Color(60, 100, 180) :
				  hovered  ? new Color(70, 70, 100) :
				  new Color(40, 40, 40);

	renderer.DrawRectangleFilled(x, y, width, height, bgColor);
	renderer.DrawText(item.Name, x + 8f, y + (height - 14f) / 2f,
		new TextRenderOptions { Color = Color.White });

	// Optional: draw the item's health bar
	float barWidth = width * (item.Health / item.MaxHealth);
	renderer.DrawRectangleFilled(x + width - 50f, y + 6f, barWidth, 8f, Color.Green);
};
```

When `RowRenderer` is `null`, the built-in fallback renders `item.ToString()` with left padding, using `TextColor` and `Font`.

---

## Fallback text properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TextColor` | `Color` | White | Text color used by the built-in fallback renderer |
| `Font` | `IFont?` | `null` | Font used by the built-in fallback renderer |

---

## Geometry

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `RowHeight` | `float` | `24` | Height of each row in pixels |
| `ScrollbarWidth` | `float` | `10` | Scrollbar track width |
| `MinThumbSize` | `float` | `10` | Minimum scrollbar thumb height |

---

## Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(30,30,30)` |
| `RowColor` | `Color` | `(40,40,40)` |
| `AlternateRowColor` | `Color` | `(45,45,45)` |
| `HoverColor` | `Color` | `(70,70,100)` |
| `SelectionColor` | `Color` | `(60,100,180)` |
| `BorderColor` | `Color` | `(80,80,80)` |
| `ScrollbarTrackColor` | `Color` | `(50,50,50)` |
| `ScrollbarThumbColor` | `Color` | `(100,100,100)` |
| `ScrollbarThumbHoverColor` | `Color` | `(140,140,140)` |
| `FocusBorderColor` | `Color` | `(120,180,255)` |

---

## Selection

```csharp
int index      = list.SelectedIndex;   // -1 = none
T?  item       = list.SelectedItem;    // default(T) when none

list.OnSelectionChanged += newIndex =>
{
	var selected = list[newIndex]; // indexer
};
```

---

## Scroll position

```csharp
float offsetY = list.ScrollOffsetY;
list.ScrollToTop();
list.ScrollToBottom();
```

---

## Focus events

```csharp
list.OnFocusGained += () => { };
list.OnFocusLost   += () => { };
```

Keyboard navigation (Up/Down arrows, Page Up/Down) is active while the list is focused.

---

## Example: player leaderboard

```csharp
var leaderboard = new UIVirtualList<PlayerScore>(new Vector2(20, 80), new Vector2(440, 300))
{
	RowHeight = 28f,
	AlternateRowColor = new Color(38, 38, 42),
	TabIndex  = 0,
};

leaderboard.RowRenderer = (renderer, score, x, y, w, h, selected, hovered) =>
{
	var bg = selected ? new Color(40, 80, 160) :
			 hovered  ? new Color(55, 55, 70) :
			 new Color(42, 42, 48);
	renderer.DrawRectangleFilled(x, y, w, h, bg);

	renderer.DrawText(score.Rank.ToString(),    x + 8f, y + 6f);
	renderer.DrawText(score.PlayerName,         x + 40f, y + 6f);
	renderer.DrawText(score.Points.ToString(), x + w - 80f, y + 6f);
};

leaderboard.SetItems(_scores.AsReadOnly());
leaderboard.OnSelectionChanged += i => ShowProfile(leaderboard[i]);

_canvas.Add(leaderboard);
```

---

## Subclassing UIVirtualListBase

If you need a non-generic virtualized list (e.g. heterogeneous rows) you can subclass `UIVirtualListBase` directly and override:

```csharp
public class MyList : UIVirtualListBase
{
	private readonly List<object> _data = new();
	public override int ItemCount => _data.Count;

	protected override void RenderRow(IRenderer renderer, int index,
		float x, float y, float width, float height,
		bool selected, bool hovered)
	{
		// custom draw
	}
}
```
