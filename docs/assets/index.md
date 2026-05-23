---
title: Assets
description: Load, cache, and manage game assets in Brine2D - textures, sounds, music, and fonts
---

# Assets

Brine2D provides a unified asset pipeline through `IAssetLoader`. No content pipeline, no build step, no `.mgcb` files - drag files into your `assets/` folder and load them.

---

## Quick Start

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;

    public GameScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        var texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
        var sound   = await _assets.GetOrLoadSoundAsync("assets/audio/jump.wav", ct);
        var music   = await _assets.GetOrLoadMusicAsync("assets/audio/theme.ogg", ct);
        var font    = await _assets.GetOrLoadFontAsync("assets/fonts/ui.ttf", size: 16, ct);
    }
}
```

---

## Topics

| Guide | Description |
|-------|-------------|
| **[Loading Assets](loading.md)** | Direct loading, caching, and releasing |
| **[Asset Manifests](manifests.md)** | Parallel preloading with typed manifests |
| **[Brine2D.Build](build-package.md)** | Compile-time asset path generation |

---

## Key Concepts

### IAssetLoader

The single service for all asset types:

| Method | Returns | Use For |
|--------|---------|---------|
| `GetOrLoadTextureAsync(path, scaleMode?, ct)` | `ITexture` | Images (.png, .jpg, .bmp, .tga, .gif, .webp) |
| `GetOrLoadSoundAsync(path, ct)` | `ISoundEffect` | Sound effects (.wav, .mp3, .flac, .aac) |
| `GetOrLoadMusicAsync(path, ct)` | `IMusic` | Music (.ogg) |
| `GetOrLoadFontAsync(path, size, ct)` | `IFont` | Fonts (.ttf, .otf) |

### Caching

Assets are cached automatically. Calling `GetOrLoadTextureAsync` twice with the same path returns the cached texture - no disk I/O on the second call.

### Scoped Lifetime

`IAssetLoader` is scoped per scene. When a scene unloads, all assets loaded through it are released automatically. No manual cleanup required for most games.

### Reference Counting

For advanced scenarios, assets use reference counting:

- Each `GetOrLoad*Async` call increments a reference count
- Each `Release*` call decrements it
- The asset is freed only when the count reaches zero
- Manifests have their own reference tracking

---

## Project Setup

Ensure your assets are copied to the output directory:

```xml
<!-- In your .csproj -->
<ItemGroup>
  <None Update="assets\**\*">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

Recommended folder structure:

```
MyGame/
+-- assets/
|   +-- images/
|   |   +-- player.png
|   |   +-- background.png
|   +-- audio/
|   |   +-- jump.wav
|   |   +-- theme.ogg
|   +-- fonts/
|       +-- ui.ttf
+-- Program.cs
+-- GameScene.cs
+-- MyGame.csproj
```

---

## Related Topics

- [Sprites & Textures](../rendering/sprites.md) - Drawing loaded textures
- [Scenes](../scenes/index.md) - Scene lifecycle and asset loading patterns