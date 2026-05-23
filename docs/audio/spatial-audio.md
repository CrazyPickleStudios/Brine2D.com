---
title: Spatial Audio
description: 2D positional audio with distance attenuation and stereo panning
---

# Spatial Audio

Spatial audio simulates sound positioning in 2D space, making your game world feel more immersive with distance-based volume attenuation, stereo panning, and Doppler effects.

## What is Spatial Audio?

Spatial audio adjusts sound based on the distance and direction between a sound source and an audio listener. As entities move in your game world, sounds automatically fade, pan left/right, and shift pitch to match their spatial relationships.

**Key Features:**

- **Distance attenuation** — Sounds fade as they move away from the listener
- **Stereo panning** — Sounds pan left/right based on horizontal position
- **Doppler effect** — Pitch shifts based on relative velocity
- **Real-time updates** — Audio adjusts every frame as entities move
- **Configurable curves** — Linear, quadratic, or custom falloff
- **ECS integration** — Component-based via `SoundEffectSourceComponent` and `AudioListenerComponent`
- **Pitch and volume variation** — Randomized per-play for natural-sounding repetition
- **Fade in/out** — Smooth volume transitions on start and stop
- **Max concurrent instances** — Limit how many copies of the same sound can overlap

## Basic Concepts

### Audio Listener

The listener represents the "ears" in your game world — typically attached to the player or camera.

**Properties:**

| Property | Description | Default |
|----------|-------------|---------|
| `GlobalSpatialVolume` | Master volume for all spatial audio (0.0–1.0) | 1.0 |
| `SpeedOfSound` | World units per second for Doppler calculations | 343 |

### Sound Effect Source

A positioned sound emitter. Uses `SoundEffectSourceComponent` (extends `AudioSourceComponent`).

**Inherited from `AudioSourceComponent`:**

| Property | Description | Default |
|----------|-------------|---------|
| `Volume` | Base volume (0.0–1.0) | 1.0 |
| `Pitch` | Playback speed (0.25–4.0) | 1.0 |
| `Priority` | Eviction priority (higher = less likely evicted) | 0 |
| `Bus` | Bus name for group operations | `"sfx"` |
| `PlayOnEnable` | Auto-play when enabled | `false` |
| `LoopCount` | -1 = infinite, 0 = once | 0 |
| `TriggerPlay` | Set `true` to play next frame | `false` |
| `TriggerStop` | Set `true` to stop next frame | `false` |
| `TriggerPause` | Set `true` to pause next frame | `false` |
| `TriggerResume` | Set `true` to resume next frame | `false` |
| `IsPlaying` | Read-only, managed by AudioSystem | — |
| `IsPaused` | Read-only, managed by AudioSystem | — |
| `PlaybackEnded` | Set by system when playback ends naturally | — |

**Spatial properties on `SoundEffectSourceComponent`:**

| Property | Description | Default |
|----------|-------------|---------|
| `SoundEffect` | The `ISoundEffect` to play | `null` |
| `EnableSpatialAudio` | Toggle spatial processing | `false` |
| `MinDistance` | Full volume radius | 50 |
| `MaxDistance` | Silent beyond this | 500 |
| `RolloffFactor` | Attenuation curve (0 = flat, 1 = linear, 2 = quadratic) | 1.0 |
| `SpatialBlend` | Stereo strength (0.0 = mono, 1.0 = full) | 1.0 |
| `DopplerFactor` | Doppler intensity (0 = off, 1 = realistic, max 5) | 0 |
| `MaxConcurrentInstances` | Global cap on simultaneous instances of same sound (0 = unlimited) | 0 |
| `PitchVariation` | Random pitch offset per play (0–1) | 0 |
| `VolumeVariation` | Random volume reduction per play (0–1) | 0 |
| `FadeInDuration` | Seconds to fade in on play | 0 |
| `FadeOutDuration` | Seconds to fade out on stop | 0 |
| `TriggerStopOldest` | Stop oldest overlapping track on this entity | `false` |

### Music Source

For positional music triggers, use `MusicSourceComponent` (extends `AudioSourceComponent`). Spatial audio does not apply to music.

| Property | Description | Default |
|----------|-------------|---------|
| `Music` | The `IMusic` to play | `null` |
| `CrossfadeDuration` | Crossfade when replacing another music entity | 0 |
| `FadeOutDuration` | Fade when stopped | 0 |
| `LoopStartMs` | Loop point offset in ms (allows intro) | 0 |
| `TriggerSeek` / `SeekPositionMs` | Seek to position | — |
| `Bus` | Default `"music"` | `"music"` |

### Distance Attenuation

```
Volume = BaseVolume x AttenuationFactor

- Within MinDistance: factor = 1.0
- Beyond MaxDistance: factor = 0.0
- Between: curve depends on RolloffFactor
```

### Stereo Panning

```
Pan = -1.0 (full left) to +1.0 (full right)

Calculated from direction between listener and source.
SpatialBlend controls strength.
Listener rotation affects panning direction.
```

## Setup

### AudioSystem

`AudioSystem` is a default system — it's added automatically to every scene. No registration needed.

### Create Audio Listener

Typically attached to the player or camera:

```csharp
var player = World.CreateEntity("Player");
player.AddComponent<TransformComponent>(t => t.Position = new Vector2(640, 360));
player.AddComponent<AudioListenerComponent>(l =>
{
    l.GlobalSpatialVolume = 1.0f;
    l.SpeedOfSound = 343f; // for Doppler
});
```

### Create Sound Effect Source

```csharp
var enemy = World.CreateEntity("Enemy");
enemy.AddComponent<TransformComponent>(t => t.Position = new Vector2(200, 300));
enemy.AddComponent<SoundEffectSourceComponent>(src =>
{
    src.SoundEffect = _enemyGrowlSound;
    src.EnableSpatialAudio = true;
    src.MinDistance = 100f;
    src.MaxDistance = 500f;
    src.RolloffFactor = 1.0f;
    src.SpatialBlend = 1.0f;
    src.Volume = 0.7f;
    src.LoopCount = -1;
    src.PlayOnEnable = true;
});
```

## Distance Attenuation

### Linear Falloff

```csharp
src.RolloffFactor = 1.0f;
// At 50% distance: volume is ~50%
```

### Quadratic Falloff

```csharp
src.RolloffFactor = 2.0f;
// At 50% distance: volume is ~25%
```

### No Falloff

```csharp
src.RolloffFactor = 0f;
// Full volume from MinDistance to MaxDistance, then silent
```

### Distance Guidelines

```csharp
// Small sounds (coins, footsteps)
src.MinDistance = 50f;
src.MaxDistance = 200f;

// Medium sounds (weapon fire, attacks)
src.MinDistance = 100f;
src.MaxDistance = 500f;

// Large sounds (explosions, boss roars)
src.MinDistance = 150f;
src.MaxDistance = 800f;

// Environmental ambient (waterfalls, wind)
src.MinDistance = 200f;
src.MaxDistance = 1000f;
```

## Stereo Panning

```csharp
src.SpatialBlend = 1.0f;  // Full stereo
src.SpatialBlend = 0.5f;  // Partial stereo (good for background sounds)
src.SpatialBlend = 0.0f;  // Mono (center, no panning)
```

## Doppler Effect

```csharp
src.DopplerFactor = 1.0f; // Realistic pitch shift from relative motion
src.DopplerFactor = 2.0f; // Exaggerated

// Tune the listener's speed of sound to match your world scale
listener.SpeedOfSound = 343f;
```

Requires `EnableSpatialAudio = true`. The Doppler pitch is multiplied with the component's `Pitch`.

## Pitch and Volume Variation

Add natural randomness to repeated sounds:

```csharp
src.PitchVariation = 0.1f;   // +/- 10% pitch each play
src.VolumeVariation = 0.05f; // Up to 5% quieter each play
```

## Fade In/Out

```csharp
src.FadeInDuration = 0.5f;  // 0.5s fade-in on play
src.FadeOutDuration = 1.0f; // 1s fade-out on stop

// Setting TriggerStop a second time during an active fade-out forces immediate stop
```

## Max Concurrent Instances

Limit overlapping copies of the same sound globally:

```csharp
src.MaxConcurrentInstances = 3; // At most 3 instances of this sound across all entities
```

## Complete Examples

### Enemy Audio

```csharp
var enemy = World.CreateEntity("Enemy");
enemy.AddComponent<TransformComponent>(t => t.Position = position);
enemy.AddComponent<SoundEffectSourceComponent>(src =>
{
    src.SoundEffect = _growlSound;
    src.EnableSpatialAudio = true;
    src.MinDistance = 80f;
    src.MaxDistance = 400f;
    src.RolloffFactor = 1.5f;
    src.SpatialBlend = 0.9f;
    src.Volume = 0.6f;
    src.LoopCount = -1;
    src.PlayOnEnable = true;
    src.DopplerFactor = 0.5f;
});
```

### Collectible Coin

```csharp
var coin = World.CreateEntity("Coin");
coin.AddComponent<TransformComponent>(t => t.Position = position);
coin.AddComponent<SoundEffectSourceComponent>(src =>
{
    src.SoundEffect = _jingleSound;
    src.EnableSpatialAudio = true;
    src.MinDistance = 30f;
    src.MaxDistance = 150f;
    src.RolloffFactor = 1.0f;
    src.SpatialBlend = 0.7f;
    src.Volume = 0.5f;
    src.LoopCount = -1;
    src.PlayOnEnable = true;
    src.PitchVariation = 0.05f;
});
```

### Ambient Zone with Music

```csharp
var zone = World.CreateEntity("BossZone");
zone.AddComponent<TransformComponent>(t => t.Position = zoneCenter);
zone.AddComponent<MusicSourceComponent>(m =>
{
    m.Music = _bossMusic;
    m.LoopCount = -1;
    m.CrossfadeDuration = 2.0f;
    m.PlayOnEnable = true;
});
```

### One-Shot with Fade-Out

```csharp
var alarm = World.CreateEntity("Alarm");
alarm.AddComponent<TransformComponent>(t => t.Position = alarmPos);
alarm.AddComponent<SoundEffectSourceComponent>(src =>
{
    src.SoundEffect = _alarmSound;
    src.EnableSpatialAudio = true;
    src.MinDistance = 100f;
    src.MaxDistance = 600f;
    src.LoopCount = -1;
    src.PlayOnEnable = true;
    src.FadeInDuration = 0.3f;
    src.FadeOutDuration = 1.0f;
});

// Later, stop with fade-out
alarm.GetComponent<SoundEffectSourceComponent>()!.TriggerStop = true;
```

## Triggering Playback

Control playback via trigger flags (consumed each frame by AudioSystem):

```csharp
var src = entity.GetComponent<SoundEffectSourceComponent>()!;

// Play
src.TriggerPlay = true;

// Stop
src.TriggerStop = true;

// Pause / Resume
src.TriggerPause = true;
src.TriggerResume = true;

// Check state
if (src.IsPlaying) { }
if (src.IsPaused) { }
if (src.PlaybackEnded) { }

// Stop oldest overlapping track on this entity
src.TriggerStopOldest = true;
```

If both `TriggerPlay` and `TriggerStop` are set in the same frame, both are cleared and no action is taken. Same for `TriggerPause`/`TriggerResume`.

## Best Practices

### Do

- **Use spatial audio for diegetic sounds** — In-world sounds (enemies, pickups, effects)
- **Disable for non-diegetic sounds** — UI, narration
- **Match distances to game scale** — Larger worlds need larger distances
- **Test with headphones** — Stereo panning is clearest with headphones
- **Use `PitchVariation`** — Avoids repetitive-sounding effects
- **Use `FadeOutDuration`** — Prevents clicks on stop

### Don't

- **Don't enable spatial audio globally** — Only for positioned sounds
- **Don't use tiny MinDistance** — Causes abrupt volume changes
- **Don't use huge MaxDistance** — Wastes processing on inaudible sounds
- **Don't overlap too many sources** — Use `MaxConcurrentInstances` to limit

## Troubleshooting

### No Spatial Audio

1. Ensure `EnableSpatialAudio = true` on the `SoundEffectSourceComponent`
2. Verify an `AudioListenerComponent` exists and is enabled
3. Check that both entities have a `TransformComponent`
4. Confirm `SpatialBlend > 0` for panning

### Sounds Cut Off Abruptly

Increase `MaxDistance` or add `FadeOutDuration`:

```csharp
src.MaxDistance = 400f;
src.FadeOutDuration = 0.5f;
```

### Sounds Too Quiet

Check `GlobalSpatialVolume` on the listener and `Volume` on the source.

### Panning Feels Wrong

Brine2D uses X+ = Right, Y+ = Down. Listener rotation affects panning direction.

### Too Many Audio Sources

Use `MaxConcurrentInstances` and disable sources beyond hearing range:

```csharp
src.MaxConcurrentInstances = 3;
// Or disable far-away entities in a behavior/system
```

## See Also

- [Sound Effects](sound-effects.md) — Basic sound playback
- [Music Playback](music.md) — Background music
- [Getting Started](getting-started.md) — Audio basics
