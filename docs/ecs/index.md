---
title: Entity Component System
description: Build flexible game objects with Brine2D's hybrid ECBS architecture
---

# Entity Component System

Brine2D uses a **hybrid Entity–Component–Behavior–System (ECBS)** model. Each concept has a specific role:

| Concept | Purpose | DI support |
|---------|---------|-----------|
| **Component** | Pure data, no logic | — |
| **Behavior** | Entity-specific logic | ✅ Full injection |
| **System** | Batch processing across many entities | ✅ Constructor injection |

---

## Quick Start

```csharp
public class GameScene : Scene
{
    protected override void OnEnter()
    {
        World.CreateEntity("Player")
            .AddComponent<TransformComponent>(t => t.Position = new Vector2(400, 300))
            .AddComponent<SpriteComponent>(s => s.TexturePath = "assets/player.png")
            .AddBehavior<PlayerMovementBehavior>();
    }
}
```

`World` is a framework property available in every scene — no constructor injection needed.

---

## Topics

### Core

| Guide | Description |
|-------|-------------|
| **[Getting Started](getting-started.md)** | End-to-end walkthrough of the ECBS API |
| **[Entities](entities.md)** | Create, tag, activate, and destroy entities |
| **[Components](components.md)** | Pure-data components and their lifecycle hooks |

### Logic and Processing

| Guide | Description |
|-------|-------------|
| **[Systems](systems.md)** | Batch-process entities each frame |
| **[Queries](queries.md)** | Find entities with fluent and cached queries |

### Advanced

| Guide | Description |
|-------|-------------|
| **[Multi-Threading](multi-threading.md)** | Automatic parallel query iteration |

---

## The Four Concepts

### Component — pure data

```csharp
public class HealthComponent : Component
{
    public int HP    { get; set; } = 100;
    public int MaxHP { get; set; } = 100;
}
```

Components inherit from `Component` and hold state only. Logic belongs in Behaviors or Systems.

[:octicons-arrow-right-24: Components guide](components.md)

---

### Behavior — entity-specific logic with DI

```csharp
public class PlayerMovementBehavior : Behavior
{
    private readonly IInputContext _input;
    private TransformComponent _transform = null!;

    public PlayerMovementBehavior(IInputContext input) => _input = input;

    protected override void OnAdded()
        => _transform = Entity!.GetRequiredComponent<TransformComponent>();

    public override void Update(GameTime gameTime)
    {
        if (_input.IsKeyDown(Key.D))
            _transform.Position += new Vector2(200f * (float)gameTime.DeltaTime, 0);
    }
}
```

Behaviors are created via DI, attached to one entity, and participate in the Update/FixedUpdate/Render pipelines.

[:octicons-arrow-right-24: Behaviors are covered in the Getting Started guide](getting-started.md)

---

### System — batch processing

```csharp
public class GravitySystem : UpdateSystemBase
{
    public override int UpdateOrder => SystemUpdateOrder.Physics;

    public override void Update(IEntityWorld world, GameTime gameTime)
    {
        world.Query()
            .With<TransformComponent>()
            .With<PhysicsBodyComponent>()
            .ForEach<TransformComponent, PhysicsBodyComponent>((entity, t, body) =>
            {
                body.Velocity += new Vector2(0, 980f) * (float)gameTime.DeltaTime;
                t.Position    += body.Velocity        * (float)gameTime.DeltaTime;
            });
    }
}
```

Systems extend `UpdateSystemBase`, `RenderSystemBase`, or `FixedUpdateSystemBase`.

[:octicons-arrow-right-24: Systems guide](systems.md)

---

### Queries — find entities

```csharp
// One-shot fluent query
World.Query()
    .With<TransformComponent>()
    .WithTag("Enemy")
    .WithinRadius(playerPos, 200f)
    .ForEach<TransformComponent>((entity, t) => { /* ... */ });

// Cached query — built once, rebuilds only when components change
private CachedEntityQuery<TransformComponent, EnemyComponent>? _enemyQuery;

protected override void OnEnter()
{
    _enemyQuery = World.CreateCachedQuery<TransformComponent, EnemyComponent>()
        .WithTag("active")
        .Build();
}
```

[:octicons-arrow-right-24: Queries guide](queries.md)

---

## Default Systems

These systems are added to every scene automatically:

| System | Pipeline | Order | Purpose |
|--------|----------|-------|---------|
| `SpriteRenderingSystem` | Render | 0 | Sprite batching and culling |
| `AudioSystem` | Update | 0 | Spatial audio processing |
| `ParticleSystem` | Both | 250 / 100 | GPU-instanced particles |
| `AnimationSystem` | Update | 400 | Sprite animation and state machines |
| `CameraSystem` | Update | 500 | Camera follow and zoom |
| `DebugRenderer` | Render | 1000 | Debug visualization (disabled by default) |

Enable/disable or remove them from `OnEnter`:

```csharp
protected override void OnEnter()
{
    World.GetSystem<ParticleSystem>()!.IsEnabled = false;
    World.GetSystem<DebugRenderer>()!.IsEnabled  = true;
}
```

> Physics systems are opt-in. Call `builder.Services.AddPhysics()` then `World.AddSystem<Box2DPhysicsSystem>()`.

---

## When to Use What

| Situation | Use |
|-----------|-----|
| Per-entity input, AI, or effects | `Behavior` |
| Batch physics, rendering, collision | `System` |
| Pure state (position, health, flags) | `Component` |
| Finding groups of entities per frame | Cached `EntityQuery` |

---

## Related Topics

- [Getting Started](getting-started.md) — end-to-end walkthrough
- [Entities](entities.md) — entity management
- [Components](components.md) — component lifecycle
- [Systems](systems.md) — system base classes and ordering
- [Queries](queries.md) — fluent and cached queries
- [Multi-Threading](multi-threading.md) — automatic parallel iteration
- [Fundamentals: ECBS Architecture](../fundamentals/entity-component-system.md) — design rationale


**Ready to build with ECS?** Start with [Getting Started](getting-started.md)!