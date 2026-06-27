---
title: Tooltip & Toast
description: UITooltip and UIToast: hover tips and timed notifications
---

# Tooltip & Toast

- **`UITooltip`**: appears after hovering over a component for a configurable delay
- **`UIToast`**: short-lived notification managed by `UICanvas`

---

## UITooltip

A `UITooltip` is attached to any `IUIComponent` via its `Tooltip` property. `UICanvas` shows and hides it automatically as the mouse hovers.

### Constructor

```csharp
var tip = new UITooltip("Increase master volume");
```

### Attaching to a component

```csharp
var slider = new UISlider(new Vector2(120, 80), new Vector2(160, 18));
slider.Tooltip = new UITooltip("Master volume (0 – 100%)");
_canvas.Add(slider);
```

Any component with a `Tooltip` property accepts one: buttons, checkboxes, dropdowns, images, labels, sliders, and more.

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Tooltip text content |
| `ShowDelay` | `float` | `0.5` | Seconds of hover before the tooltip appears |
| `CursorOffset` | `Vector2` | `(15, 15)` | Offset from the mouse cursor |
| `MaxWidth` | `float` | `200` | Text wrap width in pixels; `0` = no wrap |
| `Padding` | `float` | `8` | Interior padding around text |
| `Font` | `IFont?` | `null` | Custom font |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(40,40,40,230)` |
| `BorderColor` | `Color` | `(200,200,200,255)` |
| `TextColor` | `Color` | White |

### Example

```csharp
var deleteBtn = new UIButton("Delete", new Vector2(20, 60), new Vector2(80, 28));
deleteBtn.Tooltip = new UITooltip("Permanently remove this item.\nCannot be undone.")
{
	ShowDelay       = 0.3f,
	MaxWidth        = 180f,
	BackgroundColor = new Color(60, 20, 20, 230),
	BorderColor     = new Color(200, 60, 60),
};
_canvas.Add(deleteBtn);
```

---

## UIToast

Toasts are queued through `UICanvas.ShowToast` and removed automatically after their lifetime elapses. They fade in, remain visible, then fade out.

### Creating and showing a toast

```csharp
var toast = new UIToast
{
	Text        = "Settings saved",
	Duration    = 3f,
	FadeInTime  = 0.2f,
	FadeOutTime = 0.5f,
};
_canvas.ShowToast(toast);
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Notification text |
| `Duration` | `float` | `3` | Seconds at full opacity |
| `FadeInTime` | `float` | `0.2` | Fade-in duration in seconds |
| `FadeOutTime` | `float` | `0.4` | Fade-out duration in seconds |
| `Width` | `float` | `260` | Panel width in pixels; text wraps inside the padding |
| `Padding` | `float` | `10` | Interior padding |
| `Font` | `IFont?` | `null` | Custom font |
| `Alpha` | `float` | `0` | Read-only: current opacity driven by the canvas |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(30,30,30,220)` |
| `BorderColor` | `Color` | `(160,160,160,255)` |
| `TextColor` | `Color` | White |

### Event

```csharp
toast.OnDismissed += () => Debug.Log("Toast gone");
```

### Dismissing early

```csharp
_canvas.DismissToast(toast);
```

### Max simultaneous toasts

```csharp
_canvas.MaxVisibleToasts = 3; // default is unlimited (0)
```

When a new toast would exceed the limit the oldest active toast is dismissed immediately.

### Reading active toasts

```csharp
IReadOnlyList<UIToast> active = _canvas.ActiveToasts;
```

### Toast stacking position

Toasts are stacked in the bottom-right corner by default. The anchor and spacing are configurable:

```csharp
_canvas.ToastAnchor  = ToastAnchor.TopRight;
_canvas.ToastPadding = 16f;
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ToastAnchor` | `ToastAnchor` | `BottomRight` | Corner where toasts stack (`TopLeft`, `TopRight`, `BottomLeft`, `BottomRight`) |
| `ToastPadding` | `float` | `12` | Gap in pixels from the screen edge and between individual toasts |

### Example: save confirmation

```csharp
_settings.Save();
_canvas.ShowToast(new UIToast
{
	Text            = "✓ Settings saved",
	Duration        = 2.5f,
	BackgroundColor = new Color(20, 60, 30, 220),
	BorderColor     = new Color(60, 180, 80),
});
```

### Example: error toast

```csharp
_canvas.ShowToast(new UIToast
{
	Text            = "Connection failed: check your network.",
	Duration        = 5f,
	Width           = 300f,
	BackgroundColor = new Color(60, 20, 20, 220),
	BorderColor     = new Color(200, 60, 60),
});
```
