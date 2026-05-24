---
title: Home
hide:
  - toc
---

<div class="hero-center" markdown>

<img src="images/logo.png" alt="Brine2D Logo" class="hero-logo">

<p class="hero-tagline">A code-first 2D game engine for .NET 10.<br>
No editor. No visual tools. Just C#.</p>

[![.NET](https://img.shields.io/badge/.NET-10.0-512BD4)](https://dotnet.microsoft.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-CrazyPickleStudios-181717?logo=github)](https://github.com/CrazyPickleStudios/Brine2D)

<div class="hero-buttons">
[Get Started :material-arrow-right:](getting-started/quickstart.md){ .md-button .md-button--primary }
[View on GitHub :material-github:](https://github.com/CrazyPickleStudios/Brine2D){ .md-button }
</div>

</div>

---

## What is Brine2D?

Brine2D is a full 2D game engine — not a rendering library. Scenes, entities, audio, input, collision, particles, UI, and dependency injection all ship in a single NuGet package and work out of the box. Everything you'd normally spend the first two weeks wiring up is already here.

There is no built-in editor. Everything is configured in code. For content creation, Brine2D integrates with the tools you likely already use:

- **[Aseprite](https://www.aseprite.org/)** — sprite and animation authoring, imported directly via JSON export
- **[Tiled](https://www.mapeditor.org/)** — tile map editor, loaded natively at runtime
- **[TexturePacker](https://www.codeandweb.com/texturepacker)** — sprite atlas packing, supported out of the box

These are best-in-class tools with their own communities and years of polish. You get a better result than any built-in editor would provide, and you don't have to learn a new one. [Read more about why Brine2D has no editor.](fundamentals/no-editor.md)

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

## Common tasks

| I want to... | Go here |
|---|---|
| Create my first game | [Quickstart](getting-started/quickstart.md) |
| Understand entities, components, and behaviors | [ECS Overview](ecs/index.md) |
| Load and play sprite animations | [Animation](animation/index.md) |
| Handle keyboard, mouse, and gamepad input | [Input](features/input.md) |
| Play audio with spatial sound | [Audio](features/audio/index.md) |
| Load a Tiled map | [Tilemaps](tilemaps/index.md) |
| Add a UI button or dialog | [UI](ui/index.md) |
| Detect collisions between objects | [Collision](features/collision/index.md) |
| Switch between scenes | [Scene Management](fundamentals/scenes.md) |
| Understand the overall architecture | [Architecture](fundamentals/architecture.md) |

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