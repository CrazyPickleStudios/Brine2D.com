---
title: Brine2D.Build
description: Optional MSBuild tooling that generates compile-time asset path constants
---

# Brine2D.Build

Optional MSBuild package that generates a strongly-typed `Assets` class from your `assets/` folder on every build. Full IntelliSense, compile-time safety, no content pipeline.

!!! note "Not Yet Published"
    Brine2D.Build will be published alongside Brine2D 1.0 after cross-platform MSBuild validation.

---

## Installation

```bash
dotnet add package Brine2D.Build
```

That's it. The `.targets` file is imported automatically by NuGet.

---

## What Gets Generated

Given `assets/images/player.png` and `assets/audio/jump.wav`, Brine2D.Build generates (into `obj/`):

```csharp
namespace MyGame;

public static partial class Assets
{
    public static class Audio
    {
        public const string Jump = "assets/audio/jump.wav";
    }

    public static class Images
    {
        public const string Player = "assets/images/player.png";
    }
}
```

---

## Usage

Use generated constants with `IAssetLoader` or `AssetManifest`:

```csharp
// Direct loading
var texture = await _assets.GetOrLoadTextureAsync(Assets.Images.Player, cancellationToken: ct);

// With manifest
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<ITexture>     Player = Texture(Assets.Images.Player);
    public readonly AssetRef<ISoundEffect> Jump   = Sound(Assets.Audio.Jump);
}
```

---

## Configuration

All optional:

```xml
<PropertyGroup>
  <Brine2DAssetsFolder>content</Brine2DAssetsFolder>
  <Brine2DAssetsNamespace>MyGame</Brine2DAssetsNamespace>
  <Brine2DAssetsClassName>GameAssets</Brine2DAssetsClassName>
  <Brine2DGenerateAssets>false</Brine2DGenerateAssets>
</PropertyGroup>
```

---

## The partial Keyword

The generated class is `partial`, so you can extend it:

```csharp
public static partial class Assets
{
    public static class Runtime
    {
        public static string LevelPath(int level) => $"assets/levels/level_{level:D2}.tmj";
    }
}
```

---

## Without This Package

Brine2D.Build is entirely optional. Manifests work with string paths:

```csharp
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<ITexture> Player = Texture("assets/images/player.png");
}
```

---

## Next Steps

- **[Asset Manifests](manifests.md)** - Using manifests with or without Brine2D.Build
- **[Loading Assets](loading.md)** - Direct loading API