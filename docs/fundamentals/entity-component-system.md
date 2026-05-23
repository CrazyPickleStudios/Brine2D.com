---
title: ECS Deep Dive
description: Understanding Brine2D's hybrid Entity Component System architecture
---

# Entity Component System

Brine2D uses a **hybrid ECS** designed to be beginner-friendly with optional performance optimization. You don't need to learn systems or queries to get started - components and behaviors are enough for most games.

## The Three Building Blocks

| Concept | Purpose | Example |
|---------|---------|---------|
| **Component** | Data container with lifecycle hooks | `HealthComponent`, `TransformComponent` |
| **Behavior** | Per-entity logic with DI support | `PlayerMovementBehavior`, `EnemyAIBehavior` |
| **System** | Batch processing for performance | `MovementSystem`, `CollisionDetectionSystem` |

## Quick Example

```csharp
// 1. Component - data
public class HealthComponent : Component
{
    public int Current { get; set; } = 100;
    public int Max { get; set; } = 100;

    protected internal override void OnAdded() => Current = Max;
}

// 2. Behavior - per-entity logic
public class DamageFlashBehavior : Behavior
{
    protected override void Update(GameTime gameTime)
    {
        var health = Entity.GetComponent<HealthComponent>();
        if (health != null && health.Current < health.Max)
        {
            // Flash red when damaged
        }
    }
}

// 3. Use in a scene
protected override void OnEnter()
{
    var player = World.CreateEntity("Player");
    player.AddComponent<HealthComponent>();
    player.AddBehavior<DamageFlashBehavior>();
}
```

## When to Use What

| Scenario | Components | Behaviors | Systems |
|----------|-----------|-----------|---------|
| Data storage | :white_check_mark: | :x: | :x: |
| Unique behavior (player, boss) | :white_check_mark: | :white_check_mark: | :x: |
| Simple games (< 500 entities) | :white_check_mark: | :white_check_mark: | :x: |
| Performance-critical (1000+ entities) | :white_check_mark: | :x: | :white_check_mark: |

**Rule of thumb:** Start with components + behaviors, add systems only if profiling shows a need.

## Scoped World

Each scene gets its own `IEntityWorld`. Entities are destroyed automatically when the scene unloads:

```csharp
protected override void OnEnter()
{
    World.CreateEntity("Player");
    World.CreateEntity("Enemy");
    // Both destroyed automatically when scene unloads - no cleanup needed!
}
```

## Learn More

For the complete ECS guide with detailed coverage of entities, components, behaviors, systems, and queries:

[:octicons-arrow-right-24: ECS - Full Guide](../ecs/index.md)

[:octicons-arrow-right-24: ECS Getting Started](../ecs/getting-started.md)

[:octicons-arrow-right-24: Entities](../ecs/entities.md) |
[:octicons-arrow-right-24: Components](../ecs/components.md) |
[:octicons-arrow-right-24: Systems](../ecs/systems.md) |
[:octicons-arrow-right-24: Queries](../ecs/queries.md)