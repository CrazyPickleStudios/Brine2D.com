---
title: Configuration
description: Configure Brine2D with code-based options
---

# Configuration

Brine2D uses a **code-based configuration** model via `GameApplicationBuilder.Configure()`. Options are organized into nested groups for window, rendering, assets, audio, and ECS settings.

## Quick Example

```csharp
var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1920;
    options.Window.Height = 1080;
    options.Window.Fullscreen = false;
    options.Rendering.VSync = true;
    options.Rendering.PreferredGPUDriver = GPUDriver.Auto;
});

builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

---

## Option Groups

### Window Options

Controls window appearance and behavior.

```csharp
builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1280;
    options.Window.Height = 720;
    options.Window.Fullscreen = false;
    options.Window.Resizable = true;
    options.Window.Maximized = false;
    options.Window.Borderless = false;
});
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Title` | `string` | `"Brine2D Game"` | Window title text |
| `Width` | `int` | `1280` | Window width in pixels (1–7680) |
| `Height` | `int` | `720` | Window height in pixels (1–4320) |
| `Fullscreen` | `bool` | `false` | Start in fullscreen mode |
| `Resizable` | `bool` | `true` | Allow window resizing |
| `Maximized` | `bool` | `false` | Start maximized |
| `Borderless` | `bool` | `false` | Remove window decorations |

---

### Rendering Options

Controls GPU rendering and frame timing.

```csharp
builder.Configure(options =>
{
    options.Rendering.VSync = true;
    options.Rendering.PreferredGPUDriver = GPUDriver.Auto;
    options.Rendering.TargetFPS = 0;          // 0 = uncapped (use VSync)
    options.Rendering.MaxDeltaTimeMs = 100;
    options.Rendering.MaxVerticesPerFrame = 50_000;
    options.Rendering.ClearColor = Color.FromArgb(255, 52, 78, 65);
});
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `VSync` | `bool` | `true` | Sync with display refresh rate |
| `PreferredGPUDriver` | `GPUDriver` | `Auto` | GPU driver: `Auto`, `Vulkan`, `Metal`, `D3D11`, `D3D12` |
| `TargetFPS` | `int` | `0` | Target FPS (0 = uncapped, max 240) |
| `MaxDeltaTimeMs` | `int` | `100` | Max delta time per frame in ms |
| `MaxVerticesPerFrame` | `int` | `50,000` | Vertex buffer capacity |
| `ClearColor` | `Color` | Dark teal | Default screen clear color |

---

### Engine Options

Controls engine-level behavior.

```csharp
builder.Configure(options =>
{
    options.Headless = false;
    options.ShutdownTimeoutSeconds = 5;
    options.GameThreadPriority = ThreadPriority.Normal;
    options.LoadingScreenMinimumDisplayMs = 200;
});
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Headless` | `bool` | `false` | No window, input, or audio (for servers/tests) |
| `ShutdownTimeoutSeconds` | `int` | `5` | Graceful shutdown wait time |
| `GameThreadPriority` | `ThreadPriority` | `Normal` | Game thread priority |
| `LoadingScreenMinimumDisplayMs` | `int` | `200` | Minimum loading screen display time |

---

## Logging

Brine2D uses Microsoft.Extensions.Logging. Configure via the builder:

```csharp
builder.Logging.SetMinimumLevel(LogLevel.Debug);
builder.Logging.AddConsole();
```

Default: Console logging at `Information` level.

---

## Scene Configuration

### Register Scenes

```csharp
builder.AddScene<MenuScene>();
builder.AddScene<GameScene>();

// Or use the fluent builder
builder.AddScenes(scenes => scenes
    .Add<MenuScene>()
    .Add<GameScene>()
    .Add<SettingsScene>());
```

### Configure ECS World (All Scenes)

```csharp
builder.ConfigureScene(world =>
    world.GetSystem<ParticleSystem>()!.IsEnabled = false);

builder.ConfigureScene(world =>
    world.AddSystem<MyDebugOverlaySystem>());
```

### Exclude Default Systems

```csharp
builder.ExcludeDefaultSystem<ParticleSystem>();
builder.ExcludeDefaultSystem<CollisionDetectionSystem>();
```

### Add Custom Default Systems

```csharp
builder.AddDefaultSystem<FogOfWarSystem>();
builder.AddDefaultSystem<FogOfWarSystem>(s => s.Radius = 200f);
```

### Custom Fallback Scene

```csharp
builder.UseFallbackScene<MyErrorScene>();
```

---

## Common Patterns

### Pattern 1: Debug vs Release Settings

```csharp
builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1280;
    options.Window.Height = 720;

#if DEBUG
    options.Window.Title += " [DEBUG]";
    options.Rendering.VSync = false;
#endif
});
```

### Pattern 2: Dynamic Resolution

```csharp
builder.Configure(options =>
{
    if (args.Contains("--720p"))
    {
        options.Window.Width = 1280;
        options.Window.Height = 720;
    }
    else if (args.Contains("--1080p"))
    {
        options.Window.Width = 1920;
        options.Window.Height = 1080;
    }
});
```

### Pattern 3: Headless Testing

```csharp
builder.Configure(options =>
{
    options.Headless = true; // No window, input, or audio
});
```

---

## Validation

All options are validated automatically when you call `builder.Build()`. Invalid values throw a `GameConfigurationException` with detailed error messages:

```
Game application configuration is invalid:
  - Width must be between 1 and 7680
  - Title cannot exceed 100 characters
Fix: Check your builder.Configure(options => ...) calls in Program.cs
```

---

## Best Practices

### **DO: Use Configure for All Settings**

```csharp
builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width = 1280;
    options.Window.Height = 720;
    options.Rendering.VSync = true;
});
```

### **DO: Use Strongly-Typed Options for Game Settings**

```csharp
builder.Services.Configure<GameplayOptions>(
    builder.Configuration.GetSection("Gameplay"));
```

### **DON'T: Reload Configuration Mid-Frame**

If you need to apply new settings (like resolution), do it between scenes, not during rendering.

---

## Next Steps

- [Your First Game](first-game.md) - Build a complete game
- [Project Structure](project-structure.md) - Understanding the architecture
- [Scenes](../scenes/index.md) - Deep dive into scenes

---

Configuration in Brine2D keeps things simple - configure once, validate automatically, and focus on your game!
