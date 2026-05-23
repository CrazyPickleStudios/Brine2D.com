---
title: Home
---

<div class="hero-center" markdown>

<img src="images/logo.png" alt="Brine2D Logo" class="hero-logo">

<p class="hero-tagline">A 2D game engine for .NET 10, built on SDL3.<br>
If you know ASP.NET, you already know how this works.</p>

[![.NET](https://img.shields.io/badge/.NET-10.0-512BD4)](https://dotnet.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-CrazyPickleStudios-181717?logo=github)](https://github.com/CrazyPickleStudios/Brine2D)

[Get Started :material-arrow-right:](getting-started/quickstart.md){ .md-button .md-button--primary }
[View on GitHub :material-github:](https://github.com/CrazyPickleStudios/Brine2D){ .md-button }

</div>

---

## What is Brine2D?

Brine2D is a full 2D game engine - not a rendering library. Scenes, entities, audio, input, collision, particles, UI, and a DI container all ship together and work out of the box. Everything you'd normally spend the first two weeks building yourself is already here.

It follows the same hosting model as ASP.NET Core: `GameApplicationBuilder` → configure → build → run. If you've written a `WebApplication`, you'll be writing games in about ten minutes.

```csharp
var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "My Game";
    options.Window.Width  = 1280;
    options.Window.Height = 720;
});

builder.AddScene<GameScene>();

await using var game = builder.Build();
await game.RunAsync<GameScene>();
```

```csharp
public class GameScene : Scene
{
    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Hello, Brine2D!", 100, 100, Color.White);
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyPressed(Key.Escape))
            Game.RequestExit();
    }
}
```

That's a window, a game loop, input, and rendering. No boilerplate, no XML, no content pipeline.

---

## Features

| Feature | What it does |
|---|---|
| **GPU Rendering** | Hardware-accelerated via SDL3 GPU (Vulkan / Metal / D3D12). Sprites, sprite sheets, animations, cameras, line drawing, render targets. |
| **Hybrid ECS** | Components for data, Behaviors for per-entity logic with DI, Systems for batch processing. One `World` per scene, cleaned up automatically. |
| **Scene Management** | Async loading, transitions with fades, loading screens with progress. Register scenes at startup, swap at runtime. |
| **Asset Pipeline** | Unified `IAssetLoader` with ref-counted caching. Typed `AssetManifest` for parallel preloading. Assets release when the scene unloads. |
| **Input** | Keyboard, mouse, gamepad. Polling and event-driven. Input layers for UI-eats-input patterns. |
| **Spatial Audio** | Distance attenuation, stereo panning, configurable falloff. Plugs into ECS with audio source/listener components. |
| **Particles** | GPU-accelerated emitters with configurable lifetime, integrated with ECS. |
| **Collision** | AABB and circle colliders, spatial queries, collision events. |
| **UI** | Buttons, sliders, text inputs, dialogs, tabs, scroll views, tooltips, dropdowns. |
| **DI everywhere** | Built on `Microsoft.Extensions.DependencyInjection`. Scenes and Behaviors get constructor injection. Framework services come as properties - no wiring needed. |

---

## Project structure

One NuGet package. No separate renderer or platform packages.

```
Brine2D/
├── Assets        # Loading, caching, manifests
├── Audio         # Playback, spatial audio, SDL3 backend
├── Core          # GameTime, Color, math helpers
├── ECS           # Entities, components, behaviors, systems, queries
├── Engine        # Game loop, scenes, transitions, loading screens
├── Hosting       # Builder, options, DI wiring
├── Input         # Keyboard, mouse, gamepad, input layers
├── Rendering     # Sprites, text, cameras, particles, SDL3 GPU backend
└── UI            # Components, layout, input handling
```

---

## Requirements

- .NET 10 SDK
- Windows, macOS, or Linux
- SDL3 (ships automatically via the SDL3-CS NuGet dependency)

---

<div class="grid cards" markdown>

-   :material-clock-fast: **Quickstart**

    ---

    From `dotnet new` to a running game in five minutes.

    [:octicons-arrow-right-24: Get Started](getting-started/quickstart.md)

-   :material-school: **Tutorials**

    ---

    Step-by-step: sprites, input, animation, collision.

    [:octicons-arrow-right-24: Tutorials](tutorials/index.md)

-   :material-book-open-variant: **Fundamentals**

    ---

    Architecture, scenes, ECS, DI - how it all fits together.

    [:octicons-arrow-right-24: Fundamentals](fundamentals/index.md)

-   :material-test-tube: **Feature Demos**

    ---

    Runnable samples for every major subsystem.

    [:octicons-arrow-right-24: Samples](samples/feature-demos.md)

</div>

---

<div class="hero-center" markdown>

**MIT licensed. Made with :heart: by [CrazyPickle Studios](https://github.com/CrazyPickleStudios) :cucumber:**

</div>