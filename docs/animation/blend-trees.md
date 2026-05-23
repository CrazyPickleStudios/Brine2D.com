---
title: Blend Trees
description: AnimationBlendSelector1D and AnimationBlendSelector2D in Brine2D
---

# Blend Trees

    **Namespace:** `Brine2D.Animation`

Blend trees drive clip selection continuously from runtime parameter values rather than discrete transitions. They are ideal for movement animations (walk/run based on speed), directional facing (eight-way movement), and any situation where a float value should smoothly pick between clips.

Both trees sit on `AnimatorComponent` and are evaluated by `AnimationSystem` **before** the animator is ticked each frame, so a clip change takes effect with no one-frame lag.

!!! info "Priority vs. the state machine"
    When both a blend tree and a state machine are active, `AnimationSystem` evaluates the blend
    tree first, then the state machine. If the state machine fires a transition on the same frame,
    the state machine wins. Set only the tree or machine you want active at any given time, or use
    `IsEnabled` on either to switch between them.

---

## 1D Blend Tree

`AnimationBlendSelector1D` maps a single float value to the nearest registered threshold and plays the corresponding clip.

### Setup

```csharp
var sel = new AnimationBlendSelector1D(animComp.Animator);
animComp.BlendSelector1D = sel;

sel.AddNode(0f,   "idle");
sel.AddNode(1f,   "walk");
sel.AddNode(4f,   "run");
```

`Value` selects the clip whose threshold is nearest. Nodes are kept sorted by threshold.

### Setting the Value

```csharp
// Setting Value evaluates immediately
sel.Value = velocity.Length();
```

### Speed Interpolation

When adjacent nodes carry a speed override, `SpriteAnimator.Speed` is linearly interpolated between them as `Value` moves between their thresholds.

```csharp
sel.AddNode(0f, "walk", speed: 0.5f);
sel.AddNode(4f, "run",  speed: 2.0f);
// At Value = 2.0, Speed â‰ˆ 1.25
```

### Key Properties

| Property | Default | Purpose |
|---|---|---|
| `Value` | `0` | Current blend parameter; triggers evaluation on set |
| `CrossFadeDuration` | `0` | Cross-fade seconds on clip change; `0` = hard cut |
| `RespectNonLoopingClips` | `true` | Yield to non-looping clips started outside the tree |
| `AllowZeroSpeed` | `false` | Allow a speed node value of exactly `0` |
| `IsEnabled` | `true` | When `false`, tree evaluation is skipped |
| `NodeCount` | â€” | Number of registered nodes |
| `ActiveClip` | â€” | Name of the currently selected clip |

### Events

```csharp
sel.OnClipChanged += (prev, next) =>
{
    // prev may be null on the first evaluation
};
```

### Node Management

```csharp
sel.AddNode(6f, "sprint", speed: 3f);
sel.RemoveNode("sprint");
sel.ClearNodes();
```

### Validation

```csharp
var issues = sel.ValidateNodes();
foreach (var msg in issues)
    Logger.LogWarning(msg);
```

---

## 2D Blend Tree

`AnimationBlendSelector2D` maps a 2D float coordinate to the nearest registered node using Euclidean distance (nearest-neighbor / Voronoi). Ideal for eight-way directional movement.

### Setup

```csharp
var sel = new AnimationBlendSelector2D(animComp.Animator);
animComp.BlendSelector2D = sel;

// Eight-way directional movement
sel.AddNode( 0f,  1f, "walk_up");
sel.AddNode( 0f, -1f, "walk_down");
sel.AddNode(-1f,  0f, "walk_left");
sel.AddNode( 1f,  0f, "walk_right");
sel.AddNode( 0.7f,  0.7f, "walk_up_right");
sel.AddNode(-0.7f,  0.7f, "walk_up_left");
sel.AddNode( 0.7f, -0.7f, "walk_down_right");
sel.AddNode(-0.7f, -0.7f, "walk_down_left");
```

### Setting the Value

```csharp
// SetValue evaluates immediately
sel.SetValue(velocity.X, velocity.Y);

// Read back
float x = sel.X;
float y = sel.Y;
```

### Speed Interpolation

When the two nearest nodes both carry a speed override, `SpriteAnimator.Speed` is interpolated between them by proximity.

```csharp
sel.AddNode(0f, 0f, "idle", speed: 0f);
sel.AddNode(1f, 0f, "walk", speed: 1f);
sel.AddNode(4f, 0f, "run",  speed: 2f);
sel.AllowZeroSpeed = true; // allow the idle node's speed = 0
```

### Key Properties

| Property | Default | Purpose |
|---|---|---|
| `X`, `Y` | `0` | Current 2D blend parameter (read-only; set via `SetValue`) |
| `CrossFadeDuration` | `0` | Cross-fade seconds on clip change |
| `RespectNonLoopingClips` | `true` | Yield to non-looping clips started outside the tree |
| `AllowZeroSpeed` | `false` | Allow a speed node value of exactly `0` |
| `IsEnabled` | `true` | When `false`, tree evaluation is skipped |
| `NodeCount` | â€” | Number of registered nodes |
| `ActiveClip` | â€” | Name of the currently selected clip |

### Events

```csharp
sel.OnClipChanged += (prev, next) => { };
```

### Node Management

```csharp
sel.AddNode(2f, 1f, "walk_up_right");
sel.RemoveNode("walk_up_right");         // by clip name
sel.RemoveNode(2f, 1f);                  // by position
sel.ClearNodes();
```

### Validation

```csharp
var issues = sel.ValidateNodes();
foreach (var msg in issues)
    Logger.LogWarning(msg);
```

---

## Blend Trees on Layers

Each `AnimationLayer` also supports a blend tree independently of the base animator:

```csharp
var layer = animComp.AddLayer("legs", priority: 1);
var sel = new AnimationBlendSelector1D(layer.Animator);
layer.BlendSelector1D = sel;

sel.AddNode(0f, "idle_legs");
sel.AddNode(2f, "walk_legs");
sel.AddNode(5f, "run_legs");
```

See [Layers](layers.md) for full layer setup.

---

## Switching Between 1D and 2D

When both `BlendSelector1D` and `BlendSelector2D` are set on the same `AnimatorComponent` or layer, only `BlendSelector1D` is evaluated. Set the unused property to `null` to switch:

```csharp
animComp.BlendSelector1D = null;   // switch to 2D
animComp.BlendSelector2D = sel2D;

animComp.BlendSelector2D = null;   // switch to 1D
animComp.BlendSelector1D = sel1D;
```

---

## Interaction with the State Machine

Blend trees and the state machine are not mutually exclusive. A common pattern:

- Use the **blend tree** to drive directional walk/run clips.
- Use the **state machine** to handle one-shot overrides (attack, hurt, jump) with on-complete transitions back to the default state.

```csharp
// Blend tree drives walk/run direction
animComp.BlendSelector2D = dirSel;

// State machine handles overrides
sm.AddAnyTriggerTransition("attack", p, "attackPressed", canInterrupt: false);
sm.AddOnCompleteTransition("attack", "idle");
sm.SetDefaultState("idle");
```

When the state machine fires "attack", the animator stops being driven by the blend tree for that clip's duration (because `RespectNonLoopingClips` is `true` by default). When "attack" completes and the state machine returns to "idle", the blend tree resumes control.
