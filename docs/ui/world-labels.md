---
title: World Labels
description: UIWorldLabel and IUIWorldComponent: project world-space positions to screen-space UI
---

# World Labels

`UIWorldLabel` renders text that is anchored to a 3D world position. Each frame the canvas projects the `WorldPosition` through `UICanvas.WorldCamera` to compute the screen position. Typical uses: floating name tags, damage numbers, waypoint markers, health bars above enemies.

---

## Setup

### Assign a camera

```csharp
_canvas.WorldCamera = _gameCamera; // ICamera
```

The camera must be set for projection to work. When `WorldCamera` is `null`, world components are rendered at their last assigned `Position` (screen-space fallback).

### Add a world label

```csharp
var label = new UIWorldLabel
{
	WorldPosition = new Vector3(10f, 0f, 5f),
	Text          = "Enemy",
	TextColor     = Color.Red,
};
_canvas.AddWorldComponent(label);

// Remove later
_canvas.RemoveWorldComponent(label);
```

World components do **not** go through `UICanvas.Add`. Use `AddWorldComponent` and `RemoveWorldComponent`.

---

## Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `WorldPosition` | `Vector3` | `(0,0,0)` | 3D anchor point in world space |
| `ScreenOffset` | `Vector2` | `(0,0)` | Pixel offset added after projection (e.g. centre label above entity) |
| `CullWhenOffScreen` | `bool` | `true` | Skip rendering when the projected position is outside the viewport |
| `Text` | `string` | `""` | Label text |
| `TextColor` | `Color` | White | Text color |
| `Font` | `IFont?` | `null` | Custom font |
| `MaxWidth` | `float` | `0` | Wrap width; `0` = no wrap |

---

## Background and border

When `BackgroundPadding > 0` a filled rectangle is drawn behind the text:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `BackgroundPadding` | `float` | `0` | Interior padding; `0` = no background |
| `BackgroundColor` | `Color` | `(0,0,0,160)` | Background fill |
| `BorderColor` | `Color?` | `null` | Optional border color; `null` = no border |
| `BorderThickness` | `float` | `1` | Border width in pixels |

---

## Centering the label

The projection gives the world point's screen coordinate. Use `ScreenOffset` to nudge the label relative to that point:

```csharp
// Centre the label horizontally 40 px above the entity
label.ScreenOffset = new Vector2(-label.Size.X / 2f, -40f);
```

`Size` is measured on the first `Render` call. For the initial frame you can estimate it or use a fixed offset that works for your font size.

---

## Updating labels each frame

```csharp
// In your game loop / entity update:
_nameLabel.WorldPosition = _enemy.Position3D;
_nameLabel.Text          = $"{_enemy.Name} ({_enemy.Health} HP)";
```

---

## Example: floating name tags

```csharp
var nameLabel = new UIWorldLabel
{
	Text             = player.Name,
	TextColor        = Color.White,
	BackgroundPadding = 4f,
	BackgroundColor   = new Color(0, 0, 0, 140),
	CullWhenOffScreen = true,
};
_canvas.AddWorldComponent(nameLabel);
_canvas.WorldCamera = _mainCamera;

// Update each frame
nameLabel.WorldPosition = player.WorldPosition + Vector3.UnitY * 2.2f;
nameLabel.ScreenOffset  = new Vector2(-40f, 0f); // rough centering
```

---

## Example: damage numbers

```csharp
void ShowDamage(Vector3 worldPos, int damage)
{
	var dmg = new UIWorldLabel
	{
		WorldPosition    = worldPos,
		ScreenOffset     = new Vector2(-12f, -30f),
		Text             = $"-{damage}",
		TextColor        = new Color(255, 80, 80),
		CullWhenOffScreen = true,
	};
	_canvas.AddWorldComponent(dmg);

	// Tween upward and fade out then remove
	float y = worldPos.Y;
	var tween = new UITween(0f, 1f, 0.8f, t =>
	{
		dmg.WorldPosition  = worldPos + Vector3.UnitY * t * 1.5f;
		dmg.TextColor      = new Color(255, 80, 80, (byte)(255 * (1f - t)));
	});
	tween.OnComplete += () => _canvas.RemoveWorldComponent(dmg);
	_canvas.StartTween(tween);
}
```

---

## IUIWorldComponent

`UIWorldLabel` implements `IUIWorldComponent`. If you need a custom world-space component, implement this interface:

```csharp
public interface IUIWorldComponent : IUIComponent
{
	Vector3 WorldPosition { get; set; }
	Vector2 ScreenOffset  { get; set; }
	bool    CullWhenOffScreen { get; set; }
}
```

Register custom world components the same way: `_canvas.AddWorldComponent(myComponent)`.
