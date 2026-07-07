---
title: Systems
description: Update, render, and fixed-update system base classes, ordering constants, and registration in Brine2D
---

# Systems

Systems process all entities matching a given component profile each frame. They are the batch-processing layer of the ECBS — while Behaviors handle per-entity logic with DI and lifecycle hooks, a System iterates many entities efficiently in a single pass.

Systems are optional. Most game logic fits naturally in Behaviors. Reach for a System when you need to process large numbers of entities at once, want to centralize cross-cutting logic (e.g., all physics bodies in one place), or need fine-grained control over execution order relative to other systems.

---

## The Three System Types

| Base Class | Override | Signature |
|------------|----------|-----------|
| `UpdateSystemBase` | `Update` | `void Update(IEntityWorld world, GameTime gameTime)` |
| `RenderSystemBase` | `Render` | `void Render(IEntityWorld world, IRenderer renderer, GameTime gameTime)` |
| `FixedUpdateSystemBase` | `FixedUpdate` | `void FixedUpdate(IEntityWorld world, GameTime fixedTime)` |

All three share the same optional hooks and the same `IsEnabled` toggle.

---

## UpdateSystemBase

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Query;
using Brine2D.ECS.Systems;
using Brine2D.ECS.Components;

public class MovementSystem : UpdateSystemBase
{
	private CachedEntityQuery<TransformComponent, VelocityComponent>? _query;

	public override int UpdateOrder => SystemUpdateOrder.Physics;

	public override void OnStart(IEntityWorld world)
	{
		_query = world.CreateCachedQuery<TransformComponent, VelocityComponent>().Build();
	}

	public override void Update(IEntityWorld world, GameTime gameTime)
	{
		float dt = (float)gameTime.ElapsedGameTime.TotalSeconds;
		_query!.ForEach((entity, transform, velocity) =>
		{
			transform.Position += velocity.Value * dt;
		});
	}

	protected override void Dispose(bool disposing)
	{
		if (disposing) _query?.Dispose();
		base.Dispose(disposing);
	}
}
```

---

## RenderSystemBase

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Query;
using Brine2D.ECS.Systems;
using Brine2D.Rendering;

public class SpriteRenderSystem : RenderSystemBase
{
	private CachedEntityQuery<TransformComponent, SpriteComponent>? _query;

	public override int RenderOrder => SystemRenderOrder.Sprites;

	public override void OnStart(IEntityWorld world)
	{
		_query = world.CreateCachedQuery<TransformComponent, SpriteComponent>().Build();
	}

	public override void Render(IEntityWorld world, IRenderer renderer, GameTime gameTime)
	{
		_query!.ForEach((entity, transform, sprite) =>
		{
			renderer.DrawSprite(sprite.Texture, transform.Position);
		});
	}

	protected override void Dispose(bool disposing)
	{
		if (disposing) _query?.Dispose();
		base.Dispose(disposing);
	}
}
```

---

## FixedUpdateSystemBase

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Systems;

public class PhysicsSystem : FixedUpdateSystemBase
{
	public override int FixedUpdateOrder => SystemFixedUpdateOrder.Physics;

	public override void FixedUpdate(IEntityWorld world, GameTime fixedTime)
	{
		// fixedTime.ElapsedGameTime is always the configured fixed timestep
		world.Query()
			 .With<RigidBodyComponent>()
			 .ForEach<RigidBodyComponent>((entity, rb) => rb.Step());
	}
}
```

---

## OnStart

All three base classes call `OnStart(IEntityWorld)` once, before the first tick. Use it to create cached queries and other one-time setup that needs the world to be ready:

```csharp
public override void OnStart(IEntityWorld world)
{
	_query = world.CreateCachedQuery<HealthComponent>().Build();
}
```

If `OnStart` throws, the system sets `StartFailed = true` and skips every subsequent tick. Call `ResetStart()` to allow a retry on the next frame.

---

## IsEnabled

```csharp
World.GetSystem<MovementSystem>().IsEnabled = false; // pause
World.GetSystem<MovementSystem>().IsEnabled = true;  // resume
```

---

## Execution Order Constants

### SystemUpdateOrder

| Constant | Value | Typical Use |
|----------|-------|-------------|
| `PreInput` | -200 | Input buffering, replay |
| `Input` | -100 | Keyboard/mouse/gamepad reading |
| `PostInput` | -50 | Input smoothing, dead zones |
| `EarlyUpdate` | -25 | Pre-frame setup |
| `Update` | **0** | Default — most game logic |
| `PostUpdate` | 50 | Post-logic, pre-physics |
| `PrePhysics` | 90 | Force accumulation |
| `Physics` | 100 | Velocity integration |
| `PostPhysics` | 150 | Physics cleanup |
| `Collision` | 200 | Collision detection |
| `PostCollision` | 250 | Damage, triggers |
| `Animation` | 400 | Skeletal/sprite animation |
| `Particles` | 500 | Visual effects |
| `Audio` | 600 | 3-D audio positioning |
| `LateUpdate` | 800 | Camera follow, UI |
| `VeryLateUpdate` | 900 | Final position adjustments |
| `PreRender` | 1000 | Frustum culling |

Use offsets for fine-grained control:

```csharp
public override int UpdateOrder => SystemUpdateOrder.Physics + 10; // just after physics
```

### SystemRenderOrder

| Constant | Value |
|----------|-------|
| `Background` | -100 |
| `Tilemap` | -50 |
| `Sprites` | **0** |
| `Particles` | 100 |
| `Lighting` | 500 |
| `UI` | 900 |
| `Debug` | 1000 |

### SystemFixedUpdateOrder

| Constant | Value |
|----------|-------|
| `EarlyFixedUpdate` | -100 |
| `PrePhysics` | -50 |
| `Physics` | **0** |
| `PostPhysics` | 50 |
| `Collision` | 100 |

---

## Registering Systems

Register systems in your scene's `OnLoadAsync`:

```csharp
protected override async Task OnLoadAsync(CancellationToken ct)
{
	World.AddSystem<MovementSystem>();
	World.AddSystem<SpriteRenderSystem>();
	World.AddSystem<PhysicsSystem>();
}
```

Systems are instantiated via DI, so constructor injection works:

```csharp
public class AudioPositioningSystem : UpdateSystemBase
{
	private readonly IAudioService _audio;

	public AudioPositioningSystem(IAudioService audio)
	{
		_audio = audio;
	}

	public override void Update(IEntityWorld world, GameTime gameTime) { /* ... */ }
}
```

---

## Removing Systems

```csharp
World.RemoveSystem<MovementSystem>();
```

The system's `Dispose` method is called automatically when it is removed or when the world is torn down.

---

## [Sequential] Attribute

By default, cached query iteration inside a system can run in parallel when `ECSOptions.EnableMultiThreading` is `true`. Apply `[Sequential]` to force a single-threaded pass for systems with ordering dependencies or non-thread-safe state:

```csharp
[Sequential]
public class SaveStateSystem : UpdateSystemBase
{
	public override void Update(IEntityWorld world, GameTime gameTime)
	{
		// writes to a shared file — must be single-threaded
	}
}
```

`[Sequential]` is **not inherited**: derived classes must re-apply it if needed.

---

## Disposing Cached Queries

Every `CachedEntityQuery<...>` you create registers itself in the world's invalidation index. You must dispose it when the system is disposed, or it will remain registered until the entire world is torn down:

```csharp
protected override void Dispose(bool disposing)
{
	if (disposing)
	{
		_movementQuery?.Dispose();
		_renderQuery?.Dispose();
	}
	base.Dispose(disposing);
}
```

---

## Related Topics

- [Queries](queries.md) — full filter reference for both one-shot and cached queries
- [Multi-threading](multi-threading.md) — parallel query execution and `ECSOptions`
- [Getting Started](getting-started.md) — end-to-end walkthrough
