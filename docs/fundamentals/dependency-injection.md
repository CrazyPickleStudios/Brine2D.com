---
title: Dependency Injection
description: How Brine2D uses Microsoft's DI container - scoped scenes, framework properties, and custom services
---

# Dependency Injection

Brine2D is built on Microsoft's DI container, bringing the same patterns you know from ASP.NET Core to game development. Services are scoped per scene, framework properties are injected automatically, and your custom services integrate naturally.

---

## How Brine2D Uses DI

### Framework Properties (Automatic)

Six services are injected into every scene automatically - you don't register or inject them:

```csharp
public class GameScene : Scene
{
    protected override void OnUpdate(GameTime gameTime)
    {
        // All available as properties - no constructor injection needed
        Logger.LogDebug("Frame {Frame}", Game.GameTime.FrameCount);
        if (Input.IsKeyPressed(Key.Escape)) Game.RequestExit();
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Hello", 10, 10, Color.White);
    }

    protected override void OnEnter()
    {
        Audio.PlayMusic(_theme);
        var player = World.CreateEntity("Player");
    }
}
```

These are set by `SceneManager` before `OnLoadAsync` - they are NOT available in the constructor.

### Constructor Injection (Your Services)

Inject your own services via the constructor, just like ASP.NET:

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;
    private readonly ISceneManager _sceneManager;
    private readonly GameState _gameState;

    public GameScene(
        IAssetLoader assets,
        ISceneManager sceneManager,
        GameState gameState)
    {
        _assets = assets;
        _sceneManager = sceneManager;
        _gameState = gameState;
    }
}
```

---

## Service Lifetimes in Brine2D

| Lifetime | .NET Equivalent | Brine2D Behavior | Example |
|----------|----------------|------------------|---------|
| **Singleton** | One per app | Shared across all scenes | `GameState`, `EventBus` |
| **Scoped** | One per scope | One per scene - destroyed on scene unload | `IAssetLoader`, `IEntityWorld` |
| **Transient** | Always new | New instance each time resolved | Lightweight services |

### Scoped = Per Scene

This is the key difference from generic .NET DI. In ASP.NET, scoped services live per HTTP request. In Brine2D, **scoped services live per scene**:

```csharp
// IAssetLoader is scoped - each scene gets its own instance
// When the scene unloads, its IAssetLoader releases all loaded assets
public class GameScene : Scene
{
    private readonly IAssetLoader _assets; // Fresh instance per scene

    public GameScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        // Assets loaded here are tracked by this scene's IAssetLoader
        _texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
    }

    // When scene unloads: _assets releases all tracked assets automatically
}
```

`IEntityWorld` (the `World` property) is also scoped - each scene gets an isolated world that's destroyed on unload.

---

## Registering Services

### In Program.cs

```csharp
var builder = GameApplication.CreateBuilder(args);

// Singleton - shared across all scenes
builder.Services.AddSingleton<GameState>();
builder.Services.AddSingleton<IEnemyFactory, EnemyFactory>();

// Scoped - one per scene, destroyed on unload
builder.Services.AddScoped<ILevelManager, LevelManager>();

// Transient - new instance each time
builder.Services.AddTransient<IParticleEmitter, ParticleEmitter>();

// Scenes
builder.AddScene<MenuScene>();
builder.AddScene<GameScene>();
```

### Extension Method Pattern

```csharp
public static class MyGameExtensions
{
    public static IServiceCollection AddMyGameSystems(this IServiceCollection services)
    {
        services.AddSingleton<IEnemyFactory, EnemyFactory>();
        services.AddScoped<ILevelManager, LevelManager>();
        return services;
    }
}

// Usage
builder.Services.AddMyGameSystems();
```

---

## Behavior and DI

`Behavior` supports constructor injection - behaviors are resolved from DI:

```csharp
public class PlayerMovementBehavior : Behavior
{
    private readonly IInputContext _input;

    // Inject services that aren't available as framework properties
    public PlayerMovementBehavior(IInputContext input)
    {
        _input = input;
    }

    protected override void Update(GameTime gameTime)
    {
        if (_input.IsKeyDown(Key.W))
        {
            var transform = Entity.GetRequiredComponent<TransformComponent>();
            transform.Position += new Vector2(0, -200f * (float)gameTime.DeltaTime);
        }
    }
}

// Add to entity
var player = World.CreateEntity("Player");
player.AddBehavior<PlayerMovementBehavior>(); // DI resolves IInputContext automatically
```

---

## Options Pattern

Configure services with `IOptions<T>`, just like ASP.NET:

```csharp
builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1280;
    options.Window.Height = 720;
    options.Rendering.VSync = true;
});
```

---

## Best Practices

### :white_check_mark: DO

1. **Use framework properties** for Logger, Renderer, Input, Audio, Game, World
2. **Constructor-inject your services** - `IAssetLoader`, `ISceneManager`, your custom services
3. **Use scoped for scene-specific state** - prevents leaks between scenes
4. **Use singletons for shared state** - `GameState`, `EventBus`
5. **Store dependencies in readonly fields**

### :x: DON'T

1. **Don't inject `IServiceProvider`** - inject specific services
2. **Don't create services manually** - `new SDL3Renderer()` defeats DI
3. **Don't make everything singleton** - causes memory leaks across scenes
4. **Don't store entity references in singletons** - entities are scoped to scenes

---

## Troubleshooting

### "Service not found" Error

Make sure you registered the service in `Program.cs`:

```csharp
builder.Services.AddSingleton<GameState>(); // Don't forget!
```

### State persists between scenes

Change from Singleton to Scoped:

```csharp
builder.Services.AddSingleton<CollisionSystem>(); // âŒ Persists forever
builder.Services.AddScoped<CollisionSystem>();     // âœ… Fresh per scene
```

---

## Summary

| Concept | Brine2D Pattern |
|---------|----------------|
| **Framework services** | `Logger`, `Renderer`, `Input`, `Audio`, `Game`, `World` - automatic properties |
| **Your services** | Constructor injection: `IAssetLoader`, `ISceneManager`, custom services |
| **Per-scene state** | Scoped lifetime - `IAssetLoader`, `IEntityWorld` |
| **Shared state** | Singleton - `GameState`, `EventBus` |
| **Configuration** | `builder.Configure(options => ...)` |

---

## Next Steps

- **[Builder Pattern](builder-pattern.md)** - `GameApplicationBuilder` API
- **[Scenes](scenes.md)** - Scene lifecycle and scoping
- **[ECS](entity-component-system.md)** - Entity Component System