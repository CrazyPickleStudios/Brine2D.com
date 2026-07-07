---
title: Queries
description: One-shot and cached entity queries — filters, execution, and ForEach in Brine2D
---

# Queries

Brine2D has two complementary query APIs:

| Type | Created via | Use when |
|------|-------------|----------|
| `EntityQuery` | `World.Query()` | One-shot or infrequent queries |
| `CachedEntityQuery<T...>` | `World.CreateCachedQuery<T...>().Build()` | Per-frame iteration in systems |

---

## One-Shot Queries — EntityQuery

`World.Query()` starts a fluent builder. Call `Execute()` to enumerate the results, or any of the terminal helpers (`First()`, `ForEach(...)`, `Count()`, `Any()`, `Random()`).

```csharp
// All active enemies in a radius
var nearby = World.Query()
	.With<TransformComponent>()
	.WithTag("Enemy")
	.WithinRadius(playerPos, 300f)
	.Execute();

foreach (var entity in nearby)
	Console.WriteLine(entity.Name);
```

Because `Execute()` re-evaluates the full filter set on every call, prefer `CachedEntityQuery` inside system `Update` loops.

---

## EntityQuery Filter Methods

### Component Filters

| Method | Description |
|--------|-------------|
| `.With<T>()` | Entity must have component `T`. |
| `.With<T>(filter)` | Entity must have `T` and the component must pass the predicate. |
| `.Without<T>()` | Entity must NOT have component `T`. |

### Behavior Filters

| Method | Description |
|--------|-------------|
| `.WithBehavior<T>()` | Entity must have behavior `T`. |
| `.WithoutBehavior<T>()` | Entity must NOT have behavior `T`. |

### Tag Filters

| Method | Description |
|--------|-------------|
| `.WithTag(tag)` | Entity must have this tag. |
| `.WithoutTag(tag)` | Entity must NOT have this tag. |
| `.WithAllTags(...)` | Entity must have every tag in the list. |
| `.WithAnyTag(...)` | Entity must have at least one tag in the list. |

### Activity / Enable Filters

| Method | Description |
|--------|-------------|
| `.OnlyActive()` | Active entities only (**default**). |
| `.IncludeInactive()` | Include inactive entities too. |
| `.OnlyEnabled()` | Additionally require all `.With<T>()` components to have `IsEnabled = true`. |

### Spatial Filters

Both require the entity to have a `TransformComponent`.

| Method | Description |
|--------|-------------|
| `.WithinRadius(center, radius)` | Entity's position within a circular radius. |
| `.WithinBounds(Rectangle)` | Entity's position inside a rectangle. |

These filters can be combined:

```csharp
World.Query()
	.With<TransformComponent>()
	.WithinRadius(origin, 400f)
	.WithinBounds(screenRect)
	.ForEach(e => e.AddTag("Visible"));
```

### Custom Predicate

```csharp
World.Query()
	.With<HealthComponent>()
	.Where(e => e.GetComponent<HealthComponent>()!.HP < 20)
	.ForEach(e => e.AddTag("Critical"));
```

### Sorting and Pagination

```csharp
var ranked = World.Query()
	.With<ScoreComponent>()
	.OrderByDescending(e => e.GetComponent<ScoreComponent>()!.Value)
	.Take(10)
	.Execute();
```

| Method | Description |
|--------|-------------|
| `.OrderBy<TKey>(selector)` | Ascending sort. |
| `.OrderByDescending<TKey>(selector)` | Descending sort. |
| `.ThenBy<TKey>(selector)` | Secondary ascending sort (tie-breaker). |
| `.ThenByDescending<TKey>(selector)` | Secondary descending sort. |
| `.Take(n)` | Return at most N entities. |
| `.Skip(n)` | Skip the first N entities. |

---

## Terminal Methods

### Execute

```csharp
IEnumerable<Entity> results = World.Query().With<HealthComponent>().Execute();
```

### ForEach

`ForEach` has component-typed overloads that resolve components directly from their pool, avoiding a second lookup per entity:

```csharp
// Entity only
World.Query().ForEach(entity => Console.WriteLine(entity.Name));

// Entity + 1 component
World.Query().With<HealthComponent>().ForEach<HealthComponent>(
	(entity, health) => health.HP -= 10);

// Entity + 2 components
World.Query().With<TransformComponent>().With<VelocityComponent>()
	.ForEach<TransformComponent, VelocityComponent>(
		(entity, t, v) => t.Position += v.Value * dt);

// Up to 4 components supported
```

### Other Terminals

| Method | Description |
|--------|-------------|
| `.First()` | First matching entity, or `null`. |
| `.Count()` | Number of matching entities. |
| `.Any()` | `true` if at least one entity matches. |
| `.Random()` | Single random entity via reservoir sampling (no full materialisation). |
| `.Random(n)` | `n` random entities via reservoir sampling. |
| `.Clone()` | Copy the query for further modification. |

---

## Cached Queries — CachedEntityQuery

Cached queries store the matching entity set and only rebuild when a structural change (component added/removed, tag added/removed, entity destroyed, `IsActive` changed, `IsEnabled` changed) invalidates the cache. This makes per-frame iteration fast.

### Creating and Storing

Create in `OnStart`, store as a field, dispose in `Dispose`:

```csharp
public class MovementSystem : UpdateSystemBase
{
	private CachedEntityQuery<TransformComponent, VelocityComponent>? _query;

	public override void OnStart(IEntityWorld world)
	{
		_query = world.CreateCachedQuery<TransformComponent, VelocityComponent>()
			.WithTag("Movable")
			.OnlyEnabled()
			.Build();
	}

	public override void Update(IEntityWorld world, GameTime gameTime)
	{
		float dt = (float)gameTime.ElapsedGameTime.TotalSeconds;
		_query!.ForEach((entity, transform, velocity) =>
			transform.Position += velocity.Value * dt);
	}

	protected override void Dispose(bool disposing)
	{
		if (disposing) _query?.Dispose();
		base.Dispose(disposing);
	}
}
```

Arities 1–5 are supported:

```csharp
world.CreateCachedQuery<TransformComponent>().Build()
world.CreateCachedQuery<TransformComponent, SpriteComponent>().Build()
world.CreateCachedQuery<TransformComponent, RigidBodyComponent, ColliderComponent>().Build()
// … up to 5 type parameters
```

### CachedEntityQueryBuilder Filters

The builder supports the same filter categories as `EntityQuery`:

| Method | Description |
|--------|-------------|
| `.WithTag(tag)` | Must have tag. |
| `.WithAllTags(...)` | Must have all tags. |
| `.WithAnyTag(...)` | Must have any of the tags. |
| `.WithoutTag(tag)` | Must NOT have tag. |
| `.Without<T>()` | Must NOT have component `T`. |
| `.WithBehavior<T>()` | Must have behavior `T`. |
| `.WithoutBehavior<T>()` | Must NOT have behavior `T`. |
| `.IncludeInactive()` | Include inactive entities (default: active only). |
| `.OnlyEnabled()` | Require required components to have `IsEnabled = true`. |
| `.WithinRadius(center, r)` | Position check at cache-rebuild time (see note below). |
| `.WithinBounds(Rectangle)` | Bounds check at cache-rebuild time (see note below). |
| `.Where(predicate)` | Custom entity-level predicate. |
| `.WithComponentFilter<T>(predicate)` | Component-level predicate (avoids extra pool lookup). |

!!! note "Spatial filters and cached queries"
	Spatial filters on cached queries are evaluated when the cache **rebuilds** (i.e. on the first structural change after the last query execution). Because position changes are not structural events, the cached result may be stale if entities move between structural changes. Use `World.Query().WithinRadius(...)` for queries that must reflect current-frame positions.

---

## Query Invalidation

A cached query marks itself dirty and rebuilds on next access when any of these occur:

- A component matching one of the query's required or excluded types is added or removed
- A tag matching any of the query's tag filters is added or removed
- An entity in the result set is destroyed
- Any entity's `IsActive` changes (when using `OnlyActive` / `IncludeInactive`)
- Any required component's `IsEnabled` changes (when using `OnlyEnabled`)

---

## Disposing Cached Queries

Always dispose cached queries in the system's `Dispose` override. A disposed query unregisters itself from the world's invalidation index:

```csharp
protected override void Dispose(bool disposing)
{
	if (disposing) _query?.Dispose();
	base.Dispose(disposing);
}
```

Forgetting to dispose leaves the query object alive in the world's internal index until the world itself is disposed, preventing GC of the query and anything it references.

---

## Related Topics

- [Systems](systems.md) — where cached queries are used
- [Multi-threading](multi-threading.md) — parallel `ForEach` inside cached queries
- [Entities](entities.md) — tags, `IsActive`, hierarchy
- [Components](components.md) — `IsEnabled`, lifecycle hooks
