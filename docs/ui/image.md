---
title: UIImage
description: Texture display with tint, alpha, rotation, source rect, and sprite animation
---

# UIImage

`UIImage` renders a texture inside a specified screen-space rectangle. It supports tint/alpha, rotation, source-rect cropping, aspect-ratio preservation, and optional `SpriteAnimator` integration for frame animation.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructors

```csharp
// Explicit size
var img = new UIImage(texture, new Vector2(100, 50), new Vector2(128, 128));

// Size from texture dimensions
var img = new UIImage(texture, new Vector2(100, 50));
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `texture` | `ITexture?` | Texture to render; `null` = invisible |
| `position` | `Vector2` | Screen-space top-left in pixels |
| `size` | `Vector2` | Destination rectangle size |

---

## Core properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Texture` | `ITexture?` | `null` | Texture to display |
| `SourceRect` | `Rectangle?` | `null` | Sub-rectangle of the texture; `null` = entire texture |
| `MaintainAspectRatio` | `bool` | `true` | Letterbox inside the `Size` rectangle |
| `Tint` | `Color` | White | Modulation color multiplied with the texture |
| `Alpha` | `float` | `1.0` | Opacity: clamped to `[0, 1]` |
| `Rotation` | `float` | `0` | Rotation in radians around the image centre |

---

## Tinting and transparency

```csharp
img.Tint  = new Color(255, 100, 100); // red-shifted
img.Alpha = 0.5f;                     // 50% transparent
```

The rendered pixel color is `Tint × texture.color` with alpha `Tint.A × Alpha`.

---

## Source rect (sprite sheets)

```csharp
img.SourceRect = new Rectangle(0, 0, 32, 32); // first 32×32 tile
```

When an `Animator` is attached its current frame's source rect automatically overrides `SourceRect` each frame.

---

## Rotation

```csharp
img.Rotation = MathF.PI / 4f; // 45 degrees
```

Rotation is applied around the center of the destination rectangle.

---

## Aspect ratio

When `MaintainAspectRatio = true` (default) the image letterboxes itself to fit within `Size` while preserving the texture's proportions. Set it to `false` to stretch the texture exactly to `Size`:

```csharp
img.MaintainAspectRatio = false;
```

---

## Sprite animation

Attach a `SpriteAnimator` to drive frame-by-frame animation:

```csharp
var sheet = renderer.LoadTexture("ui/icon_spin.png");
var animator = new SpriteAnimator();
animator.AddAnimation("spin", new SpriteAnimation(
	frames: GenerateFrames(sheet, frameWidth: 32, frameHeight: 32, count: 8),
	fps: 12f,
	loop: true));
animator.Play("spin");

var icon = new UIImage(sheet, new Vector2(10, 10), new Vector2(32, 32))
{
	Animator = animator,
};
_canvas.Add(icon);
```

`UIImage.Update(deltaTime)` advances the animator automatically each frame.

---

## Click event

```csharp
img.OnClick += () => OpenFullscreen();
```

---

## Anchoring

```csharp
var logo = new UIImage(logoTexture, Vector2.Zero)
{
	Anchor       = UIAnchor.TopCenter,
	AnchorOffset = new Vector2(-64, 20),
};
```

See [Positioning & Anchoring](positioning.md).

---

## Example: health icon bar

```csharp
var heartTexture = renderer.LoadTexture("ui/heart.png");

for (int i = 0; i < maxHearts; i++)
{
	var heart = new UIImage(heartTexture, new Vector2(10 + i * 28, 10), new Vector2(24, 24))
	{
		Alpha = i < currentHearts ? 1f : 0.25f,
	};
	_canvas.Add(heart);
	_heartImages.Add(heart);
}
```
