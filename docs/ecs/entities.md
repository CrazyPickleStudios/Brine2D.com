---
title: Entities
description: Entity lifecycle, hierarchy, tags, components, and prefabs in Brine2D
---

# Entities

An **Entity** is the fundamental container in the ECS. It holds components and behaviors, participates in the scene hierarchy, and can be queried by the system layer.

---

## Creating Entities

Use `World.CreateEntity()` from inside a scene or system:

```csharp
// Named entity
var player = World.CreateEntity("Player");

// Generic overload for a subclass (rare; prefer components/behaviors)
var enemy = World.CreateEntity<EnemyEntity>("Enemy");
```

---

## Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `Id` | `long` | Unique process-wide ID. Assigned atomically at creation; never reused. `0` is an invalid sentinel. |
| `Name` | `string` | Human-readable name. Not required to be unique. |
| `World` | `IEntityWorld?` | The world this entity belongs to. `null` if not yet in a world. |
| `IsActive` | `bool` | Whether the entity is processed by systems and queries. See [IsActive](#isactive). |
| `Parent` | `Entity?` | Parent entity, or `null` if this is a root entity. |
| `Children` | `IReadOnlyList<Entity>` | Direct children. |
| `IsRoot` | `bool` | `true` when `Parent == null`. |
| `Tags` | `IReadOnlySet<string>` | Current tag set. |

---

## Lifecycle Methods

Override these in an `Entity` subclass (advanced usage). For most cases, use **Behaviors** instead.

```csharp
public class PlayerEntity : Entity
{
	protected internal override void OnInitialize()
	{
		// Called once when added to the world.
	}

	protected internal override void OnActivated()
	{
		// Called when IsActive changes false → true.
	}

	protected internal override void OnDeactivated()
	{
		// Called when IsActive changes true → false.
	}

	protected internal override void OnDestroy()
	{
		// Called during destruction, before components are removed.
		base.OnDestroy(); // always call base — it handles children + components
	}
}
```

---

## IsActive

`IsActive` controls whether the entity is included in query results and processed by systems.

```csharp
entity.IsActive = false; // deactivate just this entity
entity.IsActive = true;  // reactivate
```

Toggling `IsActive` is **non-cascading** — children keep their own `IsActive` state. To toggle an entire hierarchy at once:

```csharp
entity.SetActiveHierarchically(false); // deactivates entity + all descendants
entity.SetActiveHierarchically(true);  // reactivates entity + all descendants
```

When an entity becomes inactive, `OnDeactivated` fires on the entity and `OnDisabled` fires on every enabled component and behavior. The reverse happens on reactivation.

---

## Component Management

All component methods return `this` for fluent chaining.

```csharp
entity
	.AddComponent<TransformComponent>(t => t.Position = new Vector2(100, 200))
	.AddComponent<HealthComponent>(h => { h.HP = 50; h.MaxHP = 100; });
```

| Method | Description |
|--------|-------------|
| `AddComponent<T>()` | Creates a new `T` and attaches it. Silently ignored if already present. |
| `AddComponent<T>(Action<T>)` | Creates, configures, then attaches `T`. |
| `AddComponent<T>(T component)` | Attaches an existing instance. |
| `GetComponent<T>()` | Returns the component or `null`. |
| `TryGetComponent<T>(out T?)` | Single pool lookup; avoids double-check pattern. |
| `GetRequiredComponent<T>()` | Returns the component or throws with a diagnostic message. |
| `HasComponent<T>()` | `true` if this entity currently has `T`. |
| `RemoveComponent<T>()` | Detaches and returns `true` if found, `false` otherwise. |
| `GetAllComponents()` | Enumerates all attached components. |
| `GetComponentInChildren<T>()` | Depth-first search through children. |
| `GetComponentInParent<T>()` | Walks up the parent chain. |

---

## Tag Management

Tags are plain strings. All tag methods return `this`.

```csharp
entity.AddTag("Enemy").AddTag("Boss");
entity.AddTags("Hostile", "Damageable");

bool isEnemy = entity.HasTag("Enemy");
bool isBoth  = entity.HasAllTags("Enemy", "Hostile");
bool isEither = entity.HasAnyTag("Boss", "Elite");

entity.RemoveTag("Boss");
entity.ClearTags();
```

---

## Hierarchy

```csharp
// Set a parent
child.SetParent(parent);

// Add a child (equivalent to child.SetParent(parent))
parent.AddChild(child);

// Detach from parent
child.DetachFromParent();

// Remove a specific child
parent.RemoveChild(child);
```

**Hierarchy traversal:**

```csharp
// Depth-first iteration (allocates per call; fine for one-off use)
foreach (var desc in entity.GetDescendants())
	Console.WriteLine(desc.Name);

// Zero-copy equivalent for hot paths (reuse the list)
var buffer = new List<Entity>();
entity.CollectDescendants(buffer);

// Search helpers
var healthBar  = entity.FindDescendant("HealthBar");
var hostiles   = entity.GetDescendantsWithTag("Hostile");
int depth      = entity.GetDepth();   // 0 = root
var root       = entity.GetRoot();
```

**Circular hierarchy and cross-world parenting** are both rejected: circular attempts are silently ignored (logged as warnings); cross-world parenting throws `InvalidOperationException`.

---

## Destroying Entities

```csharp
entity.Destroy();
// or
World.DestroyEntity(entity);
```

Destruction is **deferred** until the end of the current frame so that in-flight iterations remain safe. The entity's `OnDestroy` is called immediately, which recursively destroys children in depth-first order. Components receive `OnRemoved` during destruction. After the frame, the entity is fully removed from all pools and indexes.

After `Destroy()`, the entity's `Component.Entity` references are set to `null`. Cache checks like `component.Entity == null` can detect whether the owner has been destroyed.

---

## Prefabs

`EntityPrefab` is a reusable entity template. Define it once, instantiate many times.

### Defining a Prefab

```csharp
var enemyPrefab = new EntityPrefab("Enemy")
	.AddTag("Enemy")
	.AddTag("Hostile")
	.AddComponent<TransformComponent>()
	.AddComponent<HealthComponent>(h => h.MaxHP = 50)
	.AddBehavior<EnemyAIBehavior>(ai => ai.PatrolRadius = 200f);
```

### Child Prefabs

```csharp
var shadowPrefab  = new EntityPrefab("Shadow").AddComponent<SpriteComponent>();
var weaponPrefab  = new EntityPrefab("Sword").AddComponent<TransformComponent>();

var enemyPrefab = new EntityPrefab("Enemy")
	.AddComponent<TransformComponent>()
	.AddChildPrefab(shadowPrefab)
	.AddChildPrefab(weaponPrefab, child =>
		child.GetComponent<TransformComponent>()!.Position = new Vector2(16, 0));
```

Child prefabs are instantiated and parented automatically each time the root prefab is instantiated.

### Instantiating

```csharp
// Basic
var enemy = enemyPrefab.Instantiate(World);

// With spawn transform
var enemy2 = enemyPrefab.Instantiate(World,
	position: new Vector2(300, 150),
	rotation: 0.5f,
	scale:    new Vector2(1.5f, 1.5f));

// Override name (useful when spawning multiple instances)
var enemy3 = enemyPrefab.Instantiate(World, position: spawnPoint, name: "Elite Enemy");
```

`Instantiate` creates the entity, applies tags, runs all component/behavior configurators, sets the spawn transform on the `TransformComponent` if present, and recursively instantiates child prefabs.

---

## Related Topics

- [Components](components.md) — data containers and lifecycle hooks
- [Getting Started](getting-started.md) — end-to-end walkthrough
- [Queries](queries.md) — find entities by tag, component, or spatial criteria
- [Systems](systems.md) — batch-process all entities per frame
