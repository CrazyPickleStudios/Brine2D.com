---
title: ECS Getting Started
description: Get started with Entity Component System in Brine2D - build your first hybrid ECS game
---

# ECS Getting Started

Build your first game using Brine2D's **hybrid ECS** - components with methods, entities with optional logic, and systems for performance optimization.

## Overview

This guide takes you from zero to a working ECS game in 15 minutes. You'll learn:

- How to access **World** in scenes
- Creating entities with **World.CreateEntity()**
- Adding components with **methods and logic**
- Using **entity queries** to find entities
- Building optional systems for performance

**Prerequisites:**
- Completed [Quick Start](../../getting-started/quickstart.md)
- Basic C# knowledge
- Understanding of [Hybrid ECS Concepts](../../concepts/entity-component-system.md)

**What you'll build:**
A simple game with player, enemies, and pickups using Brine2D's flexible hybrid ECS.

---

## World Access Patterns

### The World Property

**Every scene has a `World` property** - set automatically by SceneManager:

```csharp
public class GameScene : Scene
{
    // ✅ World is available automatically - no injection needed!
    
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // Access World directly
        var player = World.CreateEntity("Player");
        var enemy = World.CreateEntity("Enemy");
        
        Logger.LogInformation("Created {Count} entities", World.Entities.Count);
        
        return Task.CompletedTask;
    }
}
```

**Pattern:** `World` is a framework property (like `Logger` and `Renderer`) - set by SceneManager, not injected.

---

### World Scope

**Each scene gets its own isolated World** - automatic cleanup!

```csharp
// MenuScene
public class MenuScene : Scene
{
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // Create 10 UI button entities
        for (int i = 0; i < 10; i++)
        {
            CreateButton(i);
        }
        
        Logger.LogInformation("Menu has {Count} entities", World.Entities.Count); // 10
        
        return Task.CompletedTask;
    }
}

// Later: Load GameScene
await sceneManager.LoadSceneAsync<GameScene>();

// GameScene
public class GameScene : Scene
{
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // ✅ World is fresh - no leftover menu buttons!
        Logger.LogInformation("Game has {Count} entities", World.Entities.Count); // 0
        
        // Create game entities
        CreatePlayer();
        CreateEnemies();
        
        return Task.CompletedTask;
    }
}
```

**Pattern:** Each scene gets a fresh, isolated World. No manual cleanup needed!

---

## Project Setup

### Step 1: Create Project

```sh
dotnet new console -n ECSDemo
cd ECSDemo
dotnet add package Brine2D --version 0.9.0-beta
dotnet add package Brine2D.SDL --version 0.9.0-beta
```

---

### Step 2: Basic Program Setup

Create `Program.cs`:

```csharp
using Brine2D.Hosting;
using Brine2D.SDL;
using ECSDemo;
using Microsoft.Extensions.DependencyInjection;

var builder = GameApplication.CreateBuilder(args);

builder.Services.AddBrine2D(options =>
{
    options.Window.Title = "ECS Demo";
    options.Window.Width = 800;
    options.Window.Height = 600;
});

// Register scene
builder.AddScene<GameScene>();

var game = builder.Build();
await game.RunAsync<GameScene>();
```

---

## Creating Components (With Methods!)

### Step 3: Define Components with Logic

**Brine2D's hybrid ECS allows methods in components** - beginner-friendly!

Create `Components/HealthComponent.cs`:

```csharp
using Brine2D.ECS;

namespace ECSDemo.Components;

public class HealthComponent : Component
{
    public int Current { get; set; }
    public int Max { get; set; }
    
    public bool IsDead => Current <= 0;
    
    // ✅ Methods allowed in Brine2D!
    public void TakeDamage(int amount)
    {
        Current = Math.Max(0, Current - amount);
        
        if (IsDead)
        {
            // Notify death
            Entity?.World?.DestroyEntity(Entity);
        }
    }
    
    public void Heal(int amount)
    {
        Current = Math.Min(Max, Current + amount);
    }
    
    // ✅ Lifecycle methods available
    protected internal override void OnUpdate(GameTime gameTime)
    {
        // Optional: Health regeneration over time
        if (Current < Max)
        {
            Current = Math.Min(Max, Current + 1);
        }
    }
}
```

Create `Components/TransformComponent.cs`:

```csharp
using Brine2D.ECS;
using System.Numerics;

namespace ECSDemo.Components;

public class TransformComponent : Component
{
    public Vector2 Position { get; set; }
    public float Rotation { get; set; }
    public Vector2 Scale { get; set; } = Vector2.One;
    
    // ✅ Helper methods
    public void Move(Vector2 delta)
    {
        Position += delta;
    }
    
    public void RotateTowards(Vector2 target)
    {
        var direction = Vector2.Normalize(target - Position);
        Rotation = MathF.Atan2(direction.Y, direction.X);
    }
}
```

Create `Components/VelocityComponent.cs`:

```csharp
using Brine2D.ECS;
using System.Numerics;

namespace ECSDemo.Components;

public class VelocityComponent : Component
{
    public Vector2 Value { get; set; }
    public float Speed { get; set; } = 100f;
    
    // ✅ Lifecycle method - auto-movement
    protected internal override void OnUpdate(GameTime gameTime)
    {
        if (Value != Vector2.Zero)
        {
            var transform = GetRequiredComponent<TransformComponent>();
            transform.Position += Value * (float)gameTime.DeltaTime;
        }
    }
}
```

Create `Components/SpriteComponent.cs`:

```csharp
using Brine2D.Core;
using Brine2D.ECS;

namespace ECSDemo.Components;

public class SpriteComponent : Component
{
    public int Width { get; set; }
    public int Height { get; set; }
    public Color Color { get; set; } = Color.White;
    
    // ✅ Render itself
    protected internal override void OnRender(IRenderer renderer)
    {
        var transform = GetComponent<TransformComponent>();
        if (transform != null)
        {
            renderer.DrawRectangleFilled(
                transform.Position.X - Width / 2,
                transform.Position.Y - Height / 2,
                Width, Height,
                Color);
        }
    }
}
```

**Pattern:** Components can have methods and lifecycle hooks - simple and intuitive!

---

## Creating Entities

### Step 4: Create Player Entity

Create `GameScene.cs`:

```csharp
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Input;
using ECSDemo.Components;
using System.Numerics;

namespace ECSDemo;

public class GameScene : Scene
{
    private readonly IInputContext _input;
    private Entity? _player;
    
    public GameScene(IInputContext input)
    {
        _input = input;
    }
    
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // ✅ World available automatically!
        CreatePlayer();
        CreateEnemies();
        CreatePickups();
        
        Logger.LogInformation("Created {Count} entities", World.Entities.Count);
        
        return Task.CompletedTask;
    }
    
    private void CreatePlayer()
    {
        // ✅ Create entity via World
        _player = World.CreateEntity("Player");
        
        // Add components
        var transform = _player.AddComponent<TransformComponent>();
        transform.Position = new Vector2(400, 300);
        
        var sprite = _player.AddComponent<SpriteComponent>();
        sprite.Width = 32;
        sprite.Height = 32;
        sprite.Color = Color.Blue;
        
        var health = _player.AddComponent<HealthComponent>();
        health.Max = 100;
        health.Current = 100;
        
        // Tag for easy lookup
        _player.Tags.Add("Player");
    }
    
    private void CreateEnemies()
    {
        var random = new Random();
        
        for (int i = 0; i < 5; i++)
        {
            var enemy = World.CreateEntity($"Enemy{i}");
            
            var transform = enemy.AddComponent<TransformComponent>();
            transform.Position = new Vector2(
                random.Next(100, 700),
                random.Next(100, 500));
            
            var sprite = enemy.AddComponent<SpriteComponent>();
            sprite.Width = 24;
            sprite.Height = 24;
            sprite.Color = Color.Red;
            
            var velocity = enemy.AddComponent<VelocityComponent>();
            velocity.Value = new Vector2(
                random.NextSingle() * 2 - 1,
                random.NextSingle() * 2 - 1);
            velocity.Speed = 50f;
            
            enemy.Tags.Add("Enemy");
        }
    }
    
    private void CreatePickups()
    {
        var random = new Random();
        
        for (int i = 0; i < 10; i++)
        {
            var pickup = World.CreateEntity($"Pickup{i}");
            
            var transform = pickup.AddComponent<TransformComponent>();
            transform.Position = new Vector2(
                random.Next(100, 700),
                random.Next(100, 500));
            
            var sprite = pickup.AddComponent<SpriteComponent>();
            sprite.Width = 16;
            sprite.Height = 16;
            sprite.Color = Color.Yellow;
            
            pickup.Tags.Add("Pickup");
        }
    }
}
```

---

## Entity Queries (Finding Entities)

### Step 5: Query and Update Entities

Add to `GameScene.cs`:

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    HandlePlayerInput();
    CheckCollisions();
}

private void HandlePlayerInput()
{
    // ✅ Find player by tag
    var players = World.GetEntitiesByTag("Player");
    if (players.Count == 0) return;
    
    var player = players[0];
    var transform = player.GetComponent<TransformComponent>();
    
    if (transform == null) return;
    
    // Move player
    var movement = Vector2.Zero;
    if (_input.IsKeyDown(Key.W)) movement.Y -= 1;
    if (_input.IsKeyDown(Key.S)) movement.Y += 1;
    if (_input.IsKeyDown(Key.A)) movement.X -= 1;
    if (_input.IsKeyDown(Key.D)) movement.X += 1;
    
    if (movement != Vector2.Zero)
    {
        movement = Vector2.Normalize(movement);
        transform.Move(movement * 200f * (float)gameTime.DeltaTime);
    }
}

private void CheckCollisions()
{
    // ✅ Get player
    var players = World.GetEntitiesByTag("Player");
    if (players.Count == 0) return;
    
    var player = players[0];
    var playerTransform = player.GetComponent<TransformComponent>();
    var playerHealth = player.GetComponent<HealthComponent>();
    
    if (playerTransform == null || playerHealth == null) return;
    
    // ✅ Check collisions with enemies
    var enemies = World.GetEntitiesByTag("Enemy");
    foreach (var enemy in enemies)
    {
        var enemyTransform = enemy.GetComponent<TransformComponent>();
        if (enemyTransform == null) continue;
        
        var distance = Vector2.Distance(
            playerTransform.Position, 
            enemyTransform.Position);
        
        if (distance < 30) // Collision radius
        {
            playerHealth.TakeDamage(10);
            World.DestroyEntity(enemy);
            
            Logger.LogInformation("Player hit! Health: {Health}", playerHealth.Current);
        }
    }
    
    // ✅ Check pickups
    var pickups = World.GetEntitiesByTag("Pickup");
    foreach (var pickup in pickups)
    {
        var pickupTransform = pickup.GetComponent<TransformComponent>();
        if (pickupTransform == null) continue;
        
        var distance = Vector2.Distance(
            playerTransform.Position,
            pickupTransform.Position);
        
        if (distance < 25) // Pickup radius
        {
            playerHealth.Heal(20);
            World.DestroyEntity(pickup);
            
            Logger.LogInformation("Pickup collected! Health: {Health}", playerHealth.Current);
        }
    }
}
```

---

## World Query Methods

### All Query Methods Available

```csharp
// 1. Get all entities
IReadOnlyList<Entity> all = World.Entities;

// 2. Find by name (first match)
Entity? player = World.GetEntityByName("Player");

// 3. Find by ID
Entity? entity = World.GetEntityById(someGuid);

// 4. Find by tag
IReadOnlyList<Entity> enemies = World.GetEntitiesByTag("Enemy");

// 5. Find with component
IReadOnlyList<Entity> damageable = World.GetEntitiesWithComponent<HealthComponent>();

// 6. Find with multiple components
IReadOnlyList<Entity> movable = World.GetEntitiesWithComponents<
    TransformComponent, 
    VelocityComponent>();

// 7. Find with predicate
Entity? boss = World.FindEntity(e => 
    e.Tags.Contains("Enemy") && 
    e.GetComponent<HealthComponent>()?.Max > 100);
```

**Pattern:** All query methods return snapshots - safe to iterate while modifying entities.

---

## Rendering Entities

### Step 6: Render Scene

Add to `GameScene.cs`:

```csharp
protected override void OnRender(GameTime gameTime)
{
    // Option 1: Components render themselves (automatic)
    // SpriteComponent.OnRender() is called automatically!
    
    // Option 2: Manual rendering
    RenderHUD();
}

private void RenderHUD()
{
    // Find player
    var players = World.GetEntitiesByTag("Player");
    if (players.Count == 0) return;
    
    var player = players[0];
    var health = player.GetComponent<HealthComponent>();
    
    if (health != null)
    {
        Renderer.DrawText(
            $"Health: {health.Current}/{health.Max}",
            10, 10,
            Color.White);
    }
    
    // Show entity counts
    var enemies = World.GetEntitiesByTag("Enemy");
    var pickups = World.GetEntitiesByTag("Pickup");
    
    Renderer.DrawText(
        $"Enemies: {enemies.Count}  Pickups: {pickups.Count}",
        10, 40,
        Color.LightGray);
    
    // Instructions
    Renderer.DrawText("WASD to move", 10, 80, Color.Gray);
    Renderer.DrawText("Collect yellow pickups, avoid red enemies!", 10, 110, Color.Gray);
}
```

---

## Optional: Using Systems

Systems are **optional** - use them for **performance optimization** with 1000+ entities:

### Step 7: Create a System (Advanced)

Create `Systems/MovementSystem.cs`:

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using ECSDemo.Components;

namespace ECSDemo.Systems;

// ✅ Optional: Use systems for batch processing (performance)
public class MovementSystem : IUpdateSystem
{
    private readonly IEntityWorld _world;
    
    public string Name => "MovementSystem";
    public int UpdateOrder => 100;
    
    public MovementSystem(IEntityWorld world)
    {
        _world = world;
    }
    
    public void Update(GameTime gameTime)
    {
        var deltaTime = (float)gameTime.DeltaTime;
        
        // ✅ Batch process all moving entities
        var entities = _world.GetEntitiesWithComponents<
            TransformComponent, 
            VelocityComponent>();
        
        foreach (var entity in entities)
        {
            var transform = entity.GetComponent<TransformComponent>();
            var velocity = entity.GetComponent<VelocityComponent>();
            
            if (transform != null && velocity != null)
            {
                transform.Position += velocity.Value * velocity.Speed * deltaTime;
            }
        }
    }
}
```

Register system in `Program.cs`:

```csharp
// Optional: Register systems for performance
builder.Services.AddBrine2D(options => { ... });

// Add ECS systems (optional)
builder.Services.AddObjectECS();
builder.Services.ConfigureSystemPipelines(pipelines =>
{
    pipelines.AddSystem<MovementSystem>();
});
```

**Pattern:** Systems are optional - most games don't need them! Use components with methods first, add systems only if profiling shows performance issues.

---

## Entity Factories (Best Practice)

### Step 8: Encapsulate Entity Creation

Create `EntityFactory.cs`:

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using ECSDemo.Components;
using System.Numerics;

namespace ECSDemo;

public static class EntityFactory
{
    public static Entity CreatePlayer(IEntityWorld world, Vector2 position)
    {
        var entity = world.CreateEntity("Player");
        
        var transform = entity.AddComponent<TransformComponent>();
        transform.Position = position;
        
        var sprite = entity.AddComponent<SpriteComponent>();
        sprite.Width = 32;
        sprite.Height = 32;
        sprite.Color = Color.Blue;
        
        var health = entity.AddComponent<HealthComponent>();
        health.Max = 100;
        health.Current = 100;
        
        entity.Tags.Add("Player");
        
        return entity;
    }
    
    public static Entity CreateEnemy(IEntityWorld world, Vector2 position)
    {
        var entity = world.CreateEntity("Enemy");
        
        var transform = entity.AddComponent<TransformComponent>();
        transform.Position = position;
        
        var sprite = entity.AddComponent<SpriteComponent>();
        sprite.Width = 24;
        sprite.Height = 24;
        sprite.Color = Color.Red;
        
        var velocity = entity.AddComponent<VelocityComponent>();
        velocity.Speed = 50f;
        
        var health = entity.AddComponent<HealthComponent>();
        health.Max = 50;
        health.Current = 50;
        
        entity.Tags.Add("Enemy");
        
        return entity;
    }
    
    public static Entity CreatePickup(IEntityWorld world, Vector2 position)
    {
        var entity = world.CreateEntity("Pickup");
        
        var transform = entity.AddComponent<TransformComponent>();
        transform.Position = position;
        
        var sprite = entity.AddComponent<SpriteComponent>();
        sprite.Width = 16;
        sprite.Height = 16;
        sprite.Color = Color.Yellow;
        
        entity.Tags.Add("Pickup");
        
        return entity;
    }
}
```

Use in `GameScene.cs`:

```csharp
protected override Task OnLoadAsync(CancellationToken ct)
{
    // ✅ Clean entity creation via factory
    _player = EntityFactory.CreatePlayer(World, new Vector2(400, 300));
    
    var random = new Random();
    for (int i = 0; i < 5; i++)
    {
        EntityFactory.CreateEnemy(World, new Vector2(
            random.Next(100, 700),
            random.Next(100, 500)));
    }
    
    for (int i = 0; i < 10; i++)
    {
        EntityFactory.CreatePickup(World, new Vector2(
            random.Next(100, 700),
            random.Next(100, 500)));
    }
    
    return Task.CompletedTask;
}
```

---

## Complete Working Example

Here's the complete `GameScene.cs`:

```csharp
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Input;
using ECSDemo.Components;
using System.Numerics;

namespace ECSDemo;

public class GameScene : Scene
{
    private readonly IInputContext _input;
    private Entity? _player;
    
    public GameScene(IInputContext input)
    {
        _input = input;
    }
    
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // ✅ World available automatically - scoped per scene!
        
        // Create entities via factory
        _player = EntityFactory.CreatePlayer(World, new Vector2(400, 300));
        
        var random = new Random();
        for (int i = 0; i < 5; i++)
        {
            EntityFactory.CreateEnemy(World, new Vector2(
                random.Next(100, 700),
                random.Next(100, 500)));
        }
        
        for (int i = 0; i < 10; i++)
        {
            EntityFactory.CreatePickup(World, new Vector2(
                random.Next(100, 700),
                random.Next(100, 500)));
        }
        
        Logger.LogInformation("Created {Count} entities", World.Entities.Count);
        
        return Task.CompletedTask;
    }
    
    protected override void OnUpdate(GameTime gameTime)
    {
        HandlePlayerInput(gameTime);
        CheckCollisions();
        
        // Check win condition
        if (World.GetEntitiesByTag("Pickup").Count == 0)
        {
            Logger.LogInformation("You win! All pickups collected!");
            Environment.Exit(0);
        }
    }
    
    private void HandlePlayerInput(GameTime gameTime)
    {
        var players = World.GetEntitiesByTag("Player");
        if (players.Count == 0) return;
        
        var player = players[0];
        var transform = player.GetComponent<TransformComponent>();
        
        if (transform == null) return;
        
        var movement = Vector2.Zero;
        if (_input.IsKeyDown(Key.W)) movement.Y -= 1;
        if (_input.IsKeyDown(Key.S)) movement.Y += 1;
        if (_input.IsKeyDown(Key.A)) movement.X -= 1;
        if (_input.IsKeyDown(Key.D)) movement.X += 1;
        
        if (movement != Vector2.Zero)
        {
            movement = Vector2.Normalize(movement);
            transform.Move(movement * 200f * (float)gameTime.DeltaTime);
        }
    }
    
    private void CheckCollisions()
    {
        var players = World.GetEntitiesByTag("Player");
        if (players.Count == 0) return;
        
        var player = players[0];
        var playerTransform = player.GetComponent<TransformComponent>();
        var playerHealth = player.GetComponent<HealthComponent>();
        
        if (playerTransform == null || playerHealth == null) return;
        
        // Check enemies
        var enemies = World.GetEntitiesByTag("Enemy");
        foreach (var enemy in enemies)
        {
            var enemyTransform = enemy.GetComponent<TransformComponent>();
            if (enemyTransform == null) continue;
            
            var distance = Vector2.Distance(
                playerTransform.Position,
                enemyTransform.Position);
            
            if (distance < 30)
            {
                playerHealth.TakeDamage(10);
                World.DestroyEntity(enemy);
                Logger.LogInformation("Hit! Health: {Health}", playerHealth.Current);
            }
        }
        
        // Check pickups
        var pickups = World.GetEntitiesByTag("Pickup");
        foreach (var pickup in pickups)
        {
            var pickupTransform = pickup.GetComponent<TransformComponent>();
            if (pickupTransform == null) continue;
            
            var distance = Vector2.Distance(
                playerTransform.Position,
                pickupTransform.Position);
            
            if (distance < 25)
            {
                playerHealth.Heal(20);
                World.DestroyEntity(pickup);
                Logger.LogInformation("Pickup! Health: {Health}", playerHealth.Current);
            }
        }
    }
    
    protected override void OnRender(GameTime gameTime)
    {
        // Components render automatically via OnRender()
        RenderHUD();
    }
    
    private void RenderHUD()
    {
        var players = World.GetEntitiesByTag("Player");
        if (players.Count == 0) return;
        
        var player = players[0];
        var health = player.GetComponent<HealthComponent>();
        
        if (health != null)
        {
            Renderer.DrawText(
                $"Health: {health.Current}/{health.Max}",
                10, 10,
                Color.White);
        }
        
        var enemies = World.GetEntitiesByTag("Enemy");
        var pickups = World.GetEntitiesByTag("Pickup");
        
        Renderer.DrawText(
            $"Enemies: {enemies.Count}  Pickups: {pickups.Count}",
            10, 40,
            Color.LightGray);
        
        Renderer.DrawText("WASD to move", 10, 80, Color.Gray);
        Renderer.DrawText("Collect yellow, avoid red!", 10, 110, Color.Gray);
    }
    
    protected override Task OnUnloadAsync(CancellationToken ct)
    {
        // ✅ No cleanup needed - World disposed automatically!
        return Task.CompletedTask;
    }
}
```

---

## Running the Game

Build and run:

```sh
dotnet run
```

**Controls:**
- **WASD** - Move player
- **Collect yellow** - Heal (+20 HP)
- **Avoid red** - Damage (-10 HP)
- **Collect all pickups** - Win!

---

## Summary

**World access patterns:**

| Pattern | Usage |
|---------|-------|
| **World property** | Available automatically in scenes |
| **World.CreateEntity()** | Create entities |
| **World.DestroyEntity()** | Destroy entities |
| **World.GetEntitiesByTag()** | Find by tag |
| **World.GetEntitiesWithComponent<T>()** | Find with component |
| **World.Entities** | Get all entities |
| **Scoped World** | Automatic cleanup per scene |

**Key concepts:**

| Concept | Description |
|---------|-------------|
| **Hybrid ECS** | Components can have methods and logic |
| **Optional systems** | Use for performance optimization only |
| **Entity queries** | Safe snapshots, can modify during iteration |
| **Automatic cleanup** | World disposed when scene unloads |
| **Factory pattern** | Encapsulate entity creation |

**Recommended workflow:**

1. ✅ Start with **components with methods** (beginner-friendly)
2. ✅ Use **entity factories** to encapsulate creation
3. ✅ Query entities with **World.GetEntitiesByTag()** or **World.GetEntitiesWithComponent<T>()**
4. ✅ Add **systems** only if profiling shows performance issues

---

## Next Steps

- **[Components Guide](components.md)** - Deep dive into components with methods
- **[Queries Guide](queries.md)** - Advanced query patterns
- **[Systems Guide](systems.md)** - When and how to use systems
- **[Entities Guide](entities.md)** - Entity lifecycle and patterns
- **[ECS Concepts](../../concepts/entity-component-system.md)** - Understanding hybrid ECS

---

**Remember:** Brine2D's hybrid ECS is beginner-friendly - components can have methods, systems are optional, and World is automatically scoped per scene! 🎮