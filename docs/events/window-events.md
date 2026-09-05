---
title: Window Events
description: Handle window resize, focus, minimize, and visibility events in Brine2D
---

# Window Events

Brine2D publishes a set of window and application lifecycle events through `IEventBus` so
your scenes can react to the OS window without polling. All events below live in the
`Brine2D.Events` namespace.

---

## Setup

Constructor-inject `IEventBus`, subscribe in `OnEnter()`, and dispose the returned token in
`OnExit()`:

```csharp
using Brine2D.Events;

public class GameScene : Scene
{
    private readonly IEventBus _eventBus;
    private IDisposable? _resizeSubscription;
    private IDisposable? _focusSubscription;

    public GameScene(IEventBus eventBus)
    {
        _eventBus = eventBus;
    }

    protected override void OnEnter()
    {
        _resizeSubscription = _eventBus.Subscribe<WindowResizedEvent>(OnWindowResized);
        _focusSubscription = _eventBus.Subscribe<WindowFocusLostEvent>(_ => OnWindowFocusLost());
    }

    protected override void OnExit()
    {
        _resizeSubscription?.Dispose();
        _focusSubscription?.Dispose();
    }

    private void OnWindowResized(WindowResizedEvent e)
    {
        Logger.LogInformation("Window resized to {Width}x{Height}", e.Width, e.Height);
    }

    private void OnWindowFocusLost()
    {
        // e.g. pause the game
    }
}
```

---

## Event Reference

| Event | Payload | When Fired |
|-------|---------|------------|
| `WindowResizedEvent` | `int Width, int Height` | The window's client size changed |
| `WindowFocusGainedEvent` | — | The window gained input focus |
| `WindowFocusLostEvent` | — | The window lost input focus |
| `WindowMinimizedEvent` | — | The window was minimized |
| `WindowRestoredEvent` | — | The window was restored from minimized state |
| `WindowHiddenEvent` | — | The window was hidden (e.g., system sleep, lock screen, display off) — rendering is suspended until `WindowShownEvent` |
| `WindowShownEvent` | — | The window became visible again after being hidden |
| `ApplicationQuitRequestedEvent` | — | The user requested to quit (e.g., clicked the window close button) |

---

## Handling Resize

`WindowResizedEvent` is the most commonly used window event - use it to keep cameras and UI
layout in sync with the window's new dimensions:

```csharp
protected override void OnEnter()
{
    _resizeSubscription = _eventBus.Subscribe<WindowResizedEvent>(e =>
    {
        var aspectRatio = (float)e.Width / e.Height;
        Camera.AspectRatio = aspectRatio;

        UICanvas.UpdateLayout(e.Width, e.Height);
    });
}
```

---

## Handling Focus Changes

Pause gameplay or audio when the window loses focus, and resume when it regains focus:

```csharp
protected override void OnEnter()
{
    _focusLostSubscription = _eventBus.Subscribe<WindowFocusLostEvent>(_ =>
    {
        Game.IsPaused = true;
        Audio.PauseMusic();
    });

    _focusGainedSubscription = _eventBus.Subscribe<WindowFocusGainedEvent>(_ =>
    {
        Game.IsPaused = false;
        Audio.ResumeMusic();
    });
}
```

---

## Handling Minimize / Visibility

Stop expensive work while the window isn't visible:

```csharp
protected override void OnEnter()
{
    _minimizedSubscription = _eventBus.Subscribe<WindowMinimizedEvent>(_ => PauseSimulation());
    _restoredSubscription = _eventBus.Subscribe<WindowRestoredEvent>(_ => ResumeSimulation());

    // WindowHiddenEvent/WindowShownEvent cover OS-level visibility changes
    // (e.g. system sleep, lock screen) in addition to user minimize/restore.
    _hiddenSubscription = _eventBus.Subscribe<WindowHiddenEvent>(_ => PauseSimulation());
    _shownSubscription = _eventBus.Subscribe<WindowShownEvent>(_ => ResumeSimulation());
}
```

---

## Handling Quit Requests

`ApplicationQuitRequestedEvent` fires when the user clicks the window close button. Subscribe
to it if you need to intercept the close (e.g., prompt to save) instead of quitting
immediately:

```csharp
protected override void OnEnter()
{
    _quitSubscription = _eventBus.Subscribe<ApplicationQuitRequestedEvent>(_ =>
    {
        if (HasUnsavedChanges)
        {
            ShowSavePrompt();
            return;
        }

        Game.RequestExit();
    });
}
```

---

## Related Topics

- [Events overview](index.md) - `IEventBus` fundamentals and custom events
- [Dependency Injection](../fundamentals/dependency-injection.md) - Inject `IEventBus`
