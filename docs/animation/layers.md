---
title: Animation Layers
description: Independent parallel animation tracks with AnimationLayer in Brine2D
---

# Animation Layers

**Namespace:** `Brine2D.Animation`

Animation layers let you run multiple independent animation tracks on the same entity simultaneously. Each layer has its own `SpriteAnimator`, `AnimationStateMachine`, `AnimationParameters`, and optional blend tree. The base animator is always priority `0`; layers are applied in ascending priority order on top of it.

Typical uses:

- Upper-body attack animation on top of a lower-body walk cycle
- Separate facial expression track on a character
- Hit-flash or tint effect layer with an `Additive` blend mode
- Driving a different texture atlas per layer

---

## Adding a Layer

```csharp
var layer = animComp.AddLayer("upper_body", priority: 1);
```

`AddLayer` throws `ArgumentException` if a layer with the same name already exists, and `ArgumentOutOfRangeException` if `priority < 1`.

### Adding clips and playing

```csharp
var slash = new AnimationClip("slash") { PlaybackMode = PlaybackMode.OnceHoldLast };
slash.AddFrame(new SpriteFrame(new Rectangle(0, 64, 48, 48)));
slash.AddFrame(new SpriteFrame(new Rectangle(48, 64, 48, 48)));

layer.Animator.AddAnimation(slash);
layer.Animator.Play("slash");
```

---

## AnimationLayer Properties

| Property | Type | Default | Purpose |
|---|---|---|---|
| `Name` | `string` | — | Human-readable identifier |
| `Priority` | `int` | `1` | Evaluation order; higher values win. Must be ≥ 1 |
| `Weight` | `float` | `1.0` | Blend weight `[0, 1]`; `1.0` = full effect, `0.0` = no effect |
| `Mask` | `AnimationLayerMask` | `Default` | Which `SpriteComponent` properties this layer writes |
| `BlendMode` | `AnimationLayerBlendMode` | `Override` | How values are combined with lower-priority results |
| `Animator` | `SpriteAnimator` | — | The layer's animator |
| `StateMachine` | `AnimationStateMachine` | — | The layer's state machine |
| `Parameters` | `AnimationParameters` | — | Named parameter store for this layer's transitions |
| `BlendSelector1D` | `AnimationBlendSelector1D?` | `null` | Optional 1D blend tree for this layer |
| `BlendSelector2D` | `AnimationBlendSelector2D?` | `null` | Optional 2D blend tree for this layer |

---

## AnimationLayerMask

`AnimationLayerMask` is a flags enum that controls exactly which `SpriteComponent` fields the layer is allowed to overwrite each frame.

| Flag | Description |
|---|---|
| `SourceRect` | The sprite source rectangle |
| `Origin` | The sprite pivot point |
| `FlipX` | Horizontal flip |
| `FlipY` | Vertical flip |
| `Tint` | Sprite tint colour |
| `Texture` | The sprite texture reference |
| `Default` | `SourceRect \| Origin` — the default for new layers |
| `All` | All of the above |

```csharp
// Drive a full swap including texture (e.g. equipment overlay)
layer.Mask = AnimationLayerMask.All;

// Tint-only flash layer
layer.Mask = AnimationLayerMask.Tint;

// Combine flags explicitly
layer.Mask = AnimationLayerMask.SourceRect | AnimationLayerMask.Tint;
```

!!! note "Texture flag"
    `Texture` is excluded from `Default` to avoid accidentally clobbering the base sprite texture.
    Add it explicitly only when the layer is intended to drive a different atlas.

---

## AnimationLayerBlendMode

| Value | Behaviour |
|---|---|
| `Override` | The layer's values overwrite the existing `SpriteComponent` values, lerped by `Weight`. This is the default |
| `Additive` | Tint RGB channels are **added** to the existing tint. Alpha is lerped by `Weight`. Non-tint properties fall back to `Override` behaviour |

```csharp
// Hit-flash: briefly add a bright colour on top of the base tint
var flash = animComp.AddLayer("hit_flash", priority: 10);
flash.Mask      = AnimationLayerMask.Tint;
flash.BlendMode = AnimationLayerBlendMode.Additive;
flash.Weight    = 0f; // start invisible

// Animate the weight from code to pulse the flash
flash.Weight = MathF.Max(0f, flash.Weight - deltaTime * 4f);
```

---

## Priority and Ordering

The base animator is always priority `0`. Layers with higher priority are applied last and win. `AnimatorComponent` keeps the layer list sorted automatically whenever a layer's `Priority` changes.

```csharp
var legs  = animComp.AddLayer("legs",  priority: 1);
var torso = animComp.AddLayer("torso", priority: 2);
var face  = animComp.AddLayer("face",  priority: 3);

// Change priority at runtime — list re-sorts automatically
torso.Priority = 5;
```

---

## Removing a Layer

```csharp
bool removed = animComp.RemoveLayer("upper_body"); // disposes the layer
```

---

## Layer State Machines and Parameters

Each layer's `StateMachine` and `Parameters` work exactly like the base animator's — see [State Machine](state-machine.md) for the full API. The layer state machine is evaluated independently each frame by `AnimationSystem`.

```csharp
var layer = animComp.AddLayer("face", priority: 2);
var p  = layer.Parameters;
var sm = layer.StateMachine;

sm.SetDefaultState("face_neutral");
sm.AddAnyTriggerTransition("face_happy", p, "playerScored", canInterrupt: true);
sm.AddOnCompleteTransition("face_happy", "face_neutral");

// Each frame:
if (scored) p.SetTrigger("playerScored");
```

---

## Blend Trees on Layers

Layers support both 1D and 2D blend trees. `BlendSelector1D` takes priority when both are set.

```csharp
var layer = animComp.AddLayer("legs", priority: 1);
var sel = new AnimationBlendSelector1D(layer.Animator);
layer.BlendSelector1D = sel;

sel.AddNode(0f, "idle_legs");
sel.AddNode(2f, "walk_legs");
sel.AddNode(5f, "run_legs");

// Update every frame
sel.Value = velocity.Length();
```

---

## Full Example: Upper/Lower Body Split

```csharp
// Base animator: lower body (walk/run driven by blend tree)
var baseSel = new AnimationBlendSelector1D(animComp.Animator);
animComp.BlendSelector1D = baseSel;
baseSel.AddNode(0f, "idle");
baseSel.AddNode(2f, "walk");
baseSel.AddNode(5f, "run");

// Layer: upper body (attacks as one-shots)
var upper = animComp.AddLayer("upper_body", priority: 1);
upper.Mask = AnimationLayerMask.SourceRect | AnimationLayerMask.Origin;

upper.Animator.AddAnimation(attackClip);

var p  = upper.Parameters;
var sm = upper.StateMachine;
sm.AddAnyTriggerTransition("attack_upper", p, "attackPressed", canInterrupt: false);
sm.AddOnCompleteTransition("attack_upper", "idle_upper");
sm.SetDefaultState("idle_upper");

// Each frame
baseSel.Value = speed;
if (attackInput) p.SetTrigger("attackPressed");
```
