---
title: Components
description: Deep dive into Brine2D's hybrid components - data, methods, and lifecycle
---

# Components

Components in Brine2D's **hybrid ECS** can contain both **data and methods** - making them beginner-friendly while still allowing optional system-based optimization.

## Overview

**What makes Brine2D components unique?**

- ✅ **Methods allowed** - components can have logic (Unity-style)
- ✅ **Lifecycle hooks** - OnAdded, OnUpdate, OnEnabled, OnDisabled, OnRemoved
- ✅ **Helper methods** - GetComponent, GetRequiredComponent, TryGetComponent
- ✅ **Entity access** - easy access to sibling components and entity properties
- ✅ **Enable/disable** - runtime control via IsEnabled flag

**Two approaches:**

| Approach | When to Use | Complexity |
|----------|-------------|------------|
| **Components with methods** | Most games (recommended) | ⭐ Beginner |
| **Pure data + systems** | Performance-critical (1000+ entities) | ⭐⭐⭐ Advanced |

---

## The Component Base Class

### Core Properties

```csharp
public abstract class Component
{
    // Entity relationship
    public Entity? Entity { get; internal set; }
    public bool IsAttached => Entity != null;
    
    // State
    public bool IsEnabled { get; set; } = true;
    
    // Shortcuts
    public string EntityName => Entity?.Name ?? string.Empty;
    public HashSet<string> EntityTags => Entity?.Tags ?? new HashSet<string>();
    public TransformComponent? Transform => Entity?.GetComponent<TransformComponent>();
    
    // Helper methods
    public T? GetComponent<T>() where T : Component;
    public T GetRequiredComponent<T>() where T : Component;
    public bool TryGetComponent<T>(out T? component) where T : Component;
    public T? GetComponentInChildren<T>() where T : Component;
    public T? GetComponentInParent<T>() where T : Component;
    public void Destroy();
    
    // Lifecycle (override in derived classes)
    protected internal virtual void OnAdded() { }
    protected internal virtual void OnRemoved() { }
    protected internal virtual void OnEnabled() { }
    protected internal virtual void OnDisabled() { }
    protected internal virtual void OnUpdate(GameTime gameTime) { }
}
```

**Pattern:** Every component can access its entity, other components, and has lifecycle hooks.

---

## Creating Components

### Simple Component with Data Only

```csharp
using Brine2D.ECS;
using System.Numerics;

public class TransformComponent : Component
{
    public Vector2 Position { get; set; }
    public float Rotation { get; set; }
    public Vector2 Scale { get; set; } = Vector2.One;
}

// Usage
var entity = World.CreateEntity("Player");
var transform = entity.AddComponent<TransformComponent>();
transform.Position = new Vector2(100, 100);
transform.Rotation = 45f;
```

**Pattern:** Simplest form - just data, no logic.

---

### Component with Methods (Recommended)

```csharp
using Brine2D.ECS;

public class HealthComponent : Component
{
    public int Current { get; set; }
    public int Max { get; set; }
    
    public bool IsDead => Current <= 0;
    public float HealthPercent => (float)Current / Max;
    
    // ✅ Methods allowed in Brine2D!
    public void TakeDamage(int amount)
    {
        Current = Math.Max(0, Current - amount);
        
        if (IsDead)
        {
            OnDeath();
        }
    }
    
    public void Heal(int amount)
    {
        Current = Math.Min(Max, Current + amount);
    }
    
    public void SetHealth(int health)
    {
        Current = Math.Clamp(health, 0, Max);
    }
    
    private void OnDeath()
    {
        // Death logic
        Logger.LogInformation("{Entity} died!", EntityName);
    }
}

// Usage - intuitive and clear!
var health = entity.AddComponent<HealthComponent>();
health.Max = 100;
health.Current = 100;

health.TakeDamage(25); // Simple method call
health.Heal(10);
```

**Pattern:** Components with methods are intuitive - just like Unity!

---

### Component with Lifecycle Methods

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using System.Numerics;

public class VelocityComponent : Component
{
    public Vector2 Value { get; set; }
    public float Speed { get; set; } = 100f;
    public float MaxSpeed { get; set; } = 500f;
    
    // ✅ Lifecycle method - auto-movement
    protected internal override void OnUpdate(GameTime gameTime)
    {
        if (!IsEnabled) return;
        
        if (Value != Vector2.Zero)
        {
            // Get sibling component
            var transform = GetRequiredComponent<TransformComponent>();
            
            // Apply velocity
            var deltaTime = (float)gameTime.DeltaTime;
            transform.Position += Value * Speed * deltaTime;
            
            // Clamp speed
            if (Value.Length() > MaxSpeed)
            {
                Value = Vector2.Normalize(Value) * MaxSpeed;
            }
        }
    }
    
    // ✅ Helper methods
    public void AddForce(Vector2 force)
    {
        Value += force;
    }
    
    public void Stop()
    {
        Value = Vector2.Zero;
    }
}

// Usage - component handles movement automatically!
var velocity = entity.AddComponent<VelocityComponent>();
velocity.Value = new Vector2(1, 0); // Moving right
velocity.Speed = 200f;

// Component updates position every frame automatically
```

**Pattern:** `OnUpdate()` is called automatically - no systems needed!

---

## Component Lifecycle

### Lifecycle Flow

```mermaid
stateDiagram-v2
    [*] --> Created: new Component()
    
    Created --> Added: entity.AddComponent()
    
    Added --> Attached: OnAdded()
    note right of Attached
        Component.Entity set
        Setup resources
        Subscribe to events
    end note
    
    Attached --> Enabled: IsEnabled = true
    
    Enabled --> EnablingEvent: OnEnabled()
    
    EnablingEvent --> Active: Ready
    
    Active --> Updating: OnUpdate(gameTime)
    note right of Updating
        Called every frame
        if IsEnabled = true
    end note
    
    Updating --> Active: Frame complete
    
    Active --> Disabling: IsEnabled = false
    
    Disabling --> DisablingEvent: OnDisabled()
    
    DisablingEvent --> Disabled: Paused
    
    Disabled --> EnablingEvent: IsEnabled = true
    
    Active --> Removing: entity.RemoveComponent()
    
    Removing --> RemovedEvent: OnRemoved()
    note right of RemovedEvent
        Component.Entity = null
        Cleanup resources
        Unsubscribe events
    end note
    
    RemovedEvent --> [*]
```

---

### Lifecycle Methods

#### OnAdded()

```csharp
public class MyComponent : Component
{
    private ITexture? _texture;
    
    protected internal override void OnAdded()
    {
        // ✅ Called once when added to entity
        // Use for: Initialization, resource loading, event subscription
        
        base.OnAdded();
        
        Logger.LogInformation("Component added to {Entity}", EntityName);
        
        // Setup resources
        _texture = LoadTexture("sprite.png");
        
        // Get required sibling components
        var transform = GetRequiredComponent<TransformComponent>();
        transform.Position = Vector2.Zero;
        
        // Subscribe to events
        if (TryGetComponent<HealthComponent>(out var health))
        {
            health.OnDeath += HandleDeath;
        }
    }
    
    private void HandleDeath()
    {
        Logger.LogInformation("Entity died!");
    }
}
```

**Use for:**
- Resource initialization
- Getting required components
- Event subscription
- One-time setup

---

#### OnRemoved()

```csharp
public class MyComponent : Component
{
    private ITexture? _texture;
    
    protected internal override void OnRemoved()
    {
        // ✅ Called once when removed from entity
        // Use for: Cleanup, resource disposal, event unsubscription
        
        Logger.LogInformation("Component removed from {Entity}", EntityName);
        
        // Dispose resources
        _texture?.Dispose();
        _texture = null;
        
        // Unsubscribe events
        if (TryGetComponent<HealthComponent>(out var health))
        {
            health.OnDeath -= HandleDeath;
        }
        
        base.OnRemoved();
    }
}
```

**Use for:**
- Resource disposal
- Event unsubscription
- Save state
- Cleanup

---

#### OnEnabled()

```csharp
public class MyComponent : Component
{
    protected internal override void OnEnabled()
    {
        // ✅ Called when IsEnabled changes from false to true
        // Use for: Resume logic, re-enable features
        
        base.OnEnabled();
        
        Logger.LogInformation("Component enabled on {Entity}", EntityName);
        
        // Resume logic
        ResumeAnimation();
        EnableCollision();
    }
}
```

**Use for:**
- Resume paused logic
- Re-enable features
- Refresh state

---

#### OnDisabled()

```csharp
public class MyComponent : Component
{
    protected internal override void OnDisabled()
    {
        // ✅ Called when IsEnabled changes from true to false
        // Use for: Pause logic, disable features
        
        base.OnDisabled();
        
        Logger.LogInformation("Component disabled on {Entity}", EntityName);
        
        // Pause logic
        PauseAnimation();
        DisableCollision();
    }
}
```

**Use for:**
- Pause active logic
- Disable features temporarily
- Save temporary state

---

#### OnUpdate(gameTime)

```csharp
public class MyComponent : Component
{
    private float _timer;
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        // ✅ Called every frame (if IsEnabled = true)
        // Use for: Per-frame logic, animation, timers
        
        if (!IsEnabled) return; // Safety check
        
        var deltaTime = (float)gameTime.DeltaTime;
        
        // Update timer
        _timer += deltaTime;
        
        // Get sibling components
        var transform = GetComponent<TransformComponent>();
        if (transform != null)
        {
            // Update position
            transform.Position += new Vector2(100, 0) * deltaTime;
        }
        
        // Periodic action
        if (_timer >= 1f)
        {
            PerformAction();
            _timer = 0f;
        }
    }
    
    private void PerformAction()
    {
        Logger.LogDebug("Action performed!");
    }
}
```

**Use for:**
- Per-frame updates
- Animation
- Timers
- Movement
- State changes

---

## Component Helper Methods

### Getting Sibling Components

```csharp
public class MyComponent : Component
{
    protected internal override void OnUpdate(GameTime gameTime)
    {
        // Method 1: GetComponent (safe, returns null if missing)
        var transform = GetComponent<TransformComponent>();
        if (transform != null)
        {
            transform.Position += Vector2.One;
        }
        
        // Method 2: GetRequiredComponent (throws if missing)
        var sprite = GetRequiredComponent<SpriteComponent>();
        sprite.Color = Color.Red; // Safe - guaranteed to exist
        
        // Method 3: TryGetComponent (safe retrieval pattern)
        if (TryGetComponent<HealthComponent>(out var health))
        {
            health.TakeDamage(10);
        }
    }
}
```

**Pattern:** Use `GetRequiredComponent<T>()` for essential components, `GetComponent<T>()` for optional ones.

---

### Getting Components in Hierarchy

```csharp
public class MyComponent : Component
{
    protected internal override void OnAdded()
    {
        // Get component in children (recursive search)
        var childHealth = GetComponentInChildren<HealthComponent>();
        
        // Get component in parent (searches upward)
        var parentTransform = GetComponentInParent<TransformComponent>();
        
        // Access Transform shortcut
        var transform = Transform; // Same as GetComponent<TransformComponent>()
        
        if (transform != null)
        {
            Logger.LogInformation("Position: {Position}", transform.Position);
        }
    }
}
```

**Use for:**
- Complex hierarchies (tank + turret)
- UI layouts (panel + buttons)
- Character rigs

---

### Entity Properties

```csharp
public class MyComponent : Component
{
    protected internal override void OnAdded()
    {
        // Access entity properties
        Logger.LogInformation("Attached to entity: {Name}", EntityName);
        
        // Check entity tags
        if (EntityTags.Contains("Enemy"))
        {
            Logger.LogInformation("This is an enemy!");
        }
        
        // Check if attached
        if (IsAttached)
        {
            Logger.LogInformation("Component is attached to an entity");
        }
        
        // Get entity directly
        if (Entity != null)
        {
            Logger.LogInformation("Entity ID: {Id}", Entity.Id);
        }
    }
}
```

**Properties available:**
- `Entity` - the entity this component is attached to
- `IsAttached` - whether component is attached to an entity
- `EntityName` - name of the entity
- `EntityTags` - tags of the entity
- `Transform` - shortcut for GetComponent<TransformComponent>()

---

## Component State Management

### IsEnabled Flag

```csharp
public class MyComponent : Component
{
    public void Initialize()
    {
        // Component enabled by default
        IsEnabled = true;
        
        // Disable temporarily
        IsEnabled = false; // OnDisabled() called
        
        // Re-enable
        IsEnabled = true; // OnEnabled() called
    }
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        // OnUpdate only called if IsEnabled = true
        // But good practice to check anyway
        if (!IsEnabled) return;
        
        // Update logic
    }
}

// Usage
var component = entity.GetComponent<MyComponent>();
if (component != null)
{
    component.IsEnabled = false; // Pause component
    
    // Later...
    component.IsEnabled = true; // Resume component
}
```

**Pattern:** Use `IsEnabled` to pause/resume components without removing them.

---

### Removing Components

```csharp
public class MyComponent : Component
{
    public void CheckHealth()
    {
        if (TryGetComponent<HealthComponent>(out var health))
        {
            if (health.IsDead)
            {
                // Remove this component
                Destroy(); // Calls Entity.RemoveComponent(this)
                
                // OnRemoved() will be called automatically
            }
        }
    }
}

// Or remove from entity directly
entity.RemoveComponent<MyComponent>();
```

**Pattern:** `Destroy()` removes the component and calls `OnRemoved()`.

---

## Built-in Components

### TransformComponent

```csharp
using Brine2D.ECS.Components;

public class TransformComponent : Component
{
    // Local transform (relative to parent)
    public Vector2 LocalPosition { get; set; }
    public float LocalRotation { get; set; }
    public Vector2 LocalScale { get; set; } = Vector2.One;
    
    // World transform (calculated from hierarchy)
    public Vector2 WorldPosition { get; set; }
    public float WorldRotation { get; set; }
    public Vector2 WorldScale { get; set; } = Vector2.One;
    
    // Hierarchy
    public TransformComponent? Parent { get; }
    public IReadOnlyList<TransformComponent> Children { get; }
    
    // Helper properties
    public Vector2 Right { get; }
    public Vector2 Up { get; }
    public Vector2 Forward { get; }
}

// Usage
var transform = entity.AddComponent<TransformComponent>();
transform.LocalPosition = new Vector2(100, 100);
transform.LocalRotation = 45f;
transform.LocalScale = new Vector2(2, 2);
```

---

### LifetimeComponent

```csharp
using Brine2D.ECS.Components;

public class LifetimeComponent : Component
{
    public float Lifetime { get; set; } = 5f; // Seconds
    public float TimeRemaining { get; set; }
    public bool AutoDestroy { get; set; } = true;
    
    public event Action? OnLifetimeExpired;
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        TimeRemaining -= (float)gameTime.DeltaTime;
        
        if (TimeRemaining <= 0)
        {
            OnLifetimeExpired?.Invoke();
            
            if (AutoDestroy)
            {
                Entity?.Destroy();
            }
        }
    }
    
    public void ResetLifetime() { }
    public void ExtendLifetime(float time) { }
}

// Usage - entity auto-destroys after 5 seconds
var lifetime = entity.AddComponent<LifetimeComponent>();
lifetime.Lifetime = 5f;
lifetime.OnLifetimeExpired += () => Logger.LogInformation("Entity expired!");
```

---

## Complete Component Examples

### Example 1: Auto-Rotate Component

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Components;

public class AutoRotateComponent : Component
{
    public float RotationSpeed { get; set; } = 90f; // Degrees per second
    public bool Clockwise { get; set; } = true;
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        if (!IsEnabled) return;
        
        var transform = GetRequiredComponent<TransformComponent>();
        
        var deltaTime = (float)gameTime.DeltaTime;
        var rotation = RotationSpeed * deltaTime;
        
        if (!Clockwise)
        {
            rotation = -rotation;
        }
        
        transform.LocalRotation += rotation;
        
        // Wrap angle to 0-360
        if (transform.LocalRotation >= 360f)
        {
            transform.LocalRotation -= 360f;
        }
        else if (transform.LocalRotation < 0f)
        {
            transform.LocalRotation += 360f;
        }
    }
}

// Usage
var autoRotate = entity.AddComponent<AutoRotateComponent>();
autoRotate.RotationSpeed = 180f; // 180 degrees per second
autoRotate.Clockwise = true;
```

---

### Example 2: Health Regeneration Component

```csharp
using Brine2D.Core;
using Brine2D.ECS;

public class HealthRegenComponent : Component
{
    public int RegenPerSecond { get; set; } = 5;
    public float RegenDelay { get; set; } = 2f; // Wait 2s after damage
    public bool EnableRegen { get; set; } = true;
    
    private float _timeSinceLastDamage;
    private int _lastHealth;
    
    protected internal override void OnAdded()
    {
        base.OnAdded();
        
        var health = GetRequiredComponent<HealthComponent>();
        _lastHealth = health.Current;
    }
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        if (!IsEnabled || !EnableRegen) return;
        
        var health = GetComponent<HealthComponent>();
        if (health == null || health.IsDead) return;
        
        var deltaTime = (float)gameTime.DeltaTime;
        
        // Check if damaged
        if (health.Current < _lastHealth)
        {
            _timeSinceLastDamage = 0f;
        }
        _lastHealth = health.Current;
        
        // Update timer
        _timeSinceLastDamage += deltaTime;
        
        // Regenerate if delay passed
        if (_timeSinceLastDamage >= RegenDelay && health.Current < health.Max)
        {
            var regenAmount = (int)(RegenPerSecond * deltaTime);
            health.Heal(regenAmount);
        }
    }
}

// Usage
var healthRegen = entity.AddComponent<HealthRegenComponent>();
healthRegen.RegenPerSecond = 10;
healthRegen.RegenDelay = 3f; // Wait 3 seconds after damage
```

---

### Example 3: Follow Component

```csharp
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.ECS.Components;
using System.Numerics;

public class FollowComponent : Component
{
    public Guid TargetId { get; set; }
    public float FollowSpeed { get; set; } = 100f;
    public float MinDistance { get; set; } = 10f;
    public bool RotateToTarget { get; set; } = true;
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        if (!IsEnabled) return;
        if (TargetId == Guid.Empty) return;
        
        // Get target from World
        var target = Entity?.World?.GetEntityById(TargetId);
        if (target == null) return;
        
        var transform = GetRequiredComponent<TransformComponent>();
        var targetTransform = target.GetComponent<TransformComponent>();
        if (targetTransform == null) return;
        
        var deltaTime = (float)gameTime.DeltaTime;
        
        // Calculate direction
        var direction = targetTransform.WorldPosition - transform.WorldPosition;
        var distance = direction.Length();
        
        // Move if far enough
        if (distance > MinDistance)
        {
            direction = Vector2.Normalize(direction);
            transform.WorldPosition += direction * FollowSpeed * deltaTime;
            
            // Rotate to face target
            if (RotateToTarget)
            {
                var angle = MathF.Atan2(direction.Y, direction.X);
                transform.LocalRotation = angle * (180f / MathF.PI);
            }
        }
    }
    
    public void SetTarget(Entity target)
    {
        TargetId = target.Id;
    }
}

// Usage
var follow = entity.AddComponent<FollowComponent>();
follow.SetTarget(player);
follow.FollowSpeed = 150f;
follow.MinDistance = 20f;
```

---

## Best Practices

### ✅ DO

**1. Use methods in components (beginner-friendly)**

```csharp
// ✅ Good - intuitive methods
public class HealthComponent : Component
{
    public int Current { get; set; }
    public int Max { get; set; }
    
    public void TakeDamage(int amount)
    {
        Current = Math.Max(0, Current - amount);
    }
}

// Usage is clear
health.TakeDamage(25);
```

**2. Use lifecycle methods for automatic behavior**

```csharp
// ✅ Good - component updates itself
public class VelocityComponent : Component
{
    public Vector2 Value { get; set; }
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        var transform = GetRequiredComponent<TransformComponent>();
        transform.Position += Value * (float)gameTime.DeltaTime;
    }
}
```

**3. Use GetRequiredComponent for essential dependencies**

```csharp
// ✅ Good - fail fast if missing
protected internal override void OnUpdate(GameTime gameTime)
{
    var transform = GetRequiredComponent<TransformComponent>();
    transform.Position += Vector2.One; // Safe
}
```

**4. Clean up in OnRemoved**

```csharp
// ✅ Good - proper cleanup
protected internal override void OnRemoved()
{
    _texture?.Dispose();
    UnsubscribeEvents();
    base.OnRemoved();
}
```

---

### ❌ DON'T

**1. Don't avoid methods for no reason**

```csharp
// ❌ Bad - missing methods makes code verbose
public class HealthComponent : Component
{
    public int Current { get; set; }
}

// Usage is tedious
health.Current = Math.Max(0, health.Current - 25);

// ✅ Good - add methods
public void TakeDamage(int amount)
{
    Current = Math.Max(0, Current - amount);
}
```

**2. Don't store entity references**

```csharp
// ❌ Bad - entity reference can become invalid
public class FollowComponent : Component
{
    public Entity? Target { get; set; } // Can be destroyed!
}

// ✅ Good - store entity ID
public class FollowComponent : Component
{
    public Guid TargetId { get; set; }
    
    protected internal override void OnUpdate(GameTime gameTime)
    {
        var target = Entity?.World?.GetEntityById(TargetId);
        // ...
    }
}
```

**3. Don't forget to check IsEnabled**

```csharp
// ❌ Bad - doesn't respect IsEnabled
protected internal override void OnUpdate(GameTime gameTime)
{
    // Always runs even if disabled!
}

// ✅ Good - check IsEnabled
protected internal override void OnUpdate(GameTime gameTime)
{
    if (!IsEnabled) return;
    // Update logic
}
```

**4. Don't put unrelated logic in one component**

```csharp
// ❌ Bad - doing too much
public class PlayerComponent : Component
{
    // Movement
    public Vector2 Velocity { get; set; }
    
    // Health
    public int Health { get; set; }
    
    // Inventory
    public List<Item> Items { get; set; }
    
    // Too much responsibility!
}

// ✅ Good - separate concerns
public class VelocityComponent : Component { }
public class HealthComponent : Component { }
public class InventoryComponent : Component { }
```

---

## Summary

**Component features:**

| Feature | Usage |
|---------|-------|
| **Methods** | Logic in components (recommended) |
| **Lifecycle** | OnAdded, OnUpdate, OnEnabled, OnDisabled, OnRemoved |
| **Helpers** | GetComponent, GetRequiredComponent, TryGetComponent |
| **Entity access** | Entity, EntityName, EntityTags, Transform |
| **State** | IsEnabled, IsAttached |
| **Remove** | Destroy() or entity.RemoveComponent<T>() |

**Lifecycle methods:**

| Method | When Called | Use For |
|--------|-------------|---------|
| **OnAdded()** | Once (when added) | Setup, initialization |
| **OnRemoved()** | Once (when removed) | Cleanup, disposal |
| **OnEnabled()** | IsEnabled true → false | Resume logic |
| **OnDisabled()** | IsEnabled false → true | Pause logic |
| **OnUpdate(gameTime)** | Every frame (if enabled) | Game logic, animation |

**Helper methods:**

| Method | Returns | Throws |
|--------|---------|--------|
| **GetComponent<T>()** | T? (null if missing) | No |
| **GetRequiredComponent<T>()** | T (guaranteed) | Yes (if missing) |
| **TryGetComponent<T>(out T?)** | bool | No |
| **GetComponentInChildren<T>()** | T? (recursive) | No |
| **GetComponentInParent<T>()** | T? (upward search) | No |

---

## Next Steps

- **[Entities Guide](entities.md)** - Entity management and patterns
- **[Systems Guide](systems.md)** - Optional systems for performance
- **[Queries Guide](queries.md)** - Find entities with components
- **[ECS Getting Started](getting-started.md)** - Complete ECS tutorial
- **[ECS Concepts](../../concepts/entity-component-system.md)** - Understanding hybrid ECS

---

**Remember:** Brine2D components can have methods and lifecycle hooks - this makes them beginner-friendly while still allowing optional system-based optimization for performance! 🎮