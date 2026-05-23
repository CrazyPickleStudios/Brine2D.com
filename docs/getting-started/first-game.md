---
title: Your First Game
description: Build a complete game with sprites, audio, collision detection, and scoring
---

# Your First Game

Build a complete game from scratch in 30 minutes. You'll create an asteroid dodging game with sprites, audio, collision detection, and scoring.

You'll build **Asteroid Dodge** — a spaceship game where you dodge incoming asteroids, collect power-ups, and track a high score. It covers sprite loading, player input, collision, audio, and cross-scene state.

---

## Prerequisites

Before starting:

- :white_check_mark: Completed [Quick Start](quickstart.md)
- :white_check_mark: Basic C# knowledge
- :white_check_mark: 30 minutes

---

## Step 1: Project Setup

Create a new project:

```sh
dotnet new console -n AsteroidDodge
cd AsteroidDodge
dotnet add package Brine2D
```

Create folder structure:

```sh
mkdir assets
mkdir assets/images
mkdir assets/audio
```

**Download assets** (or create your own):
- `player.png` - 32x32 spaceship sprite
- `asteroid.png` - 32x32 asteroid sprite
- `powerup.png` - 32x32 star sprite
- `explosion.wav` - Collision sound effect
- `collect.wav` - Power-up collection sound

---

## Step 2: Program Setup

Replace `Program.cs`:

```csharp
using Brine2D.Hosting;

var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "Asteroid Dodge";
    options.Window.Width = 800;
    options.Window.Height = 600;
});

builder.Services.AddSingleton<GameState>();
builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

---

## Step 3: Game State Service

Create `GameState.cs` - a **singleton service** for persistent data:

```csharp
public class GameState
{
    public int Score { get; set; }
    public int HighScore { get; set; }
    public bool IsGameOver { get; set; }

    public void Reset()
    {
        Score = 0;
        IsGameOver = false;
    }

    public void AddScore(int points)
    {
        Score += points;
        if (Score > HighScore)
        {
            HighScore = Score;
        }
    }
}
```

**Why singleton?** The game state persists across scenes (menu -> game -> game over), so it needs to survive scene changes.

---

## Step 4: Game Scene

Create `GameScene.cs`:

```csharp
using System.Numerics;
using Brine2D.Assets;
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Components;
using Brine2D.Engine;
using Brine2D.Input;
using Brine2D.Audio;
using Brine2D.Rendering;

public class GameScene : Scene
{
    private readonly IAssetLoader _assets;
    private readonly GameState _gameState;

    private Entity? _player;
    private readonly List<Entity> _asteroids = new();
    private readonly List<Entity> _powerups = new();

    private ITexture? _playerTexture;
    private ITexture? _asteroidTexture;
    private ITexture? _powerupTexture;

    private ISoundEffect? _explosionSound;
    private ISoundEffect? _collectSound;

    private readonly Random _random = new();
    private float _spawnTimer;
    private const float SpawnInterval = 1.5f;

    public GameScene(IAssetLoader assets, GameState gameState)
    {
        _assets = assets;
        _gameState = gameState;
    }

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        _gameState.Reset();

        _playerTexture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
        _asteroidTexture = await _assets.GetOrLoadTextureAsync("assets/images/asteroid.png", cancellationToken: ct);
        _powerupTexture = await _assets.GetOrLoadTextureAsync("assets/images/powerup.png", cancellationToken: ct);

        _explosionSound = await _assets.GetOrLoadSoundAsync("assets/audio/explosion.wav", ct);
        _collectSound = await _assets.GetOrLoadSoundAsync("assets/audio/collect.wav", ct);

        Logger.LogInformation("Assets loaded");
    }

    protected override void OnEnter()
    {
        CreatePlayer();
    }

    private void CreatePlayer()
    {
        _player = World.CreateEntity("Player");

        var transform = _player.AddComponent<TransformComponent>();
        transform.Position = new Vector2(400, 300);

        var sprite = _player.AddComponent<SpriteComponent>();
        sprite.Texture = _playerTexture;
        sprite.Width = 32;
        sprite.Height = 32;

        _player.AddTag("Player");
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (_gameState.IsGameOver)
        {
            if (Input.IsKeyPressed(Key.R))
            {
                _gameState.Reset();
                RestartGame();
            }
            return;
        }

        var deltaTime = (float)gameTime.DeltaTime;

        UpdatePlayer(deltaTime);
        UpdateAsteroids(deltaTime);
        UpdatePowerups(deltaTime);
        UpdateSpawning(deltaTime);
        CheckCollisions();
    }

    private void UpdatePlayer(float deltaTime)
    {
        if (_player == null) return;

        var transform = _player.GetComponent<TransformComponent>();
        if (transform == null) return;

        const float speed = 300f;
        var movement = Vector2.Zero;

        if (Input.IsKeyDown(Key.W) || Input.IsKeyDown(Key.Up))    movement.Y -= 1;
        if (Input.IsKeyDown(Key.S) || Input.IsKeyDown(Key.Down))  movement.Y += 1;
        if (Input.IsKeyDown(Key.A) || Input.IsKeyDown(Key.Left))  movement.X -= 1;
        if (Input.IsKeyDown(Key.D) || Input.IsKeyDown(Key.Right)) movement.X += 1;

        if (movement != Vector2.Zero)
        {
            movement = Vector2.Normalize(movement);
            transform.Position += movement * speed * deltaTime;
        }

        transform.Position = new Vector2(
            Math.Clamp(transform.Position.X, 16, Renderer.Width - 16),
            Math.Clamp(transform.Position.Y, 16, Renderer.Height - 16));
    }

    // ... UpdateAsteroids, UpdatePowerups, UpdateSpawning, CheckCollisions ...

    protected override void OnRender(GameTime gameTime)
    {
        if (_gameState.IsGameOver)
        {
            Renderer.DrawText("GAME OVER", Renderer.Width / 2 - 50, Renderer.Height / 2, Color.Red);
            Renderer.DrawText($"Score: {_gameState.Score}", Renderer.Width / 2 - 40, Renderer.Height / 2 + 30, Color.White);
            Renderer.DrawText("Press R to Restart", Renderer.Width / 2 - 60, Renderer.Height / 2 + 60, Color.Gray);
            return;
        }

        Renderer.DrawText($"Score: {_gameState.Score}", 10, 10, Color.White);
        Renderer.DrawText($"High Score: {_gameState.HighScore}", 10, 35, Color.Gold);
    }

    private void RestartGame()
    {
        foreach (var asteroid in _asteroids)
            World.DestroyEntity(asteroid);
        _asteroids.Clear();

        foreach (var powerup in _powerups)
            World.DestroyEntity(powerup);
        _powerups.Clear();

        if (_player != null)
            World.DestroyEntity(_player);

        CreatePlayer();
    }
}
```

---

## Key Takeaways

### 1. Framework Properties

```csharp
public GameScene(IAssetLoader assets, GameState gameState)
{
    _assets = assets;
    _gameState = gameState;
}

protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
{
    Logger.LogInformation("Loading");
    _texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
}

protected override void OnUpdate(GameTime gameTime)
{
    if (Input.IsKeyPressed(Key.Escape)) { }
}

protected override void OnRender(GameTime gameTime)
{
    Renderer.DrawText("Hello", 10, 10, Color.White);
}
```

### 2. Scoped World

```csharp
// World is scoped per scene - automatic cleanup!
protected override Task OnUnloadAsync(CancellationToken ct)
{
    // All entities destroyed automatically when the scene unloads
    return Task.CompletedTask;
}
```

### 3. Persistent Data

```csharp
// Use singleton service for data that survives scene changes
builder.Services.AddSingleton<GameState>();
```

### 4. Asset Loading

```csharp
// Load assets in OnLoadAsync via IAssetLoader
protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
{
    _texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
    _sound = await _assets.GetOrLoadSoundAsync("assets/audio/jump.wav", ct);
    _font = await _assets.GetOrLoadFontAsync("assets/fonts/ui.ttf", size: 16, cancellationToken: ct);
}
```

---

## Troubleshooting

### Problem: NullReferenceException when accessing World in constructor

**Cause:** Framework properties not set yet during construction.

**Solution:**

```csharp
// âŒ Wrong - World is null in constructor!
public GameScene()
{
    var player = World.CreateEntity("Player"); // Throws!
}

// âœ… Correct - Use OnEnter or OnLoadAsync
protected override void OnEnter()
{
    var player = World.CreateEntity("Player"); // Works!
}
```

---

### Problem: Entities from previous game still visible after restart

**Solution:**

```csharp
private void RestartGame()
{
    foreach (var asteroid in _asteroids.ToList())
        World.DestroyEntity(asteroid);
    _asteroids.Clear();

    if (_player != null)
        World.DestroyEntity(_player);

    CreatePlayer();
}
```

---

## Next Steps

Now that you've built a complete game, explore more features:

- **[Project Structure](project-structure.md)** - Organize larger projects
- **[Scenes](../scenes/index.md)** - Scene lifecycle and transitions
- **[Rendering](../rendering/sprites.md)** - Sprites and textures
- **[Input](../input/keyboard.md)** - Keyboard, mouse, and gamepad

---

**Congratulations!** You've built a complete game with Brine2D. You now understand:
- Framework property pattern
- Scoped EntityWorld
- Asset loading via `IAssetLoader`
- Persistent data management
- Collision detection
- Game state management
