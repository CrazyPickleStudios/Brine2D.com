---
title: Getting Started
description: Installation, quick start, and first game tutorials
---

# Get Started with Brine2D

Welcome to Brine2D! Get up and running in minutes with our step-by-step guides designed for developers familiar with .NET and ASP.NET Core patterns.

---

## Learning Path

Follow these guides in order for the smoothest onboarding experience:

| Step | Guide | Time | What You'll Learn |
|------|-------|------|-------------------|
| **1** | [Installation](installation.md) | 5 min | Install .NET 10 SDK and Brine2D |
| **2** | [Quick Start](quickstart.md) | 5 min | Create your first game window with a moving sprite |
| **3** | [Your First Game](first-game.md) | 30 min | Build a complete game with sprites, audio, and collision |
| **4** | [Project Structure](project-structure.md) | 10 min | Organize your game project professionally |
| **5** | [Configuration](configuration.md) | 10 min | Configure game settings and options |

**Total time: ~1 hour**

---

## Prerequisites

Before you begin, make sure you have:

- **Basic C# knowledge** - Variables, classes, methods
- **Familiarity with .NET** - Creating console apps, using NuGet
- **Optional: ASP.NET Core experience** - Brine2D uses similar patterns

---

## Quick Start Preview

Want to see what you'll build? Here's a minimal Brine2D game:

```csharp
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Hosting;
using Brine2D.Input;

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

    public GameScene(IGameContext gameContext)
    {
        _gameContext = gameContext;
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Hello, Brine2D!", 100, 100, Color.White);
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyPressed(Key.Escape))
            _gameContext.RequestExit();
    }
}
```

[:octicons-arrow-right-24: Full Tutorial](quickstart.md)

---

## What Makes Brine2D Different?

### ASP.NET-Inspired Architecture

| ASP.NET Core | Brine2D | Benefit |
|--------------|---------|---------|
| `WebApplication.CreateBuilder()` | `GameApplication.CreateBuilder()` | Familiar builder pattern |
| Dependency Injection | Dependency Injection | Testable, maintainable code |
| `ILogger<T>` | `Logger` property | Structured logging |
| Request Scope | Scene Scope | Automatic cleanup |

**If you've built ASP.NET apps**, you already know most of Brine2D's patterns!

---

### Hybrid Entity Component System

Unlike strict ECS engines, Brine2D's ECS is **beginner-friendly**:

- **Components** - Data containers with `OnAdded`/`OnRemoved` hooks
- **Behaviors** - Per-entity logic with DI support (like Unity MonoBehaviours)
- **Systems** - Optional batch processing for performance optimization

```csharp
// Data component
public class HealthComponent : Component
{
    public int Current { get; set; }
    public int Max { get; set; }

    protected internal override void OnAdded()
    {
        Current = Max;
    }
}

// Per-entity logic with DI
public class PlayerMovementBehavior : Behavior
{
    private readonly IInputContext _input;

    public PlayerMovementBehavior(IInputContext input)
    {
        _input = input;
    }

    public override void Update(GameTime gameTime)
    {
        // Move player based on input
    }
}
```

---

### Automatic Scene Scoping

**Each scene gets its own isolated EntityWorld** - automatic cleanup, no memory leaks!

```csharp
public class MenuScene : Scene
{
    protected override void OnEnter()
    {
        for (int i = 0; i < 100; i++)
            World.CreateEntity($"Button_{i}");
    }

    // No cleanup needed - World disposed automatically on scene unload!
}
```

---

## Common Questions

### Do I need game development experience?

**No!** If you can build ASP.NET Core apps, you can build Brine2D games. The patterns are nearly identical.

### What platforms does Brine2D support?

- :white_check_mark: **Windows** (10/11)
- :white_check_mark: **Linux** (Ubuntu, Fedora, etc.)
- :white_check_mark: **macOS** (Intel and Apple Silicon)

### Can I use this for commercial games?

**Yes!** Brine2D is **MIT licensed** - use it anywhere, including commercial projects, no royalties.

### Is there a visual editor?

**No.** Brine2D is **code-first** - everything is C# code. If you prefer visual editors, try Unity or Godot.

**Advantage:** Better version control, easier code review, no editor lock-in.

---

## Next Steps by Experience Level

### Complete Beginners

Start here and follow in order:

1. [Installation](installation.md) - Install prerequisites
2. [Quick Start](quickstart.md) - Your first window
3. [Your First Game](first-game.md) - Complete game tutorial

### Experienced Developers

Jump to what you need:

- **Want to understand architecture?** ? [Fundamentals](../fundamentals/scenes.md)
- **Need specific features?** ? [Rendering](../rendering/index.md), [Input](../input/index.md)

### ASP.NET Developers

You'll feel right at home:

1. [Quick Start](quickstart.md) - Familiar builder pattern
2. [Scenes](../scenes/index.md) - Scene lifecycle and DI patterns

---

## Learning Resources

### Documentation

- **[Tutorials](../tutorials/index.md)** - Step-by-step learning paths
- **[Fundamentals](../fundamentals/scenes.md)** - Deep architectural knowledge
- **[Samples](../samples/feature-demos.md)** - Working example projects

### External Resources

- [.NET 10 Documentation](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10) - Language features
- [ASP.NET Core Fundamentals](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/) - Learn the patterns

---

## Need Help?

- [Open an issue](https://github.com/CrazyPickleStudios/Brine2D/issues) - Bug reports, feature requests
- [Start a discussion](https://github.com/CrazyPickleStudios/Brine2D/discussions) - Questions, ideas

---

**Ready to build your first game?** Start with [Installation](installation.md)!
