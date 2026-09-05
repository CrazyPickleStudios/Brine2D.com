---
title: Events
description: Handle window events and custom event system in Brine2D
---

# Events

Learn how to handle window events and create custom event systems in your Brine2D games.

---

## Quick Start

```csharp
using Brine2D.Events;

public class GameScene : Scene
{
    private readonly IEventBus _eventBus;
    private IDisposable? _subscription;

    public GameScene(IEventBus eventBus)
    {
        _eventBus = eventBus;
    }

    protected override void OnEnter()
    {
        // Subscribe to window resize event
        _subscription = _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
    }

    private void OnWindowResized(WindowResizedEvent e)
    {
        Logger.LogInformation("Window resized to {Width}x{Height}",
            e.Width, e.Height);

        // Adjust camera, UI, etc.
        UpdateCameraAspectRatio(e.Width, e.Height);
    }

    protected override void OnExit()
    {
        // Dispose the subscription token to prevent memory leaks
        _subscription?.Dispose();
    }
}
```

---

## Topics

| Guide | Description | Level |
|-------|-------------|-------|
| **[Window Events](window-events.md)** | Handle window resize, focus, minimize, etc. | ? Beginner |

---

## Key Concepts

### IEventBus

`IEventBus` is the pub/sub abstraction for the engine's event bus. Inject the interface
(rather than the concrete `EventBus` type) to keep your scenes and systems testable:

```csharp
public interface IEventBus
{
    // Subscribe to events - returns a disposal token that unsubscribes automatically
    IDisposable Subscribe<TEvent>(Action<TEvent> handler) where TEvent : class;

    // Manually unsubscribe (prefer disposing the Subscribe token instead)
    void Unsubscribe<TEvent>(Action<TEvent> handler) where TEvent : class;

    // Publish events
    void Publish<TEvent>(TEvent eventData) where TEvent : class;

    // Clear all subscribers for a specific event type
    void ClearSubscribers<TEvent>() where TEvent : class;
}
```

**Already registered for you** - `IEventBus` is a framework-provided singleton, automatically
available across all scenes. You don't need to call `AddSingleton` yourself; just
constructor-inject `IEventBus` like any other service:

```csharp
public class GameScene : Scene
{
    private readonly IEventBus _eventBus;

    public GameScene(IEventBus eventBus)
    {
        _eventBus = eventBus;
    }
}
```

---

### Built-In Events

Brine2D provides window and application events out of the box:

| Event | When Fired |
|-------|------------|
| **WindowResizedEvent(int Width, int Height)** | Window size changed |
| **WindowFocusGainedEvent** | Window gained focus |
| **WindowFocusLostEvent** | Window lost focus |
| **WindowMinimizedEvent** | Window minimized |
| **WindowRestoredEvent** | Window restored from minimize |
| **WindowHiddenEvent** | Window hidden (e.g., system sleep, lock screen) — rendering suspended |
| **WindowShownEvent** | Window becomes visible again after being hidden |
| **ApplicationQuitRequestedEvent** | Application quit requested (e.g., window close button) |

All of the above live in the `Brine2D.Events` namespace.

[:octicons-arrow-right-24: Full list: Window Events](window-events.md)

---

## Common Tasks

### Handle Window Resize

```csharp
protected override void OnEnter()
{
    _subscription = _eventBus.Subscribe<WindowResizedEvent>(e =>
    {
        // Update camera aspect ratio
        var aspectRatio = (float)e.Width / e.Height;
        _camera.AspectRatio = aspectRatio;

        // Update UI layout
        _uiCanvas.UpdateLayout(e.Width, e.Height);
    });
}
```

[:octicons-arrow-right-24: Full guide: Window Events](window-events.md)

---

### Create Custom Event

```csharp
// Define event
public class PlayerDiedEvent
{
    public int Score { get; set; }
    public Vector2 Position { get; set; }
}

// Publish event
_eventBus.Publish(new PlayerDiedEvent
{
    Score = _playerScore,
    Position = _playerPosition
});

// Subscribe to event
_subscription = _eventBus.Subscribe<PlayerDiedEvent>(e =>
{
    Logger.LogInformation("Player died at {Pos} with score {Score}",
        e.Position, e.Score);

    ShowGameOverScreen(e.Score);
});
```

---

### Decouple Game Logic

```csharp
// Instead of direct coupling
public class Player
{
    private readonly GameManager _gameManager;

    public void Die()
    {
        _gameManager.OnPlayerDied(this);  // ? Tight coupling
    }
}

// Use events for loose coupling
public class Player
{
    private readonly IEventBus _eventBus;

    public Player(IEventBus eventBus) => _eventBus = eventBus;

    public void Die()
    {
        _eventBus.Publish(new PlayerDiedEvent { ... });  // ? Decoupled
    }
}

// Multiple listeners can react
_eventBus.Subscribe<PlayerDiedEvent>(e => UpdateUI());
_eventBus.Subscribe<PlayerDiedEvent>(e => PlaySound());
_eventBus.Subscribe<PlayerDiedEvent>(e => ShowGameOver());
```

---

### Event-Driven AI

```csharp
// Player shoots - publish event
_eventBus.Publish(new WeaponFiredEvent
{
    Position = _playerPosition,
    Loudness = 100f
});

// Enemies react to sound
_eventBus.Subscribe<WeaponFiredEvent>(e =>
{
    foreach (var enemy in _enemies)
    {
        var distance = Vector2.Distance(enemy.Position, e.Position);

        if (distance < e.Loudness)
        {
            enemy.Investigate(e.Position);
        }
    }
});
```

---

## Best Practices

### ? DO

1. **Dispose the Subscribe token in OnExit()** - Prevents memory leaks
2. **Use IEventBus for decoupling** - Loose coupling between systems
3. **Create typed events** - Clear event data structure
4. **Subscribe in OnEnter()** - Framework properties and services are available here
5. **Constructor-inject IEventBus** - It's already registered as a singleton for you

```csharp
// ? Good pattern
private IDisposable? _subscription;

protected override void OnEnter()
{
    _subscription = _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
}

protected override void OnExit()
{
    _subscription?.Dispose();
}

private void OnWindowResized(WindowResizedEvent e)
{
    // Handle event
}
```

---

### ? DON'T

1. **Don't forget to dispose the subscription** - Memory leaks
2. **Don't use for high-frequency events** - Performance overhead
3. **Don't mutate event data** - Events should be immutable
4. **Don't use generic object events** - Use typed events
5. **Don't create circular event chains** - Stack overflow

```csharp
// ? Bad - forgot to dispose the subscription
protected override void OnEnter()
{
    _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
}
// OnExit missing the Dispose() call - memory leak!

// ? Bad - high frequency
protected override void OnUpdate(GameTime gameTime)
{
    _eventBus.Publish(new FrameUpdateEvent());  // 60 times per second - slow!
}

// ? Bad - circular events
_eventBus.Subscribe<EventA>(e => _eventBus.Publish(new EventB()));
_eventBus.Subscribe<EventB>(e => _eventBus.Publish(new EventA()));  // Stack overflow!
```

---

## Event Patterns

### Observer Pattern

```csharp
// Classic observer pattern via IEventBus
public class HealthChangedEvent
{
    public Entity Entity { get; set; }
    public int OldHealth { get; set; }
    public int NewHealth { get; set; }
}

// Publisher
public class HealthComponent : Component
{
    private readonly IEventBus _eventBus;
    private int _health;

    public HealthComponent(IEventBus eventBus) => _eventBus = eventBus;

    public int Health
    {
        get => _health;
        set
        {
            var old = _health;
            _health = value;

            _eventBus.Publish(new HealthChangedEvent
            {
                Entity = Entity,
                OldHealth = old,
                NewHealth = value
            });
        }
    }
}

// Observers
_eventBus.Subscribe<HealthChangedEvent>(e => UpdateHealthBar(e));
_eventBus.Subscribe<HealthChangedEvent>(e => CheckDeath(e));
_eventBus.Subscribe<HealthChangedEvent>(e => PlayDamageSound(e));
```

---

### Command Pattern

```csharp
// Commands as events
public interface ICommand
{
    void Execute();
}

public class MoveCommand : ICommand
{
    public Vector2 Direction { get; set; }
    public void Execute() { /* move logic */ }
}

// Publish command
_eventBus.Publish<ICommand>(new MoveCommand { Direction = Vector2.Up });

// Execute commands
_eventBus.Subscribe<ICommand>(cmd => cmd.Execute());
```

---

## Troubleshooting

### Memory Leak

**Symptom:** Memory usage grows after scene changes

**Cause:** Event subscriptions not disposed

**Solution:**

```csharp
private IDisposable? _subscription;

protected override void OnEnter()
{
    _subscription = _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
}

protected override void OnExit()
{
    _subscription?.Dispose();  // ? Prevents leak
}
```

---

### Events Not Firing

**Symptom:** Subscribed but handler never called

**Solutions:**

1. **Check event type matches:**

```csharp
// ? Different types won't match
_eventBus.Publish(new PlayerDiedEvent());
_eventBus.Subscribe<EnemyDiedEvent>(e => { }); // Won't fire

// ? Same type
_eventBus.Publish(new PlayerDiedEvent());
_eventBus.Subscribe<PlayerDiedEvent>(e => { }); // Will fire
```

2. **Verify subscription happened:**

```csharp
Logger.LogInformation("Subscribed to PlayerDiedEvent");
_subscription = _eventBus.Subscribe<PlayerDiedEvent>(e =>
{
    Logger.LogInformation("Event received!");  // Debug
});
```

---

### Exception in Handler

**Symptom:** Exception in one handler breaks others

**Good news:** `IEventBus.Publish` already catches and logs exceptions per-handler internally
— an exception thrown by one subscriber does not prevent the remaining subscribers from
running. If you're not seeing this behavior, check your logging configuration for the
`EventBus` category.

---

## Performance Considerations

### Event Bus Overhead

**Cost per event:**
- Lookup: O(1) - Fast dictionary lookup
- Notify: O(n) - Iterate all subscribers (allocation-free on the hot path)

**Recommendation:**
- ? Use for infrequent events (player died, level complete)
- ? Avoid for high-frequency events (every frame update)

```csharp
// ? Good - infrequent
_eventBus.Publish(new LevelCompleteEvent());
_eventBus.Publish(new PlayerDiedEvent());

// ? Bad - every frame
protected override void OnUpdate(GameTime gameTime)
{
    _eventBus.Publish(new FrameUpdateEvent());  // 60 times per second!
}
```

---

## Related Topics

- [Window Events](window-events.md) - Handle window events
- [Dependency Injection](../fundamentals/dependency-injection.md) - Inject IEventBus
- [Architecture](../fundamentals/architecture.md) - Event-driven architecture
