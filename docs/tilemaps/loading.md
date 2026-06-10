---
title: Loading Tilemaps
description: Load Tiled JSON tilemaps in Brine2D
---

# Loading Tilemaps

`TmjLoader` reads Tiled JSON maps (`.tmj`) and returns a `Tilemap` ready for use. It's injected via `ITilemapLoader` once you call `AddTilemapServices()`.

---

## Setup

Register the tilemap services in your game builder:

```csharp
builder.Services.AddTilemapServices();
```

This registers:

- `ITilemapLoader` → `TmjLoader` (singleton)
- `TilemapAnimator` (transient)
- `TilemapSystem` (transient)

---

## Loading a Map

Inject `ITilemapLoader` and call `LoadAsync` in your scene's `OnLoadAsync`:

```csharp
public class GameScene : Scene
{
    private readonly ITilemapLoader _loader;

    public GameScene(ITilemapLoader loader)
    {
        _loader = loader;
    }

    protected override async Task OnLoadAsync(CancellationToken ct)
    {
        var tilemap = await _loader.LoadAsync("assets/maps/level1.tmj", ct);

        World.CreateEntity()
            .AddComponent<TilemapComponent>(c => c.Tilemap = tilemap);
    }
}
```

`LoadAsync` throws on invalid files — it never returns null. If the file is missing, malformed, or uses an unsupported map type, you'll get a descriptive exception.

---

## Tilesets

### Embedded tilesets

Tilesets defined directly in the `.tmj` file are loaded automatically — no extra configuration needed.

### External tilesets (.tsj)

Tilesets saved as separate `.tsj` files are also supported. Brine2D resolves the `.tsj` path relative to the `.tmj` file, exactly as Tiled stores it.

!!! note
    Make sure your `.tsj` files are copied to the output directory alongside your `.tmj` files.

---

## Tile Data Encodings

Brine2D supports all tile data formats Tiled can export:

| Encoding | Supported |
|----------|:---------:|
| CSV (array) | :white_check_mark: |
| Base64 (uncompressed) | :white_check_mark: |
| Base64 + zlib | :white_check_mark: |
| Base64 + gzip | :white_check_mark: |
| Base64 + zstd | :white_check_mark: |

You can choose any of these in Tiled under **Map → Map Properties → Tile Layer Format**.

---

## Supported Map Types

| Setting | Required value |
|---------|---------------|
| Orientation | Orthogonal |
| Tile render order | `right-down` (Tiled default) |
| Infinite map | Off (fixed-size only) |
| Tileset type | Single-image (not image-collection) |

!!! warning
    Maps that don't meet these requirements throw `NotSupportedException` at load time with a message explaining what to change and where to find the setting in Tiled.

---

## Layer Types

All Tiled layer types are handled:

| Layer type | Loaded as |
|------------|-----------|
| Tile layer | `TilemapLayer` → `tilemap.Layers` |
| Object group | `TilemapObject` list → `tilemap.ObjectLayers` |
| Image layer | `TilemapImageLayer` → `tilemap.ImageLayers` |
| Group layer | Flattened transparently — child layers are loaded as if ungrouped |

Group layers are never surfaced directly. Their visibility, opacity, tint, offset, and parallax are composed into each child layer.

---

## Copying Assets to Output

Make sure your map and tileset files are copied during build. Add this to your `.csproj`:

```xml
<ItemGroup>
  <None Update="assets\**\*">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

---

## What Gets Loaded

After `LoadAsync` returns, the `Tilemap` object contains:

| Property | Description |
|----------|-------------|
| `Width`, `Height` | Map dimensions in tiles |
| `TileWidth`, `TileHeight` | Tile dimensions in pixels |
| `Layers` | All tile layers, sorted by document order (ZOrder) |
| `Tilesets` | All tilesets, sorted by `FirstGid` |
| `ObjectLayers` | Objects keyed by layer name |
| `ImageLayers` | Image layers in document order |
| `Properties` | Map-level custom properties |
| `BackgroundColor` | From Tiled's Map Properties |

[:octicons-arrow-right-24: Next: Rendering](rendering.md)
