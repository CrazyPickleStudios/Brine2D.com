---
title: Project Structure
description: Organize your Brine2D project for maintainability and scalability
---

# Project Structure

Learn how to organize your Brine2D project for clean, maintainable, and scalable game development.

## Overview

A well-organized project structure:

- Makes code easy to find and navigate
- Separates concerns (scenes, systems, entities)
- Scales from prototypes to full games
- Simplifies team collaboration

---

## Basic Structure

### Minimal Project

For prototypes and learning:

```
MyGame/
├── MyGame.csproj
├── Program.cs
├── GameScene.cs
└── assets/
    ├── images/
    ├── audio/
    └── fonts/
```

**When to use:**
- Quick prototypes
- Tutorial projects
- Single-scene games
- Learning Brine2D

**Program.cs:**

```csharp
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

---

### Standard Project

For most games:

```
MyGame/
├── MyGame.csproj
├── Program.cs
├── Scenes/
│   ├── MenuScene.cs
│   ├── GameScene.cs
│   └── PauseScene.cs
├── Behaviors/
│   ├── PlayerMovementBehavior.cs
│   └── EnemyAIBehavior.cs
├── Systems/
│   ├── MovementSystem.cs
│   └── CombatSystem.cs
└── assets/
    ├── images/
    │   ├── player/
    │   ├── enemies/
    │   └── ui/
    ├── audio/
    │   ├── effects/
    │   └── music/
    └── fonts/
```

**When to use:**
- Most 2D games
- Multi-scene projects
- Medium-sized teams

---

### Large Project

For complex games with many features:

```
MyGame/
├── MyGame.csproj
├── Program.cs
├── Scenes/
│   ├── Menu/
│   │   ├── MainMenuScene.cs
│   │   ├── OptionsScene.cs
│   │   └── CreditsScene.cs
│   └── Gameplay/
│       ├── Level1Scene.cs
│       └── BossScene.cs
├── Entities/
│   ├── Characters/
│   │   ├── Player.cs
│   │   └── Enemy.cs
│   └── Items/
│       ├── Weapon.cs
│       └── Collectible.cs
├── Behaviors/
│   ├── PlayerMovementBehavior.cs
│   └── EnemyAIBehavior.cs
├── Components/
│   ├── HealthComponent.cs
│   └── InventoryComponent.cs
├── Systems/
│   ├── Gameplay/
│   │   ├── MovementSystem.cs
│   │   └── CombatSystem.cs
│   └── Rendering/
│       └── AnimationSystem.cs
├── Services/
│   ├── GameStateManager.cs
│   └── SaveManager.cs
├── Manifests/
│   ├── LevelAssets.cs
│   └── MenuAssets.cs
└── assets/
    ├── images/
    ├── audio/
    └── fonts/
```

---

## Namespace Conventions

**Match folders to namespaces:**

```csharp
// File: Scenes/GameScene.cs
namespace MyGame.Scenes;

public class GameScene : Scene { }
```

```csharp
// File: Behaviors/PlayerMovementBehavior.cs
namespace MyGame.Behaviors;

public class PlayerMovementBehavior : Behavior { }
```

---

## Asset Organization

### Recommended Layout

```
assets/
├── images/
│   ├── player.png
│   ├── enemy.png
│   └── tileset.png
├── audio/
│   ├── jump.wav
│   ├── hurt.wav
│   └── music/
│       └── theme.ogg
└── fonts/
    ├── ui.ttf
    └── mono.ttf
```

### Referencing Assets

```csharp
// Use forward slashes (cross-platform)
var texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png");
var sound = await _assets.GetOrLoadSoundAsync("assets/audio/jump.wav");
var font = await _assets.GetOrLoadFontAsync("assets/fonts/ui.ttf", size: 16);
```

### Copy Assets to Output

Add to your `.csproj`:

```xml
<ItemGroup>
  <None Update="assets\**\*">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

---

## Troubleshooting

### Problem: Namespace not found

**Symptom:**

```
error CS0246: The type or namespace name 'GameScene' could not be found
```

**Solution:**

1. **Check namespace matches folder:**
   ```csharp
   // File: Scenes/GameScene.cs
   namespace MyGame.Scenes; // Must match
   ```

2. **Add using statement:**
   ```csharp
   using MyGame.Scenes;
   ```

---

### Problem: Assets not found

**Symptom:**

```
FileNotFoundException: Could not find file 'assets/player.png'
```

**Solution:**

1. **Copy assets to output:**
   ```xml
   <ItemGroup>
     <None Update="assets\**\*">
       <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
     </None>
   </ItemGroup>
   ```

2. **Use correct path separator:**
   ```csharp
   // :white_check_mark: Works on all platforms
   "assets/images/player.png"

   // :x: Windows only
   "assets\\images\\player.png"
   ```

---

## Summary

| Project Size | Folders | When to Use |
|--------------|---------|-------------|
| **Minimal** | 1-2 files + assets | Prototypes, learning |
| **Standard** | Scenes, Behaviors, Systems | Most games |
| **Large** | Nested folders | Complex games |

**Key principles:**

| Principle | Description |
|-----------|-------------|
| **Match folders to namespaces** | `Scenes/GameScene.cs` -> `MyGame.Scenes` |
| **Group by purpose** | Scenes, Behaviors, Systems, Assets |
| **Start small, grow** | Add folders as needed |
| **Consistent naming** | `*Scene.cs`, `*System.cs`, `*Component.cs`, `*Behavior.cs` |

---

## Next Steps

- **[Configuration](configuration.md)** - Configure your game
- **[First Game](first-game.md)** - Build a complete game
- **[Scenes](../scenes/index.md)** - Understand scene architecture

---

## Quick Reference

```
# Standard project structure
MyGame/
├── MyGame.csproj           # Project configuration
├── Program.cs              # Entry point
├── Scenes/                 # Game scenes
│   ├── MenuScene.cs
│   └── GameScene.cs
├── Behaviors/              # Behaviors
│   ├── PlayerMovementBehavior.cs
│   └── EnemyAIBehavior.cs
├── Systems/                # ECS systems
│   └── HealthSystem.cs
└── assets/                 # Game assets
    ├── images/
    ├── audio/
    └── fonts/
```

```csharp
// Namespace pattern
// File: Scenes/Gameplay/Level1Scene.cs
namespace MyGame.Scenes.Gameplay;

public class Level1Scene : Scene
{
    // Implementation
}
```

```xml
<!-- Copy assets to output -->
<ItemGroup>
  <None Update="assets\**\*">
    <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
  </None>
</ItemGroup>
```

---

Ready to configure your game? Check out [Configuration](configuration.md)!
