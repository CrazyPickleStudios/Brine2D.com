---
title: Sound Effects
description: Loading, playing, and managing sound effects in Brine2D
---

# Sound Effects

This guide covers everything you need to work with sound effects — loading, playback, track management, and the ECS-driven `SoundEffectSourceComponent`.

For a quick introduction to audio in general, see [Getting Started](getting-started.md).

---

## Loading Sound Effects

Sound effects are loaded through `ISoundLoader` (part of `IAudioService`). All loaded sounds are cached — loading the same path twice returns the cached instance.

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assetLoader;

    public GameScene(IAssetLoader assetLoader) => _assetLoader = assetLoader;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        var jump = await _assetLoader.GetOrLoadSoundAsync("assets/audio/jump.wav", ct);
        var hit  = await _assetLoader.GetOrLoadSoundAsync("assets/audio/hit.wav", ct);
    }
}
```

**With an asset manifest** (recommended for scenes with many assets):

```csharp
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<ISoundEffect> Jump   = Sound("assets/audio/jump.wav");
    public readonly AssetRef<ISoundEffect> Hit    = Sound("assets/audio/hit.wav");
    public readonly AssetRef<ISoundEffect> Coin   = Sound("assets/audio/coin.wav");
    public readonly AssetRef<ISoundEffect> Death  = Sound("assets/audio/death.wav");
}
```

```csharp
private readonly LevelAssets _assets = new();

protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    => await _assetLoader.PreloadAsync(_assets, cancellationToken: ct);
```

### Supported Formats

| Format | Extension | Notes |
|---|---|---|
| WAV | `.wav` | Uncompressed, lowest latency |
| OGG Vorbis | `.ogg` | Good compression, recommended for larger files |
| MP3 | `.mp3` | Widely supported |
| FLAC | `.flac` | Lossless compression |

Short effects (footsteps, UI clicks) work best as `.wav`. Longer effects (ambience loops, voice lines) benefit from `.ogg` compression.

---

## Playing Sounds

### Basic Playback

The simplest way to play a sound:

```csharp
Audio.PlaySound(_assets.Jump);
```

This plays the sound once at full volume, centered pan, normal pitch, default priority, on no bus.

### Playback Parameters

`PlaySound` accepts optional parameters for fine-grained control:

```csharp
Audio.PlaySound(
    _assets.Jump,
    volume: 0.8f,       // 0.0 – 1.0 (default: 1.0)
    loops: 0,           // 0 = play once, -1 = loop forever, n = play n+1 times
    pan: -0.5f,         // -1.0 (left) to 1.0 (right), 0.0 = center
    pitch: 1.2f,        // 0.5 = half speed, 1.0 = normal, 2.0 = double speed
    priority: 5,        // higher = harder to evict (default: 0)
    bus: "sfx"          // optional bus name for group control
);
```

### Looping Sounds

```csharp
// Loop forever (e.g., an engine hum or ambient wind)
var track = Audio.PlaySound(_assets.Wind, loops: -1);

// Loop 3 times (plays 4 times total)
Audio.PlaySound(_assets.Alarm, loops: 3);
```

---

## Track Handles

Every `PlaySound` call returns a track handle (`nint`) that you can use to control the sound after it starts playing.

```csharp
var track = Audio.PlaySound(_assets.EngineHum, loops: -1);
```

### Checking Track State

```csharp
if (Audio.IsTrackAlive(track))
{
    // Track is still playing or paused
}
```

!!! tip
    Always check `IsTrackAlive` before calling other track methods. A track becomes invalid once playback finishes or the track is stopped.

### Adjusting a Playing Track

```csharp
// Volume (0.0 – 1.0)
Audio.SetTrackVolume(track, 0.5f);

// Pan (-1.0 left to 1.0 right)
Audio.SetTrackPan(track, -0.3f);

// Pitch (0.5 – 2.0)
Audio.SetTrackPitch(track, 1.5f);

// Volume and pan together (slightly more efficient than two separate calls)
Audio.SetTrackVolumeAndPan(track, volume: 0.7f, pan: 0.2f);
```

### Pausing, Resuming, and Stopping

```csharp
Audio.PauseTrack(track);
Audio.ResumeTrack(track);
Audio.StopTrack(track);
```

### Bus Tagging

You can assign a track to a bus after creation:

```csharp
var track = Audio.PlaySound(_assets.Footstep);
Audio.TagTrack(track, "player");
```

---

## Bulk Operations

Control all playing sounds at once:

```csharp
// Pause/resume everything (e.g., when opening a pause menu)
Audio.PauseAllSounds();
Audio.ResumeAllSounds();

// Stop everything
Audio.StopAllSounds();
```

### Bus Control

Buses let you group sounds and control them together:

```csharp
// Pause all sounds on the "enemies" bus
Audio.PauseBus("enemies");
Audio.ResumeBus("enemies");
Audio.StopBus("enemies");

// Adjust volume for an entire bus
Audio.SetBusVolume("enemies", 0.3f);
```

Sounds are assigned to a bus via the `bus` parameter on `PlaySound`, via `TagTrack`, or via the `Bus` property on `AudioSourceComponent`.

---

## Volume Hierarchy

Sound effect volume flows through a three-level hierarchy:

```
Final volume = MasterVolume × SoundVolume × per-track volume
```

```csharp
// Global volumes (0.0 – 1.0)
Audio.MasterVolume = 0.8f;   // affects everything (sounds + music)
Audio.SoundVolume  = 0.6f;   // affects all sound effects

// Per-track volume
Audio.SetTrackVolume(track, 0.5f);

// Effective volume: 0.8 × 0.6 × 0.5 = 0.24
```

---

## Priority and Track Eviction

SDL3_mixer has a finite number of mixing channels (`MaxSoundTracks`). When all channels are in use, Brine2D uses priority-based eviction:

- A new sound with **higher priority** evicts the lowest-priority playing sound.
- A new sound with **equal or lower priority** than all playing sounds is **dropped silently**.

```csharp
// UI feedback — low priority, okay to drop
Audio.PlaySound(_assets.Click, priority: 0);

// Player attack — medium priority
Audio.PlaySound(_assets.Slash, priority: 5);

// Boss roar — high priority, should always play
Audio.PlaySound(_assets.BossRoar, priority: 10);
```

You can check how many tracks are active:

```csharp
int active = Audio.ActiveSoundTrackCount;
int max    = Audio.MaxSoundTracks;
```

---

## ECS: SoundEffectSourceComponent

For entity-driven sound effects, add a `SoundEffectSourceComponent` to an entity. The `AudioSystem` processes these components automatically.

```csharp
World.CreateEntity("Torch")
    .AddComponent<TransformComponent>(t => t.Position = new Vector2(400, 300))
    .AddComponent<SoundEffectSourceComponent>(s =>
    {
        s.SoundEffect = _assets.FireLoop;
        s.LoopCount   = -1;           // loop forever
        s.Volume      = 0.7f;
        s.PlayOnEnable = true;        // start playing when the entity is created
    });
```

### Inherited Properties (from AudioSourceComponent)

These properties are shared with `MusicSourceComponent`:

| Property | Type | Default | Description |
|---|---|---|---|
| `Volume` | `float` | `1.0` | Base volume (0.0 – 1.0) |
| `Pitch` | `float` | `1.0` | Playback pitch (0.5 – 2.0) |
| `Priority` | `int` | `0` | Track priority for eviction |
| `Bus` | `string?` | `null` | Bus name for group control |
| `PlayOnEnable` | `bool` | `false` | Auto-play when entity is enabled |
| `LoopCount` | `int` | `0` | 0 = once, -1 = forever, n = n+1 times |

### Trigger Properties

Control playback through trigger flags. The `AudioSystem` reads and resets these each frame:

```csharp
var source = entity.GetComponent<SoundEffectSourceComponent>()!;

source.TriggerPlay   = true;   // start playback next frame
source.TriggerStop   = true;   // stop playback next frame
source.TriggerPause  = true;   // pause next frame
source.TriggerResume = true;   // resume next frame
```

### Read-Only State

| Property | Type | Description |
|---|---|---|
| `IsPlaying` | `bool` | Currently playing |
| `IsPaused` | `bool` | Currently paused |
| `PlaybackEnded` | `bool` | Finished playing (reset on next play) |

### Spatial Audio Properties

`SoundEffectSourceComponent` adds spatial audio support on top of the base component. These properties are covered in detail in the [Spatial Audio](spatial-audio.md) guide.

| Property | Type | Default | Description |
|---|---|---|---|
| `SoundEffect` | `ISoundEffect?` | `null` | The sound to play |
| `EnableSpatialAudio` | `bool` | `false` | Enable distance/pan calculations |
| `MinDistance` | `float` | `100` | Distance at which volume starts to fall off |
| `MaxDistance` | `float` | `800` | Distance at which the sound is silent |
| `RolloffFactor` | `float` | `1.0` | How quickly volume drops with distance |
| `SpatialBlend` | `float` | `1.0` | 0 = fully non-spatial, 1 = fully spatial |
| `DopplerFactor` | `float` | `0.0` | Doppler pitch shift intensity |
| `MaxConcurrentInstances` | `int` | `0` | Max simultaneous plays (0 = unlimited) |
| `PitchVariation` | `float` | `0.0` | Random pitch offset per play (±) |
| `VolumeVariation` | `float` | `0.0` | Random volume offset per play (±) |
| `FadeInDuration` | `float` | `0.0` | Fade-in time in seconds |
| `FadeOutDuration` | `float` | `0.0` | Fade-out time in seconds |
| `TriggerStopOldest` | `bool` | `false` | Stop oldest instance when `MaxConcurrentInstances` is exceeded |

### Example: Footsteps with Variation

```csharp
entity.AddComponent<SoundEffectSourceComponent>(s =>
{
    s.SoundEffect     = _assets.Footstep;
    s.PitchVariation  = 0.15f;   // ±15% random pitch each play
    s.VolumeVariation = 0.1f;    // ±10% random volume each play
    s.Priority        = 1;
});
```

Each time `TriggerPlay` is set, the sound plays with a slightly different pitch and volume, preventing the "machine gun" repetition effect.

### Example: Limited Concurrent Instances

```csharp
entity.AddComponent<SoundEffectSourceComponent>(s =>
{
    s.SoundEffect            = _assets.LaserShot;
    s.MaxConcurrentInstances = 3;
    s.TriggerStopOldest      = true;  // stop oldest when 4th shot fires
});
```

### Example: Fade In/Out

```csharp
entity.AddComponent<SoundEffectSourceComponent>(s =>
{
    s.SoundEffect    = _assets.AmbientWind;
    s.LoopCount      = -1;
    s.FadeInDuration  = 2.0f;   // 2-second fade in
    s.FadeOutDuration = 1.5f;   // 1.5-second fade out on stop
    s.PlayOnEnable   = true;
});
```

---

## What's Next?

- [Music Playback](music.md) — streaming music, crossfading, and seeking
- [Spatial Audio](spatial-audio.md) — distance attenuation, panning, Doppler
- [Getting Started](getting-started.md) — full audio tutorial from scratch
