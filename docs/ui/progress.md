---
title: Progress Bar
description: UIProgressBar: directional fill bar with optional label and custom text
---

# UIProgressBar

`UIProgressBar` renders a filled bar that visually represents a value within a range. The fill can travel in any of four directions and optional text can be displayed centred over the bar: either as a percentage or via a custom formatter.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var bar = new UIProgressBar(new Vector2(20, 60), new Vector2(200, 20));
_canvas.Add(bar);
```

---

## Value

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Value` | `float` | `0` | Current value; clamped to `[MinValue, MaxValue]` |
| `MinValue` | `float` | `0` | Minimum |
| `MaxValue` | `float` | `1` | Maximum |

```csharp
bar.MinValue = 0f;
bar.MaxValue = 100f;
bar.Value    = 67f;
```

---

## Fill direction

```csharp
bar.Direction = ProgressBarDirection.LeftToRight; // default
bar.Direction = ProgressBarDirection.RightToLeft;
bar.Direction = ProgressBarDirection.BottomToTop;
bar.Direction = ProgressBarDirection.TopToBottom;
```

`BottomToTop` is typical for vertical health/ammo bars; `TopToBottom` works for download-style progress.

---

## Colors and border

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `BackgroundColor` | `Color` | `(40,40,40)` | Empty portion |
| `FillColor` | `Color` | `(0,200,0)` | Filled portion |
| `BorderColor` | `Color` | `(100,100,100)` | Outline |
| `BorderThickness` | `float` | `2` | Outline width in pixels |

---

## Text overlay

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ShowPercentage` | `bool` | `true` | Draw text over the centre of the bar |
| `PercentageFormat` | `string` | `"{0:0}%"` | Format string; `{0}` is the percentage 0–100 |
| `ProgressTextProvider` | `Func<float, float, string>?` | `null` | Custom text delegate; overrides `PercentageFormat` |
| `TextColor` | `Color` | White | Text color |
| `Font` | `IFont?` | `null` | Custom font |

```csharp
// Show "67 / 100 HP" instead of "67%"
bar.ProgressTextProvider = (value, max) => $"{value:0} / {max:0} HP";
```

---

## Label

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Label` | `string` | `""` | Text rendered above the bar |
| `LabelColor` | `Color` | White | Label text color |

---

## Event

```csharp
bar.OnValueChanged += newValue => UpdateUI(newValue);
```

---

## Example: health bar

```csharp
var hpBar = new UIProgressBar(new Vector2(10, 10), new Vector2(180, 16))
{
	MinValue         = 0f,
	MaxValue         = 100f,
	Value            = 75f,
	FillColor        = new Color(220, 50, 50),
	BackgroundColor  = new Color(50, 20, 20),
	BorderColor      = new Color(80, 80, 80),
	ShowPercentage   = false,
	Anchor           = UIAnchor.TopLeft,
	AnchorOffset     = new Vector2(10, 10),
};
_canvas.Add(hpBar);

// Update each frame
hpBar.Value = _player.Health;
```

## Example: loading bar with custom text

```csharp
var loadBar = new UIProgressBar(new Vector2(0, 0), new Vector2(400, 24))
{
	MinValue              = 0f,
	MaxValue              = 1f,
	FillColor             = new Color(60, 140, 255),
	ShowPercentage        = true,
	ProgressTextProvider  = (v, max) => $"Loading… {v / max * 100:0}%",
	Anchor                = UIAnchor.MiddleCenter,
	AnchorOffset          = new Vector2(-200, 0),
};
_canvas.Add(loadBar);
```

## Example: vertical ammo bar

```csharp
var ammoBar = new UIProgressBar(new Vector2(0, 0), new Vector2(12, 80))
{
	Direction       = ProgressBarDirection.BottomToTop,
	MinValue        = 0f,
	MaxValue        = 30f,
	FillColor       = new Color(255, 200, 50),
	ShowPercentage  = false,
	Anchor          = UIAnchor.BottomRight,
	AnchorOffset    = new Vector2(-30, -20),
};
_canvas.Add(ammoBar);
```
