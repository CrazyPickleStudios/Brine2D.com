---
title: Collision & Objects
description: Generate collision rects, query objects, and convert coordinates in Brine2D tilemaps
---

# Collision & Objects

The `Tilemap` data model provides helpers for generating physics collision geometry from tile properties, querying objects placed in Tiled, and converting between world space and tile coordinates.

---

## Collision Rects

### Setting up in Tiled

Two things must be true for a tile to contribute a collision rect:

1. **The layer** must have a boolean custom property named `collision` or `hasCollision` set to `true`
2. **Each tile** that should be solid needs a boolean custom property named `solid` or `isSolid` set to `true`

To add tile properties in Tiled: open the tileset, select the tile in the Tileset Editor, and add a custom property in the Properties panel.

### Generating rects

```csharp
// One rect per solid tile:
var rects = tilemap.GenerateCollisionRects("Collision");

// Greedy-merged rects — adjacent solid tiles are combined into larger rectangles.
// Fewer, larger rects are better for most physics solvers:
var merged = tilemap.MergeCollisionRects("Collision");
```

Rects are in world space (pixels), accounting for the layer's `OffsetX`/`OffsetY`. Parallax is not applied — collision layers should use the default parallax of 1.0.

### One-way platforms

Mark tiles with a boolean property named `onewayplatform` or `isOneWayPlatform` to generate one-way platform rects:

```csharp
var platforms = tilemap.GenerateOneWayPlatformRects("Collision");
var mergedPlatforms = tilemap.MergeOneWayPlatformRects("Collision");
```

!!! note
    A tile can be both `solid` and `isOneWayPlatform` — they're checked independently. Typically you'd use them on separate tiles.

---

## Object Layers

Objects placed in Tiled object groups are loaded into `tilemap.ObjectLayers`, keyed by layer name.

### Querying objects

```csharp
// All objects in a layer:
var triggers = tilemap.GetObjects("Triggers");

// First object with a given name:
var spawnPoint = tilemap.GetObject("Objects", "PlayerSpawn");

// By unique ID (Tiled assigns a unique ID per object per map):
var boss = tilemap.GetObjectById(14);

// By type/class (set in Tiled's object properties):
var enemies = tilemap.GetObjectsByType("Enemy");
```

### Object properties

```csharp
// Read a custom property from an object:
var obj = tilemap.GetObject("Objects", "Chest");
if (obj != null)
{
    string lootTable = obj.CustomProperties.Get<string>("loot_table", "default");
    int gold = obj.CustomProperties.Get<int>("gold", 0);
}
```

### Object shapes

The `Shape` property tells you what kind of object it is:

| `TilemapObjectShape` | Description |
|----------------------|-------------|
| `Rectangle` | Default shape — `X`, `Y`, `Width`, `Height` |
| `Ellipse` | Ellipse — same bounds as rectangle |
| `Point` | Zero-size point — just `X`, `Y` |
| `Polygon` | Closed polygon — `Points` list (relative to `X`/`Y`) |
| `Polyline` | Open line — `Points` list (relative to `X`/`Y`) |
| `Tile` | Tile stamp — has a `Gid` and flip flags |
| `Text` | Text label — `TextContent` string |

```csharp
var obj = tilemap.GetObject("Objects", "Patrol");
if (obj.Shape == TilemapObjectShape.Polygon && obj.Points != null)
{
    foreach (var (px, py) in obj.Points)
    {
        // Points are relative to obj.X / obj.Y
        var worldX = obj.X + px;
        var worldY = obj.Y + py;
    }
}
```

---

## Coordinate Conversion

### World to tile

```csharp
// Basic conversion (no layer offset or parallax):
var (tx, ty) = tilemap.WorldToTile(player.X, player.Y);

// With layer offset:
var (tx, ty) = tilemap.WorldToTile(player.X, player.Y, layer);

// With layer offset and parallax (exact inverse of what the renderer draws):
var (tx, ty) = tilemap.WorldToTile(player.X, player.Y, layer, camera.Position);
```

### Tile to world

```csharp
// Basic (top-left corner of tile in world space):
var (wx, wy) = tilemap.TileToWorld(tx, ty);

// With layer offset:
var (wx, wy) = tilemap.TileToWorld(tx, ty, layer);

// With layer offset and parallax:
var (wx, wy) = tilemap.TileToWorld(tx, ty, layer, camera.Position);
```

!!! note "Use the parallax overload for parallax layers"
    For layers with a parallax factor other than 1.0, use the camera overload. The basic and layer overloads don't account for parallax and will give wrong results for those layers.

---

## Custom Properties on Maps and Layers

Custom properties aren't limited to tiles and objects. Maps and layers have them too.

```csharp
// Map-level property:
string levelName = tilemap.Properties.Get<string>("level_name", "Unknown");

// Tile layer property:
var layer = tilemap.GetLayer("Ground");
bool hasIce = layer?.Properties.Get<bool>("icy", false) ?? false;

// Object layer property:
if (tilemap.ObjectLayerProperties.TryGetValue("Triggers", out var layerProps))
{
    string zone = layerProps.Get<string>("zone", "");
}
```

### Typed property helpers

`Dictionary<string, string>.Get<T>` and `TryGet<T>` are extension methods from `TilemapPropertyExtensions`. They handle parsing and return a default if the key is missing or unparseable:

| Type | Notes |
|------|-------|
| `string` | Returned as-is |
| `int` | Parsed with `InvariantCulture` |
| `float` | Parsed with `InvariantCulture` |
| `double` | Parsed with `InvariantCulture` |
| `bool` | `true`/`false` strings, or `1`/`0` |

For color properties, use the `GetColor` extension:

```csharp
Color fogColor = tilemap.Properties.GetColor("fog_color", Color.Transparent);
```

Color strings must be in Tiled's format: `#RRGGBB` or `#AARRGGBB`.

---

## Related Topics

- [Loading Tilemaps](loading.md) — load the map data
- [Rendering](rendering.md) — ECS rendering, parallax, image layers
- [Collision Detection](../collision/index.md) — pass collision rects to the physics system
