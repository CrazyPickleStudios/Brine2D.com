---
title: Music Playback
description: Streaming music, crossfading, and the MusicSourceComponent in Brine2D
---

# Music Playback

This guide covers music streaming — loading, playback, crossfading, seeking, and the ECS-driven `MusicSourceComponent`.

For a quick introduction to audio in general, see [Getting Started](getting-started.md).

---

## Loading Music

Music is loaded through `IMusicLoader` (part of `IAudioService`). Like sound effects, loaded music is cached.

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assetLoader;

    public GameScene(IAssetLoader assetLoader) => _assetLoader = assetLoader;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        var theme = await _assetLoader.GetOrLoadMusicAsync("assets/audio/music/theme.ogg", ct);
    }
}
```

**With an asset manifest:**

```csharp
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<IMusic> Theme   = Music("assets/audio/music/theme.ogg");
    public readonly AssetRef<IMusic> Boss    = Music("assets/audio/music/boss.ogg");
    public readonly AssetRef<IMusic> Victory = Music("assets/audio/music/victory.ogg");
}
```

### Supported Formats

| Format | Extension | Notes |
|---|---|---|
| OGG Vorbis | `.ogg` | Recommended — good compression, seamless looping |
| MP3 | `.mp3` | Widely supported |
| WAV | `.wav` | Uncompressed, large files |
| FLAC | `.flac` | Lossless compression |

`.ogg` is the best choice for most game music — it supports gapless looping and has good compression.

!!! note "One Music Track"
    SDL3_mixer supports a single music stream at a time. Playing new music replaces the current track. Use `CrossfadeMusic` for smooth transitions between tracks.

---

## Playing Music

### Basic Playback

```csharp
Audio.PlayMusic(_assets.Theme);
```

This starts the music immediately, playing once with no loop.

### Playback Parameters

```csharp
Audio.PlayMusic(
    _assets.Theme,
    loops: -1,            // -1 = loop forever, 0 = play once, n = play n+1 times
    loopStartMs: 5000,    // loop restarts at 5 seconds instead of the beginning
    bus: "music"          // optional bus name
);
```

### Loop Points

Many game music tracks have an intro that should only play once. Use `loopStartMs` to set where the loop restarts:

```csharp
// 4-second intro, then loops from the 4-second mark onward
Audio.PlayMusic(_assets.Theme, loops: -1, loopStartMs: 4000);
```

---

## Crossfading

Smoothly transition between two music tracks:

```csharp
// Fade from current track to boss music over 2 seconds
Audio.CrossfadeMusic(
    _assets.BossTheme,
    fadeDuration: 2.0f,
    loops: -1
);
```

The current music fades out while the new music fades in simultaneously. All `PlayMusic` parameters are supported:

```csharp
Audio.CrossfadeMusic(
    _assets.BossTheme,
    fadeDuration: 1.5f,
    loops: -1,
    loopStartMs: 3000,
    bus: "music"
);
```

---

## Stopping Music

### Immediate Stop

```csharp
Audio.StopMusic();
```

### Fade Out

```csharp
// Fade out over 2 seconds
Audio.StopMusic(fadeDuration: 2.0f);
```

### Pause and Resume

```csharp
Audio.PauseMusic();
Audio.ResumeMusic();
```

---

## Seeking

Jump to a specific position in the current track:

```csharp
Audio.SeekMusic(positionMs: 30000);  // jump to 30 seconds
```

Query the current position and total duration:

```csharp
double currentMs = Audio.MusicPositionMs;
double totalMs   = Audio.MusicDurationMs;

double progress = currentMs / totalMs;  // 0.0 – 1.0
```

---

## Music State

```csharp
bool playing  = Audio.IsMusicPlaying;
bool paused   = Audio.IsMusicPaused;
bool fading   = Audio.IsMusicFadingOut;
```

---

## Pitch and Volume

Adjust the playing music track in real time:

```csharp
Audio.SetMusicPitch(0.8f);         // slow down (0.5 – 2.0)
Audio.SetMusicTrackVolume(0.5f);   // per-track volume (0.0 – 1.0)
```

### Volume Hierarchy

Music volume flows through the same hierarchy as sound effects:

```
Final volume = MasterVolume × MusicVolume × per-track volume
```

```csharp
Audio.MasterVolume = 0.8f;          // affects everything
Audio.MusicVolume  = 0.7f;          // affects all music
Audio.SetMusicTrackVolume(0.5f);    // affects the current track

// Effective volume: 0.8 × 0.7 × 0.5 = 0.28
```

---

## Bus Control

Music can be assigned to a bus for group control alongside sound effects:

```csharp
Audio.PlayMusic(_assets.Theme, loops: -1, bus: "music");

// Later: mute all audio in the "music" bus
Audio.PauseBus("music");
Audio.ResumeBus("music");
Audio.SetBusVolume("music", 0.5f);
```

---

## ECS: MusicSourceComponent

For entity-driven music, add a `MusicSourceComponent`. The `AudioSystem` processes it automatically.

```csharp
World.CreateEntity("BGM")
    .AddComponent<MusicSourceComponent>(m =>
    {
        m.Music       = _assets.Theme;
        m.LoopCount   = -1;
        m.PlayOnEnable = true;
        m.Bus         = "music";
    });
```

### Inherited Properties (from AudioSourceComponent)

| Property | Type | Default | Description |
|---|---|---|---|
| `Volume` | `float` | `1.0` | Base volume (0.0 – 1.0) |
| `Pitch` | `float` | `1.0` | Playback pitch (0.5 – 2.0) |
| `Priority` | `int` | `0` | Track priority |
| `Bus` | `string?` | `"music"` | Bus name (defaults to "music") |
| `PlayOnEnable` | `bool` | `false` | Auto-play when entity is enabled |
| `LoopCount` | `int` | `0` | 0 = once, -1 = forever, n = n+1 times |

### Music-Specific Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `Music` | `IMusic?` | `null` | The music track to play |
| `CrossfadeDuration` | `float` | `0.0` | Crossfade time in seconds (0 = instant switch) |
| `FadeOutDuration` | `float` | `0.0` | Fade-out time when stopping |
| `LoopStartMs` | `double` | `0.0` | Position in ms where loops restart |
| `TriggerSeek` | `bool` | `false` | Seek to `SeekPositionMs` next frame |
| `SeekPositionMs` | `double` | `0.0` | Target position for seek |

### Trigger Properties

Same as `SoundEffectSourceComponent` — the `AudioSystem` reads and resets these each frame:

```csharp
var music = entity.GetComponent<MusicSourceComponent>()!;

music.TriggerPlay   = true;   // start playback
music.TriggerStop   = true;   // stop (with optional fade-out)
music.TriggerPause  = true;   // pause
music.TriggerResume = true;   // resume
```

### Read-Only State

| Property | Type | Description |
|---|---|---|
| `IsPlaying` | `bool` | Currently playing |
| `IsPaused` | `bool` | Currently paused |
| `PlaybackEnded` | `bool` | Finished playing |

### Example: Crossfade Between Zones

```csharp
// Zone trigger changes the music with a crossfade
var bgm = entity.GetComponent<MusicSourceComponent>()!;
bgm.Music             = _assets.DungeonTheme;
bgm.CrossfadeDuration = 2.0f;
bgm.LoopCount         = -1;
bgm.TriggerPlay       = true;
```

### Example: Music with Loop Point

```csharp
entity.AddComponent<MusicSourceComponent>(m =>
{
    m.Music        = _assets.BossTheme;
    m.LoopCount    = -1;
    m.LoopStartMs  = 4500;     // intro plays once, loops from 4.5s
    m.PlayOnEnable = true;
});
```

### Example: Fade Out on Scene Exit

```csharp
protected override void OnExit()
{
    var bgm = _bgmEntity.GetComponent<MusicSourceComponent>()!;
    bgm.FadeOutDuration = 1.5f;
    bgm.TriggerStop     = true;
}
```

### Example: Seeking

```csharp
var bgm = entity.GetComponent<MusicSourceComponent>()!;
bgm.SeekPositionMs = 30000;   // jump to 30 seconds
bgm.TriggerSeek    = true;
```

---

## What's Next?

- [Sound Effects](sound-effects.md) — one-shot and looping sound effects, track management
- [Spatial Audio](spatial-audio.md) — distance attenuation, panning, Doppler
- [Getting Started](getting-started.md) — full audio tutorial from scratch
