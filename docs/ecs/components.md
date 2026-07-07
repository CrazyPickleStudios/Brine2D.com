---
title: Components
description: Pure-data components in Brine2D's ECBS — properties, lifecycle hooks, and IsEnabled
---

# Components

Components are **pure data containers**. They inherit from `Component`, hold state, and expose lifecycle hooks that fire at well-defined attachment/removal moments. Per-frame logic belongs in a **Behavior** or **System**.

---

## Defining a Component

```csharp
using Brine2D.ECS;

public class HealthComponent : Component
{
	public int HP    { get; set; } = 100;
	public int MaxHP { get; set; } = 100;
}
```

That's the minimum. Properties of any type — value types, strings, collections, nested objects — are all fine.

---

## Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `Entity` | `Entity?` | The entity this component is attached to. `null` after removal. |
| `IsEnabled` | `bool` | Whether this component is currently enabled. See [IsEnabled](#isenabled). |

---

## Lifecycle Hooks

Override any of these virtual methods to react to component events. All have empty default implementations.

```csharp
public class SpawnEffectComponent : Component
{
	protected internal override void OnAdded()
	{
		// Called immediately when AddComponent<T>() attaches this component.
		// Entity is already set. Safe to call Entity.GetComponent<T>() here.
		Logger.LogDebug("{Name} spawned", Entity!.Name);
	}

	protected internal override void OnRemoved()
	{
		// Called when RemoveComponent<T>() or entity destruction removes this component.
		// Entity is still set at this point; it is cleared after this method returns.
	}

	protected internal override void OnEnabled()
	{
		// Called when IsEnabled changes from false → true,
		// or when the owning entity's IsActive changes to true (if IsEnabled is already true).
	}

	protected internal override void OnDisabled()
	{
		// Called when IsEnabled changes from true → false,
		// or when the owning entity's IsActive changes to false (if IsEnabled is already true).
	}
}
```

**Execution order:** `OnAdded` → frame ticks → `OnEnabled`/`OnDisabled` (as toggled) → `OnRemoved`.

---

## IsEnabled

`Component.IsEnabled` controls whether built-in systems skip this specific component. The entity and all other components continue to run normally.

```csharp
entity.GetComponent<SpriteComponent>()!.IsEnabled = false;  // hides sprite but entity still updates
entity.GetComponent<SpriteComponent>()!.IsEnabled = true;   // shows sprite again
```

This triggers `OnDisabled` / `OnEnabled` on the component and invalidates any cached queries built with `.OnlyEnabled()`.

`IsEnabled` is distinct from `Entity.IsActive`:

| Toggle | Scope | Effect |
|--------|-------|--------|
| `entity.IsActive = false` | Entire entity | Skipped by all systems, queries, behaviors |
| `component.IsEnabled = false` | Single component | Skipped by systems that check this flag |

---

## Accessing Sibling Components

From inside a component, use `Entity` to reach sibling components or the world:

```csharp
protected internal override void OnAdded()
{
	var transform = Entity!.GetComponent<TransformComponent>();
	var rigid     = Entity!.GetRequiredComponent<RigidBodyComponent>(); // throws if missing
}

protected internal override void OnRemoved()
{
	Entity!.World?.DestroyEntity(Entity!);  // destroy owner on removal
}
```

---

## Useful Patterns

### Read-only derived state

```csharp
public class HealthComponent : Component
{
	public int HP    { get; set; } = 100;
	public int MaxHP { get; set; } = 100;

	public float Fraction => MaxHP > 0 ? (float)HP / MaxHP : 0f;
	public bool  IsDead   => HP <= 0;
}
```

### Component that disables itself when empty

```csharp
public class AmmoComponent : Component
{
	private int _count;

	public int Count
	{
		get => _count;
		set
		{
			_count = value;
			IsEnabled = _count > 0;
		}
	}
}
```

### Subscribing to an event in OnAdded

```csharp
public class HealthBarComponent : Component
{
	private EventBus? _bus;

	protected internal override void OnAdded()
	{
		_bus = Entity!.GetRequiredComponent<EventBusComponent>().Bus;
		_bus.Subscribe<DamageEvent>(OnDamage);
	}

	protected internal override void OnRemoved()
	{
		_bus?.Unsubscribe<DamageEvent>(OnDamage);
	}

	private void OnDamage(DamageEvent e) { /* update bar */ }
}
```

---

## What Components Do Not Have

| Feature | Where it lives instead |
|---------|----------------------|
| `Update(GameTime)` per frame | `Behavior.Update` or a `System` |
| `Render(IRenderer, GameTime)` | `Behavior.Render` or a `RenderSystemBase` |
| `FixedUpdate(GameTime)` | `Behavior.FixedUpdate` or a `FixedUpdateSystemBase` |
| Constructor injection / DI | `Behavior` constructor |

Components are constructed via `new()` (parameterless). If you need DI or per-frame logic, use a **Behavior** instead.

---

## Built-in Components

Brine2D ships several ready-to-use components in `Brine2D.ECS.Components`:

| Component | Purpose |
|-----------|---------|
| `TransformComponent` | World/local position, rotation, scale with hierarchy propagation |

More components are added in feature packages (`Brine2D.Physics`, `Brine2D.Audio`, etc.).

---

## Related Topics

- [Getting Started](getting-started.md) — end-to-end walkthrough
- [Entities](entities.md) — entity hierarchy and lifecycle
- [Systems](systems.md) — batch-process components each frame
- [Queries](queries.md) — filter entities by component type
