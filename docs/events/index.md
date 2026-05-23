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
    private readonly EventBus _eventBus;
    
    public GameScene(EventBus eventBus)
    {
        _eventBus = eventBus;
    }
    
    protected override Task OnInitializeAsync(CancellationToken ct)
    {
        // Subscribe to window resize event
        _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
        
        return Task.CompletedTask;
    }
    
    private void OnWindowResized(WindowResizedEvent e)
    {
        Logger.LogInformation("Window resized to {Width}x{Height}", 
            e.Width, e.Height);
        
        // Adjust camera, UI, etc.
        UpdateCameraAspectRatio(e.Width, e.Height);
    }
    
    protected override Task OnUnloadAsync(CancellationToken ct)
    {
        // Unsubscribe to prevent memory leaks
        _eventBus.Unsubscribe<WindowResizedEvent>(OnWindowResized);
        
        return Task.CompletedTask;
    }
}
```

---

## Topics

| Guide | Description |
|-------|-------------|
| **[Window Events](window-events.md)** | Handle window resize, focus, minimize, etc. | â­ Beginner |

---

## Key Concepts

### EventBus

The `EventBus` provides pub/sub event system:

```csharp
public class EventBus
{
    // Subscribe to events
    void Subscribe<TEvent>(Action<TEvent> handler);
    
    // Unsubscribe
    void Unsubscribe<TEvent>(Action<TEvent> handler);
    
    // Publish events
    void Publish<TEvent>(TEvent eventData);
}
```

**Register as singleton** (shared across scenes):

```csharp
builder.Services.AddSingleton<EventBus>();
```

---

### Built-In Events

Brine2D provides window events out of the box:

| Event | When Fired |
|-------|------------|
| **WindowResizedEvent** | Window size changed |
| **WindowFocusedEvent** | Window gained focus |
| **WindowUnfocusedEvent** | Window lost focus |
| **WindowMinimizedEvent** | Window minimized |
| **WindowRestoredEvent** | Window restored from minimize |
| **WindowClosedEvent** | Window close requested |

[:octicons-arrow-right-24: Full list: Window Events](window-events.md)

---

## Common Tasks

### Handle Window Resize

```csharp
protected override Task OnInitializeAsync(CancellationToken ct)
{
    _eventBus.Subscribe<WindowResizedEvent>(e =>
    {
        // Update camera aspect ratio
        var aspectRatio = (float)e.Width / e.Height;
        _camera.AspectRatio = aspectRatio;
        
        // Update UI layout
        _uiCanvas.UpdateLayout(e.Width, e.Height);
    });
    
    return Task.CompletedTask;
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
_eventBus.Subscribe<PlayerDiedEvent>(e =>
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
        _gameManager.OnPlayerDied(this);  // âŒ Tight coupling
    }
}

// Use events for loose coupling
public class Player
{
    private readonly EventBus _eventBus;
    
    public void Die()
    {
        _eventBus.Publish(new PlayerDiedEvent { ... });  // âœ… Decoupled
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

### âœ… DO

1. **Unsubscribe in OnUnloadAsync()** - Prevent memory leaks
2. **Use EventBus for decoupling** - Loose coupling between systems
3. **Create typed events** - Clear event data structure
4. **Subscribe in OnInitializeAsync()** - Early setup
5. **Use singleton EventBus** - Shared across scenes

```csharp
// âœ… Good pattern
protected override Task OnInitializeAsync(CancellationToken ct)
{
    _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
    return Task.CompletedTask;
}

protected override Task OnUnloadAsync(CancellationToken ct)
{
    _eventBus.Unsubscribe<WindowResizedEvent>(OnWindowResized);
    return Task.CompletedTask;
}

private void OnWindowResized(WindowResizedEvent e)
{
    // Handle event
}
```

---

### âŒ DON'T

1. **Don't forget to unsubscribe** - Memory leaks
2. **Don't use for high-frequency events** - Performance overhead
3. **Don't mutate event data** - Events should be immutable
4. **Don't use generic object events** - Use typed events
5. **Don't create circular event chains** - Stack overflow

```csharp
// âŒ Bad - forgot to unsubscribe
protected override Task OnInitializeAsync(CancellationToken ct)
{
    _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
    return Task.CompletedTask;
}
// OnUnloadAsync missing - memory leak!

// âŒ Bad - high frequency
protected override void OnUpdate(GameTime gameTime)
{
    _eventBus.Publish(new FrameUpdateEvent());  // 60 times per second - slow!
}

// âŒ Bad - circular events
_eventBus.Subscribe<EventA>(e => _eventBus.Publish(new EventB()));
_eventBus.Subscribe<EventB>(e => _eventBus.Publish(new EventA()));  // Stack overflow!
```

---

## Event Patterns

### Observer Pattern

```csharp
// Classic observer pattern via EventBus
public class HealthChangedEvent
{
    public Entity Entity { get; set; }
    public int OldHealth { get; set; }
    public int NewHealth { get; set; }
}

// Publisher
public class HealthComponent : Component
{
    private readonly EventBus _eventBus;
    private int _health;
    
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

**Cause:** Event handlers not unsubscribed

**Solution:**

```csharp
// Track handlers to unsubscribe
private Action<WindowResizedEvent> _resizeHandler;

protected override Task OnInitializeAsync(CancellationToken ct)
{
    _resizeHandler = OnWindowResized;
    _eventBus.Subscribe(_resizeHandler);
    return Task.CompletedTask;
}

protected override Task OnUnloadAsync(CancellationToken ct)
{
    _eventBus.Unsubscribe(_resizeHandler);  // âœ… Prevents leak
    return Task.CompletedTask;
}
```

---

### Events Not Firing

**Symptom:** Subscribed but handler never called

**Solutions:**

1. **Check event type matches:**

```csharp
// âŒ Different types won't match
_eventBus.Publish(new PlayerDiedEvent());
_eventBus.Subscribe<EnemyDiedEvent>(e => { }); // Won't fire

// âœ… Same type
_eventBus.Publish(new PlayerDiedEvent());
_eventBus.Subscribe<PlayerDiedEvent>(e => { }); // Will fire
```

2. **Verify subscription happened:**

```csharp
Logger.LogInformation("Subscribed to PlayerDiedEvent");
_eventBus.Subscribe<PlayerDiedEvent>(e =>
{
    Logger.LogInformation("Event received!");  // Debug
});
```

---

### Exception in Handler

**Symptom:** Exception in one handler breaks others

**Solution:** EventBus should catch and log exceptions

```csharp
// EventBus implementation should handle exceptions
public void Publish<TEvent>(TEvent eventData)
{
    foreach (var handler in _handlers)
    {
        try
        {
            handler(eventData);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in event handler");
            // Continue to next handler
        }
    }
}
```

---

## Performance Considerations

### Event Bus Overhead

**Cost per event:**
- Lookup: O(1) - Fast dictionary lookup
- Notify: O(n) - Iterate all subscribers

**Recommendation:**
- âœ… Use for infrequent events (player died, level complete)
- âŒ Avoid for high-frequency events (every frame update)

```csharp
// âœ… Good - infrequent
_eventBus.Publish(new LevelCompleteEvent());
_eventBus.Publish(new PlayerDiedEvent());

// âŒ Bad - every frame
protected override void OnUpdate(GameTime gameTime)
{
    _eventBus.Publish(new FrameUpdateEvent());  // 60 times per second!
}
```

---

## Related Topics

- [Window Events](window-events.md) - Handle window events
- [Dependency Injection](../fundamentals/dependency-injection.md) - Inject EventBus
- [Architecture](../fundamentals/architecture.md) - Event-driven architecture

---

**Ready to use events?** Start with [Window Events](window-events.md)!