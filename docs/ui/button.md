---
title: UIButton
description: Clickable button with per-state colors, nine-slice textures, and keyboard focus
---

# UIButton

`UIButton` is the standard clickable control. It supports four visual states (normal, hover, pressed, disabled), nine-slice texture skinning per state, configurable text alignment, and keyboard focus.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var button = new UIButton("Play", new Vector2(100, 200), new Vector2(160, 48));
_canvas.Add(button);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `string` | Label text rendered inside the button |
| `position` | `Vector2` | Screen-space top-left in pixels |
| `size` | `Vector2` | Width and height in pixels |

---

## Events

```csharp
button.OnClick      += () => StartGame();
button.OnRightClick += () => OpenContextMenu();

button.OnHoverEnter += () => PlayHoverSound();
button.OnHoverExit  += () => { };

button.OnFocusGained += () => { };
button.OnFocusLost   += () => { };
```

| Event | Fires when |
|-------|-----------|
| `OnClick` | Left mouse button released over the button, or Enter/Space while focused |
| `OnRightClick` | Right mouse button released over the button |
| `OnHoverEnter` | Mouse cursor enters the button's bounds |
| `OnHoverExit` | Mouse cursor leaves the button's bounds |
| `OnFocusGained` | Button receives keyboard focus |
| `OnFocusLost` | Button loses keyboard focus |

---

## Text properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Text` | `string` | `""` | Label text |
| `Font` | `IFont?` | `null` | Custom font; `null` uses the renderer default |
| `TextColor` | `Color` | White | Label color |
| `TextAlignment` | `TextAlignment` | `Center` | `Left`, `Center`, or `Right` |
| `TextPadding` | `float` | `8` | Pixels from the edge when aligned Left or Right |

---

## Color properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `NormalColor` | `Color` | `(70, 70, 70)` | Idle fill color |
| `HoverColor` | `Color` | `(90, 90, 90)` | Fill color while the mouse hovers |
| `PressedColor` | `Color` | `(50, 50, 50)` | Fill color while held down |
| `DisabledColor` | `Color` | `(60, 60, 60, 180)` | Fill color when `Enabled = false` |
| `FocusColor` | `Color` | `(120, 180, 255)` | Border ring color when focused |

```csharp
button.NormalColor  = new Color(30, 60, 120);
button.HoverColor   = new Color(50, 90, 160);
button.PressedColor = new Color(20, 45, 90);
button.TextColor    = Color.White;
```

---

## Nine-slice textures

Texture overrides replace the solid color fills for each state. All states share the same `TextureBorder` insets and `TextureTint`.

| Property | Type | Description |
|----------|------|-------------|
| `NormalTexture` | `ITexture?` | Base texture for the idle state |
| `HoverTexture` | `ITexture?` | Hover state texture; falls back to `NormalTexture` |
| `PressedTexture` | `ITexture?` | Pressed state texture; falls back to `NormalTexture` |
| `DisabledTexture` | `ITexture?` | Disabled state texture; falls back to `NormalTexture` |
| `TextureBorder` | `NineSliceBorder` | Texel insets for the nine-slice cut |
| `TextureTint` | `Color` | Tint applied to whichever texture is active |

```csharp
button.NormalTexture  = renderer.LoadTexture("ui/btn_normal.png");
button.HoverTexture   = renderer.LoadTexture("ui/btn_hover.png");
button.PressedTexture = renderer.LoadTexture("ui/btn_pressed.png");
button.TextureBorder  = new NineSliceBorder(8, 8, 8, 8); // left, top, right, bottom
```

You only need to supply the states you want to differentiate. Any state texture that is `null` falls back to `NormalTexture`.

---

## Keyboard focus

Focus is managed automatically by `UICanvas` via the Tab key. Pressing Enter or Space while a button is focused fires `OnClick`.

```csharp
button.TabIndex = 0; // lower = focused earlier
bool hasFocus   = button.IsFocused;
```

---

## Anchoring

```csharp
var btn = new UIButton("Quit", Vector2.Zero, new Vector2(100, 36))
{
	Anchor       = UIAnchor.BottomRight,
	AnchorOffset = new Vector2(-20, -20),
};
```

See [Positioning & Anchoring](positioning.md) for the full anchor reference.

---

## Disabling

```csharp
button.Enabled = false; // renders with DisabledColor, ignores all input
```

---

## Common patterns

### Confirm / cancel dialog buttons

```csharp
var ok     = new UIButton("OK",     new Vector2(160, 260), new Vector2(80, 32));
var cancel = new UIButton("Cancel", new Vector2(260, 260), new Vector2(80, 32));

ok.OnClick     += () => { Confirm(); _canvas.Remove(_dialogPanel); };
cancel.OnClick += () => { _canvas.Remove(_dialogPanel); };

ok.TabIndex     = 0;
cancel.TabIndex = 1;
```

### Icon button (no text)

```csharp
var closeBtn = new UIButton(string.Empty, new Vector2(440, 10), new Vector2(24, 24))
{
	NormalTexture  = renderer.LoadTexture("ui/close_normal.png"),
	HoverTexture   = renderer.LoadTexture("ui/close_hover.png"),
	TextureBorder  = new NineSliceBorder(0, 0, 0, 0),
};
```
