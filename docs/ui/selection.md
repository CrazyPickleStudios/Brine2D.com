---
title: Checkbox & Radio Button
description: UICheckbox, UIRadioButton, and UIRadioButtonGroup: boolean and exclusive selection controls
---

# Checkbox & Radio Button

- **`UICheckbox`**: independent boolean toggle with a label
- **`UIRadioButton`** + **`UIRadioButtonGroup`**: mutually exclusive selection within a group

Both implement `IUIComponent` and `IAnchoredUIComponent`.

---

## UICheckbox

### Constructor

```csharp
var cb = new UICheckbox("Enable shadows", new Vector2(20, 40));
_canvas.Add(cb);
```

`Size` is calculated automatically from the box size and label text.

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Label` | `string` | `""` | Text displayed beside the box |
| `Font` | `IFont?` | `null` | Custom font |
| `BoxSize` | `float` | `18` | Width and height of the checkbox square in pixels |
| `IsChecked` | `bool` | `false` | Current state |
| `LabelSpacing` | `float` | `8` | Gap between box and label in pixels |

### Colors

| Property | Type | Default |
|----------|------|---------|
| `UncheckedColor` | `Color` | `(60,60,60)` |
| `CheckedColor` | `Color` | `(100,150,255)` |
| `HoverColor` | `Color` | `(80,80,80)` |
| `CheckmarkColor` | `Color` | White |
| `BorderColor` | `Color` | `(150,150,150)` |
| `LabelColor` | `Color` | White |
| `FocusColor` | `Color` | `(120,180,255)` |

### Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnCheckedChanged` | `Action<bool>` | `IsChecked` toggles |
| `OnHoverEnter` | `Action` | Mouse enters bounds |
| `OnHoverExit` | `Action` | Mouse leaves bounds |
| `OnFocusGained` | `Action` | Receives keyboard focus |
| `OnFocusLost` | `Action` | Loses keyboard focus |

Space or Enter toggles the checkbox when it has keyboard focus.

### Example: settings panel

```csharp
var vSync = new UICheckbox("VSync", new Vector2(20, 60))
{
	IsChecked  = _settings.VSync,
	CheckedColor = new Color(60, 180, 100),
	TabIndex   = 0,
};
vSync.OnCheckedChanged += enabled =>
{
	_settings.VSync = enabled;
	_settings.Save();
};
_canvas.Add(vSync);
```

---

## UIRadioButton & UIRadioButtonGroup

Radio buttons must belong to a `UIRadioButtonGroup`. Selecting one button in the group automatically deselects all others.

### Setup

```csharp
var group = new UIRadioButtonGroup();

var optA = new UIRadioButton("Windowed",    group, new Vector2(20, 80));
var optB = new UIRadioButton("Borderless",  group, new Vector2(20, 106));
var optC = new UIRadioButton("Fullscreen",  group, new Vector2(20, 132));

_canvas.Add(optA);
_canvas.Add(optB);
_canvas.Add(optC);
```

### UIRadioButton properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Label` | `string` | `""` | Text beside the button |
| `Group` | `UIRadioButtonGroup` | required | The group this button belongs to |
| `IsChecked` | `bool` | `false` | Read-only outside the class; set via `group` or by clicking |
| `ButtonSize` | `float` | `20` | Diameter of the radio circle in pixels |
| `LabelSpacing` | `float` | `8` | Gap between circle and label in pixels |

### UIRadioButton colors

| Property | Type | Default |
|----------|------|---------|
| `UncheckedColor` | `Color` | `(60,60,60)` |
| `CheckedColor` | `Color` | `(100,150,255)` |
| `HoverColor` | `Color` | `(80,80,80)` |
| `DotColor` | `Color` | White |
| `BorderColor` | `Color` | `(150,150,150)` |
| `LabelColor` | `Color` | White |
| `FocusColor` | `Color` | `(120,180,255)` |

### UIRadioButton events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnSelected` | `Action` | This button becomes selected |
| `OnHoverEnter` | `Action` | Mouse enters bounds |
| `OnHoverExit` | `Action` | Mouse leaves bounds |
| `OnFocusGained` | `Action` | Receives keyboard focus |
| `OnFocusLost` | `Action` | Loses keyboard focus |

### UIRadioButtonGroup API

| Member | Description |
|--------|-------------|
| `SelectedButton` | Currently selected `UIRadioButton`, or `null` |
| `SelectedIndex` | Zero-based index of the selected button, or `-1` |
| `GetButtons()` | All buttons registered to this group |
| `OnSelectionChanged` | `event Action<UIRadioButton?>`: fires after each selection change |

### Example: display mode selector

```csharp
var group = new UIRadioButtonGroup();

var modes = new[] { "Windowed", "Borderless", "Fullscreen" };
for (int i = 0; i < modes.Length; i++)
{
	var btn = new UIRadioButton(modes[i], group, new Vector2(20, 80 + i * 26))
	{
		CheckedColor = new Color(60, 180, 100),
		TabIndex     = i,
	};
	_canvas.Add(btn);
}

// Pre-select current mode
group.GetButtons()[_settings.DisplayModeIndex].IsChecked = true;

group.OnSelectionChanged += selected =>
{
	_settings.DisplayModeIndex = group.SelectedIndex;
	ApplyDisplayMode(group.SelectedIndex);
};
```

!!! note
	`IsChecked` has an `internal` setter: you cannot set it directly from outside the assembly. Pre-select a button by clicking it via code: the group's `SelectButton` is also internal, so the pattern above (`IsChecked = true` from within an initial setup) works because it is called before the first frame. Alternatively, add the first `OnSelectionChanged` listener before adding any buttons, then click the desired button via the canvas's input routing if you need a proper selection event.
