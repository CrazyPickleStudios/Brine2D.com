---
title: Positioning & Anchoring
description: UIAnchor, AnchorOffset, ZOrder, and TabIndex
---

# Positioning & Anchoring

All `IUIComponent` instances are positioned in screen space by a `Vector2 Position` (pixels from the top-left corner). Components that implement `IAnchoredUIComponent` can additionally be pinned to any of nine anchor points so they stay in the correct corner or centre of the screen as the window resizes.

---

## Pixel positioning

```csharp
var label = new UILabel("Score: 0", new Vector2(20, 20));

// Move it later
label.Position = new Vector2(40, 40);
```

`(0, 0)` is the top-left corner of the screen. X increases right; Y increases down.

---

## IAnchoredUIComponent

Controls that implement `IAnchoredUIComponent` expose two extra properties:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Anchor` | `UIAnchor` | `TopLeft` | Which point on the screen this component is relative to |
| `AnchorOffset` | `Vector2` | `(0, 0)` | Pixel offset added to the resolved anchor origin |

At render time the canvas resolves `Position = anchorOrigin + AnchorOffset`.

Most built-in controls implement `IAnchoredUIComponent`. Check the component's page to confirm.

---

## UIAnchor values

```
TopLeft      TopCenter      TopRight
MiddleLeft   MiddleCenter   MiddleRight
BottomLeft   BottomCenter   BottomRight
```

```csharp
var btn = new UIButton("Settings", Vector2.Zero, new Vector2(120, 36))
{
	Anchor       = UIAnchor.BottomRight,
	AnchorOffset = new Vector2(-20, -20),  // 20 px in from corner
};
_canvas.Add(btn);
```

The button stays 20 px from the bottom-right corner regardless of screen size as long as `UICanvas.ScreenSize` is kept up to date.

---

## Anchor origin reference

| Anchor | Screen origin |
|--------|---------------|
| `TopLeft` | `(0, 0)` |
| `TopCenter` | `(width / 2, 0)` |
| `TopRight` | `(width, 0)` |
| `MiddleLeft` | `(0, height / 2)` |
| `MiddleCenter` | `(width / 2, height / 2)` |
| `MiddleRight` | `(width, height / 2)` |
| `BottomLeft` | `(0, height)` |
| `BottomCenter` | `(width / 2, height)` |
| `BottomRight` | `(width, height)` |

**Tip:** `AnchorOffset` is added to the origin. To place a 120×36 button in the dead centre of the screen:

```csharp
btn.Anchor       = UIAnchor.MiddleCenter;
btn.AnchorOffset = new Vector2(-60, -18); // half of width / height
```

---

## ZOrder

`ZOrder` controls which component renders on top and which receives input first when components overlap.

```csharp
var background = new UIPanel(...) { ZOrder = 0  };
var content    = new UIPanel(...) { ZOrder = 10 };
var tooltip    = new UIPanel(...) { ZOrder = 100 };
```

Higher values appear on top. Components with equal `ZOrder` fall back to add order (last added = on top).

---

## TabIndex

`TabIndex` sets the keyboard focus order when the user presses Tab or Shift+Tab.

```csharp
var nameField  = new UITextInput(...) { TabIndex = 0 };
var emailField = new UITextInput(...) { TabIndex = 1 };
var submitBtn  = new UIButton(...)   { TabIndex = 2 };
```

Lower values receive focus first. Components with the same `TabIndex` are ordered by add order (last added = focused first). The default value is `int.MaxValue`, which means non-tabbed components are visited last.

---

## Size

`Size` is always in pixels. For most components you set it in the constructor:

```csharp
var slider = new UISlider(new Vector2(100, 300), new Vector2(200, 20));
// position = (100, 300), size = (200, 20)
```

`UILabel` and `UICheckbox` recalculate their own `Size` during the first `Render` call based on text metrics and the active font, so you typically do not need to set `Size` on them manually.
