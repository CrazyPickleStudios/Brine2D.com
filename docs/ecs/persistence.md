---
title: Persistence
description: Save and restore entity worlds with EntitySerializer and AotEntitySerializer
---

# Persistence

Brine2D ships two serializers that can save and restore an entire entity world — all entities, their components, their property values, and their parent–child relationships — to and from a JSON snapshot.

| Serializer | Setup | AOT / Trim safe | Best for |
|---|---|---|---|
| `EntitySerializer` | None | ❌ Uses reflection | Most games |
| `AotEntitySerializer` | Register component types | ✅ With explicit `JsonTypeInfo<T>` | NativeAOT / trimmed publish |

Both produce the same JSON format and expose the same API surface.

---

## EntitySerializer

`EntitySerializer` is the zero-setup option. It discovers and serializes all public component properties automatically via `System.Text.Json` reflection.

### Setup

Register the serializer in DI or construct it directly:

```csharp
// Via DI (Program.cs)
builder.Services.AddSingleton<EntitySerializer>();

// Or construct directly
var serializer = new EntitySerializer();
```

### Saving a world

```csharp
await _serializer.SaveWorldAsync(world, "saves/slot1.json");
```

`SaveWorldAsync` creates the file and any missing parent directories automatically.

### Restoring a world

```csharp
// Load and restore in one call (most common)
await _serializer.LoadAndRestoreWorldAsync(world, "saves/slot1.json");

// Or load the snapshot separately and restore later
WorldSnapshot snapshot = await _serializer.LoadSnapshotAsync("saves/slot1.json");
_serializer.RestoreWorldFromSnapshot(world, snapshot);
```

`RestoreWorldFromSnapshot` destroys all current entities in the world before recreating the saved ones.

### Working with snapshots directly

```csharp
// Capture current state
WorldSnapshot snapshot = _serializer.CreateWorldSnapshot(world);

// Serialize to JSON string (e.g. for network transmission)
string json = JsonSerializer.Serialize(snapshot, EntitySerializer.CreateDefaultOptions());

// Restore from snapshot object
_serializer.RestoreWorldFromSnapshot(world, snapshot);
```

---

## AotEntitySerializer

`AotEntitySerializer` uses an explicit `ComponentTypeRegistry` instead of runtime reflection. This makes it compatible with NativeAOT and IL-trimmed publishing when each component type is registered with a source-generated `JsonTypeInfo<T>`.

### Setup — non-trimmed publishing (recommended starting point)

Two calls cover everything:

```csharp
var registry = new ComponentTypeRegistry();
registry.RegisterBrineComponents();                   // all built-in engine components
registry.RegisterAllComponents(GetType().Assembly);   // all your game components

var serializer = new AotEntitySerializer(registry);
```

`RegisterBrineComponents()` scans the engine assembly. `RegisterAllComponents(Assembly)` scans the provided assembly and registers every concrete, non-abstract `Component` subclass it finds. Both use reflection internally and are not suitable for trimmed publishing.

### Setup — NativeAOT / IL-trimmed publishing

For fully trim-safe operation, supply a source-generated `JsonSerializerContext`:

```csharp
// MyGameSnapshotContext.cs
[JsonSerializable(typeof(HealthComponent))]
[JsonSerializable(typeof(InventoryComponent))]
[JsonSerializable(typeof(QuestComponent))]
public partial class MyGameSnapshotContext : JsonSerializerContext { }
```

```csharp
var registry = new ComponentTypeRegistry();

// Register each type with its source-generated JsonTypeInfo
registry.Register<HealthComponent>(MyGameSnapshotContext.Default.HealthComponent);
registry.Register<InventoryComponent>(MyGameSnapshotContext.Default.InventoryComponent);
registry.Register<QuestComponent>(MyGameSnapshotContext.Default.QuestComponent);

// Built-in components: use RegisterBrineComponents() for non-trimmed,
// or register individually with JsonTypeInfo for fully trimmed builds.
registry.RegisterBrineComponents();

var serializer = new AotEntitySerializer(registry);
```

!!! note "Built-in components and trimming"
	`RegisterBrineComponents()` uses reflection and is not suitable for fully trimmed / NativeAOT publishing. A fully AOT-safe registration path for built-in engine components is on the post-1.0 roadmap. For trimmed publishing today, only register the built-in component types your game actually uses, each with a source-generated `JsonTypeInfo<T>`.

### Saving and restoring

The API is identical to `EntitySerializer`:

```csharp
await serializer.SaveWorldAsync(world, "saves/slot1.json");
await serializer.LoadAndRestoreWorldAsync(world, "saves/slot1.json");
```

### Checking registration

```csharp
bool registered = registry.IsRegistered<HealthComponent>();  // true/false
int count = registry.Count;                                   // total registered types
```

---

## What is and isn't persisted

### Persisted

- Entity name, tags, and `IsActive` state
- Parent–child entity hierarchy
- All serializable component properties (those not marked `[JsonIgnore]`)

### Not persisted

| What | Why |
|---|---|
| Behaviors | Re-add via prefab factory after restore |
| Runtime-only component properties | Marked `[JsonIgnore]` — interface handles, frame state, computed values |
| Entity IDs | Remapped on restore; do not store cross-entity references as `long` IDs |
| Systems | Systems are registered on the scene, not the world snapshot |

### Runtime-only properties on built-in components

All built-in engine components have been audited. The following are **excluded** from snapshots:

- `SpriteComponent`: `Texture`, `CrossFadeGhosts`, `Material`
- `AnimatorComponent`: `Animator`, `StateMachine`, `Parameters`, `Layers`, `BlendSelector1D/2D`, `CurrentHitBox`
- `AudioSourceComponent`: `IsPlaying`, `IsPaused`, `TriggerPlay/Stop/Pause/Resume`, `PlaybackEnded`
- `SoundEffectSourceComponent`: `SoundEffect`, `SpatialVolume/Pan/Pitch`, `TriggerStopOldest`
- `MusicSourceComponent`: `Music`
- `JointComponent`: `ConnectedBody`, `IsLive`
- `KinematicCharacterBody`: `IsGrounded`, `IsOnWall`, `IsOnCeiling`, `FloorNormal/WallNormal/CeilingNormal`, `PlatformVelocity`, `EffectiveVelocity`, `LastMoveAndCollideHit`, `MotionRemainder`
- `AIControllerComponent`: `CurrentTarget`, `HasTarget`, `MoveDirection`, `DistanceToTarget`
- `PlayerControllerComponent`: `ActionMap`, `InputDirection`, `IsMoving`
- `TilemapComponent`: `Tilemap`, `Animator`, `IsLoaded`
- `ParticleEmitterComponent`: `ParticleTexture`, `Forces`, delegates (`OnParticleDied` etc.), `ActiveParticles`, `ParticleCount`, `IsPaused`

---

## Cross-entity references

Entity IDs (`long`) are runtime values assigned by the engine's global counter. When a world is restored, every entity receives a **new** ID. Any component that stored a cross-entity reference as a `long` will hold a stale value after restore.

**Resolution:** re-resolve cross-entity references by entity name or tag after calling `RestoreWorldFromSnapshot` / `LoadAndRestoreWorldAsync`:

```csharp
await serializer.LoadAndRestoreWorldAsync(world, "save.json");

// Re-resolve cross-entity references
var player = world.FindEntityByName("Player");
var camera = world.FindEntityByName("MainCamera");
camera.GetComponent<CameraFollowComponent>()!.Target = player;
```

---

## Excluding custom properties

Apply `[JsonIgnore]` to any component property you don't want persisted:

```csharp
using System.Text.Json.Serialization;

public class HealthComponent : Component
{
	public int HP    { get; set; } = 100;
	public int MaxHP { get; set; } = 100;

	// Computed — no need to persist
	[JsonIgnore]
	public bool IsDead => HP <= 0;

	// Runtime handle set by a system — not serializable
	[JsonIgnore]
	public IHealthBarWidget? HealthBar { get; set; }
}
```

---

## Snapshot format

Snapshots are plain JSON objects and can be inspected, edited, or transmitted directly:

```json
{
  "entities": [
	{
	  "id": 1,
	  "parentId": 0,
	  "name": "Player",
	  "isActive": true,
	  "tags": ["player", "controllable"],
	  "components": {
		"TransformComponent": { "Position": { "X": 400, "Y": 300 }, "Rotation": 0, "Scale": { "X": 1, "Y": 1 } },
		"HealthComponent":    { "HP": 80, "MaxHP": 100 }
	  }
	}
  ]
}
```

Component entries use the type's short name as the key. The schema is forward-compatible: unknown component keys are silently skipped on restore, and missing component keys restore as defaults.
