---
title: UI Framework
description: Build user interfaces with Brine2D's UI component system
---

# UI Framework

Learn how to create user interfaces with Brine2D's built-in UI framework: buttons, text inputs, dialogs, and more.

---

## Quick Start

```csharp
using Brine2D.UI;
using System.Numerics;

public class MenuScene : Scene
{
    private readonly UICanvas _canvas;

    public MenuScene(UICanvas canvas)
    {
        _canvas = canvas;
    }

    protected override Task OnLoadAsync(CancellationToken ct)
    {
        var playButton = new UIButton("Play", new Vector2(350, 250), new Vector2(100, 40));

        playButton.OnClick += () =>
        {
            Logger.LogInformation("Play button clicked!");
        };

        _canvas.Add(playButton);

        return Task.CompletedTask;
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        _canvas.Update((float)gameTime.DeltaTime);
    }

    protected override void OnRender(GameTime gameTime)
    {
        _canvas.Render(Renderer);
    }
}
```

---

## Topics

### System

| Guide | Description |
|---|---|
| **[UICanvas](canvas.md)** | DI setup, screen size, input layers, focus, find-by-name |
| **[Positioning & Anchoring](positioning.md)** | UIAnchor, AnchorOffset, ZOrder, TabIndex |

### Components

| Guide | Description |
|---|---|
| **[Quick Reference](components.md)** | All components at a glance |
| **[Button](button.md)** | UIButton: states, textures, focus |
| **[Label & Rich Text](label.md)** | UILabel, UIRichTextLabel: BBCode, wrapping, shadows |
| **[Image](image.md)** | UIImage: tint, rotation, source rect, animation |
| **[Text Input & Area](text-input.md)** | UITextInput, UITextArea: selection, undo, password |
| **[Slider & SpinBox](slider.md)** | UISlider, UISpinBox: orientation, step, labels |
| **[Checkbox & Radio](selection.md)** | UICheckbox, UIRadioButton, UIRadioButtonGroup |
| **[Dropdown](dropdown.md)** | UIDropdown: items, keyboard navigation |
| **[Progress Bar](progress.md)** | UIProgressBar: direction, custom text, HUD patterns |
| **[Tooltip & Toast](tooltip-toast.md)** | UITooltip, UIToast: delay, positioning, dismissal |

### Layout

| Guide | Description |
|---|---|
| **[Panel, Stack & Grid](layout.md)** | UIPanel, UIStackPanel, UIGrid |
| **[Scroll View](scroll-view.md)** | UIScrollView: content sizing, scrollbars |
| **[Tab Container](tab-container.md)** | UITabContainer: tabs, scrollable tab bar |

### Dialogs & Menus

| Guide | Description |
|---|---|
| **[Dialog](dialog.md)** | UIDialog: modal, draggable, custom children |
| **[Menus](menus.md)** | UIMenuBar, UIContextMenu, UIMenuItem |

### Advanced

| Guide | Description |
|---|---|
| **[Virtual List](virtual-list.md)** | UIVirtualList\<T\>: virtualized scrolling, custom row renderer |
| **[Tree View](tree-view.md)** | UITreeView, UITreeNode: hierarchy, keyboard navigation |
| **[Drag & Drop](drag-drop.md)** | RegisterDraggable, UIDropTarget, IDragPayload |
| **[World Labels](world-labels.md)** | UIWorldLabel: world-space projection |
| **[Animation & Tweens](animation.md)** | UITween, UITweenSequence, UIEasing |
| **[Custom UI](custom.md)** | Implement IUIComponent and IAnchoredUIComponent |

---

## Key Concepts

### UICanvas

The `UICanvas` manages all UI elements for a scene:

```csharp
// Register as scoped (per-scene)
builder.Services.AddUICanvas();

// Inject in scene
public class MenuScene : Scene
{
    private readonly UICanvas _canvas;

    public MenuScene(UICanvas canvas)
    {
        _canvas = canvas;
    }
}
```

**Benefits:**
- Automatic input handling
- Z-ordering (layers)
- Lifecycle management
- Input layer integration

[:octicons-arrow-right-24: Learn more: UI Components](components.md)

---

### Available Components

Brine2D includes **25+ production-ready UI components**:

| Component | Description |
|-----------|-------------|
| **UIButton** | Clickable button with text and optional nine-slice textures |
| **UILabel** | Static or dynamic text |
| **UIRichTextLabel** | BBCode-formatted text with alignment, shadows, and wrapping |
| **UITextInput** | Single-line text entry with selection, undo/redo, and password mode |
| **UITextArea** | Multi-line text editor with selection, scrolling, and undo/redo |
| **UISlider** | Value slider with optional label and step snapping |
| **UISpinBox** | Numeric field with increment/decrement buttons |
| **UICheckbox** | Toggle on/off with label |
| **UIRadioButton** | Single selection from a `UIRadioButtonGroup` |
| **UIProgressBar** | Loading or health bar with optional percentage text |
| **UIDropdown** | Dropdown selection menu |
| **UIPanel** | Container with background and optional child clipping |
| **UIScrollView** | Scrollable container with optional horizontal/vertical scrollbars |
| **UIStackPanel** | Auto-stacks children vertically or horizontally |
| **UIGrid** | Arranges children in a fixed-column grid |
| **UITabContainer** | Tabbed interface with scrollable tab bar |
| **UIDialog** | Modal popup with title bar, message, and buttons |
| **UIImage** | Display a texture with optional animation, tint, and rotation |
| **UITooltip** | Hover information attached to any component |
| **UIToast** | Timed notification shown via `UICanvas.ShowToast` |
| **UIContextMenu** | Right-click overlay shown via `UICanvas.ShowContextMenu` |
| **UIMenuBar** | Horizontal menu bar with dropdown submenus |
| **UIVirtualList\<T\>** | High-performance virtualized scrolling list |
| **UITreeView** | Hierarchical tree with expand/collapse and keyboard navigation |
| **UIDropTarget** | Drag-and-drop drop zone |
| **UIWorldLabel** | World-space label projected to screen coordinates |

[:octicons-arrow-right-24: Full list: UI Components](components.md)

---

## Common Tasks

### Create Button

```csharp
var button = new UIButton("Start Game", new Vector2(350, 250), new Vector2(100, 40))
{
    NormalColor = Color.Blue,
    TextColor = Color.White
};

button.OnClick += () =>
{
    Logger.LogInformation("Button clicked!");
};

_canvas.Add(button);
```

---

### Create Text Input

```csharp
var nameInput = new UITextInput(new Vector2(300, 200), new Vector2(200, 30))
{
    Placeholder = "Enter your name..."
};

nameInput.OnTextChanged += text =>
{
    Logger.LogInformation("Name: {Name}", text);
};

_canvas.Add(nameInput);
```

---

### Create Slider

```csharp
var volumeSlider = new UISlider(new Vector2(300, 250), new Vector2(200, 20))
{
    MinValue = 0f,
    MaxValue = 1f,
    Value = 0.8f
};

volumeSlider.OnValueChanged += value =>
{
    _audio.SetMasterVolume(value);
    Logger.LogInformation("Volume: {Volume:P0}", value);
};

_canvas.Add(volumeSlider);
```

---

### Create Dialog

```csharp
var dialog = new UIDialog("Quit Game?", "Are you sure you want to quit?", new Vector2(300, 150));

dialog.AddButton("Yes", () =>
{
    Application.Quit();
});

dialog.AddButton("No", () =>
{
    dialog.Visible = false;
});

_canvas.Add(dialog);
```

---

### HUD (Health Bar)

```csharp
var healthLabel = new UILabel("Health:", new Vector2(10, 10))
{
    Color = Color.White
};

var healthBar = new UIProgressBar(new Vector2(80, 10), new Vector2(200, 20))
{
    MinValue = 0,
    MaxValue = 100,
    Value = 75,
    FillColor = Color.Green,
    BackgroundColor = new Color(50, 50, 50)
};

_canvas.Add(healthLabel);
_canvas.Add(healthBar);

// Update health each frame
healthBar.Value = _playerHealth;
```

---

### Layout Container

```csharp
// Automatic vertical layout
var menu = new UIStackPanel(new Vector2(350, 200))
{
    Orientation = StackOrientation.Vertical,
    Spacing = 10
};

menu.AddChild(new UIButton("Play",    new Vector2(0, 0), new Vector2(100, 40)));
menu.AddChild(new UIButton("Options", new Vector2(0, 0), new Vector2(100, 40)));
menu.AddChild(new UIButton("Quit",    new Vector2(0, 0), new Vector2(100, 40)));

_canvas.Add(menu);
// Buttons are automatically positioned vertically with 10 px spacing
```

---

## Input Layers

The `UICanvas` implements `IInputLayer` and should be registered so it can consume input before game logic:

```csharp
protected override Task OnLoadAsync(CancellationToken ct)
{
    // Register canvas as a high-priority input layer (priority 1000)
    _inputLayerManager.RegisterLayer(_canvas);

    // Build UI...
    return Task.CompletedTask;
}
```

When a `UIDialog` is open it automatically blocks input to anything below it. When the dialog closes, normal input resumes.

[:octicons-arrow-right-24: Learn more: Input Layers](../input/layers.md)

---

## Best Practices

### ✅ DO

1. **Use UICanvas**: one per scene, injected via DI
2. **Position with `Vector2`**: `new Vector2(x, y)` for `Position` and `Size`
3. **Handle events**: `OnClick`, `OnValueChanged`, `OnTextChanged`, etc.
4. **Use layout panels**: `UIStackPanel` or `UIGrid` for automatic positioning
5. **Z-order matters**: last added renders on top when `ZOrder` is equal

```csharp
// ✅ Good pattern
protected override Task OnLoadAsync(CancellationToken ct)
{
    CreateMenuUI();
    return Task.CompletedTask;
}

protected override void OnUpdate(GameTime gameTime)
{
    _canvas.Update((float)gameTime.DeltaTime);
}

protected override void OnRender(GameTime gameTime)
{
    DrawGameObjects();
    _canvas.Render(Renderer); // UI renders on top
}
```

---

### ❌ DON'T

1. **Don't skip `Update()`**: animations, tooltips, and toasts need it
2. **Don't skip `Render()`**: nothing will appear
3. **Don't hardcode positions**: use anchors or layout panels for different screen sizes

```csharp
// ❌ Bad: hardcoded for 1280×720
var button = new UIButton("Play", new Vector2(640, 360), new Vector2(100, 40));

// ✅ Good: anchored to center
var button = new UIButton("Play", Vector2.Zero, new Vector2(100, 40))
{
    Anchor = UIAnchor.MiddleCenter,
    AnchorOffset = new Vector2(-50, -20)
};
```

---

## Styling

### Custom Colors

```csharp
var button = new UIButton("Custom", new Vector2(10, 10), new Vector2(120, 40))
{
    NormalColor  = new Color(50, 50, 50, 255),
    HoverColor   = new Color(70, 70, 70, 255),
    PressedColor = new Color(30, 30, 30, 255),
    TextColor    = Color.White
};
```

---

### Custom Fonts

```csharp
var label = new UILabel("Custom Font", new Vector2(100, 100))
{
    Font  = await _assets.GetOrLoadFontAsync("assets/fonts/custom.ttf", 24),
    Color = Color.Gold
};
```

---

### Anchoring

Every component implementing `IAnchoredUIComponent` supports `Anchor` and `AnchorOffset` for resolution-independent placement:

```csharp
var label = new UILabel("Score: 0", Vector2.Zero)
{
    Anchor       = UIAnchor.TopRight,
    AnchorOffset = new Vector2(-120, 10)   // 120 px from right edge, 10 px from top
};

_canvas.Add(label);
// UICanvas resolves the anchor position automatically during Render
```

---

## Troubleshooting

### UI Not Responding to Input

**Symptom:** Buttons don't respond to clicks.

**Solutions:**

1. **Check `Update()` is called:**

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    _canvas.Update((float)gameTime.DeltaTime);  // Must be called!
}
```

2. **Verify the component is added:**

```csharp
_canvas.Add(button);  // Don't forget!
```

3. **Register the canvas as an input layer:**

```csharp
_inputLayerManager.RegisterLayer(_canvas);
```

4. **Check Z-order: the topmost element receives input first:**

```csharp
_canvas.Add(background);  // Lower (rendered first)
_canvas.Add(button);      // Higher (receives input first)
```

---

### UI Not Visible

**Symptom:** UI elements are not drawn.

**Solutions:**

1. **Check `Render()` is called:**

```csharp
protected override void OnRender(GameTime gameTime)
{
    _canvas.Render(Renderer);  // Must be called!
}
```

2. **Check coordinates are on screen:**

```csharp
Logger.LogDebug("Button at {Pos}", button.Position);
```

3. **Check visibility:**

```csharp
button.Visible = true;  // Defaults to true
```

---

### Text Not Showing

**Symptom:** Button or label has no text.

**Solutions:**

1. **Check font is loaded** (if using a custom font):

```csharp
if (button.Font == null)
    Logger.LogWarning("Button has no font: using renderer default");
```

2. **Check text color:**

```csharp
button.TextColor = Color.White;  // Not transparent!
```

---

## Related Topics

- [UI Components](components.md): complete component reference
- [Custom UI](custom.md): build your own components
- [Input Layers](../input/layers.md): priority-based input routing
- [Mouse Input](../input/mouse.md): mouse handling

---

**Ready to build UI?** Start with [UI Components](components.md)!
