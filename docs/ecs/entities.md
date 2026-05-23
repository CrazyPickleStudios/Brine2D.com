---
title: Entities
description: Understanding entities in Brine2D's hybrid ECS - containers, lifecycle, and patterns
---

# Entities

Entities are the foundation of Brine2D's **hybrid ECS** - they can be simple component containers or inherit custom behavior. Learn how to create, manage, and organize entities effectively.

## Overview

**What are entities?**

Entities in Brine2D are:
- **Unique identifiers** (Guid + Name)
- **Component containers** (hold data and logic)
- **Tag holders** (for quick lookups)
- **Optional behaviors** (override lifecycle methods)
- **Scoped to World** (automatic cleanup per scene)

**Two approaches:**

| Approach | When to Use | Complexity |
|----------|-------------|------------|
| **Simple entities** | Most games (component-based) | ⭐ Beginner |
| **Custom entities** | Specialized objects (inheritance) | ⭐⭐ Intermediate |

---

## The Entity Class

### Core Properties

```csharp
public class Entity
{
    // Identity
    public Guid Id { get; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    
    // State
    public bool IsActive { get; set; } = true;
    public IEntityWorld? World { get; internal set; }
    
    // Organization
    public HashSet<string> Tags => _tags;
    
    // Lifecycle (override in derived classes)
    public virtual void OnInitialize() { }
    public virtual void OnUpdate(GameTime gameTime) { }
    public virtual void OnRender(IRenderer renderer) { }
    public virtual void OnDestroy() { }
}
```

**Pattern:** Every entity has a unique ID, optional name, tags for organization, and lifecycle hooks.

---

## Creating Entities

### Simple Entity Creation

```csharp
public class GameScene : Scene
{
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // Create entity via World
        var player = World.CreateEntity("Player");
        
        // Add components
        var transform = player.AddComponent<TransformComponent>();
        transform.Position = new Vector2(400, 300);
        
        var sprite = player.AddComponent<SpriteComponent>();
        sprite.Width = 32;
        sprite.Height = 32;
        
        // Add tags for easy lookup
        player.Tags.Add("Player");
        player.Tags.Add("Controllable");
        
        return Task.CompletedTask;
    }
}
```

**Pattern:** Use `World.CreateEntity()` to create entities, then add components and tags.

---

### Custom Entity Classes

Derive from `Entity` for specialized behavior:

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Components;
using System.Numerics;

public class PlayerEntity : Entity
{
    private TransformComponent? _transform;
    private SpriteComponent? _sprite;
    private HealthComponent? _health;
    
    public override void OnInitialize()
    {
        // Called once when entity is created
        Name = "Player";
        
        // Setup components
        _transform = AddComponent<TransformComponent>();
        _transform.Position = new Vector2(400, 300);
        
        _sprite = AddComponent<SpriteComponent>();
        _sprite.Width = 32;
        _sprite.Height = 32;
        _sprite.Color = Color.Blue;
        
        _health = AddComponent<HealthComponent>();
        _health.Max = 100;
        _health.Current = 100;
        
        Tags.Add("Player");
    }
    
    public override void OnUpdate(GameTime gameTime)
    {
        // Custom player logic here
        HandleMovement(gameTime);
        
        // ✅ Call base to update components
        base.OnUpdate(gameTime);
    }
    
    public override void OnRender(IRenderer renderer)
    {
        // Custom rendering (optional)
        // Components render automatically via base.OnRender()
    }
    
    public override void OnDestroy()
    {
        // Cleanup logic
        Logger.LogInformation("Player destroyed");
        
        // ✅ Call base to cleanup components
        base.OnDestroy();
    }
    
    private void HandleMovement(GameTime gameTime)
    {
        // Player-specific logic
    }
}

// Usage
var player = World.CreateEntity<PlayerEntity>();
```

**Pattern:** Custom entities encapsulate initialization and behavior - Unity GameObject style.

---

## Entity Lifecycle

### Complete Lifecycle Flow

```mermaid
stateDiagram-v2
    [*] --> Created: World.CreateEntity()
    
    Created --> Initializing: OnInitialize()
    note right of Initializing
        Called once
        Setup components
        Add tags
    end note
    
    Initializing --> Active: Added to World
    
    Active --> Updating: OnUpdate(gameTime)
    note right of Updating
        Called every frame
        Update logic
        Base calls component.OnUpdate()
    end note
    
    Updating --> Rendering: OnRender(renderer)
    note right of Rendering
        Called every frame
        Custom rendering
        Base calls component.OnRender()
    end note
    
    Rendering --> Active: Frame complete
    
    Active --> Destroying: World.DestroyEntity()
    
    Destroying --> Cleanup: OnDestroy()
    note right of Cleanup
        Called once
        Cleanup resources
        Base removes all components
    end note
    
    Cleanup --> [*]
```

---

### Lifecycle Methods

#### OnInitialize()

```csharp
public override void OnInitialize()
{
    // ✅ Called once when entity is created
    // Use for: Setup, adding components, initializing state
    
    Name = "MyEntity";
    
    var transform = AddComponent<TransformComponent>();
    transform.Position = new Vector2(100, 100);
    
    Tags.Add("Enemy");
    
    Logger.LogInformation("Entity {Name} initialized", Name);
}
```

**Use for:**
- Adding components
- Initial state setup
- Adding tags
- One-time configuration

---

#### OnUpdate(gameTime)

```csharp
public override void OnUpdate(GameTime gameTime)
{
    // ✅ Called every frame (if IsActive = true)
    // Use for: Game logic, movement, state changes
    
    var transform = GetComponent<TransformComponent>();
    if (transform != null)
    {
        // Custom logic
        transform.Position += new Vector2(100, 0) * (float)gameTime.DeltaTime;
    }
    
    // ✅ ALWAYS call base to update components!
    base.OnUpdate(gameTime);
}
```

**Important:** Call `base.OnUpdate(gameTime)` to update all components!

**Use for:**
- Per-frame logic
- State updates
- Behavior implementation
- Input handling

---

#### OnRender(renderer)

```csharp
public override void OnRender(IRenderer renderer)
{
    // ✅ Called every frame during render phase
    // Use for: Custom rendering, debug visualization
    
    var transform = GetComponent<TransformComponent>();
    if (transform != null)
    {
        // Custom rendering
        renderer.DrawCircleOutline(
            transform.Position.X,
            transform.Position.Y,
            50f,
            Color.Red,
            2f);
    }
    
    // Components render automatically (SpriteComponent, etc.)
    // No need to call base unless you want default behavior
}
```

**Use for:**
- Custom rendering
- Debug visualization
- Effects overlays

---

#### OnDestroy()

```csharp
public override void OnDestroy()
{
    // ✅ Called once when entity is destroyed
    // Use for: Cleanup, disposing resources, saving state
    
    Logger.LogInformation("Entity {Name} destroyed", Name);
    
    // Cleanup custom resources
    _customTexture?.Dispose();
    
    // ✅ ALWAYS call base to cleanup components!
    base.OnDestroy();
}
```

**Important:** Call `base.OnDestroy()` to cleanup all components!

**Use for:**
- Resource disposal
- State saving
- Event unsubscription
- Custom cleanup

---

## Component Management

### Adding Components

```csharp
// Method 1: Create and add in one step
var transform = entity.AddComponent<TransformComponent>();
transform.Position = new Vector2(100, 100);

// Method 2: Add pre-configured component
var sprite = new SpriteComponent
{
    Width = 32,
    Height = 32,
    Color = Color.Red
};
entity.AddComponent(sprite);

// ✅ Adding duplicate components returns existing
var transform2 = entity.AddComponent<TransformComponent>();
// transform2 == transform (same instance)
```

**Pattern:** `AddComponent<T>()` prevents duplicates - returns existing if already added.

---

### Getting Components

```csharp
// Method 1: Try get (safe)
var transform = entity.GetComponent<TransformComponent>();
if (transform != null)
{
    transform.Position += Vector2.One;
}

// Method 2: Get required (throws if missing - ASP.NET pattern)
var transform = entity.GetRequiredComponent<TransformComponent>();
transform.Position += Vector2.One; // Safe, guaranteed to exist

// Method 3: Check existence
if (entity.HasComponent<HealthComponent>())
{
    var health = entity.GetComponent<HealthComponent>();
    health.TakeDamage(10);
}
```

**Pattern:** Use `GetComponent<T>()` for optional components, `GetRequiredComponent<T>()` when component must exist.

---

### Removing Components

```csharp
// Remove component by type
bool removed = entity.RemoveComponent<VelocityComponent>();

if (removed)
{
    Logger.LogInformation("Velocity removed");
}

// Get all components
var allComponents = entity.GetAllComponents();
foreach (var component in allComponents)
{
    Logger.LogDebug("Component: {Type}", component.GetType().Name);
}
```

**Pattern:** Removing components calls `OnRemoved()` lifecycle method on the component.

---

## Tag Management

### Working with Tags

```csharp
// Add tags
entity.Tags.Add("Enemy");
entity.Tags.Add("Flying");
entity.Tags.Add("Boss");

// Check tags
if (entity.Tags.Contains("Enemy"))
{
    // Enemy logic
}

// Remove tags
entity.Tags.Remove("Flying");

// Clear all tags
entity.Tags.Clear();

// Query by tags
var enemies = World.GetEntitiesByTag("Enemy");
var bosses = World.GetEntitiesByTag("Boss");

// Multiple tag check
if (entity.Tags.Contains("Enemy") && entity.Tags.Contains("Boss"))
{
    // Boss enemy logic
}
```

**Use tags for:**
- Category identification (Enemy, Player, Projectile)
- Behavior flags (Flying, Invincible, Stunned)
- Querying entities quickly
- Temporary states

---

## Entity State

### IsActive Flag

```csharp
// Create entity
var enemy = World.CreateEntity("Enemy");
enemy.IsActive = true; // Active by default

// Temporarily disable
enemy.IsActive = false; // Won't be updated or rendered

// Re-enable
enemy.IsActive = true;

// ✅ World.Update() skips inactive entities
// ✅ Queries can filter by IsActive
```

**Pattern:** Use `IsActive` to temporarily disable entities without destroying them.

---

### Destroying Entities

```csharp
// Method 1: Via World
World.DestroyEntity(entity);

// Method 2: Self-destruct
entity.Destroy(); // Calls World.DestroyEntity(this)

// ✅ Destruction is deferred if called during frame update
// Entity marked inactive immediately, removed at frame boundary
```

**Pattern:** Destruction is deferred during frame processing - safe to call in `OnUpdate()`.

---

## Entity Hierarchy (Advanced)

### Parent-Child Relationships

Entities can form hierarchies using **TransformComponent**:

```csharp
using Brine2D.ECS;
using Brine2D.ECS.Components;

// Create parent
var tank = World.CreateEntity("Tank");
var tankTransform = tank.AddComponent<TransformComponent>();
tankTransform.Position = new Vector2(400, 300);

// Create child (turret)
var turret = World.CreateEntity("Turret");
var turretTransform = turret.AddComponent<TransformComponent>();
turretTransform.Position = new Vector2(0, -20); // Relative to parent

// ✅ Set parent via extension method
turret.SetParent(tank);

// Child moves with parent
tankTransform.Position = new Vector2(500, 300);
// turret world position is now (500, 280)

// Get parent
var parent = turret.GetParent(); // Returns tank

// Get children
var children = tank.GetChildren(); // Returns turret

// Get all descendants (recursive)
var descendants = tank.GetDescendants();
```

**Pattern:** Hierarchy is managed through `TransformComponent` - children move/rotate with parent.

---

### Hierarchy Extension Methods

```csharp
// Set parent (keeping world position)
entity.SetParent(parent, keepWorldPosition: true);

// Set parent (using local position)
entity.SetParent(parent, keepWorldPosition: false);

// Get parent entity
Entity? parent = entity.GetParent();

// Get all direct children
IEnumerable<Entity> children = entity.GetChildren();

// Get all descendants (children + grandchildren + ...)
IEnumerable<Entity> descendants = entity.GetDescendants();

// Get root entity (topmost parent)
Entity root = entity.GetRoot();

// Remove from hierarchy
entity.SetParent(null);
```

**Use hierarchy for:**
- Complex objects (tank + turret)
- UI layouts (panel + buttons)
- Character rigs (body + limbs)
- Scene graphs

---

## Entity Patterns

### Pattern 1: Entity Factories

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Components;
using System.Numerics;

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
        entity.Tags.Add("Controllable");
        
        return entity;
    }
    
    public static Entity CreateEnemy(IEntityWorld world, Vector2 position, EnemyType type)
    {
        var entity = world.CreateEntity($"Enemy_{type}");
        
        var transform = entity.AddComponent<TransformComponent>();
        transform.Position = position;
        
        var sprite = entity.AddComponent<SpriteComponent>();
        sprite.Width = 24;
        sprite.Height = 24;
        sprite.Color = type switch
        {
            EnemyType.Grunt => Color.Red,
            EnemyType.Tank => Color.DarkRed,
            EnemyType.Flyer => Color.Orange,
            _ => Color.Red
        };
        
        var health = entity.AddComponent<HealthComponent>();
        health.Max = type switch
        {
            EnemyType.Grunt => 50,
            EnemyType.Tank => 200,
            EnemyType.Flyer => 30,
            _ => 50
        };
        health.Current = health.Max;
        
        entity.Tags.Add("Enemy");
        if (type == EnemyType.Flyer)
        {
            entity.Tags.Add("Flying");
        }
        
        return entity;
    }
}

// Usage
var player = EntityFactory.CreatePlayer(World, new Vector2(400, 300));
var grunt = EntityFactory.CreateEnemy(World, new Vector2(200, 200), EnemyType.Grunt);
```

**Pattern:** Factory methods encapsulate entity creation - clean, reusable, testable.

---

### Pattern 2: Prefabs (Entity Templates)

```csharp
using Brine2D.ECS;
using Brine2D.ECS.Components;

public class EntityPrefabs
{
    public static void ApplyPlayerPrefab(Entity entity, Vector2 position)
    {
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
    }
    
    public static void ApplyPowerupPrefab(Entity entity, Vector2 position)
    {
        var transform = entity.AddComponent<TransformComponent>();
        transform.Position = position;
        
        var sprite = entity.AddComponent<SpriteComponent>();
        sprite.Width = 16;
        sprite.Height = 16;
        sprite.Color = Color.Yellow;
        
        var lifetime = entity.AddComponent<LifetimeComponent>();
        lifetime.TimeToLive = 10f; // Despawn after 10 seconds
        
        entity.Tags.Add("Pickup");
    }
}

// Usage
var player = World.CreateEntity("Player");
EntityPrefabs.ApplyPlayerPrefab(player, new Vector2(400, 300));

var powerup = World.CreateEntity("Powerup");
EntityPrefabs.ApplyPowerupPrefab(powerup, new Vector2(600, 200));
```

**Pattern:** Prefab methods apply pre-configured component sets to entities.

---

### Pattern 3: Entity Pooling

```csharp
public class EntityPool
{
    private readonly IEntityWorld _world;
    private readonly Stack<Entity> _pool = new();
    private readonly Func<Entity> _factory;
    
    public EntityPool(IEntityWorld world, Func<Entity> factory, int initialSize = 10)
    {
        _world = world;
        _factory = factory;
        
        // Pre-create entities
        for (int i = 0; i < initialSize; i++)
        {
            var entity = _factory();
            entity.IsActive = false;
            _pool.Push(entity);
        }
    }
    
    public Entity Get()
    {
        if (_pool.Count > 0)
        {
            var entity = _pool.Pop();
            entity.IsActive = true;
            return entity;
        }
        
        // Create new if pool exhausted
        return _factory();
    }
    
    public void Return(Entity entity)
    {
        entity.IsActive = false;
        _pool.Push(entity);
    }
}

// Usage
var projectilePool = new EntityPool(
    World,
    () => EntityFactory.CreateProjectile(World, Vector2.Zero),
    initialSize: 50);

// Get from pool
var projectile = projectilePool.Get();
var transform = projectile.GetComponent<TransformComponent>();
transform.Position = playerPosition;

// Return to pool (instead of destroying)
projectilePool.Return(projectile);
```

**Pattern:** Object pooling reduces allocations - use for frequently created/destroyed entities (projectiles, particles).

---

## Best Practices

### ✅ DO

**1. Use factories for complex entities**

```csharp
// ✅ Good - encapsulated creation
var player = EntityFactory.CreatePlayer(World, position);

// ❌ Bad - scattered creation logic
var player = World.CreateEntity("Player");
player.AddComponent<TransformComponent>().Position = position;
player.AddComponent<SpriteComponent>().Width = 32;
// ... repeated everywhere
```

**2. Use tags for categorization**

```csharp
// ✅ Good - tags for quick lookup
entity.Tags.Add("Enemy");
entity.Tags.Add("Flying");
var enemies = World.GetEntitiesByTag("Enemy");

// ❌ Bad - tag components for simple categories
public class EnemyTag : Component { } // Overkill for simple flag
```

**3. Call base in lifecycle methods**

```csharp
// ✅ Good - components update
public override void OnUpdate(GameTime gameTime)
{
    // Custom logic
    base.OnUpdate(gameTime); // Updates components
}

// ❌ Bad - components never update
public override void OnUpdate(GameTime gameTime)
{
    // Custom logic
    // Missing base.OnUpdate() - components won't update!
}
```

**4. Use GetRequiredComponent for essential components**

```csharp
// ✅ Good - fail fast if missing
var transform = entity.GetRequiredComponent<TransformComponent>();
transform.Position += Vector2.One;

// ❌ Bad - null checks everywhere
var transform = entity.GetComponent<TransformComponent>();
if (transform != null)
{
    transform.Position += Vector2.One;
}
```

---

### ❌ DON'T

**1. Don't store entity references long-term**

```csharp
// ❌ Bad - entity reference can become invalid
private Entity? _target;

public void SetTarget(Entity target)
{
    _target = target; // Might be destroyed later!
}

// ✅ Good - store entity ID
private Guid _targetId;

public void SetTarget(Entity target)
{
    _targetId = target.Id;
}

public Entity? GetTarget()
{
    return World?.GetEntityById(_targetId);
}
```

**2. Don't create entities during iteration**

```csharp
// ❌ Bad - modifying collection during iteration
foreach (var entity in World.Entities)
{
    World.CreateEntity("New"); // ❌ Can cause issues
}

// ✅ Good - defer creation
var entitiesToCreate = new List<Action>();

foreach (var entity in World.Entities)
{
    entitiesToCreate.Add(() => World.CreateEntity("New"));
}

foreach (var create in entitiesToCreate)
{
    create();
}
```

**3. Don't forget to call base in OnDestroy**

```csharp
// ❌ Bad - components not cleaned up
public override void OnDestroy()
{
    // Cleanup
    // Missing base.OnDestroy() - components leak!
}

// ✅ Good - components cleaned up
public override void OnDestroy()
{
    // Cleanup
    base.OnDestroy(); // Removes all components
}
```

**4. Don't use entities for simple data**

```csharp
// ❌ Bad - entity for simple value
var scoreEntity = World.CreateEntity("Score");
scoreEntity.AddComponent<ScoreComponent>().Value = 0;

// ✅ Good - use a field/property
private int _score = 0;
```

---

## Summary

**Entity features:**

| Feature | Usage |
|---------|-------|
| **World.CreateEntity()** | Create entities |
| **Entity.AddComponent<T>()** | Add components |
| **Entity.GetComponent<T>()** | Get components (safe) |
| **Entity.GetRequiredComponent<T>()** | Get components (throws if missing) |
| **Entity.Tags** | Categorize entities |
| **Entity.IsActive** | Enable/disable entity |
| **Entity.Destroy()** | Remove from world |

**Lifecycle methods:**

| Method | When Called | Use For |
|--------|-------------|---------|
| **OnInitialize()** | Once (creation) | Setup, add components |
| **OnUpdate(gameTime)** | Every frame | Game logic, state updates |
| **OnRender(renderer)** | Every frame | Custom rendering |
| **OnDestroy()** | Once (destruction) | Cleanup, save state |

**Common patterns:**

| Pattern | Usage |
|---------|-------|
| **Entity factories** | Encapsulate creation logic |
| **Custom entities** | Inherit for specialized behavior |
| **Tags** | Quick categorization and lookup |
| **Hierarchy** | Parent-child relationships via Transform |
| **Pooling** | Reuse entities (projectiles, particles) |

---

## Next Steps

- **[Components Guide](components.md)** - Deep dive into components with methods
- **[Systems Guide](systems.md)** - Optional systems for performance
- **[Queries Guide](queries.md)** - Find entities efficiently
- **[ECS Getting Started](getting-started.md)** - Complete ECS tutorial
- **[ECS Concepts](../../concepts/entity-component-system.md)** - Understanding hybrid ECS

---

**Remember:** Entities are flexible - use them as simple component containers or derive custom classes for specialized behavior. Tags make lookups fast, and World scoping means automatic cleanup! 🎮