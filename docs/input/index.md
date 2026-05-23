---
title: Input
description: Handle keyboard, mouse, and gamepad input in Brine2D games
---

# Input

Learn how to handle player input from keyboard, mouse, and gamepads in your Brine2D games.

---

## Quick Start

```csharp
using Brine2D.Input;

public class GameScene : Scene
{
    protected override void OnUpdate(GameTime gameTime)
    {
        var speed = 200f * (float)gameTime.DeltaTime;

        // Keyboard
        if (Input.IsKeyDown(Key.W)) _position.Y -= speed;
        if (Input.IsKeyDown(Key.S)) _position.Y += speed;
        if (Input.IsKeyDown(Key.A)) _position.X -= speed;
        if (Input.IsKeyDown(Key.D)) _position.X += speed;

        // Mouse
        if (Input.IsMouseButtonPressed(MouseButton.Left))
            Logger.LogInformation("Clicked at {Pos}", Input.MousePosition);

        // Gamepad
        if (Input.IsGamepadButtonPressed(GamepadButton.A))
            Logger.LogInformation("Gamepad A pressed");
    }
}
```

---

## Topics

### Getting Started

| Guide | Description |
|-------|-------------|
| **[Keyboard](keyboard.md)** | Handle keyboard input | :star: Beginner |
| **[Mouse](mouse.md)** | Mouse position, clicks, and scroll wheel | :star: Beginner |

### Advanced

| Guide | Description |
|-------|-------------|
| **[Gamepad Support](gamepad.md)** | Controller/gamepad input | :star::star: Intermediate |
| **[Input Actions](actions.md)** | Rebindable logical actions with multiple bindings | :star::star: Intermediate |
| **[Input Layers](layers.md)** | Priority-based input routing for UI | :star::star::star: Advanced |

---

## Key Concepts

### The `Input` Framework Property

`Input` is an `IInputContext` available on every `Scene` from `OnLoadAsync` onwards -- no constructor injection needed:

```csharp
public class GameScene : Scene
{
    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyDown(Key.W))
            _position.Y -= 200f * (float)gameTime.DeltaTime;
    }
}
```

---

### Keyboard

```csharp
if (Input.IsKeyDown(Key.W))      MoveUp();          // Held (continuous)
if (Input.IsKeyPressed(Key.Space)) Jump();           // Just pressed (one-shot)
if (Input.IsKeyReleased(Key.E))  ReleaseCharge();   // Just released
if (Input.IsAnyKeyPressed())     StartGame();        // Any key this frame
```

[:octicons-arrow-right-24: Full guide: Keyboard](keyboard.md)

---

### Mouse

```csharp
var pos    = Input.MousePosition;        // Vector2, screen coordinates
var delta  = Input.MouseDelta;           // Frame-to-frame movement
var scroll = Input.ScrollWheelDelta;     // float, positive = up
var hscroll = Input.ScrollWheelDeltaX;  // float, horizontal scroll

if (Input.IsMouseButtonPressed(MouseButton.Left))
    SpawnAt(pos);

Input.IsCursorVisible   = false;  // Hide OS cursor
Input.IsRelativeMouseMode = true; // Capture mouse for FPS cameras
```

[:octicons-arrow-right-24: Full guide: Mouse](mouse.md)

---

### Gamepad

```csharp
if (Input.IsGamepadConnected())
{
    if (Input.IsGamepadButtonPressed(GamepadButton.A)) Jump();

    // Sticks return Vector2 with radial deadzone already applied (default 0.15)
    var stick = Input.GetGamepadLeftStick();
    _position += stick * speed * deltaTime;

    var trigger = Input.GetGamepadTrigger(GamepadAxis.RightTrigger);

    Input.RumbleGamepad(0.5f, 0.8f, TimeSpan.FromMilliseconds(200));
}
```

[:octicons-arrow-right-24: Full guide: Gamepad Support](gamepad.md)

---

### Input Actions (Rebindable)

```csharp
var jumpAction = new InputAction("Jump",
    new KeyBinding(Key.Space),
    new GamepadButtonBinding(GamepadButton.A));

if (jumpAction.IsPressed(Input)) Jump();
```

[:octicons-arrow-right-24: Full guide: Input Actions](actions.md)

---

### Input Layers (UI Priority)

```csharp
_inputLayerManager.RegisterLayer(myUiLayer);

protected override void OnUpdate(GameTime gameTime)
{
    _inputLayerManager.ProcessInput();

    if (!_inputLayerManager.KeyboardConsumed) HandleGameKeyboard();
    if (!_inputLayerManager.MouseConsumed)    HandleGameMouse();
    if (!_inputLayerManager.GamepadConsumed)  HandleGameGamepad();
}
```

[:octicons-arrow-right-24: Full guide: Input Layers](layers.md)

---

## Best Practices

### :white_check_mark: DO

1. **Use the `Input` framework property** in scenes
2. **Poll input in `OnUpdate()`** only
3. **Use `deltaTime` for movement** -- frame-rate independent
4. **Use `IsKeyPressed()` for one-shot actions** -- jump, shoot, toggle
5. **Use `IsKeyDown()` for continuous actions** -- movement, sprint

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    if (Input.IsKeyDown(Key.W))
        _position.Y -= _speed * (float)gameTime.DeltaTime;

    if (Input.IsKeyPressed(Key.Space))
        Jump();
}
```

---

### :x: DON'T

1. **Don't poll input in `OnRender()`** -- wrong lifecycle method
2. **Don't forget `deltaTime`** -- movement will be FPS-dependent
3. **Don't use `IsKeyPressed()` for movement** -- will be choppy

```csharp
// Bad pattern
protected override void OnRender(GameTime gameTime)
{
    if (Input.IsKeyDown(Key.W))
        _position.Y -= _speed; // No deltaTime and wrong lifecycle!
}
```

---

## Troubleshooting

### Input Not Responding

1. **Check you are in `OnUpdate`**, not `OnRender`
2. **Click the game window** -- input only works when focused

### Movement Too Fast or Slow

```csharp
// Wrong -- FPS dependent
_position.Y -= 5;

// Correct -- 200 pixels per second regardless of frame rate
_position.Y -= 200f * (float)gameTime.DeltaTime;
```

### Gamepad Not Detected

```csharp
if (!Input.IsGamepadConnected())
{
    Logger.LogWarning("No gamepad connected");
    return;
}
```

---

## Related Topics

- [Keyboard](keyboard.md)
- [Mouse](mouse.md)
- [Gamepad Support](gamepad.md)
- [Input Actions](actions.md)
- [Input Layers](layers.md)