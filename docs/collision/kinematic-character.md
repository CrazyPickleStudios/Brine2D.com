---
title: Kinematic Character Controller
description: KinematicCharacterBody and KinematicCharacterSystem for platformers and top-down games in Brine2D
---

# Kinematic Character Controller

`KinematicCharacterBody` adds character-controller behaviour to a `Kinematic` physics body. Set `Velocity` each fixed-update frame and the system slides it along contact surfaces, detects ground/wall/ceiling contacts, and integrates position. It is the right choice for platform characters and top-down actors that need precise, physics-aware movement without full dynamic simulation.

---

## Setup

Register physics with `AddPhysics()` — the kinematic character systems are included automatically:

```csharp
services.AddPhysics(opts => { opts.Gravity = new Vector2(0, 980); });
```

Add **both** kinematic systems to your scene:

```csharp
protected override void OnLoadAsync(IEntityWorld world)
{
    world.AddSystem<Box2DPhysicsSystem>();
    world.AddSystem<PrePhysicsKinematicCharacterSystem>();
    world.AddSystem<PostPhysicsKinematicCharacterSystem>();
}
```

Create a character entity with both `PhysicsBodyComponent` (Kinematic) and `KinematicCharacterBody`:

```csharp
var player = world.CreateEntity("Player");
player.AddComponent<TransformComponent>(t => t.Position = new Vector2(200, 300));
player.AddComponent<PhysicsBodyComponent>(b =>
{
    b.Shape        = new CapsuleShape(new Vector2(0, -12), new Vector2(0, 12), 10);
    b.BodyType     = PhysicsBodyType.Kinematic;
    b.FixedRotation = true;
});
player.AddComponent<KinematicCharacterBody>(c =>
{
    c.SnapDistance = 8f; // Snap to floor on stairs/slopes
});
```

---

## Moving the Character

Set `Velocity` each fixed-update frame. The pre-physics step slides the velocity along contact surfaces and integrates it into `TransformComponent.Position` before Box2D runs.

### `MoveAndSlide`

The character moves by `Velocity * deltaTime`, deflecting off surfaces up to `MaxSlides` times. Use for standard platform or top-down movement.

```csharp
protected override void OnFixedUpdate(GameTime fixedTime)
{
    var character = _playerEntity.GetComponent<KinematicCharacterBody>();

    var velocity = Vector2.Zero;

    if (Input.IsKeyDown(Key.A)) velocity.X -= _speed;
    if (Input.IsKeyDown(Key.D)) velocity.X += _speed;

    if (character.IsGrounded && Input.IsKeyPressed(Key.Space))
        velocity.Y = -_jumpForce;
    else
        velocity.Y = character.Velocity.Y + _gravity * (float)fixedTime.DeltaTime;

    character.MoveAndSlide(velocity);
}
```

`MoveAndSlide` is a fluent method that sets `Velocity` and returns `this`.

### `MoveAndCollide`

The character moves exactly by the given vector without sliding. If a solid surface is hit it stops at the contact point and `LastMoveAndCollideHit` is set. Use for projectile-style movement or step-based tools.

```csharp
character.MoveAndCollide(new Vector2(0, 8)); // Probe downward 8 px

if (character.LastMoveAndCollideHit.HasValue)
    Logger.LogDebug("Hit at {Point}", character.LastMoveAndCollideHit.Value.Point);
```

`MoveAndCollide` is mutually exclusive with `MoveAndSlide` per tick -- velocity integration is skipped for any tick in which a `MoveAndCollide` motion is queued.

---

## Ground, Wall, and Ceiling Detection

These are updated each tick by the post-physics step.

```csharp
if (character.IsGrounded)
{
    Logger.LogDebug("Floor normal: {Normal}", character.FloorNormal);
}

if (character.IsOnWall)
{
    Logger.LogDebug("Wall normal: {Normal}", character.WallNormal);
}

if (character.IsOnCeiling)
{
    Logger.LogDebug("Ceiling normal: {Normal}", character.CeilingNormal);
}

// Touching a wall but not floor or ceiling
if (character.IsOnWallOnly) WallSlide();
```

### Angle Limits

```csharp
character.FloorAngleLimit   = 0.8f; // Radians (~46 deg) from "up"
character.CeilingAngleLimit = 0.8f; // Radians from "down"
character.WallAngleLimit    = float.PositiveInfinity; // All non-floor/ceiling contacts
```

---

## Landing and Airborne Events

```csharp
character.OnLanded   += c => PlayLandSound();
character.OnAirborne += c => StartFallAnimation();
```

---

## Moving Platforms

`KinematicCharacterBody` automatically detects and rides moving platforms (both `Kinematic` and `Dynamic` bodies). The platform's velocity is carried to the character each tick.

```csharp
// Read the current platform velocity
var platformVelocity = character.PlatformVelocity;
```

---

## Snap to Floor

Prevent the character from going airborne on small steps and slopes:

```csharp
character.SnapDistance = 8f; // Probe this many pixels downward to find the floor
```

---

## Slope Locking

Prevent sliding down slopes when the character is not actively pushing into them:

```csharp
character.StopOnSlope = true;
```

---

## Pushing Dynamic Objects

```csharp
character.PushForce = 500f; // pixels/s^2 applied to dynamic bodies on contact
```

---

## Speed Cap

```csharp
character.MaxSpeed = 600f; // Clamp velocity magnitude before slide integration
```

---

## Step Climbing

```csharp
character.StepHeight = 12f; // Auto-step onto ledges up to this many pixels tall
```

---

## Custom Up Direction

For wall-walking or per-character gravity:

```csharp
character.UpDirection = new Vector2(0, -1); // Default: derived from world gravity each tick
character.UpDirection = new Vector2(0, 1);  // Ceiling walker
```

---

## Reading Slide Collisions

`GetSlideCollisions()` returns all contacts resolved in the last post-physics step. The list is cleared every tick -- do not hold a reference across frames.

```csharp
foreach (var pair in character.GetSlideCollisions())
{
    Logger.LogDebug("Sliding against {Entity}, normal {Normal}",
        pair.Other?.Entity?.Name, pair.Contact.Normal);
}
```

---

## `EffectiveVelocity`

The slide-corrected velocity actually applied this tick, after surface deflection. Useful for animation blending:

```csharp
var speed = character.EffectiveVelocity.Length();
animator.SetFloat("Speed", speed);
```

---

## Debugging

```csharp
character.EnableDebugLogging = true; // Emits per-tick trace output -- disable before shipping
```

---

## Summary

| Property | Description |
|----------|-------------|
| `Velocity` | Desired velocity in pixels/s. Set every fixed-update frame. |
| `MoveAndSlide(vel)` | Set velocity and slide along surfaces. |
| `MoveAndCollide(motion)` | Discrete cast -- stops at first hit. |
| `IsGrounded` | Resting on a floor surface this tick |
| `IsOnWall` | Touching a wall this tick |
| `IsOnCeiling` | Touching a ceiling this tick |
| `FloorNormal` | Averaged floor contact normal |
| `WallNormal` | Wall contact normal |
| `CeilingNormal` | Ceiling contact normal |
| `EffectiveVelocity` | Post-deflection velocity applied this tick |
| `PlatformVelocity` | Velocity of the moving platform underfoot |
| `SnapDistance` | Floor-snap probe distance in pixels |
| `StopOnSlope` | Prevent sliding down passive slopes |
| `PushForce` | Impulse applied to dynamic bodies on contact |
| `MaxSpeed` | Velocity magnitude cap before integration |
| `StepHeight` | Auto step-up height in pixels |
| `MaxSlides` | Max deflection iterations per pre-step (default 3) |
| `GetSlideCollisions()` | All contacts resolved last tick |
| `LastMoveAndCollideHit` | Result of the last `MoveAndCollide` call |
| `MotionRemainder` | Unused motion remainder from `MoveAndCollide` |

---

## Related Topics

- [Physics Overview](index.md)
- [Collision System](system.md)
- [Shapes & Bodies](colliders.md)
- [Tutorials: Platformer](../tutorials/platformer.md)
