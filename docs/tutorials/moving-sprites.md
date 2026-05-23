---
title: Moving Sprites Tutorial
description: Learn to load textures, draw sprites, and create smooth movement in Brine2D
---

# Moving Sprites

**Difficulty:** Beginner | **Time:** 15 minutes

In this tutorial, you'll learn the fundamentals of rendering and moving sprites in Brine2D.

## What You'll Build

A simple game scene with:

- A sprite loaded from an image file
- Smooth keyboard-controlled movement
- Frame-rate independent motion using delta time
- Proper boundary checking

## Prerequisites

- Completed [Quick Start](../getting-started/quickstart.md)
- A sprite image file at `assets/images/player.png`

---

## Step 1: Create the Scene

Create `MovingSpriteScene.cs`:

```csharp
using System.Numerics;
using Brine2D.Assets;
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Input;
using Brine2D.Rendering;

namespace MyGame;

public class MovingSpriteScene : Scene
{
    private readonly IAssetLoader _assets;

    private ITexture? _playerTexture;
    private Vector2 _playerPosition = new(400, 300);
    private const float Speed = 200f; // pixels per second

    public MovingSpriteScene(IAssetLoader assets)
    {
        _assets = assets;
    }
}
```

**What's happening:**

- We inject `IAssetLoader` - the unified service for loading textures, sounds, fonts, and music
- Framework properties (`Input`, `Renderer`, `Logger`, `World`, `Audio`, `Game`) are set automatically - no constructor injection needed for those

---

## Step 2: Load the Sprite

Override `OnLoadAsync` to load your texture:

```csharp
protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
{
    Logger.LogInformation("Loading player sprite...");

    _playerTexture = await _assets.GetOrLoadTextureAsync(
        "assets/images/player.png",
        TextureScaleMode.Nearest,  // Sharp scaling for pixel art
        ct);

    Logger.LogInformation("Sprite loaded: {W}x{H}",
        _playerTexture.Width, _playerTexture.Height);
}
```

**Key points:**

- `GetOrLoadTextureAsync` loads and caches the texture - subsequent calls return the cached version
- `TextureScaleMode.Nearest` keeps pixel art sharp when scaled
- Always pass the `CancellationToken`

---

## Step 3: Draw the Sprite

Override `OnRender` to draw the texture:

```csharp
protected override void OnRender(GameTime gameTime)
{
    if (_playerTexture != null)
    {
        Renderer.DrawTexture(_playerTexture, _playerPosition.X, _playerPosition.Y);
    }
}
```

**Note:** Frame management (clear, begin, end) is automatic - just draw.

---

## Step 4: Add Movement

Override `OnUpdate` to handle keyboard input:

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    var deltaTime = (float)gameTime.DeltaTime;

    // Calculate movement direction
    var movement = Vector2.Zero;
    if (Input.IsKeyDown(Key.Left) || Input.IsKeyDown(Key.A))  movement.X -= 1;
    if (Input.IsKeyDown(Key.Right) || Input.IsKeyDown(Key.D)) movement.X += 1;
    if (Input.IsKeyDown(Key.Up) || Input.IsKeyDown(Key.W))    movement.Y -= 1;
    if (Input.IsKeyDown(Key.Down) || Input.IsKeyDown(Key.S))  movement.Y += 1;

    // Normalize to prevent faster diagonal movement
    if (movement != Vector2.Zero)
    {
        movement = Vector2.Normalize(movement);
        _playerPosition += movement * Speed * deltaTime;
    }

    // Keep player on screen
    var spriteWidth = _playerTexture?.Width ?? 32;
    var spriteHeight = _playerTexture?.Height ?? 32;
    _playerPosition.X = Math.Clamp(_playerPosition.X, 0, Renderer.Width - spriteWidth);
    _playerPosition.Y = Math.Clamp(_playerPosition.Y, 0, Renderer.Height - spriteHeight);
}
```

**Key points:**

- `IsKeyDown` returns `true` every frame the key is held - perfect for movement
- Multiplying by `deltaTime` makes movement frame-rate independent (same speed at 30fps and 144fps)
- `Vector2.Normalize` prevents diagonal movement from being 41% faster

---

## Step 5: Register and Run

In `Program.cs`:

```csharp
using Brine2D.Hosting;
using MyGame;

var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "Moving Sprites Tutorial";
    options.Window.Width = 1280;
    options.Window.Height = 720;
});

builder.AddScene<MovingSpriteScene>();

await using var game = builder.Build();
await game.RunAsync<MovingSpriteScene>();
```

---

## Complete Code

```csharp
using System.Numerics;
using Brine2D.Assets;
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Input;
using Brine2D.Rendering;

namespace MyGame;

public class MovingSpriteScene : Scene
{
    private readonly IAssetLoader _assets;

    private ITexture? _playerTexture;
    private Vector2 _playerPosition = new(400, 300);
    private const float Speed = 200f;

    public MovingSpriteScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        _playerTexture = await _assets.GetOrLoadTextureAsync(
            "assets/images/player.png",
            TextureScaleMode.Nearest,
            ct);
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        var deltaTime = (float)gameTime.DeltaTime;

        var movement = Vector2.Zero;
        if (Input.IsKeyDown(Key.Left) || Input.IsKeyDown(Key.A))  movement.X -= 1;
        if (Input.IsKeyDown(Key.Right) || Input.IsKeyDown(Key.D)) movement.X += 1;
        if (Input.IsKeyDown(Key.Up) || Input.IsKeyDown(Key.W))    movement.Y -= 1;
        if (Input.IsKeyDown(Key.Down) || Input.IsKeyDown(Key.S))  movement.Y += 1;

        if (movement != Vector2.Zero)
        {
            movement = Vector2.Normalize(movement);
            _playerPosition += movement * Speed * deltaTime;
        }

        _playerPosition.X = Math.Clamp(_playerPosition.X, 0, Renderer.Width - (_playerTexture?.Width ?? 32));
        _playerPosition.Y = Math.Clamp(_playerPosition.Y, 0, Renderer.Height - (_playerTexture?.Height ?? 32));
    }

    protected override void OnRender(GameTime gameTime)
    {
        if (_playerTexture != null)
        {
            Renderer.DrawTexture(_playerTexture, _playerPosition.X, _playerPosition.Y);
        }
    }
}
```

---

## Challenges

### Easy

1. **Change the speed** - make the sprite faster or slower
2. **Different keys** - add gamepad support with `Input.GetGamepadLeftStick()`
3. **Background color** - set `Renderer.ClearColor` in `OnEnter`

### Medium

4. **Multiple sprites** - load and move 2-3 sprites independently
5. **Wrap-around** - when the sprite leaves one edge, appear on the opposite
6. **Speed boost** - hold Shift to move 2x faster

### Hard

7. **Smooth acceleration** - gradually speed up and slow down
8. **Mouse follow** - move toward the mouse with `Input.MousePosition`
9. **Rotation** - rotate the sprite to face the direction of movement

---

## What You Learned

:white_check_mark: **Loading textures** with `IAssetLoader.GetOrLoadTextureAsync()`
:white_check_mark: **Drawing sprites** with `Renderer.DrawTexture()`
:white_check_mark: **Keyboard input** with `Input.IsKeyDown()`
:white_check_mark: **Delta time** for frame-rate independent movement
:white_check_mark: **Vector math** with `Vector2.Normalize()`
:white_check_mark: **Boundary checking** with `Math.Clamp()`
:white_check_mark: **Scene lifecycle** - Load, Update, Render

---

## Next Steps

- **[Animation System](animations.md)** - Animate your sprite with sprite sheets
- **[Keyboard Guide](../input/keyboard.md)** - Master all keyboard input
- **[First Game](../getting-started/first-game.md)** - Build a complete game