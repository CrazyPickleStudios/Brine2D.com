---
title: Loading Assets
description: Load textures, sounds, music, and fonts with IAssetLoader
---

# Loading Assets

All assets are loaded through `IAssetLoader`, which caches results and manages lifetimes automatically.

---

## Inject IAssetLoader

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;

    public GameScene(IAssetLoader assets) => _assets = assets;
}
```

---

## Loading by Type

### Textures

```csharp
// Default (linear filtering - smooth scaling)
var texture = await _assets.GetOrLoadTextureAsync("assets/images/background.png", cancellationToken: ct);

// Nearest filtering - sharp pixel art
var pixelArt = await _assets.GetOrLoadTextureAsync(
    "assets/images/player.png",
    TextureScaleMode.Nearest,
    ct);
```

The `(path, scaleMode)` pair is the cache key - the same file at different scale modes is cached separately.

### Sound Effects

```csharp
var jump = await _assets.GetOrLoadSoundAsync("assets/audio/jump.wav", ct);
Audio.PlaySound(jump);
```

### Music

```csharp
var theme = await _assets.GetOrLoadMusicAsync("assets/audio/theme.ogg", ct);
Audio.PlayMusic(theme);
```

### Fonts

```csharp
var font = await _assets.GetOrLoadFontAsync("assets/fonts/ui.ttf", size: 16, ct);
Renderer.SetDefaultFont(font);
```

The `(path, size)` pair is the cache key - the same file at different sizes is cached separately.

---

## Releasing Assets

Assets loaded through a scoped `IAssetLoader` are released automatically when the scene unloads. For manual control:

```csharp
// Release a specific texture
_assets.ReleaseTexture("assets/images/player.png");

// Release with scale mode (if loaded with non-default)
_assets.ReleaseTexture("assets/images/player.png", TextureScaleMode.Nearest);

// Release other types
_assets.ReleaseSound("assets/audio/jump.wav");
_assets.ReleaseMusic("assets/audio/theme.ogg");
_assets.ReleaseFont("assets/fonts/ui.ttf", size: 16);

// Release everything
_assets.UnloadAll();
```

---

## Loading with Progress

Report progress to a loading screen:

```csharp
protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
{
    _texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
    progress?.Report(0.33f);

    _sound = await _assets.GetOrLoadSoundAsync("assets/audio/jump.wav", ct);
    progress?.Report(0.66f);

    _music = await _assets.GetOrLoadMusicAsync("assets/audio/theme.ogg", ct);
    progress?.Report(1.0f);
}
```

---

## Supported Formats

| Extension | Type | Loader |
|-----------|------|--------|
| `.png` `.jpg` `.jpeg` `.bmp` `.tga` `.gif` `.webp` | Texture | `GetOrLoadTextureAsync` |
| `.wav` `.mp3` `.flac` `.aac` | Sound | `GetOrLoadSoundAsync` |
| `.ogg` | Music | `GetOrLoadMusicAsync` |
| `.ttf` `.otf` | Font | `GetOrLoadFontAsync` |

---

## Next Steps

- **[Asset Manifests](manifests.md)** - Parallel preloading with typed manifests
- **[Brine2D.Build](build-package.md)** - Compile-time asset path generation