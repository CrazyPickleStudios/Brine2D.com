---
title: Clip Events
description: Time-offset animation callbacks with ClipEvent in Brine2D
---

# Clip Events

    **Namespace:** `Brine2D.Animation`

Clip events are named callbacks attached to an `AnimationClip` at a specific time offset. `SpriteAnimator` fires them automatically when playback crosses the event's time. They are the correct way to trigger sounds, particle bursts, hitbox toggles, or any side-effect that is tied to a specific moment in an animation.

---

## Adding Events

### By time (seconds from clip start)

```csharp
clip.AddEvent("footstep", time: 0.1f, callback: args =>
{
    audioService.Play("footstep");
});

clip.AddEvent("hitbox_on", time: 0.05f, callback: args =>
{
    hitboxActive = true;
});

clip.AddEvent("hitbox_off", time: 0.2f, callback: args =>
{
    hitboxActive = false;
});
```

Events are kept sorted by time. `AddEvent` returns `this` for chaining.

### By frame index (auto-updates when frame durations change)

```csharp
// Fires at the start of frame 2 (zero-based)
clip.AddEventAtFrame("spawn_dust", frameIndex: 2, callback: args =>
{
    particleSystem.Burst(position);
});
```

`AddEventAtFrame` re-resolves the underlying time automatically whenever any frame's `Duration` changes while it belongs to this clip. Use this instead of `AddEvent` when frame durations may be modified at runtime or when you're working with a clip loaded from Aseprite.

### ClipEventArgs

The callback receives a `ClipEventArgs` record:

```csharp
clip.AddEvent("hit", 0.08f, args =>
{
    Logger.LogDebug(
        "Event '{Name}' fired on clip '{Clip}' at t={Time:F3} (norm={Norm:F2})",
        args.EventName, args.ClipName, args.Time, args.NormalizedTime);
});
```

| Property | Type | Description |
|---|---|---|
| `EventName` | `string` | The name passed to `AddEvent` |
| `ClipName` | `string` | The `AnimationClip.Name` that owns the event |
| `Time` | `float` | The registered time offset (seconds) |
| `NormalizedTime` | `float` | `[0, 1]` playback position when the event fired |

---

## PingPong Events

By default, events only fire on the forward pass of a `PingPong` or `PingPongOnce` clip. Set `fireBothDirections: true` to also fire on the backward sweep:

```csharp
clip.AddEvent("spark", 0.15f, args => SpawnSpark(), fireBothDirections: true);
```

---

## Removing Events

```csharp
// Remove by name (first match)
clip.RemoveEvent("footstep");
```

---

## Guaranteed Delivery

`SpriteAnimator` fires every event whose time falls within the window `[prevTime, newTime]` advanced in a single `Update` tick, including events that would have been skipped due to a large delta or frame-skip. Events are never double-fired within a single update, and they are never missed due to frame-skipping â€” the event window covers the full elapsed time, not just the boundary of the current frame.

!!! warning "No delivery during time-clamped frames"
    When `GameTime.IsTimeClamped` is `true` (unusually large delta detected by the game loop),
    `AnimationSystem` ticks with zero delta. No playback advances and no events fire that tick.
    This is intentional â€” see `AnimationSystem` remarks.

---

## Events from Aseprite

When clips are loaded via `AsepriteClipLoader`, per-frame `data` fields (set via Aseprite **Frame Properties**) are stored in `SpriteFrame.UserData` as strings. You can read these in `OnFrameChanged` or an event callback to react to them:

```csharp
animator.OnFrameChanged += frame =>
{
    if (frame.UserData is string tag && tag == "footstep")
        audioService.Play("footstep");
};
```

For guaranteed timing accuracy, prefer `AddEventAtFrame` over `OnFrameChanged` when the exact moment within the frame matters â€” `OnFrameChanged` fires at the first tick the new frame becomes active, while a clip event fires at the precise accumulated time offset.

---

## Full Example

```csharp
var attack = new AnimationClip("attack") { PlaybackMode = PlaybackMode.OnceHoldLast };
attack
    .AddFrame(new SpriteFrame(new Rectangle(0,   0, 48, 48), 0.05f)) // frame 0: wind-up
    .AddFrame(new SpriteFrame(new Rectangle(48,  0, 48, 48), 0.03f)) // frame 1: strike
    .AddFrame(new SpriteFrame(new Rectangle(96,  0, 48, 48), 0.12f)) // frame 2: recovery
    .AddEventAtFrame("swing_sound", frameIndex: 0, callback: _ => audioService.Play("sword_swing"))
    .AddEventAtFrame("hitbox_on",   frameIndex: 1, callback: _ => hitboxActive = true)
    .AddEventAtFrame("hitbox_off",  frameIndex: 2, callback: _ => hitboxActive = false);
```
