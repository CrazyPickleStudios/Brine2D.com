---
title: ECS Queries
description: Master entity querying and filtering in Brine2D's ECS
---

# ECS Queries

Queries are how you **find and filter entities** in Brine2D's ECS. Think of them like LINQ or SQL queries - you specify what you're looking for, and the ECS returns matching entities efficiently.

## What Are Queries?

**Queries find entities** based on:
- Components they have (With/Without)
- Tags they contain
- Properties and conditions (Where)
- **Fluent API for complex searches**
- **Cached queries for zero-allocation performance**

```csharp
// Find all entities with Health component
var withHealth = world.GetEntitiesWithComponent<HealthComponent>();

// Find all enemies
var enemies = world.GetEntitiesByTag("Enemy");

// Fluent query API
var weakEnemies = world.Query()
    .With<HealthComponent>()
    .With<TransformComponent>()
    .Without<DeadComponent>()
    .WithTag("Enemy")
    .Where(e =>
    {
        var health = e.GetComponent<HealthComponent>();
        return health.CurrentHealth < 50;
    })
    .Execute();
```

---

## Advanced Query System

Brine2D introduces a powerful fluent query API for building complex entity searches.

### Fluent Query API

Build queries with a chainable, readable syntax:

```csharp
using Brine2D.ECS.Query;

// Find low-health enemies near the player
var dangerousEnemies = _world.Query()
    .With<EnemyComponent>()
    .With<HealthComponent>()
    .With<TransformComponent>()
    .Without<DeadComponent>()
    .WithTag("Boss")
    .Where(e => 
    {
        var health = e.GetComponent<HealthComponent>();
        var transform = e.GetComponent<TransformComponent>();
        var distance = Vector2.Distance(transform.Position, playerPosition);
        
        return health.CurrentHealth < 50 && distance < 200f;
    })
    .Execute();

foreach (var enemy in dangerousEnemies)
{
    Logger.LogInformation("Dangerous enemy: {Name}", enemy.Name);
}
```

### Query Builder Methods

| Method | Description | Example |
|--------|-------------|---------|
| `With<T>()` | Requires component | `.With<HealthComponent>()` |
| `Without<T>()` | Excludes component | `.Without<DeadComponent>()` |
| `WithTag(string)` | Requires tag | `.WithTag("Enemy")` |
| `WithoutTag(string)` | Excludes tag | `.WithoutTag("Dead")` |
| `Where(predicate)` | Custom filter | `.Where(e => e.IsActive)` |
| `Execute()` | Run query | `.Execute()` |

### Cached Queries for Performance

**Cached queries** are pre-compiled and automatically updated - perfect for systems that run every frame:

```csharp
public class MovementSystem : GameSystem
{
    private readonly CachedQuery<TransformComponent, VelocityComponent> _movingEntities;
    
    public MovementSystem(IEntityWorld world) : base(world, 100)
    {
        // Create cached query (updates automatically when entities change)
        _movingEntities = world.CreateCachedQuery<TransformComponent, VelocityComponent>();
    }
    
    public override void Update(GameTime gameTime)
    {
        var deltaTime = (float)gameTime.DeltaTime;
        
        // Zero-allocation iteration!
        foreach (var (transform, velocity) in _movingEntities)
        {
            transform.Position += velocity.Velocity * deltaTime;
        }
    }
}
```

**Benefits:**
- ✅ **Zero allocation** - No garbage collection pressure
- ✅ **Automatic updates** - Stays in sync with world changes
- ✅ **Type-safe** - Compile-time component checking
- ✅ **Fast iteration** - Direct component access

### Multi-Component Cached Queries

Query up to **5 components** simultaneously:

```csharp
// 2 components
var query2 = world.CreateCachedQuery<TransformComponent, VelocityComponent>();

// 3 components
var query3 = world.CreateCachedQuery<TransformComponent, SpriteComponent, AnimatorComponent>();

// 4 components
var query4 = world.CreateCachedQuery<TransformComponent, HealthComponent, AIComponent, VelocityComponent>();

// 5 components
var query5 = world.CreateCachedQuery<TransformComponent, HealthComponent, VelocityComponent, SpriteComponent, AIComponent>();

// Use with tuple deconstruction
foreach (var (transform, sprite, animator) in query3)
{
    // All components guaranteed to exist
    animator.Update(deltaTime);
    sprite.CurrentFrame = animator.CurrentFrame;
}
```

### Query Performance Comparison

```csharp
// ❌ Slow - Creates new list every frame
public override void Update(GameTime gameTime)
{
    var moving = _world.GetEntitiesWithComponents<TransformComponent, VelocityComponent>();
    
    foreach (var entity in moving)
    {
        var transform = entity.GetComponent<TransformComponent>();
        var velocity = entity.GetComponent<VelocityComponent>();
        transform.Position += velocity.Velocity * deltaTime;
    }
}

// ✅ Fast - Cached query, zero allocation
public override void Update(GameTime gameTime)
{
    foreach (var (transform, velocity) in _movingEntities)
    {
        transform.Position += velocity.Velocity * deltaTime;
    }
}
```

### Complex Query Example

Combining fluent API with cached queries:

```csharp
public class CombatSystem : GameSystem
{
    private readonly CachedQuery<TransformComponent, HealthComponent> _damageable;
    private Entity _player;
    
    public override void Update(GameTime gameTime)
    {
        var playerTransform = _player.GetComponent<TransformComponent>();
        var attackRange = 100f;
        
        // Find targets with fluent API
        var targets = _world.Query()
            .With<HealthComponent>()
            .With<TransformComponent>()
            .WithTag("Enemy")
            .Without<DeadComponent>()
            .Where(e =>
            {
                var transform = e.GetComponent<TransformComponent>();
                var distance = Vector2.Distance(transform.Position, playerTransform.Position);
                return distance < attackRange;
            })
            .Execute();
        
        foreach (var target in targets)
        {
            ApplyDamage(target, 10);
        }
    }
}
```

---

## Basic Queries

### Query All Entities

```csharp
// Get all entities in the world
IReadOnlyList<Entity> allEntities = world.Entities;

foreach (var entity in allEntities)
{
    Console.WriteLine($"{entity.Name} ({entity.Id})");
}
```

### Query by Single Component

```csharp
// Get all entities with a specific component
var withHealth = world.GetEntitiesWithComponent<HealthComponent>();

foreach (var entity in withHealth)
{
    var health = entity.GetComponent<HealthComponent>()!;
    Console.WriteLine($"{entity.Name}: {health.Current}/{health.Max} HP");
}
```

### Query by Multiple Components

```csharp
// Get entities that have BOTH components
var moving = world.GetEntitiesWithComponents<TransformComponent, VelocityComponent>();

foreach (var entity in moving)
{
    var transform = entity.GetComponent<TransformComponent>()!;
    var velocity = entity.GetComponent<VelocityComponent>()!;
    
    Console.WriteLine($"{entity.Name} at {transform.Position}, moving {velocity.Velocity}");
}
```

### Query by Tag

```csharp
// Get all entities with a specific tag
var enemies = world.GetEntitiesByTag("Enemy");

foreach (var enemy in enemies)
{
    Console.WriteLine($"Enemy: {enemy.Name}");
}

// Check multiple tags (manual filtering)
var bossEnemies = world.GetEntitiesByTag("Enemy")
    .Where(e => e.Tags.Contains("Boss"));
```

---

## Finding Specific Entities

### Find by Name

```csharp
// Find first entity with exact name
var player = world.GetEntityByName("Player");

if (player != null)
{
    Console.WriteLine($"Found player: {player.Id}");
}
```

### Find by ID

```csharp
// Find entity by unique ID
Guid entityId = someEntity.Id;
var found = world.GetEntityById(entityId);

if (found != null)
{
    Console.WriteLine($"Found entity: {found.Name}");
}
```

### Find by Predicate

```csharp
// Find first entity matching custom condition
var boss = world.FindEntity(e => 
    e.Tags.Contains("Enemy") && 
    e.Name.Contains("Boss") &&
    e.IsActive
);

if (boss != null)
{
    Console.WriteLine($"Found boss: {boss.Name}");
}
```

---

## Filtering Queries

### LINQ-Style Filtering

```csharp
using System.Linq;

// Get active enemies with low health
var weakEnemies = world.GetEntitiesByTag("Enemy")
    .Where(e => e.IsActive)
    .Where(e =>
    {
        var health = e.GetComponent<HealthComponent>();
        return health != null && health.Percentage < 0.3f;
    });

// Get all projectiles moving right
var rightMoving = world.GetEntitiesWithComponent<VelocityComponent>()
    .Where(e => e.Tags.Contains("Projectile"))
    .Where(e => e.GetComponent<VelocityComponent>()!.Velocity.X > 0);

// Get enemies within view distance of player
var nearbyEnemies = world.GetEntitiesByTag("Enemy")
    .Where(e =>
    {
        var enemyTransform = e.GetComponent<TransformComponent>();
        var playerTransform = player.GetComponent<TransformComponent>();
        
        if (enemyTransform == null || playerTransform == null) return false;
        
        var distance = Vector2.Distance(enemyTransform.Position, playerTransform.Position);
        return distance < 500f;
    });
```

---

## Spatial Queries

### Distance-Based Queries

```csharp
// Extension method for radius queries
public static class SpatialQueryExtensions
{
    public static IEnumerable<Entity> WithinRadius(
        this IEnumerable<Entity> entities,
        Vector2 center,
        float radius)
    {
        var radiusSquared = radius * radius;
        
        return entities.Where(e =>
        {
            var transform = e.GetComponent<TransformComponent>();
            if (transform == null) return false;
            
            // Use DistanceSquared for better performance (avoid sqrt)
            var distanceSquared = Vector2.DistanceSquared(transform.Position, center);
            return distanceSquared <= radiusSquared;
        });
    }
}

// Usage
var playerPos = player.GetComponent<TransformComponent>()!.Position;
var nearbyEnemies = world.GetEntitiesByTag("Enemy")
    .WithinRadius(playerPos, 200f);
```

---

## Query Performance Tips

### Do's and Don'ts

```csharp
// ✅ DO: Use cached queries in systems
var _cachedQuery = world.CreateCachedQuery<TransformComponent, VelocityComponent>();

// ❌ DON'T: Query every frame without caching
var moving = world.GetEntitiesWithComponents<TransformComponent, VelocityComponent>();

// ✅ DO: Use fluent API for complex queries
var targets = world.Query()
    .With<HealthComponent>()
    .WithTag("Enemy")
    .Without<DeadComponent>()
    .Execute();

// ❌ DON'T: Chain LINQ Where clauses unnecessarily
var targets = world.Entities
    .Where(e => e.HasComponent<HealthComponent>())
    .Where(e => e.Tags.Contains("Enemy"))
    .Where(e => !e.Tags.Contains("Dead"));

// ✅ DO: Use Any() for existence checks
var hasEnemies = world.GetEntitiesByTag("Enemy").Any();

// ❌ DON'T: Use Count() for existence checks
var hasEnemies = world.GetEntitiesByTag("Enemy").Count() > 0;
```

---

## Quick Reference

### Fluent Query API

```csharp
world.Query()                                       // Start query builder
    .With<T>()                                      // Require component
    .Without<T>()                                   // Exclude component
    .WithTag("tag")                                 // Require tag
    .WithoutTag("tag")                              // Exclude tag
    .Where(e => condition)                          // Custom filter
    .Execute()                                      // Run query
```

### Cached Queries

```csharp
world.CreateCachedQuery<T>()                        // 1 component
world.CreateCachedQuery<T1, T2>()                   // 2 components
world.CreateCachedQuery<T1, T2, T3>()               // 3 components
world.CreateCachedQuery<T1, T2, T3, T4>()           // 4 components
world.CreateCachedQuery<T1, T2, T3, T4, T5>()       // 5 components
```

### Basic Queries

```csharp
world.Entities                                      // All entities
world.GetEntityByName("Player")                     // By name
world.GetEntityById(guid)                           // By ID
world.GetEntitiesByTag("Enemy")                     // By tag
world.GetEntitiesWithComponent<T>()                 // By component
world.GetEntitiesWithComponents<T1, T2>()           // By multiple components
world.FindEntity(e => /* condition */)              // By predicate
```

---

## See It In Action

Check out the **Query System Demo** in FeatureDemos to see advanced queries in action!

```bash
cd samples/FeatureDemos
dotnet run
# Select "1" for Query System Demo
```

---

## Next Steps

Now that you've mastered queries, explore related topics:

<div class="grid cards" markdown>

-   **FeatureDemos**

    ---

    See Query System Demo in action

    [:octicons-arrow-right-24: View Demos](../../samples/index.md)

-   **Systems Guide**

    ---

    Use queries in systems for performance

    [:octicons-arrow-right-24: Systems Guide](systems.md)

-   **Components Guide**

    ---

    Design effective components for querying

    [:octicons-arrow-right-24: Components Guide](components.md)

</div>

---

**Remember:** Use **cached queries** in systems that run every frame, and **fluent API** for complex one-time searches. Always profile your queries!