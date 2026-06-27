---
title: Slider & SpinBox
description: UISlider and UISpinBox: numeric value controls with keyboard support
---

# Slider & SpinBox

Brine2D provides two numeric input controls:

- **`UISlider`**: drag handle on a track; horizontal or vertical
- **`UISpinBox`**: numeric field with increment/decrement buttons and optional direct keyboard entry

Both implement `IUIComponent` and `IAnchoredUIComponent`.

---

## UISlider

### Constructor

```csharp
var slider = new UISlider(new Vector2(100, 200), new Vector2(200, 20));
_canvas.Add(slider);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Value` | `float` | `0` | Current value; clamped to `[MinValue, MaxValue]` |
| `MinValue` | `float` | `0` | Minimum |
| `MaxValue` | `float` | `1` | Maximum |
| `Step` | `float` | `0` | Snap increment; `0` = smooth |
| `Orientation` | `SliderOrientation` | `Horizontal` | `Horizontal` or `Vertical` |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `TrackColor` | `Color` | `(60,60,60)` |
| `FillColor` | `Color` | `(80,140,220)` |
| `HandleColor` | `Color` | `(200,200,200)` |
| `HandleHoverColor` | `Color` | `(255,255,255)` |
| `FocusColor` | `Color` | `(120,180,255)` |

### Handle

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `HandleSize` | `float` | `16` | Width and height of the drag handle in pixels |

### Value display

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ShowValue` | `bool` | `false` | Render the current value as text beside the slider |
| `ValueTextColor` | `Color` | White | Text color for the displayed value |
| `ValueFormat` | `string` | `"0.##"` | Format string passed to `float.ToString` |

### Label

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Label` | `string` | `""` | Optional text rendered adjacent to the track |
| `LabelPosition` | `SliderLabelPosition` | `Left` | `Left`, `Right`, `Above`, or `Below` |
| `LabelColor` | `Color` | White | Label text color |
| `LabelFont` | `IFont?` | `null` | Custom label font |
| `LabelSpacing` | `float` | `8` | Gap between label and track in pixels |

### Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnValueChanged` | `Action<float>` | Value changes during drag or keyboard nudge |
| `OnFocusGained` | `Action` | Slider receives keyboard focus |
| `OnFocusLost` | `Action` | Slider loses keyboard focus |

### Keyboard

When focused, Left/Right (horizontal) or Up/Down (vertical) nudge the value by one `Step` (or 1% of the range when `Step = 0`).

### Orientation

```csharp
// Vertical fader: value 1.0 = top, value 0.0 = bottom
var fader = new UISlider(new Vector2(300, 100), new Vector2(20, 160))
{
	Orientation = SliderOrientation.Vertical,
	MinValue    = 0f,
	MaxValue    = 1f,
};
```

### Example: volume slider

```csharp
var volumeSlider = new UISlider(new Vector2(140, 80), new Vector2(180, 18))
{
	MinValue  = 0f,
	MaxValue  = 1f,
	Value     = 0.75f,
	Step      = 0.05f,
	FillColor = new Color(60, 180, 100),
	Label     = "Volume",
	ShowValue = true,
	ValueFormat = "P0",
	TabIndex  = 0,
};
volumeSlider.OnValueChanged += v => AudioSystem.SetMasterVolume(v);
_canvas.Add(volumeSlider);
```

---

## UISpinBox

### Constructor

```csharp
var spin = new UISpinBox(new Vector2(100, 60), new Vector2(120, 32));
_canvas.Add(spin);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Value` | `float` | `0` | Current value; clamped to `[MinValue, MaxValue]` |
| `MinValue` | `float` | `0` | Minimum |
| `MaxValue` | `float` | `100` | Maximum |
| `Step` | `float` | `1` | Amount added/subtracted per button click or arrow key |
| `ValueFormat` | `string` | `"0"` | Format string for displayed value |
| `Font` | `IFont?` | `null` | Custom font |
| `IsFocused` | `bool` | `false` | Read-only |
| `IsEditing` | `bool` | `false` | Read-only: `true` while user is typing a value directly |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(40,40,40)` |
| `FocusedBackgroundColor` | `Color` | `(50,50,50)` |
| `BorderColor` | `Color` | `(100,100,100)` |
| `FocusedBorderColor` | `Color` | `(120,180,255)` |
| `TextColor` | `Color` | White |
| `ButtonColor` | `Color` | `(70,70,70)` |
| `ButtonHoverColor` | `Color` | `(100,100,100)` |
| `ButtonPressedColor` | `Color` | `(120,180,255)` |
| `ButtonSymbolColor` | `Color` | White |

### Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnValueChanged` | `Action<float>` | Value changes |
| `OnFocusGained` | `Action` | Gains focus |
| `OnFocusLost` | `Action` | Loses focus |

### Direct keyboard entry

When the user double-clicks the value area the control enters edit mode (`IsEditing = true`). Typing a number and pressing Enter (or clicking away) commits the value.

### Example: integer spin box

```csharp
var depthSpin = new UISpinBox(new Vector2(120, 50), new Vector2(100, 28))
{
	MinValue    = 1,
	MaxValue    = 99,
	Value       = 10,
	Step        = 1,
	ValueFormat = "0",
};
depthSpin.OnValueChanged += v => _settings.RenderDepth = (int)v;
_canvas.Add(depthSpin);
```

---

## Choosing between the two

| Scenario | Use |
|----------|-----|
| Continuous range (volume, brightness) | `UISlider` |
| Discrete integer setting | `UISpinBox` with `Step = 1` |
| Compact numeric entry in a form | `UISpinBox` |
| Visual progress indication (not editable) | [`UIProgressBar`](progress.md) |
