---
title: Animation & Tweens
description: UITween, UITweenSequence, and UIEasing: property animation for UI components
---

# Animation & Tweens

Brine2D's UI animation system lets you smoothly interpolate any `float` property on a UI component. Tweens are driven by `UICanvas` automatically: you just create them, register them, and the canvas handles updates.

---

## UITween

`UITween` animates a single `float` value from `from` to `to` over `duration` seconds using an optional easing function.

### Constructor

```csharp
var tween = new UITween(
	from:     panel.Position.X,
	to:       panel.Position.X + 200f,
	duration: 0.4f,
	setter:   v => panel.Position = panel.Position with { X = v },
	easing:   UIEasing.CubicOut);

_canvas.StartTween(tween);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | `float` | Start value |
| `to` | `float` | End value |
| `duration` | `float` | Seconds; must be `> 0` |
| `setter` | `Action<float>` | Called every frame with the current value |
| `easing` | `Func<float, float>?` | Easing function; `null` = `UIEasing.Linear` |

### Configuration properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Duration` | `float` |: | Set in constructor; read-only after |
| `Delay` | `float` | `0` | Seconds before the tween starts |
| `LoopMode` | `UITweenLoopMode` | `Once` | `Once`, `Loop`, or `PingPong` |
| `IsPaused` | `bool` | `false` | Pause / resume the tween |

### State

| Property | Type | Description |
|----------|------|-------------|
| `IsComplete` | `bool` | `true` when a `Once` tween finishes |
| `Progress` | `float` | Normalised time `[0, 1]` before easing |

### Events

```csharp
tween.OnUpdate   += value => Debug.Log($"Value: {value}");
tween.OnComplete += ()    => panel.Visible = false;
```

### Loop modes

```csharp
tween.LoopMode = UITweenLoopMode.Once;     // play once and stop
tween.LoopMode = UITweenLoopMode.Loop;     // restart from 'from' on completion
tween.LoopMode = UITweenLoopMode.PingPong; // alternate direction each cycle
```

### Manual completion and reset

```csharp
tween.Complete(); // jump to end value immediately, fires OnComplete
tween.Reset();    // return to start value, clear complete flag
```

### Stopping early

```csharp
_canvas.StopTween(tween);
_canvas.StopAllTweens();
```

---

## UITweenSequence

`UITweenSequence` chains multiple tweens so each starts only after the previous one finishes.

### Fluent builder

```csharp
var seq = new UITweenSequence()
	.Then(0f, 1f, 0.3f, v => overlay.Alpha = v, UIEasing.SineOut)   // fade in
	.Then(1f, 0f, 0.5f, v => overlay.Alpha = v, UIEasing.SineIn);   // fade out

seq.OnComplete += () => _canvas.Remove(overlay);
_canvas.StartTween(seq);
```

`.Then` accepts either a pre-built `UITween` or the same parameters as the `UITween` constructor.

### State and control

| Member | Description |
|--------|-------------|
| `IsComplete` | `true` when all tweens have run |
| `IsPaused` | Pause / resume the whole sequence |
| `Current` | The currently active `UITween`, or `null` |
| `CompleteAll()` | Jump all tweens to their end values |
| `Reset()` | Restart from the first tween |
| `OnComplete` | Fires when the last tween finishes |

---

## UIEasing reference

All functions accept normalised time `t ∈ [0, 1]` and return normalised progress. Back, Bounce, and Elastic curves may exceed the `[0, 1]` range (overshoot).

### Linear

| Method | Curve |
|--------|-------|
| `UIEasing.Linear` | Constant rate |

### Quadratic

| Method | Curve |
|--------|-------|
| `UIEasing.QuadIn` | Slow start |
| `UIEasing.QuadOut` | Slow end |
| `UIEasing.QuadInOut` | Slow start and end |

### Cubic

| Method | Curve |
|--------|-------|
| `UIEasing.CubicIn` |: |
| `UIEasing.CubicOut` | *(common choice for UI slide-ins)* |
| `UIEasing.CubicInOut` |: |

### Quartic

`UIEasing.QuartIn`, `QuartOut`, `QuartInOut`

### Sine

`UIEasing.SineIn`, `SineOut`, `SineInOut`

### Exponential

`UIEasing.ExpoIn`, `ExpoOut`, `ExpoInOut`

### Back (overshoot)

`UIEasing.BackIn`, `BackOut`, `BackInOut`: slight overshoot before/after the target value.

### Bounce

`UIEasing.BounceIn`, `BounceOut`, `BounceInOut`: bouncing-ball effect.

### Elastic

`UIEasing.ElasticIn`, `ElasticOut`, `ElasticInOut`: spring-like oscillation.

---

## Reading active tweens

```csharp
IReadOnlyList<UITween>         activeTweens    = _canvas.ActiveTweens;
IReadOnlyList<UITweenSequence> activeSequences = _canvas.ActiveTweenSequences;
```

---

## Common patterns

### Slide a panel in from off-screen

```csharp
float offScreen = -panel.Size.X;
float onScreen  = 0f;

panel.Position = panel.Position with { X = offScreen };
_canvas.Add(panel);

_canvas.StartTween(new UITween(
	from:     offScreen,
	to:       onScreen,
	duration: 0.35f,
	setter:   v => panel.Position = panel.Position with { X = v },
	easing:   UIEasing.CubicOut));
```

### Fade a label in then out

`UIImage` exposes an `Alpha` property directly. For other component types, tween a `Color` component's alpha channel via the `BackgroundColor` setter.

```csharp
// UIImage fade using Alpha property
var img = new UIImage(texture, new Vector2(100, 100), new Vector2(200, 200)) { Alpha = 0f };
_canvas.Add(img);

var seq = new UITweenSequence()
	.Then(0f, 1f, 0.2f, a => img.Alpha = a,  UIEasing.Linear)
	.Then(1f, 1f, 1.5f, _ => { })             // hold for 1.5 s
	.Then(1f, 0f, 0.4f, a => img.Alpha = a,  UIEasing.SineIn);

seq.OnComplete += () => _canvas.Remove(img);
_canvas.StartTween(seq);
```

### Pulsing highlight (loop)

```csharp
var overlay = new UIImage(highlightTexture, new Vector2(0, 0), size) { Alpha = 0.6f };
_canvas.Add(overlay);

var pulse = new UITween(
	from:     0.6f,
	to:       1.0f,
	duration: 0.7f,
	setter:   v => overlay.Alpha = v,
	easing:   UIEasing.SineInOut)
{
	LoopMode = UITweenLoopMode.PingPong,
};
_canvas.StartTween(pulse);
```

### Delayed entrance

```csharp
var tween = new UITween(0f, 1f, 0.4f, v => btn.Alpha = v, UIEasing.QuadOut)
{
	Delay = 0.5f, // wait 0.5 s before starting
};
_canvas.StartTween(tween);
```
