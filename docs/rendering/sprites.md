---
title: Sprites & Textures
description: Load and draw sprites and textures in Brine2D
---

# Sprites & Textures

Load textures with `IAssetLoader` and draw them with the `Renderer` framework property.

---

## Quick Start

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;
    private ITexture? _playerTexture;

    public GameScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        _playerTexture = await _assets.GetOrLoadTextureAsync(
            "assets/images/player.png",
            cancellationToken: ct);
    }

    protected override void OnRender(GameTime gameTime)
    {
        if (_playerTexture != null)
        {
            Renderer.DrawTexture(_playerTexture, 100, 100);
        }
    }
}
```

---

## Loading Textures

```csharp
// Basic load
var texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);

// Pixel art - use Nearest filtering for sharp scaling
var pixelArt = await _assets.GetOrLoadTextureAsync(
    "assets/images/player.png",
    TextureScaleMode.Nearest,
    ct);

// Smooth graphics - use Linear filtering (default)
var smooth = await _assets.GetOrLoadTextureAsync(
    "assets/images/background.png",
    TextureScaleMode.Linear,
    ct);
```

---

## Drawing

```csharp
// Draw at position (top-left)
Renderer.DrawTexture(texture, 100f, 200f);

// Draw at position (Vector2)
Renderer.DrawTexture(texture, new Vector2(100, 200));

// Draw with explicit size
Renderer.DrawTexture(texture, 100f, 200f, 64f, 64f);

// Full control - position, source rect, origin, rotation, scale, color, flip
Renderer.DrawTexture(
    texture,
    position: new Vector2(400, 300),
    sourceRect: new Rectangle(0, 0, 32, 32),  // Sprite sheet region
    origin: new Vector2(16, 16),               // Center pivot
    rotation: MathF.PI / 4,                    // 45 degrees
    scale: new Vector2(2f, 2f),                // 2x size
    color: Color.White,
    flip: SpriteFlip.None);
```

---

## Sprite Sheets

```csharp
// Draw a specific frame from a sprite sheet
var frameWidth = 32;
var frameHeight = 32;
var column = _currentFrame % _columns;
var row = _currentFrame / _columns;

Renderer.DrawTexture(
    _spriteSheet,
    position: _position,
    sourceRect: new Rectangle(column * frameWidth, row * frameHeight, frameWidth, frameHeight),
    origin: new Vector2(frameWidth / 2f, frameHeight / 2f),
    scale: new Vector2(4f, 4f));  // Scale up pixel art
```

---

## Asset Manifest (Recommended)

For multiple textures, use an `AssetManifest` for parallel loading:

```csharp
public class LevelAssets : AssetManifest
{
    public readonly AssetRef<ITexture> Player     = Texture("assets/images/player.png", TextureScaleMode.Nearest);
    public readonly AssetRef<ITexture> Background = Texture("assets/images/background.png");
    public readonly AssetRef<ITexture> Tileset    = Texture("assets/images/tileset.png", TextureScaleMode.Nearest);
}

public class GameScene : Scene
{
    private readonly IAssetLoader _assets;
    private readonly LevelAssets _manifest = new();

    public GameScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        await _assets.PreloadAsync(_manifest, cancellationToken: ct);
    }

    protected override void OnRender(GameTime gameTime)
    {
        // Implicit conversion from AssetRef<ITexture> to ITexture
        Renderer.DrawTexture(_manifest.Background, 0, 0);
        Renderer.DrawTexture(_manifest.Player, _playerPos.X, _playerPos.Y);
    }
}
```

---

## Scale Modes

| Mode | Use For | Result |
|------|---------|--------|
| `TextureScaleMode.Nearest` | Pixel art | Sharp, blocky scaling |
| `TextureScaleMode.Linear` | Smooth graphics | Blurred, smooth scaling |

---

## Best Practices

1. **Load in `OnLoadAsync`** - never in `OnRender` or `OnUpdate`
2. **Use `Nearest` for pixel art** - `Linear` will make it blurry
3. **Use relative paths** - `"assets/images/player.png"`, not absolute paths
4. **Use `AssetManifest`** for multiple assets - parallel loading
5. **Batch by texture** - draw all sprites using the same texture together

```csharp
// âœ… Good - all enemies share one texture
foreach (var enemy in _enemies)
{
    Renderer.DrawTexture(_enemyTexture, enemy.Position);
}
```

---

## Troubleshooting

### Texture is null

- Verify the file path is correct (relative to project root)
- Check that `assets/` folder is copied to output in `.csproj`
- Ensure `OnLoadAsync` completed before accessing the texture

### Nothing renders (black screen)

1. Is `OnRender` being called?
2. Is the texture loaded (not null)?
3. Are coordinates on screen? (Try `0, 0`)

### Sprite is blurry

Use `TextureScaleMode.Nearest` for pixel art:

```csharp
await _assets.GetOrLoadTextureAsync("assets/images/player.png", TextureScaleMode.Nearest, ct);
```

---

## Next Steps

- **[Cameras](cameras.md)** - Camera movement and zoom
- **[Drawing Primitives](primitives.md)** - Lines, rectangles, circles
- **[Texture Atlasing](texture-atlasing.md)** - Runtime sprite packing