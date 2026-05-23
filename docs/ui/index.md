---
title: UI Framework
description: Build user interfaces with Brine2D's UI component system
---

# UI Framework

Learn how to create user interfaces with Brine2D's built-in UI framework - buttons, text inputs, dialogs, and more.

---

## Quick Start

```csharp
using Brine2D.UI;

public class MenuScene : Scene
{
    private readonly UICanvas _uiCanvas;
    
    public MenuScene(UICanvas uiCanvas)
    {
        _uiCanvas = uiCanvas;
    }
    
    protected override Task OnLoadAsync(CancellationToken ct)
    {
        // Create button
        var playButton = new Button
        {
            Text = "Play",
            X = 350,
            Y = 250,
            Width = 100,
            Height = 40
        };
        
        playButton.OnClick += () =>
        {
            Logger.LogInformation("Play button clicked!");
            // Load game scene
        };
        
        _uiCanvas.AddElement(playButton);
        
        return Task.CompletedTask;
    }
    
    protected override void OnUpdate(GameTime gameTime)
    {
        _uiCanvas.Update(gameTime);
    }
    
    protected override void OnRender(GameTime gameTime)
    {
        _uiCanvas.Render(Renderer);
    }
}
```

---

## Topics

| Guide | Description |
|---|---|
| **[UI Components](components.md)** | 15+ built-in UI components|
| **[Custom UI](custom.md)** | Create custom UI elements|

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

Brine2D includes **15+ production-ready UI components**:

| Component | Description |
|-----------|-------------|
| **Button** | Clickable button with text/icon |
| **Label** | Static or dynamic text |
| **TextInput** | Text entry field |
| **Slider** | Value slider (volume, brightness) |
| **Checkbox** | Toggle on/off |
| **RadioButton** | Single selection from group |
| **ProgressBar** | Loading/health bar |
| **Panel** | Container for other elements |
| **Dialog** | Modal popup window |
| **Tooltip** | Hover information |
| **Dropdown** | Selection menu |
| **ScrollView** | Scrollable container |
| **TabControl** | Tabbed interface |
| **Image** | Display texture |
| **LayoutContainer** | Automatic positioning |

[:octicons-arrow-right-24: Full list: UI Components](components.md)

---

## Common Tasks

### Create Button

```csharp
var button = new Button
{
    Text = "Start Game",
    X = 350,
    Y = 250,
    Width = 100,
    Height = 40,
    BackgroundColor = Color.Blue,
    TextColor = Color.White
};

button.OnClick += () =>
{
    Logger.LogInformation("Button clicked!");
};

_uiCanvas.AddElement(button);
```

---

### Create Text Input

```csharp
var nameInput = new TextInput
{
    X = 300,
    Y = 200,
    Width = 200,
    Height = 30,
    Placeholder = "Enter your name..."
};

nameInput.OnTextChanged += (text) =>
{
    Logger.LogInformation("Name: {Name}", text);
};

_uiCanvas.AddElement(nameInput);
```

---

### Create Slider

```csharp
var volumeSlider = new Slider
{
    X = 300,
    Y = 250,
    Width = 200,
    Height = 20,
    MinValue = 0f,
    MaxValue = 1f,
    Value = 0.8f
};

volumeSlider.OnValueChanged += (value) =>
{
    _audio.SetMasterVolume(value);
    Logger.LogInformation("Volume: {Volume:P0}", value);
};

_uiCanvas.AddElement(volumeSlider);
```

---

### Create Dialog

```csharp
var dialog = new Dialog
{
    Title = "Quit Game?",
    Message = "Are you sure you want to quit?",
    X = 250,
    Y = 200,
    Width = 300,
    Height = 150
};

dialog.AddButton("Yes", () =>
{
    Application.Quit();
});

dialog.AddButton("No", () =>
{
    dialog.Close();
});

_uiCanvas.AddElement(dialog);
```

---

### HUD (Health Bar)

```csharp
// Health label
var healthLabel = new Label
{
    Text = "Health:",
    X = 10,
    Y = 10,
    TextColor = Color.White
};

// Health bar
var healthBar = new ProgressBar
{
    X = 80,
    Y = 10,
    Width = 200,
    Height = 20,
    MinValue = 0,
    MaxValue = 100,
    Value = 75,  // 75% health
    ForegroundColor = Color.Green,
    BackgroundColor = Color.DarkGray
};

_uiCanvas.AddElement(healthLabel);
_uiCanvas.AddElement(healthBar);

// Update health
healthBar.Value = _playerHealth;
```

---

### Layout Container

```csharp
// Automatic vertical layout
var menu = new VerticalLayoutContainer
{
    X = 350,
    Y = 200,
    Spacing = 10
};

menu.AddChild(new Button { Text = "Play", Width = 100, Height = 40 });
menu.AddChild(new Button { Text = "Options", Width = 100, Height = 40 });
menu.AddChild(new Button { Text = "Quit", Width = 100, Height = 40 });

_uiCanvas.AddElement(menu);
// Buttons automatically positioned vertically with 10px spacing
```

---

## Input Layers

UI elements automatically create input layers for priority handling:

```csharp
// UI layer (priority 100 - high)
var dialog = new Dialog { ... };
_uiCanvas.AddElement(dialog);

// When dialog is open, game input is blocked
// Dialog consumes input events first

// When dialog closes, game input resumes
```

[:octicons-arrow-right-24: Learn more: Input Layers](../input/layers.md)

---

## Best Practices

### ✅ DO

1. **Use UICanvas** - One per scene
2. **Position with X/Y** - Absolute screen coordinates
3. **Handle events** - OnClick, OnValueChanged, etc.
4. **Use layouts** - Automatic positioning
5. **Z-order matters** - Last added = on top

```csharp
// ✅ Good pattern
protected override Task OnLoadAsync(CancellationToken ct)
{
    // Create all UI
    CreateMenuUI();
    return Task.CompletedTask;
}

protected override void OnUpdate(GameTime gameTime)
{
    // Update UI
    _uiCanvas.Update(gameTime);
}

protected override void OnRender(GameTime gameTime)
{
    // Render game first
    DrawGameObjects();
    
    // Render UI last (on top)
    _uiCanvas.Render(Renderer);
}
```

---

### ❌ DON'T

1. **Don't create multiple UICanvas** - One per scene
2. **Don't forget to update** - Call Update() in OnUpdate()
3. **Don't forget to render** - Call Render() in OnRender()
4. **Don't manually handle input** - UICanvas does it
5. **Don't hardcode positions** - Use layouts or calculate from screen size

```csharp
// ❌ Bad - hardcoded for 800x600
var button = new Button { X = 400, Y = 300 };

// ✅ Good - centered
var button = new Button 
{ 
    X = (screenWidth - buttonWidth) / 2,
    Y = (screenHeight - buttonHeight) / 2
};
```

---

## Styling

### Custom Colors

```csharp
var button = new Button
{
    Text = "Custom",
    BackgroundColor = new Color(50, 50, 50, 255),     // Dark gray
    HoverColor = new Color(70, 70, 70, 255),          // Lighter on hover
    PressedColor = new Color(30, 30, 30, 255),        // Darker when pressed
    TextColor = Color.White,
    BorderColor = Color.Blue,
    BorderWidth = 2
};
```

---

### Custom Fonts

```csharp
var label = new Label
{
    Text = "Custom Font",
    Font = await _assets.GetOrLoadFontAsync("assets/fonts/custom.ttf", 24),
    TextColor = Color.Gold
};
```

---

## Troubleshooting

### UI Not Responding to Input

**Symptom:** Buttons don't respond to clicks

**Solutions:**

1. **Check Update() is called:**

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    _uiCanvas.Update(gameTime);  // Must be called!
}
```

2. **Verify element is added:**

```csharp
_uiCanvas.AddElement(button);  // Don't forget!
```

3. **Check Z-order:**

```csharp
// Elements added last are on top
_uiCanvas.AddElement(background);  // Bottom
_uiCanvas.AddElement(button);      // Top (receives input)
```

---

### UI Not Visible

**Symptom:** UI elements not drawn

**Solutions:**

1. **Check Render() is called:**

```csharp
protected override void OnRender(GameTime gameTime)
{
    _uiCanvas.Render(Renderer);  // Must be called!
}
```

2. **Check coordinates:**

```csharp
// Make sure element is on screen
Logger.LogDebug("Button at ({X}, {Y})", button.X, button.Y);
```

3. **Check visibility:**

```csharp
button.Visible = true;  // Default is true
```

---

### Text Not Showing

**Symptom:** Button has no text

**Solutions:**

1. **Check font is loaded:**

```csharp
if (button.Font == null)
{
    Logger.LogWarning("Button has no font");
}
```

2. **Check text color:**

```csharp
button.TextColor = Color.White;  // Not transparent!
```

---

## Related Topics

- [UI Components](components.md) - Complete component list
- [Custom UI](custom.md) - Build custom elements
- [Input Layers](../input/layers.md) - Priority-based input
- [Mouse Input](../input/mouse.md) - Mouse handling

---

**Ready to build UI?** Start with [UI Components](components.md)!
