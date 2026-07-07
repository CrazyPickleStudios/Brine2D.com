---
title: Multi-threading
description: Parallel cached-query iteration in Brine2D — ECSOptions, thresholds, and opting out
---

# Multi-threading

Brine2D can parallelize the **iteration** of cached entity queries across worker threads. This is controlled entirely by `ECSOptions` and the `[Sequential]` attribute — no manual threading code is needed.

---

## What Is Parallelized

Only **cached query iteration** (`CachedEntityQuery<T...>.ForEach(...)`) is parallelized. System and behavior dispatch always runs sequentially on the calling thread. Individual systems opt out via `[Sequential]`.

One-shot queries (`World.Query().ForEach(...)`) are always sequential regardless of settings.

---

## ECSOptions

Configure multi-threading when registering the ECS in your DI setup:

```csharp
services.AddBrine2DECS(options =>
{
	options.EnableMultiThreading    = true;   // default: true
	options.WorkerThreadCount       = 4;      // default: Environment.ProcessorCount
	options.ParallelEntityThreshold = 100;    // default: 100
});
```

### EnableMultiThreading

```csharp
options.EnableMultiThreading = true;
```

When `true`, cached queries with at least `ParallelEntityThreshold` matching entities iterate in parallel. When `false`, all query iteration is sequential regardless of entity count.

### WorkerThreadCount

```csharp
options.WorkerThreadCount = 4;
```

Number of worker threads used for parallel iteration. `null` (the default) uses `Environment.ProcessorCount`. Valid range: 1–128.

### ParallelEntityThreshold

```csharp
options.ParallelEntityThreshold = 100;
```

Queries with fewer than this many matching entities fall back to sequential iteration to avoid thread-dispatch overhead. Lower values give more aggressive parallelism; higher values reduce overhead for lightweight components. Default is 100.

---

## Additional ECSOptions

| Property | Default | Description |
|----------|---------|-------------|
| `InitialEntityCapacity` | 1000 | Pre-allocated entity slots. Avoids resize during gameplay. Valid range: 16–1,000,000. |
| `FixedTimeStepMs` | `1000.0 / 60.0` | Fixed timestep in ms (~16.67 ms = 60 steps/s). |
| `MaxFixedStepsPerFrame` | 8 | Caps fixed-step catch-up after long frames (e.g. debugger pause). |
| `PropagateExceptions` | `true` (Debug) / `false` (Release) | Re-throw system/behavior exceptions after logging. |
| `OnExceptionSwallowed` | `null` | Callback invoked when an exception is swallowed (`PropagateExceptions = false`). Use for crash reporters. |
| `OnFixedUpdateAccumulatorClamped` | `null` | Callback invoked when excess simulation time is discarded by `MaxFixedStepsPerFrame`. |

---

## Opting Out Per System — [Sequential]

Apply `[Sequential]` to a system to force its cached query iterations to always be sequential, even when global multi-threading is on. Use this for systems that write to shared non-thread-safe state or require strict ordering within a single `ForEach` pass:

```csharp
using Brine2D.ECS.Systems;

[Sequential]
public class SaveStateSystem : UpdateSystemBase
{
	public override void Update(IEntityWorld world, GameTime gameTime)
	{
		// writes to a shared file — must be single-threaded
	}
}
```

`[Sequential]` is **not inherited**. A derived class does not automatically inherit the attribute and will run in parallel unless it also declares `[Sequential]`.

---

## Thread Safety Guidance

When `EnableMultiThreading` is `true`, the action passed to `CachedEntityQuery<T...>.ForEach(...)` runs concurrently across entities. Keep your iteration lambdas thread-safe:

**Safe:**
- Reading and writing components on the entity passed to the callback (each entity is visited once, by one thread)
- Reading shared read-only data (constants, immutable collections)

**Unsafe:**
- Writing to shared mutable state (counters, lists, dictionaries) without synchronization
- Calling `World.CreateEntity` / `World.DestroyEntity` from inside `ForEach`
- Reading components on a *different* entity than the one passed (may race with another thread visiting that entity)

For aggregation, use local state and combine afterward:

```csharp
int totalDamage = 0;
object _lock = new();

_query.ForEach((entity, health) =>
{
	int dmg = ComputeDamage(entity, health);
	lock (_lock) totalDamage += dmg;
});
```

Or apply `[Sequential]` to the system if thread-safe aggregation is too complex.

---

## Recommended Settings

| Scenario | Recommendation |
|----------|----------------|
| Prototyping / small games | Leave defaults (`EnableMultiThreading = true`, threshold 100) |
| Many lightweight entities (1 000+) | Lower threshold to 50 |
| Heavy per-entity work (physics, pathfinding) | Lower threshold or set `WorkerThreadCount` to available cores |
| Systems with shared mutable state | Apply `[Sequential]` to those systems |
| Single-core or WebAssembly targets | `EnableMultiThreading = false` |

---

## Related Topics

- [Systems](systems.md) — base classes, `[Sequential]`, registration
- [Queries](queries.md) — cached query creation and filters
