---
title: ECS Getting Started
description: End-to-end walkthrough of Brine2D's hybrid ECBS — entities, components, behaviors, and systems
---

# ECS Getting Started

This guide walks through the four concepts of Brine2D's **hybrid ECBS** model — Components, Behaviors, Systems, and Entities — with working code for each.

**Prerequisites:** Completed [Quick Start](../../getting-started/quickstart.md) and basic C# knowledge.

---

## World Access

Every scene exposes a `World` property set automatically by the framework. No constructor injection needed.

```csharp
public class GameScene : Scene
{
    protected override void OnEnter()
    {
        var player = World.CreateEntity("Player");
        Logger.LogInformation("World has {Count} entities", World.EntityCount);
    }
}
```

Each scene gets its own isolated `IEntityWorld` that is disposed automatically when the scene unloads.

---

## Components — pure data

Components hold state only. They inherit from `Component` and have no per-frame logic.

```csharp
public class HealthComponent : Component
{
    public int HP    { get; set; } = 100;
    public int MaxHP { get; set; } = 100;
}

public class SpeedComponent : Component
{
    public float Value { get; set; } = 200f;
}
```

**Component lifecycle hooks** (override when needed):

```csharp
public class HealthComponent : Component
{
    public int HP    { get; set; } = 100;
    public int MaxHP { get; set; } = 100;

    protected internal override void OnAdded()
    {
        // Called once when added to an entity.
    }

    protected internal override void OnRemoved()
    {
        // Called once when removed from an entity.
    }

    protected internal override void OnEnabled()  { }  // IsEnabled → true
    protected internal override void OnDisabled() { }  // IsEnabled → false
}
```

Components do **not** have `Update` or `Render` methods. Per-frame logic belongs in a **Behavior** or **System**.

[:octicons-arrow-right-24: Full reference: Components](components.md)

---

## Behaviors — entity logic with DI

A `Behavior` is attached to one entity, constructed via DI, and participates in the Update/FixedUpdate/Render pipelines.

```csharp
public class PlayerMovementBehavior : Behavior
{
    private readonly IInputContext _input;
    private TransformComponent _transform = null!;

    // Constructor injection — any registered service can go here
    public PlayerMovementBehavior(IInputContext input) => _input = input;

    // OnAdded fires immediately when AddBehavior<T>() is called.
    // Cache required components here.
    protected override void OnAdded()
        => _transform = Entity!.GetRequiredComponent<TransformComponent>();

    // OnStart fires once before the very first Update/FixedUpdate/Render tick.
    // Use it for cross-entity lookups that need the full scene to be built first.
    public override void OnStart() { }

    public override void Update(GameTime gameTime)
    {
        var speed = Entity!.GetComponent<SpeedComponent>()?.Value ?? 200f;
        var delta = (float)gameTime.DeltaTime;

        if (_input.IsKeyDown(Key.W)) _transform.Position -= new Vector2(0, speed * delta);
        if (_input.IsKeyDown(Key.S)) _transform.Position += new Vector2(0, speed * delta);
        if (_input.IsKeyDown(Key.A)) _transform.Position -= new Vector2(speed * delta, 0);
        if (_input.IsKeyDown(Key.D)) _transform.Position += new Vector2(speed * delta, 0);
    }

    // FixedUpdate runs at a fixed timestep — use for physics-driven logic.
    public override void FixedUpdate(GameTime fixedTime) { }

    // Render runs after all systems have rendered.
    public override void Render(IRenderer renderer, GameTime gameTime) { }

    // Called when the owning entity is destroyed.
    protected override void OnDestroyed() { }

    // Called when RemoveBehavior<T>() is called explicitly.
    protected override void OnRemoved() { }
}
```

**Execution order** — control with `UpdateOrder` / `FixedUpdateOrder` / `RenderOrder`:

```csharp
public override int UpdateOrder      => 10;   // lower runs first; default 0
public override int FixedUpdateOrder => 0;
public override int RenderOrder      => 0;
```

**React to component changes:**

```csharp
protected override void OnComponentAdded(Component component)
{
    if (component is WeaponComponent weapon)
        _activeWeapon = weapon;
}

protected override void OnComponentRemoved(Component component)
{
    if (component is WeaponComponent)
        _activeWeapon = null;
}
```

---

## Creating Entities

`CreateEntity` returns the entity. `AddComponent` and `AddBehavior` return the same entity for chaining:

```csharp
protected override void OnEnter()
{
    World.CreateEntity("Player")
        .AddComponent<TransformComponent>(t => t.Position = new Vector2(400, 300))
        .AddComponent<SpriteComponent>(s => s.TexturePath = "assets/player.png")
        .AddComponent<HealthComponent>()
        .AddComponent<SpeedComponent>(s => s.Value = 300f)
        .AddBehavior<PlayerMovementBehavior>()
        .AddTag("Player");

    for (int i = 0; i < 5; i++)
    {
        World.CreateEntity($"Enemy{i}")
            .AddComponent<TransformComponent>(t => t.Position = new Vector2(100 + i * 80, 200))
            .AddComponent<SpriteComponent>()
            .AddComponent<HealthComponent>(h => h.HP = 50)
            .AddBehavior<EnemyAIBehavior>()
            .AddTag("Enemy");
    }
}
```

---

## EntityPrefab — reusable templates

`EntityPrefab` defines a template once and instantiates it many times:

```csharp
var coinPrefab = new EntityPrefab("Coin")
    .AddComponent<TransformComponent>()
    .AddComponent<SpriteComponent>(s => s.TexturePath = "assets/coin.png")
    .AddBehavior<CoinBehavior>()
    .AddTag("Pickup");

// Spawn many coins
for (int i = 0; i < 20; i++)
    coinPrefab.Instantiate(World, position: new Vector2(i * 40, 500));
```

Prefabs support child prefabs and per-instantiation overrides via the optional `configure` callback on `Instantiate`.

---

## Systems — batch processing

Systems extend one of the three base classes. All three take `IEntityWorld` and `GameTime` (render systems also take `IRenderer`):

```csharp
public class HealOverTimeSystem : UpdateSystemBase
{
    public override int UpdateOrder => SystemUpdateOrder.LateUpdate;

    public override void Update(IEntityWorld world, GameTime gameTime)
    {
        world.Query()
            .With<HealthComponent>()
            .WithTag("Player")
            .ForEach<HealthComponent>((entity, health) =>
            {
                if (health.HP < health.MaxHP)
                    health.HP = Math.Min(health.MaxHP, health.HP + (int)(5 * gameTime.DeltaTime));
            });
    }
}
```

Add a custom system from `OnEnter`. Remove a default system you don't need:

```csharp
protected override void OnEnter()
{
    World.AddSystem<HealOverTimeSystem>();
    World.RemoveSystem<ParticleSystem>();   // remove a default system
}
```

[:octicons-arrow-right-24: Full reference: Systems](systems.md)

---

## Queries — finding entities

**One-shot query** — re-evaluated every call:

```csharp
World.Query()
    .With<TransformComponent>()
    .WithTag("Enemy")
    .Without<DeadComponent>()
    .ForEach<TransformComponent>((entity, t) =>
    {
        // process each matching entity
    });

// Execute() returns IEnumerable<Entity> if you need the list
foreach (var entity in World.Query().WithTag("Pickup").Execute())
    Logger.LogDebug("Pickup: {Name}", entity.Name);
```

**Cached query** — built once in `OnEnter`, rebuilds only when components change:

```csharp
private CachedEntityQuery<TransformComponent, HealthComponent>? _enemyQuery;

protected override void OnEnter()
{
    _enemyQuery = World.CreateCachedQuery<TransformComponent, HealthComponent>()
        .WithTag("Enemy")
        .Build();
}

protected override void OnUpdate(GameTime gameTime)
{
    _enemyQuery!.ForEach((entity, t, health) =>
    {
        // zero allocation per frame
    });
}
```

[:octicons-arrow-right-24: Full reference: Queries](queries.md)

---

## Entity Management

```csharp
// Destroy
entity.Destroy();                       // safe to call from Update/FixedUpdate
World.DestroyEntity(entity);            // same thing via the world

// Find
var player    = World.GetEntityByName("Player");
var byId      = World.GetEntityById(someId);          // id is long
var enemies   = World.GetEntitiesByTag("Enemy");
var tagged    = World.GetEntitiesByTag("Enemy", includeInactive: true);

// Activate / deactivate
entity.IsActive = false;                // skipped by all queries and pipelines
entity.SetActiveHierarchically(false);  // cascades to all children

// Clear all entities without resetting systems
World.ClearEntities();
```

---

## Tags

Tags are strings added via fluent methods that return the entity:

```csharp
entity.AddTag("Enemy")
      .AddTag("Flying")
      .AddTags("Boss", "Invincible");

entity.HasTag("Enemy");           // true
entity.HasAllTags("Boss", "Flying");
entity.HasAnyTag("Flying", "Swimming");

entity.RemoveTag("Invincible");
entity.ClearTags();
```

---

## IsActive and IsEnabled

**`Entity.IsActive`** — when `false`, the entity is skipped entirely by all systems, behaviors, and queries (unless you call `IncludeInactive()`).

**`Component.IsEnabled`** — when `false`, built-in systems skip that specific component while the entity and other components continue processing. Cached queries built with `.OnlyEnabled()` are automatically invalidated when this changes.

**`Behavior.IsEnabled`** — when `false`, `Update/FixedUpdate/Render` are not called for that behavior.

---

## Summary

| Concept | What it does | Base type |
|---------|-------------|-----------|
| `Component` | Holds state | `Component` |
| `Behavior` | Per-entity logic + DI | `Behavior` |
| `UpdateSystemBase` | Batch update logic | `UpdateSystemBase` |
| `RenderSystemBase` | Batch render logic | `RenderSystemBase` |
| `FixedUpdateSystemBase` | Fixed-timestep logic | `FixedUpdateSystemBase` |
| `EntityPrefab` | Reusable entity template | — |

**Next steps:**

- [Components](components.md) — lifecycle hooks and the `IsEnabled` flag
- [Systems](systems.md) — base classes, ordering constants, registration
- [Queries](queries.md) — full filter reference and cached query patterns
- [Entities](entities.md) — hierarchy, prefabs, serialization

---
