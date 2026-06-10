---
title: Tilemaps
description: Load and render Tiled tilemaps in Brine2D
---

# Tilemaps

Brine2D's tilemap system is built around [Tiled Map Editor](https://www.mapeditor.org/). You author levels in Tiled, export as JSON (`.tmj`), and load them at runtime. The ECS integration handles async texture loading, tile animation, and rendering automatically.

---

## Quick Start

**1. Register services** (once, in your game builder):

```csharp
builder.Services.AddTilemapServices();
```

**2. Load the map** in `OnLoadAsync`:

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

**3. Add the system** to your world:

```csharp
protected override void OnEnter()
{
    World.AddSystem<TilemapSystem>();
}
```

That's it. `TilemapSystem` loads textures asynchronously and renders all `TilemapComponent` entities every frame.

---

## What's Supported

| Feature | Notes |
|---------|-------|
| Map format | Tiled JSON (`.tmj`) — orthogonal, fixed-size only |
| Tilesets | Embedded or external (`.tsj`); single-image only |
| Tile data | CSV, base64 (uncompressed, zlib, gzip, zstd) |
| Layer types | Tile layers, object groups, image layers, group layers |
| Group layers | Flattened automatically; visibility/opacity/tint/offset/parallax inherited |
| Tile animation | Matches Tiled's per-GID shared clock |
| Tile flipping | Horizontal, vertical, diagonal (all Tiled combinations) |
| Parallax | Per-layer X/Y multiplier, fully accounted for in rendering and coord conversion |
| Collision | Solid and one-way platform rect generation with greedy merge |
| Coordinate conversion | World to tile with layer offset and parallax overloads |
| Custom properties | Maps, layers, tilesets, tiles, and objects |
| Multiple tilesets | Full GID resolution across any number of tilesets |

!!! warning "Unsupported map types"
    Isometric, hexagonal, and infinite maps will throw `NotSupportedException` at load time.
    Only `right-down` tile render order is supported (the Tiled default).

---

## Topics

| Guide | Description |
|-------|-------------|
| [Loading Tilemaps](loading.md) | Register the loader, load `.tmj` files, understand what Tiled settings are required |
| [Rendering](rendering.md) | How `TilemapSystem` renders, image layers, parallax, `PositionOffset` |
| [Collision & Objects](collision-and-objects.md) | Collision rect generation, object queries, coordinate conversion, custom properties |

---

## Tiled Workflow

### Recommended layer setup

| Layer name | Type | Purpose |
|------------|------|---------|
| `Background` | Tile layer | Static background tiles |
| `Ground` | Tile layer | Main terrain |
| `Decoration` | Tile layer | Non-colliding decor |
| `Collision` | Tile layer | Solid/one-way tiles (can be hidden in Tiled) |
| `Objects` | Object group | Spawn points, triggers, item locations |
| `Foreground` | Tile layer | Tiles drawn in front of the player |

### Export settings

1. **File → Export As → JSON map files (\*.tmj)**
2. Orientation must be **Orthogonal**
3. **Tile render order**: leave as default (`right-down`)
4. Uncheck **Infinite map** — only fixed-size maps load

### External tilesets

If you use an external tileset (`.tsj`), it must be present at the path Tiled recorded, relative to the `.tmj`. Brine2D resolves paths relative to the map file at load time.

---

## Related Topics

- [Rendering](rendering.md) — `TilemapSystem`, image layers, parallax
- [Collision & Objects](collision-and-objects.md) — collision rects, object queries, coordinate conversion
- [ECS: Systems](../ecs/systems.md) — how systems are registered and ordered
- [Tutorials: Platformer](../tutorials/platformer.md) — end-to-end tilemap example
