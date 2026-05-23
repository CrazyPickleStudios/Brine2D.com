---
title: Asset Manifests
description: Parallel asset preloading with typed AssetManifest and AssetRef<T>
---

# Asset Manifests

Asset manifests let you declare all assets a scene needs upfront, then load them all in parallel with a single call. This is the recommended approach for scenes with multiple assets.

---

## Quick Start

```csharp
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<ITexture>     Player  = Texture("assets/images/player.png", TextureScaleMode.Nearest);
    public readonly AssetRef<ITexture>     Tileset = Texture("assets/images/tileset.png", TextureScaleMode.Nearest);
    public readonly AssetRef<ISoundEffect> Jump    = Sound("assets/audio/jump.wav");
    public readonly AssetRef<IMusic>       Theme   = Music("assets/audio/theme.ogg");
    public readonly AssetRef<IFont>        HUD     = Font("assets/fonts/ui.ttf", size: 20);
}
```

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;
    private readonly LevelAssets _manifest = new();

    public GameScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        // All assets loaded in parallel
        await _assets.PreloadAsync(_manifest, cancellationToken: ct);
    }

    protected override void OnEnter()
    {
        // Implicit conversion - no .Value needed
        _player.Sprite.Texture = _manifest.Player;
        Audio.PlayMusic(_manifest.Theme);
    }
}
```

---

## Defining a Manifest

A manifest is a class extending `AssetManifest` with `AssetRef<T>` fields:

```csharp
public class MenuAssets : AssetManifest
{
    public readonly AssetRef<ITexture> Logo       = Texture("assets/images/logo.png");
    public readonly AssetRef<ITexture> Background = Texture("assets/images/menu-bg.png");
    public readonly AssetRef<IFont>    Title      = Font("assets/fonts/title.ttf", size: 48);
    public readonly AssetRef<IFont>    Body       = Font("assets/fonts/body.ttf", size: 16);
    public readonly AssetRef<IMusic>   MenuTheme  = Music("assets/audio/menu.ogg");
}
```

**Static helpers:** `Texture()`, `Sound()`, `Music()`, `Font()`

---

## Preloading

```csharp
await _assets.PreloadAsync(_manifest, progress, cancellationToken: ct);
```

- Loads all `AssetRef<T>` fields in parallel
- Reports progress as each asset completes
- Assets are safe to use from `OnEnter` onwards
- Partial failures throw `AggregateException` - successfully loaded assets are still cached

---

## AssetRef<T>

`AssetRef<T>` wraps a loaded asset with implicit conversion:

```csharp
AssetRef<ITexture> playerRef = Texture("assets/images/player.png");

// After PreloadAsync completes:
ITexture texture = playerRef;           // Implicit conversion
ITexture texture = playerRef.Value;     // Explicit access
bool loaded = playerRef.IsLoaded;       // Check state
```

---

## Unloading

```csharp
// Unload a specific manifest (decrements reference counts)
_assets.Unload(_manifest);

// Or let scoped IAssetLoader handle it - automatic on scene unload
```

---

## Combining with Brine2D.Build

If you use the optional `Brine2D.Build` package, asset paths are generated as compile-time constants:

```csharp
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<ITexture> Player = Texture(Assets.Images.Player);
    public readonly AssetRef<IMusic>   Theme  = Music(Assets.Audio.Music.Theme);
}
```

[:octicons-arrow-right-24: Learn more: Brine2D.Build](build-package.md)

---

## Next Steps

- **[Loading Assets](loading.md)** - Direct loading API reference
- **[Brine2D.Build](build-package.md)** - Compile-time asset path generation