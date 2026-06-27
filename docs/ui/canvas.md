---
title: UICanvas
description: Central manager for UI components, input routing, and rendering
---

# UICanvas

`UICanvas` is the root of every Brine2D UI scene. It owns the component list, routes input to the correct control, manages focus, and coordinates overlays such as tooltips, toasts, dialogs, context menus, and drag-and-drop.

---

## Setup

### Dependency Injection (recommended)

```csharp
services.AddUICanvas();
```

When `IEventBus` is also registered the canvas subscribes to `WindowResizedEvent` automatically, keeping `ScreenSize` in sync.

### Manual construction

```csharp
// Minimal
var canvas = new UICanvas(inputContext);

// With automatic window-resize tracking
var canvas = new UICanvas(inputContext, eventBus);
```

---

## Game-loop integration

```csharp
// In your scene's Update
_canvas.Update((float)deltaTime);

// In your scene's Render
_canvas.Render(renderer);
```

Both calls must happen every frame. `Update` advances animations and tween state; `Render` draws every visible component in `ZOrder` order.

---

## Screen size

```csharp
// Set once at startup and again whenever the window resizes
_canvas.ScreenSize = new Vector2(1920, 1080);
```

`ScreenSize` drives anchor resolution, dialog centering, and dropdown flip logic. If you used `AddUICanvas()` with an `IEventBus` this is handled automatically.

---

## Adding and removing components

```csharp
var button = new UIButton("Play", new Vector2(100, 200), new Vector2(120, 40));
_canvas.Add(button);

// Later…
_canvas.Remove(button);

// Remove everything
_canvas.Clear();
```

`Add` automatically:

- Centers `UIDialog` on screen
- Propagates the current `ScreenSize` into nested dropdowns, tab containers, panels, and scroll views
- Registers `UIMenuBar` instances

---

## Finding components by name

```csharp
var btn = new UIButton("OK", new Vector2(0, 0), new Vector2(80, 32)) { Name = "OkButton" };
_canvas.Add(btn);

// Anywhere later
var found = _canvas.FindByName("OkButton");          // IUIComponent?
var typed = _canvas.FindByName<UIButton>("OkButton"); // UIButton?
```

`FindByName` searches recursively through panels, stack panels, grids, scroll views, tab containers, and dialogs.

---

## Input layers and priority

`UICanvas` implements `IInputLayer` with `Priority = 1000`. Register it with your engine's input dispatcher so UI input is consumed before game input:

```csharp
inputDispatcher.RegisterLayer(_canvas);
```

The canvas consumes the event when any enabled UI component handles it, preventing click-through to the game.

---

## Keyboard focus

```csharp
// Read
IUIComponent? focused = _canvas.FocusedWidget;

// Clear programmatically
_canvas.ClearWidgetFocus();
```

**Tab** cycles focus forward through components sorted by `TabIndex` (ascending). Components with equal `TabIndex` are ordered by add order. **Shift+Tab** cycles in reverse.

Focusable component types: `UIButton`, `UISlider`, `UITextInput`, `UITextArea`, `UIDropdown`, `UICheckbox`, `UIRadioButton`, `UITabContainer`, `UIScrollView`.

---

## ZOrder

Higher `ZOrder` components render on top and receive input first. Components with equal `ZOrder` fall back to add order (last added = on top).

```csharp
var hud     = new UIPanel(...) { ZOrder = 0 };
var overlay = new UIPanel(...) { ZOrder = 10 };
```

---

## Toasts

```csharp
_canvas.ShowToast("Settings saved", duration: 3f);
_canvas.ShowToast("Connection lost", duration: 5f, color: Color.Red);

// Read active toasts
IReadOnlyList<UIToast> toasts = _canvas.ActiveToasts;

// Dismiss early
_canvas.DismissToast(toast);
```

See [Tooltip & Toast](tooltip-toast.md) for full styling options.

---

## Context menus

```csharp
var menu = new UIContextMenu();
menu.AddItem("Copy",  () => Copy());
menu.AddItem("Paste", () => Paste());
menu.AddSeparator();
menu.AddItem("Delete", () => Delete(), enabled: false);

_canvas.ShowContextMenu(menu, mousePosition);
```

The canvas closes the menu automatically on selection, outside click, or Escape.

---

## Tweens

```csharp
float alpha = 1f;
var tween = new UITween(duration: 0.4f, from: 1f, to: 0f,
	easing: UIEasing.CubicOut,
	onUpdate: v => alpha = v);

_canvas.StartTween(tween);

// Stop early
_canvas.StopTween(tween);
_canvas.StopAllTweens();

// Inspect
IReadOnlyList<UITween>         active    = _canvas.ActiveTweens;
IReadOnlyList<UITweenSequence> sequences = _canvas.ActiveTweenSequences;
```

See [Animation & Tweens](animation.md) for sequences, loop modes, and easing reference.

---

## Drag and drop

```csharp
_canvas.RegisterDraggable(sourceComponent, payload);
_canvas.RegisterDropTarget(dropTarget);

// Query
bool dragging          = _canvas.IsDragging;
IUIComponent? dragSrc  = _canvas.DragSource;

// Events
_canvas.OnDragStarted   += (src, payload) => { };
_canvas.OnDragCancelled += (src, payload) => { };
```

See [Drag & Drop](drag-drop.md) for a complete walk-through.

---

## World-space labels

```csharp
var worldLabel = new UIWorldLabel
{
	WorldPosition = new Vector3(10f, 0f, 5f),
	Text          = "Enemy",
	TextColor     = Color.Red,
};
_canvas.AddWorldComponent(worldLabel);

// Remove later
_canvas.RemoveWorldComponent(worldLabel);

// Assign the camera so projection works
_canvas.WorldCamera = myCamera;
```

See [World Labels](world-labels.md) for projection details and culling options.

---

## Canvas lifecycle

| Method | Description |
|--------|-------------|
| `Add(component)` | Add a component to the canvas |
| `Remove(component)` | Remove a specific component |
| `Clear()` | Remove all components and reset all canvas state |
| `Dispose()` | Release any event-bus subscriptions |

`Clear()` resets all internal state: focus, active slider, active dropdown, active dialog, hovered controls, toasts, tweens, drag state, and the drag registry.
