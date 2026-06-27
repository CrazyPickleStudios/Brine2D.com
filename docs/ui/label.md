---
title: Label & Rich Text
description: UILabel and UIRichTextLabel: static text, wrapping, and markup
---

# Label & Rich Text

Brine2D provides two text components:

- **`UILabel`**: plain text, fast, minimal properties
- **`UIRichTextLabel`**: markup/BBCode support, alignment, line-spacing, drop shadow

Both implement `IUIComponent` and `IAnchoredUIComponent`.

---

## UILabel

### Constructor

```csharp
var label = new UILabel("Score: 0", new Vector2(20, 20));
_canvas.Add(label);
```

`Size` is estimated at construction time and updated accurately on the first `Render` call.

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Text to display |
| `Color` | `Color` | White | Text color |
| `Font` | `IFont?` | `null` | Custom font; `null` uses the renderer default |
| `MaxWidth` | `float` | `0` | Pixel width at which text wraps; `0` = no wrapping |

### Click event

```csharp
label.OnClick += () => Debug.Log("Label clicked");
```

Labels support a single `OnClick` event. This lets you use a label as a lightweight link or interactive element without the visual chrome of a button.

### Example: HUD score counter

```csharp
var scoreLabel = new UILabel("Score: 0", Vector2.Zero)
{
	Color  = Color.White,
	Font   = _hudFont,
	Anchor = UIAnchor.TopRight,
	AnchorOffset = new Vector2(-20, 20),
};
_canvas.Add(scoreLabel);

// Update each frame
scoreLabel.Text = $"Score: {_score}";
```

---

## UIRichTextLabel

### Constructor

```csharp
var rtl = new UIRichTextLabel("[color=#FF4444]Warning:[/color] low health", new Vector2(20, 50));
_canvas.Add(rtl);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Markup text |
| `Color` | `Color` | White | Default text color where no tag overrides |
| `Font` | `IFont?` | `null` | Custom font |
| `MaxWidth` | `float` | `0` | Wrap width; `0` = no wrapping |
| `MaxHeight` | `float` | `0` | Height constraint for vertical alignment; `0` = no constraint |
| `HorizontalAlign` | `TextAlignment` | `Left` | `Left`, `Center`, or `Right` within `MaxWidth` |
| `VerticalAlign` | `VerticalAlignment` | `Top` | `Top`, `Middle`, or `Bottom` within `MaxHeight` |
| `LineSpacing` | `float` | `1.2` | Line height multiplier |
| `ShadowOffset` | `Vector2?` | `null` | Drop-shadow offset; `null` disables the shadow |
| `ShadowColor` | `Color` | `(0,0,0,128)` | Shadow color |
| `MarkupParser` | `IMarkupParser?` | `null` | Custom markup parser; `null` = renderer BBCode default |

### Markup tags (BBCode)

Tags are parsed by the renderer's built-in BBCode parser by default.

| Tag | Example | Effect |
|-----|---------|--------|
| `[color=#rrggbb]` | `[color=#FF0000]red[/color]` | Inline color |
| `[b]` | `[b]bold[/b]` | Bold |
| `[i]` | `[i]italic[/i]` | Italic |
| `[u]` | `[u]underline[/u]` | Underline |
| `[s]` | `[s]strikethrough[/s]` | Strikethrough |

### Example: styled tooltip body

```csharp
var body = new UIRichTextLabel(
	"[b]Fireball[/b]\n[color=#AAAAAA]Deals [color=#FF6600]50[/color] fire damage.[/color]",
	new Vector2(10, 10))
{
	MaxWidth        = 200f,
	LineSpacing     = 1.3f,
	ShadowOffset    = new Vector2(1, 1),
	ShadowColor     = new Color(0, 0, 0, 160),
};
```

### Example: centred multi-line header

```csharp
var header = new UIRichTextLabel("Game Over", new Vector2(0, 0))
{
	Font            = _titleFont,
	Color           = Color.White,
	MaxWidth        = 400f,
	MaxHeight       = 60f,
	HorizontalAlign = TextAlignment.Center,
	VerticalAlign   = VerticalAlignment.Middle,
	Anchor          = UIAnchor.MiddleCenter,
	AnchorOffset    = new Vector2(-200, -30),
};
```

---

## Choosing between the two

| Scenario | Use |
|----------|-----|
| HUD counter, name tag, static caption | `UILabel` |
| Inline color or style variation | `UIRichTextLabel` |
| Multi-line wrapped paragraph | `UIRichTextLabel` with `MaxWidth` |
| Tooltip body with formatting | `UIRichTextLabel` |
| Performance-critical list rows | `UILabel` (lighter) |
