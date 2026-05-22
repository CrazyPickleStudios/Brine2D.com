---
title: Clips & Frames
description: Building AnimationClips and SpriteFrames manually in Brine2D
---

# Clips & Frames

!!! abstract "In this article"
    How to build `AnimationClip`s and `SpriteFrame`s manually: frame properties, named hit boxes,
    all six `PlaybackMode` values, and fluent clip construction patterns.

    **Namespace:** `Brine2D.Animation`

An `AnimationClip` is an ordered sequence of `SpriteFrame`s that a `SpriteAnimator` steps through over time. Both types are plain C# objects — no ECS required to construct them.

## SpriteFrame

A `SpriteFrame` describes one displayable moment of an animation.

```csharp
var frame = new SpriteFrame(new Rectangle(0, 0, 32, 32));         // default duration 0.1 s
var frame = new SpriteFrame(new Rectangle(0, 0, 32, 32), 0.08f); // explicit duration
```

### Properties

| Property | Type | Default | Purpose |
|---|---|---|---|
| `SourceRect` | `Rectangle` | — | Pixel region in the sprite sheet |
| `Duration` | `float` | `0.1` | Seconds to display this frame (min 0.001) |
| `Origin` | `Vector2` | `(0.5, 0.5)` | Normalised pivot point written to `SpriteComponent.Origin` |
| `DrawOffset` | `Vector2` | `(0, 0)` | Canvas-space pixel offset; used by Aseprite trim to correct trimmed sprite positions |
| `Tint` | `Color?` | `null` | Per-frame tint override (requires `AnimationLayerMask.Tint`) |
| `FlipX` | `bool?` | `null` | Per-frame horizontal flip (requires `AnimationLayerMask.FlipX`) |
| `FlipY` | `bool?` | `null` | Per-frame vertical flip (requires `AnimationLayerMask.FlipY`) |
| `Texture` | `ITexture?` | `null` | Per-frame texture override (takes priority over clip-level `Texture`) |
| `TexturePath` | `string?` | `null` | Per-frame texture path override |
| `HitBox` | `Rectangle?` | `null` | Primary hitbox shorthand (maps to the `"hitbox"` named box) |
| `UserData` | `object?` | `null` | Arbitrary payload; not consumed by the animation system |

### Named Hit Boxes

Frames support multiple named hit boxes for attack, hurt, detection zones, etc.

```csharp
frame.SetHitBox("hurtbox", new Rectangle(4, 2, 24, 28));
frame.SetHitBox("head",    new Rectangle(8, 0, 16, 10));

Rectangle? hurtbox = frame.TryGetHitBox("hurtbox"); // null if absent
Rectangle  head    = frame.GetHitBox("head");        // throws if absent
frame.RemoveHitBox("head");
```

`SpriteFrame.HitBox` is a shorthand for the box stored under `AsepriteClipLoader.HitBoxSliceName` (`"hitbox"` by default). All named boxes from Aseprite slice data are loaded automatically — see [Aseprite Integration](aseprite.md).

### Frame Lifecycle Events

```csharp
frame.OnEnter += () => { /* frame became active */ };
frame.OnExit  += () => { /* frame was replaced  */ };
```

---

## AnimationClip

An `AnimationClip` holds the frames plus metadata controlling how they play.

```csharp
var clip = new AnimationClip("walk");
```

### Core Properties

| Property | Type | Default | Purpose |
|---|---|---|---|
| `Name` | `string` | — | Identifies the clip; used as state name in the state machine |
| `PlaybackMode` | `PlaybackMode` | `Loop` | How the clip loops — see below |
| `Loop` | `bool` | `true` | Shorthand: `false` maps current mode to its non-looping equivalent |
| `RepeatCount` | `int` | `0` | Loop/PingPong only: number of passes before `OnAnimationComplete`. `0` = infinite |
| `TotalDuration` | `float` | computed | Sum of all frame durations; cached and auto-invalidated |
| `Frames` | `IReadOnlyList<SpriteFrame>` | — | Read-only view; mutate via the methods below |
| `Events` | `IReadOnlyList<ClipEvent>` | — | Read-only view of time-offset callbacks |

### Optional Clip-Level Overrides

| Property | Type | Purpose |
|---|---|---|
| `Texture` | `ITexture?` | Applied to `SpriteComponent.Texture` every frame (per-frame overrides win) |
| `TexturePath` | `string?` | Applied to `SpriteComponent.TexturePath` every frame |
| `ClipTint` | `Color?` | Applied to `SpriteComponent.Tint` every frame (per-frame overrides win) |
| `UserData` | `object?` | Arbitrary payload; not consumed by the animation system |

### Clip Lifecycle Events

```csharp
clip.OnEnter  += ()        => { /* clip became active  */ };
clip.OnExit   += ()        => { /* clip was replaced   */ };
clip.OnUpdate += (elapsed) => { /* fires every tick while active */ };
```

### Adding and Removing Frames

All mutation methods return `this` for fluent chaining:

```csharp
var clip = new AnimationClip("run")
    .AddFrame(new SpriteFrame(new Rectangle(0,   0, 32, 32), 0.08f))
    .AddFrame(new SpriteFrame(new Rectangle(32,  0, 32, 32), 0.08f))
    .AddFrame(new SpriteFrame(new Rectangle(64,  0, 32, 32), 0.08f))
    .AddFrame(new SpriteFrame(new Rectangle(96,  0, 32, 32), 0.08f));
```

| Method | Purpose |
|---|---|
| `AddFrame(frame)` | Appends a frame |
| `InsertFrame(index, frame)` | Inserts a frame at the given index |
| `RemoveFrame(frame)` | Removes a specific frame instance |
| `ClearFrames()` | Removes all frames |

!!! tip "Shared Frames"
    The same `SpriteFrame` instance can belong to multiple clips. The frame's `Duration` setter
    automatically invalidates the `TotalDuration` cache of every owning clip via weak references.

---

## PlaybackMode

`PlaybackMode` controls what happens when a clip reaches the end of its frames.

| Value | Behaviour |
|---|---|
| `Loop` | Loops indefinitely; jumps back to frame 0 after the last frame |
| `PingPong` | Loops forward then backward indefinitely |
| `OnceHoldLast` | Plays once, freezes on the last frame (or first when `Reversed`) |
| `OnceHoldFirst` | Plays once, freezes on the first frame (or last when `Reversed`) |
| `OnceStop` | Plays once, then clears `CurrentFrame` (`null`); useful for VFX that should disappear |
| `PingPongOnce` | One forward + one backward pass, then stops on the first frame of the final pass |

```csharp
var jumpClip = new AnimationClip("jump")
{
    PlaybackMode = PlaybackMode.OnceHoldLast
};

var deathClip = new AnimationClip("death")
{
    PlaybackMode = PlaybackMode.OnceStop
};

var breatheClip = new AnimationClip("breathe")
{
    PlaybackMode = PlaybackMode.PingPong
};
```

`RepeatCount` on `Loop` and `PingPong` clips makes them fire `OnAnimationComplete` after N full passes instead of looping forever.

---

## Building Clips Manually

### Uniform grid (same-size frames in a row)

```csharp
const int fw = 32, fh = 32;

var walk = new AnimationClip("walk") { PlaybackMode = PlaybackMode.Loop };
for (int i = 0; i < 8; i++)
    walk.AddFrame(new SpriteFrame(new Rectangle(i * fw, 0, fw, fh), 0.1f));
```

### Variable frame durations

```csharp
var attack = new AnimationClip("attack") { PlaybackMode = PlaybackMode.OnceHoldLast };
attack.AddFrame(new SpriteFrame(new Rectangle(0,  0, 48, 48), 0.05f)); // wind-up
attack.AddFrame(new SpriteFrame(new Rectangle(48, 0, 48, 48), 0.03f)); // strike
attack.AddFrame(new SpriteFrame(new Rectangle(96, 0, 48, 48), 0.12f)); // recovery
```

### Multi-row sprite sheet

```csharp
const int fw = 32, fh = 32, cols = 8;

var run = new AnimationClip("run") { PlaybackMode = PlaybackMode.Loop };
int startFrame = 16; // frame 16 in the sheet
for (int i = startFrame; i < startFrame + 8; i++)
{
    int col = i % cols;
    int row = i / cols;
    run.AddFrame(new SpriteFrame(new Rectangle(col * fw, row * fh, fw, fh), 0.07f));
}
```

---

## Registering and Playing Clips

Once built, register clips on a `SpriteAnimator` (directly or via `AnimatorComponent`):

```csharp
// Direct SpriteAnimator usage
var animator = new SpriteAnimator();
animator.AddAnimation(walk);
animator.AddAnimation(run);
animator.Play("walk");

// Via AnimatorComponent (preferred in ECS)
var comp = entity.GetComponent<AnimatorComponent>()!;
comp.Animator.AddAnimation(walk);
comp.Animator.AddAnimation(run);
comp.Animator.Play("walk");
```

See [Animator Component](animator-component.md) for the full playback API and ECS setup.
