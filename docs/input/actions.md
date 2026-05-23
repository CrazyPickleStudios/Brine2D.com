---
title: Input Actions
description: Rebindable logical input actions and action maps in Brine2D
---

# Input Actions

Input actions decouple your game logic from physical inputs. A "Jump" action can be bound to the spacebar, a gamepad button, and a trigger simultaneously â€” the action fires when any binding is active, and bindings can be changed at runtime without touching game code.

---

## Quick Start

```csharp
using Brine2D.Input;

// Create an action with multiple bindings
var jumpAction = new InputAction("Jump",
    new KeyBinding(Key.Space),
    new GamepadButtonBinding(GamepadButton.A));

protected override void OnUpdate(GameTime gameTime)
{
    if (jumpAction.IsPressed(Input)) Jump();
}
```

---

## `InputAction`

An `InputAction` is a named logical action with one or more `InputBinding` objects.

```csharp
var moveRight = new InputAction("MoveRight",
    new KeyAxisBinding(Key.D, Key.A),            // D = positive, A = negative
    new GamepadAxisBinding(GamepadAxis.LeftX));  // Gamepad left stick X

// Query the action
bool held    = moveRight.IsDown(Input);
bool pressed = moveRight.IsPressed(Input);
bool release = moveRight.IsReleased(Input);
float value  = moveRight.ReadValue(Input); // -1 to 1

// Read two actions as a Vector2 (X + Y)
var moveX = new InputAction("MoveX", new KeyAxisBinding(Key.D, Key.A));
var moveY = new InputAction("MoveY", new KeyAxisBinding(Key.S, Key.W));
Vector2 direction = moveX.ReadVector2(Input, moveY);
```

### Runtime Rebinding

```csharp
// Add a new binding
jumpAction.AddBinding(new GamepadButtonBinding(GamepadButton.B));

// Remove a specific binding
jumpAction.RemoveBinding(existingBinding);

// Clear all bindings
jumpAction.ClearBindings();
```

---

## `InputActionMap`

An `InputActionMap` is a named collection of actions. Typical usage is one map per game context (e.g., "Player", "UI", "Vehicle"). The whole map can be disabled without unregistering individual actions.

```csharp
var playerMap = new InputActionMap("Player");

var jump  = new InputAction("Jump",     new KeyBinding(Key.Space));
var shoot = new InputAction("Shoot",    new MouseButtonBinding(MouseButton.Left));
var moveX = new InputAction("MoveX",    new KeyAxisBinding(Key.D, Key.A));
var moveY = new InputAction("MoveY",    new KeyAxisBinding(Key.S, Key.W));

playerMap.AddAction(jump);
playerMap.AddAction(shoot);
playerMap.AddAction(moveX);
playerMap.AddAction(moveY);
```

### Querying a Map

```csharp
// By action name
bool jumping = playerMap.IsDown("Jump", Input);
bool shooting = playerMap.IsPressed("Shoot", Input);
float xAxis  = playerMap.ReadValue("MoveX", Input);

// Or get the action object directly
var jumpAction = playerMap["Jump"];
jumpAction.IsPressed(Input);

// Safe lookup (returns false if not found)
if (playerMap.TryGetAction("Jump", out var action))
    action.IsPressed(Input);
```

### Disabling a Map

```csharp
// Disable the entire map (all queries return false/zero)
playerMap.Enabled = false;

// Re-enable it
playerMap.Enabled = true;
```

---

## Binding Types

### `KeyBinding` -- Single Key

```csharp
new KeyBinding(Key.Space)
```

### `KeyAxisBinding` -- Two Keys as an Axis (-1 to 1)

```csharp
new KeyAxisBinding(positive: Key.D, negative: Key.A)
// ReadValue returns 1 when D held, -1 when A held, 0 when neither or both
```

### `CompositeKeyBinding` -- All Keys Held Simultaneously

```csharp
new CompositeKeyBinding(Key.LeftControl, Key.S) // Ctrl+S
// IsPressed fires when the last key completes the combo
```

### `MouseButtonBinding` -- Single Mouse Button

```csharp
new MouseButtonBinding(MouseButton.Left)
```

### `GamepadButtonBinding` -- Single Gamepad Button

```csharp
new GamepadButtonBinding(GamepadButton.A)
new GamepadButtonBinding(GamepadButton.Start, gamepadIndex: 1) // Player 2
```

### `GamepadAxisBinding` -- Raw Gamepad Axis with Deadzone

```csharp
new GamepadAxisBinding(GamepadAxis.LeftX)
// ReadValue rescales past the deadzone to 0--1
```

!!! note
    `GamepadAxisBinding` uses a per-axis (not radial) deadzone check. For consistent 2D
    directional input on a stick, prefer `GamepadStickBinding`.

### `GamepadStickBinding` -- Stick Axis with Radial Deadzone

```csharp
new GamepadStickBinding(GamepadStick.Left, GamepadStickAxis.X)
new GamepadStickBinding(GamepadStick.Right, GamepadStickAxis.Y, gamepadIndex: 0)
// Applies the same radial deadzone as GetGamepadLeftStick() / GetGamepadRightStick()
```

### `GamepadTriggerBinding` -- Trigger (0 to 1)

```csharp
new GamepadTriggerBinding(GamepadAxis.RightTrigger)
// IsPressed fires when trigger crosses the deadzone threshold
```

---

## Full Example: Player Action Map

```csharp
public class PlayerActions
{
    public InputActionMap Map { get; }

    public InputAction Jump    { get; }
    public InputAction MoveX   { get; }
    public InputAction MoveY   { get; }
    public InputAction Fire    { get; }

    public PlayerActions()
    {
        Map = new InputActionMap("Player");

        Jump = new InputAction("Jump",
            new KeyBinding(Key.Space),
            new GamepadButtonBinding(GamepadButton.A));

        MoveX = new InputAction("MoveX",
            new KeyAxisBinding(Key.D, Key.A),
            new GamepadStickBinding(GamepadStick.Left, GamepadStickAxis.X));

        MoveY = new InputAction("MoveY",
            new KeyAxisBinding(Key.S, Key.W),
            new GamepadStickBinding(GamepadStick.Left, GamepadStickAxis.Y));

        Fire = new InputAction("Fire",
            new MouseButtonBinding(MouseButton.Left),
            new GamepadTriggerBinding(GamepadAxis.RightTrigger));

        Map.AddAction(Jump);
        Map.AddAction(MoveX);
        Map.AddAction(MoveY);
        Map.AddAction(Fire);
    }
}
```

```csharp
public class PlayerScene : Scene
{
    private readonly PlayerActions _actions = new();

    protected override void OnUpdate(GameTime gameTime)
    {
        var dt = (float)gameTime.DeltaTime;

        var direction = MoveX.ReadVector2(Input, MoveY);
        if (direction != Vector2.Zero)
            direction = Vector2.Normalize(direction);
        _position += direction * _speed * dt;

        if (Jump.IsPressed(Input)) Jump();
        if (Fire.IsDown(Input))    Fire();
    }

    private InputAction MoveX => _actions.MoveX;
    private InputAction MoveY => _actions.MoveY;
    private InputAction Jump  => _actions.Jump;
    private InputAction Fire  => _actions.Fire;
}
```

---

## Next Steps

- **[Keyboard Input](keyboard.md)**
- **[Gamepad Input](gamepad.md)**
- **[Input Layers](layers.md)**
