---
title: Aseprite Integration
description: Loading AnimationClips directly from Aseprite JSON exports in Brine2D
---

# Aseprite Integration

!!! abstract "In this article"
    Loading `AnimationClip`s from Aseprite JSON exports: tag directions → `PlaybackMode`, slice data
    → hit boxes, trim offsets → `DrawOffset`, `ConfigureAnimator`, `RepeatCount`, and per-tag/per-frame
    `UserData` fields.

    **Namespace:** `Brine2D.Animation`

`AsepriteClipLoader` loads `AnimationClip`s directly from Aseprite's JSON sprite-sheet export. Each frame tag in the Aseprite file becomes one named `AnimationClip`. Frame durations, hitbox slices, trim offsets, tag directions, repeat counts, and user data fields are all mapped automatically.

## Exporting from Aseprite

In Aseprite: **File → Export Sprite Sheet**

- **Output:** check *JSON Data*
- **Data format:** `JSON Array` or `JSON Hash` — both are supported
- **Layers:** optional; only the final composite matters for the loader
- **Meta:** enable *Frame Tags*, *Slices* (for hitboxes), and *Layers* as needed

The loader reads:
- `meta.frameTags` → one `AnimationClip` per tag
- `meta.slices` → hit boxes per frame
- Per-frame `duration` (ms) → `SpriteFrame.Duration`
- Per-frame `spriteSourceSize` / `sourceSize` → `SpriteFrame.DrawOffset` (trim correction)
- Per-frame `data` field → `SpriteFrame.UserData`
- Per-tag `repeat` field → `AnimationClip.RepeatCount`
- Per-tag `data` field → `AnimationClip.UserData`

---

## Basic Usage

```csharp
var loader = new AsepriteClipLoader();

// Load JSON from a file path
IReadOnlyList<AnimationClip> clips = await loader.LoadAsync("assets/sprites/hero.json");

// Or from a stream
IReadOnlyList<AnimationClip> clips = await loader.LoadAsync(stream);

// Register all clips on the animator
foreach (var clip in clips)
    animator.AddAnimation(clip);
```

### No Frame Tags

When the exported JSON has no `frameTags` (or an empty array), a single clip is created from all frames. Name it by passing `defaultClipName`:

```csharp
var clips = await loader.LoadAsync("assets/sprites/coin.json", defaultClipName: "spin");
```

---

## Tag Directions and PlaybackMode

Aseprite tag directions map to `PlaybackMode` as follows:

| Aseprite direction | `PlaybackMode` | Notes |
|---|---|---|
| `forward` | `Loop` | Standard forward loop |
| `reverse` | `Loop` | Frames stored in reverse order so normal forward playback produces the correct visual |
| `pingpong` | `PingPong` | |
| `pingpong_reverse` | `PingPong` | `AnimationClip.UserData` is set to `AsepriteClipLoader.PingPongReverseTag`; use `ConfigureAnimator` to apply `Reversed = true` automatically |

---

## Applying to an Animator with ConfigureAnimator

`ConfigureAnimator` registers all loaded clips on an animator and correctly handles `pingpong_reverse` by setting `SpriteAnimator.Reversed = true` when that clip plays.

```csharp
var loader = new AsepriteClipLoader();
var clips  = await loader.LoadAsync("assets/sprites/hero.json");
loader.ConfigureAnimator(animator, clips);

// Now just play by tag name
animator.Play("walk");
animator.Play("attack");
```

Use `ConfigureAnimator` instead of manually calling `AddAnimation` when your export contains `pingpong_reverse` tags.

---

## Hit Boxes from Slices

Aseprite slice data is mapped to `SpriteFrame` hit boxes automatically.

- A slice named `"hitbox"` (the default `HitBoxSliceName`) is stored as `SpriteFrame.HitBox`.
- All other slices are stored as named boxes via `SpriteFrame.SetHitBox(sliceName, rect)`.

```csharp
// In game code, after the clips are loaded and playing:
var frame = animComp.Animator.CurrentFrame;

Rectangle? hitbox   = frame?.HitBox;
Rectangle? hurtbox  = frame?.TryGetHitBox("hurtbox");
Rectangle? headZone = frame?.TryGetHitBox("head");
```

### Custom primary hitbox name

```csharp
var loader = new AsepriteClipLoader { HitBoxSliceName = "attack_box" };
```

### Slice pivot → frame origin

When a slice carries a Aseprite `pivot` field, it is normalised by the original canvas `sourceSize` and written to `SpriteFrame.Origin`. This keeps pivots correct on trimmed exports.

---

## Trim and DrawOffset

When Aseprite's **Trim** export option is active, frames carry `spriteSourceSize` (the sub-rect of the original canvas covered by non-transparent pixels) and `sourceSize` (the full untrimmed canvas size).

`AsepriteClipLoader` maps the trim offset to `SpriteFrame.DrawOffset` so that trimmed sprites render at the correct canvas-relative position. `AnimationSystem` applies `DrawOffset` to the entity's draw position each frame — you do not need to handle it manually.

---

## RepeatCount and UserData

- The Aseprite tag `repeat` field is written to `AnimationClip.RepeatCount`. On `Loop` and `PingPong` clips this makes the clip fire `OnAnimationComplete` after N passes instead of looping forever.
- The tag `data` field (set via Aseprite **Tag User Data**) is written to `AnimationClip.UserData` as a `string` (unless direction logic already set it, e.g. `PingPongReverseTag`).
- The per-frame `data` field (set via right-click → **Frame Properties** in Aseprite) is written to `SpriteFrame.UserData` as a `string`. Frames with no `data` field leave `UserData` as `null`.

```csharp
// Read clip user data after loading
foreach (var clip in clips)
{
    if (clip.UserData is string s && s == "boss_phase_2")
        clip.PlaybackMode = PlaybackMode.OnceHoldLast;
}

// Read frame user data during gameplay
if (animator.CurrentFrame?.UserData is string frameTag)
{
    if (frameTag == "spawn_particle")
        particleSystem.Burst(entity.Transform.Position);
}
```

---

## Reference: AsepriteClipLoader Members

| Member | Type | Purpose |
|---|---|---|
| `HitBoxSliceName` | `string` | Name of the Aseprite slice that maps to `SpriteFrame.HitBox`. Default: `"hitbox"` |
| `PingPongReverseTag` | `const string` | Value placed in `AnimationClip.UserData` for `pingpong_reverse` tags: `"pingpong_reverse"` |
| `LoadAsync(path, ...)` | method | Load from file path |
| `LoadAsync(stream, ...)` | method | Load from stream |
| `ConfigureAnimator(animator, clips)` | method | Register clips and handle `pingpong_reverse` |
