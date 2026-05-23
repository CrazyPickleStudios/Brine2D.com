---
title: Quick Start
description: Create your first Brine2D game in 5 minutes - from zero to a running window
---

# Quick Start

Get a Brine2D game running in 5 minutes. This guide takes you from zero to a window with a moving sprite.

## Prerequisites

Before starting:

- :white_check_mark: [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0) installed
- :white_check_mark: IDE ready (Visual Studio 2022+, VS Code, or Rider)
- :white_check_mark: 5 minutes

**New to Brine2D?** Perfect! This guide assumes no prior knowledge.

**Already have a project?** Skip to [Add to Existing Project](#add-to-existing-project).

---

## Step 1: Create Project

Open your terminal and create a new console application:

```sh
dotnet new console -n MyFirstGame
cd MyFirstGame
```

**What this does:**
- Creates a new .NET 10 console application
- Names it `MyFirstGame`
- Changes to the project directory

---

## Step 2: Install Brine2D

Add the Brine2D package:

```sh
dotnet add package Brine2D
```

**What this does:**
- Installs **Brine2D** (core engine, rendering, input, audio - everything you need)

**Verify installation:**

```sh
dotnet list package
```

You should see:

```
Top-level Package    Requested    Resolved
> Brine2D            x.x.x        x.x.x
```

---

## Step 3: Create Your First Scene

Replace the contents of `Program.cs` with:

```csharp
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Hosting;
using Brine2D.Input;
using System.Numerics;

var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "My First Game";
    options.Window.Width = 800;
    options.Window.Height = 600;
});

builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();

public class GameScene : Scene
{
    private readonly IGameContext _gameContext;

    private Vector2 _playerPosition = new(400, 300);
    private readonly float _speed = 200f;

    public GameScene(IGameContext gameContext)
    {
        _gameContext = gameContext;
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyPressed(Key.Escape))
        {
            _gameContext.RequestExit();
        }

        var deltaTime = (float)gameTime.DeltaTime;

        if (Input.IsKeyDown(Key.W)) _playerPosition.Y -= _speed * deltaTime;
        if (Input.IsKeyDown(Key.S)) _playerPosition.Y += _speed * deltaTime;
        if (Input.IsKeyDown(Key.A)) _playerPosition.X -= _speed * deltaTime;
        if (Input.IsKeyDown(Key.D)) _playerPosition.X += _speed * deltaTime;
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawRectangleFilled(
            _playerPosition.X - 25,
            _playerPosition.Y - 25,
            50, 50,
            Color.Blue);

        Renderer.DrawText("WASD: Move | ESC: Quit", 10, 10, Color.White);
    }
}
```

**Notice the pattern:**
- Constructor only has **YOUR dependencies** (`IGameContext`)
- `Logger`, `World`, `Renderer`, `Input`, `Audio`, `Game` are available automatically as framework properties
- No need to pass framework services through the constructor!

---

## Step 4: Run Your Game

Start your game:

```sh
dotnet run
```

**You should see:**
- A window titled "My First Game"
- A blue square in the center
- Instructions at the top
- The square moves with WASD keys
- Escape quits the game

**Success!** You've created your first Brine2D game.

---

## Understanding the Code

Let's break down what each part does:

### Application Setup

```csharp
var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "My First Game";
    options.Window.Width = 800;
    options.Window.Height = 600;
});

builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

**What this does:**
1. Creates a game application builder (like ASP.NET Core)
2. Configures window and engine options
3. Registers your game scene
4. Builds and runs the game

**Pattern:** This is dependency injection - Brine2D uses ASP.NET Core patterns.

---

### Scene Class

```csharp
public class GameScene : Scene
{
    private readonly IGameContext _gameContext;

    public GameScene(IGameContext gameContext)
    {
        _gameContext = gameContext;
    }

    protected override void OnRender(GameTime gameTime)
    {
        Logger.LogDebug("Rendering frame");
        var player = World.CreateEntity("Player");
        Renderer.DrawText("Hello", 10, 10, Color.White);
    }
}
```

**What's important:**
- **Constructor**: Only YOUR services (`IGameContext`, custom services, etc.)
- **Framework properties**: `Logger`, `World`, `Renderer`, `Input`, `Audio`, `Game` set automatically by the framework
- **Clean**: No need to inject `ILogger<T>`, `IEntityWorld`, `IRenderer`, `IInputContext` - they're all properties

---

### Framework Properties

These are **available in all lifecycle methods** (after constructor):

| Property | Type | Purpose |
|----------|------|---------|
| `Logger` | `ILogger` | Logging for this scene (typed automatically) |
| `World` | `IEntityWorld` | Entity world, scoped per scene — disposed automatically on scene unload |
| `Renderer` | `IRenderer` | Drawing + render state (clear color, camera, etc.) |
| `Input` | `IInputContext` | Keyboard, mouse, and gamepad input |
| `Audio` | `IAudioPlayer` | Play sounds and music |
| `Game` | `IGameContext` | Game context (request exit, game time) |

**You never inject these** - they're set by SceneManager before any lifecycle methods run.

---

### Update Loop

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    if (Input.IsKeyPressed(Key.Escape))
    {
        _gameContext.RequestExit();
    }

    var deltaTime = (float)gameTime.DeltaTime;

    if (Input.IsKeyDown(Key.W)) _playerPosition.Y -= _speed * deltaTime;
    if (Input.IsKeyDown(Key.S)) _playerPosition.Y += _speed * deltaTime;
    if (Input.IsKeyDown(Key.A)) _playerPosition.X -= _speed * deltaTime;
    if (Input.IsKeyDown(Key.D)) _playerPosition.X += _speed * deltaTime;
}
```

**What this does:**
- Called every frame (~60 times per second)
- Handles input via the `Input` framework property
- Updates game state (position, physics, AI)
- Uses `deltaTime` for frame-rate independent movement

---

### Render Loop

```csharp
protected override void OnRender(GameTime gameTime)
{
    Renderer.DrawRectangleFilled(
        _playerPosition.X - 25,
        _playerPosition.Y - 25,
        50, 50,
        Color.Blue);

    Renderer.DrawText("WASD: Move | ESC: Quit", 10, 10, Color.White);
}
```

**What this does:**
- Called every frame after update
- Draws game objects (sprites, shapes, text) via `Renderer` property
- Frame management (clear, begin, end) is automatic

---

## Add to Existing Project

Already have a .NET 10 project? Add Brine2D:

```sh
dotnet add package Brine2D
```

Then add the startup code to your `Program.cs`:

```csharp
using Brine2D.Hosting;

var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1280;
    options.Window.Height = 720;
});

builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

---

## Common Mistakes

1. **Don't access framework properties in the constructor**
   ```csharp
   // :x: Wrong - properties not set yet!
   public GameScene()
   {
       Logger.LogInformation("Created"); // Throws!
       World.CreateEntity("Player");     // Throws!
   }
   ```

2. **Don't inject framework services via constructor**
   ```csharp
   // :x: Unnecessary - use properties instead
   public GameScene(IRenderer renderer, IEntityWorld world) { }

   // :white_check_mark: Correct - use framework properties
   protected override void OnRender(GameTime gameTime)
   {
       Renderer.DrawText("Hello", 10, 10, Color.White);
   }
   ```

3. **Don't manually clear World on unload**
   ```csharp
   // :x: Not needed - automatic!
   protected override Task OnUnloadAsync(CancellationToken ct)
   {
       foreach (var entity in World.Entities)
           World.DestroyEntity(entity); // Not needed!
       return Task.CompletedTask;
   }
   ```

4. **Don't poll input in OnRender**
   ```csharp
   // :x: Wrong
   protected override void OnRender(GameTime gameTime)
   {
       if (Input.IsKeyDown(Key.W)) { ... } // Input in update only!
   }
   ```

5. **Don't load assets in OnUpdate**
   ```csharp
   // :x: Wrong - causes lag every frame!
   protected override void OnUpdate(GameTime gameTime)
   {
       var texture = await _assets.GetOrLoadTextureAsync(...); // NO!
   }
   ```

---

## Summary

**What you learned:**

| Concept | Description |
|---------|-------------|
| **GameApplication** | Entry point, similar to ASP.NET Core |
| **Scene** | Container for game logic (update + render) |
| **Framework Properties** | Logger, World, Renderer, Input, Audio, Game - set automatically |
| **Scoped World** | Each scene has isolated EntityWorld - automatic cleanup! |
| **Dependency Injection** | YOUR services injected via constructor |
| **Game Loop** | Update (logic) → Render (drawing) |
| **deltaTime** | Frame-rate independent movement |

**Key patterns:**

```csharp
// 1. Setup
var builder = GameApplication.CreateBuilder(args);
builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1280;
    options.Window.Height = 720;
});
builder.AddScene<GameScene>();

// 2. Scene
public class GameScene : Scene
{
    public GameScene(IGameContext gameContext) { }

    protected override void OnUpdate(GameTime gameTime)
    {
        Logger.LogDebug("Updating");
        var player = World.GetEntityByName("Player");
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Hello", 10, 10, Color.White);
    }
}

// 3. Run
await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

---

## Next Steps

Now that you have a working game, explore more features:

- **[Your First Game](first-game.md)** - Build a complete game with sprites, audio, and collision
- **[Project Structure](project-structure.md)** - Organize your code
- **[Configuration](configuration.md)** - Configure game settings
- **[Input Guide](../input/keyboard.md)** - Master keyboard, mouse, and gamepad input
- **[Rendering Guide](../rendering/sprites.md)** - Work with sprites and textures

---

## Quick Reference

```csharp
// Minimal Program.cs
using Brine2D.Hosting;

var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 800;
    options.Window.Height = 600;
});

builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

```csharp
// Minimal Scene
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Input;

public class GameScene : Scene
{
    private readonly IGameContext _gameContext;

    public GameScene(IGameContext gameContext)
    {
        _gameContext = gameContext;
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyPressed(Key.Escape))
        {
            _gameContext.RequestExit();
        }
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Hello, Brine2D!", 10, 10, Color.White);
    }
}
```

---

Ready to build your first complete game? Head to [Your First Game](first-game.md)!
