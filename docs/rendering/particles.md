---
title: Particle System
description: Create stunning particle effects with Brine2D's high-performance particle system
---

# Particle System

Create fire, explosions, smoke, and other visual effects with Brine2D's high-performance particle system featuring textures, rotation, trails, blend modes, sub-emitters, custom forces, and automatic object pooling.

## Overview

Brine2D's particle system uses object pooling to render thousands of particles without allocating memory per frame. Particles are reused from a pool, ensuring smooth performance even with complex effects.

**Key features:**

- Particle textures (atlas regions and animated frames)
- Rotation with per-particle variation
- Trails with configurable head/tail alpha and size ratios
- Blend modes (Additive, Alpha, Multiply, None)
- 5 emitter shapes (Circle, Box, Line, Cone, Point)
- Sub-emitters triggered on particle birth, death, or at lifetime fractions
- Custom force objects (`IParticleForce`)
- Turbulence, damping, speed-over-lifetime, velocity inheritance
- Local-space simulation, burst mode, looping, delay, warmup
- State capture and reset (`CaptureDefaultState` / `ResetToDefaultState`)

## Quick Start

```csharp
using Brine2D.ECS;
using Brine2D.ECS.Components;
using Brine2D.Rendering;
using Brine2D.Systems.Rendering;
using System.Numerics;

public class GameScene : Scene
{
    private readonly IEntityWorld _world;

    public GameScene(IEntityWorld world) => _world = world;

    protected override void OnInitialize()
    {
        var fireEffect = _world.CreateEntity("Fire");
        fireEffect.AddComponent<TransformComponent>(t => t.Position = new Vector2(400, 300));

        var emitter = fireEffect.AddComponent<ParticleEmitterComponent>()
                                .GetComponent<ParticleEmitterComponent>();

        emitter.IsEmitting       = true;
        emitter.EmissionRate     = 50f;
        emitter.MaxParticles     = 200;
        emitter.ParticleLifetime = 2f;

        emitter.StartColor = new Color(255, 200, 0, 255);
        emitter.EndColor   = new Color(255,  50, 0,   0);
        emitter.StartSize  = 8f;
        emitter.EndSize    = 2f;

        emitter.InitialVelocity = new Vector2(0, -50);
        emitter.VelocitySpread  = 30f;
        emitter.Gravity         = new Vector2(0, 100);
    }
}
```

`ParticleSystem` automatically updates and renders all emitters — no extra wiring needed.

## Emitter Properties

### Emission

| Property | Type | Default | Description |
|---|---|---|---|
| `IsEmitting` | `bool` | `true` | Toggle emission on/off |
| `IsEnabled` | `bool` | `true` | Toggle the entire component |
| `EmissionRate` | `float` | `10` | Particles per second (continuous mode) |
| `MaxParticles` | `int` | `100` | Object-pool size; hard cap on concurrent particles |
| `ParticleLifetime` | `float` | `2` | Base lifetime in seconds |
| `LifetimeVariation` | `float` | `0.3` | ±fraction of `ParticleLifetime` randomised per particle |
| `IsBurst` | `bool` | `false` | Emit `BurstCount` particles in one frame then stop |
| `BurstCount` | `int` | `30` | Particles to emit in a single burst |
| `Duration` | `float?` | `null` | Continuous emitter auto-stops after this many seconds |
| `Loop` | `bool` | `false` | Restart after `Duration` elapses or burst expires |
| `Delay` | `float` | `0` | Seconds to wait before emission begins |
| `WarmupDuration` | `float` | `0` | Pre-simulate this many seconds on first activation |

### Shapes

```csharp
emitter.Shape = EmitterShape.Circle;  // default
```

| Value | Spawn area | Key properties |
|---|---|---|
| `Circle` | Uniform disk | `SpawnRadius`, `SpawnOnPerimeter` |
| `Box` | Rectangular area | `ShapeSize` (Vector2 width/height), `BoxAngle` |
| `Line` | Along a line | `LineLength` (or `ShapeSize.X`), `LineAngle` |
| `Cone` | Directional cone | `SpawnRadius`, `ConeAngle` (degrees) |
| `Point` | Single point | — |

Use `SpawnOnPerimeter = true` with `Circle` or `Cone` to spawn on the edge of the circle instead of uniformly within it. This is the equivalent of a "ring" emitter shape.

```csharp
// Ring / perimeter burst
emitter.Shape            = EmitterShape.Circle;
emitter.SpawnRadius      = 40f;
emitter.SpawnOnPerimeter = true;

// Rotated box spawn area
emitter.Shape     = EmitterShape.Box;
emitter.ShapeSize = new Vector2(100f, 20f);
emitter.BoxAngle  = MathF.PI / 4f; // 45 degrees

// Line emitter
emitter.Shape      = EmitterShape.Line;
emitter.LineLength = 120f;
emitter.LineAngle  = MathF.PI / 2f; // vertical

// Directional cone
emitter.Shape       = EmitterShape.Cone;
emitter.SpawnRadius = 10f;
emitter.ConeAngle   = 45f; // degrees
```

### Appearance

```csharp
// Two-color lerp over lifetime
emitter.StartColor = new Color(255, 200, 0, 255);
emitter.EndColor   = new Color(255,  50, 0,   0);

// Per-particle color variation (additive ±V per channel)
emitter.StartColorVariation = new Color(30, 30, 0, 0);
emitter.EndColorVariation   = new Color(20, 20, 0, 0);

// Multi-stop gradient (overrides Start/EndColor when set)
emitter.ColorGradient = new[]
{
    new Color(255, 255, 0, 255),  // t = 0
    new Color(255, 100, 0, 200),  // t = 0.5
    new Color(200,  50, 0,   0),  // t = 1
};

// Size
emitter.StartSize        = 8f;
emitter.EndSize          = 1f;
emitter.SizeVariation    = 2f;  // +-2 px on start size
emitter.EndSizeVariation = 1f;  // +-1 px on end size

// Blend mode
emitter.BlendMode = BlendMode.Additive;

// Render layer (lower = further back)
emitter.RenderLayer = 0;
```

**Blend modes:**

| Value | Effect | Best for |
|---|---|---|
| `Alpha` | Standard transparency (default) | Smoke, fog, water |
| `Additive` | Bright, glowing overlaps | Fire, explosions, energy |
| `Multiply` | Darkening / shadows | Shadows, darkening fog |
| `None` | Fully opaque | Solid debris, sparks |

### Textures

Assign textures by setting `ParticleTexture` or `ParticleAtlasRegion` directly. Particle textures are loaded via `IAssetLoader` or `AtlasBuilder`; there is no `TexturePath` string on the component.

```csharp
// Single texture loaded via assets
var tex = await _assets.GetOrLoadTextureAsync("assets/particles/fire.png", cancellationToken: ct);
emitter.ParticleTexture = tex;

// Atlas region
emitter.ParticleAtlasRegion = myAtlas["fire"];

// Animated frames distributed evenly over lifetime
emitter.ParticleFrames = new[]
{
    myAtlas["fire_0"],
    myAtlas["fire_1"],
    myAtlas["fire_2"],
    myAtlas["fire_3"],
};
```

When no texture is set, particles render as solid-filled circles.

### Rotation

```csharp
// Fixed starting angle with per-particle randomisation
emitter.InitialRotation          = 0f;       // base angle (radians)
emitter.InitialRotationVariation = MathF.PI; // +-PI = fully random start angle

// Constant spin
emitter.RotationSpeed          = 2f;   // radians/sec
emitter.RotationSpeedVariation = 0.5f; // +-0.5 rad/s per particle
```

### Trails

```csharp
emitter.EnableTrails = true;
emitter.TrailLength  = 10;                 // history slots
emitter.TrailMode    = TrailMode.Sprites;  // or TrailMode.Lines

// Opacity of the segment nearest the particle head (newest)
emitter.TrailHeadAlpha = 0.8f;
// Opacity of the segment farthest from the head (oldest)
emitter.TrailTailAlpha = 0.0f;

// Size multipliers applied to trail segments
emitter.TrailHeadSizeRatio = 1.0f;  // head matches particle size
emitter.TrailTailSizeRatio = 0.5f;  // tail is half the particle size
```

`TrailMode.Lines` connects history positions with continuous line calls. It falls back to `Sprites` automatically when a texture or atlas region is set.

### Physics

```csharp
// Spawn position offset from the transform
emitter.SpawnOffset = new Vector2(0, -10);

// Initial velocity and spread
emitter.InitialVelocity = new Vector2(0, -100);
emitter.VelocitySpread  = 45f;   // +-22.5 degree random direction jitter
emitter.SpeedVariation  = 0.5f;  // +-50% speed multiplier per particle

// Gravity
emitter.Gravity = new Vector2(0, 200);

// Drag: velocity *= exp(-Damping * dt) per frame
emitter.Damping = 0.693f;  // ~halves speed each second

// Speed-over-lifetime (takes priority over Damping for base velocity)
emitter.StartSpeedMultiplier = 1f;
emitter.EndSpeedMultiplier   = 0f;  // decelerate to a halt

// Inherit the emitter entity's own velocity
emitter.VelocityInheritance = 0.5f;  // 50% of entity velocity added at spawn

// Turbulence (coherent noise field)
emitter.TurbulenceStrength  = 80f;
emitter.TurbulenceFrequency = 0.02f;  // noise spatial scale
```

### Local-Space Simulation

When `SimulateInLocalSpace` is `true`, all live particles move with the emitter entity.

```csharp
emitter.SimulateInLocalSpace = true;
// InitialVelocity is treated as local-space here; it is NOT rotated by the entity's rotation.
```

> **Note:** avoid animating `TransformComponent.Scale` on entities with local-space simulation while particles are live, as it stretches all particle positions.

## Lifecycle Methods

```csharp
// Start or restart from a clean state
emitter.Play();

// Stop emission and clear all live particles on next update
emitter.Stop();

// Freeze all update/movement/emission
emitter.Pause();
emitter.Resume();

// Re-arm a burst emitter without clearing live particles
emitter.ResetBurst();

// Capture current configuration as the snapshot to restore
emitter.CaptureDefaultState();

// Restore the captured snapshot (throws if never captured)
emitter.ResetToDefaultState();

// Safe variant — returns false instead of throwing
bool restored = emitter.TryResetToDefaultState();
```

## Callbacks

```csharp
emitter.OnParticleSpawned = particle =>
{
    // Particle is live; do not hold a reference beyond this callback.
};

emitter.OnParticleDied = particle =>
{
    // Particle has final state; returned to pool immediately after.
};

emitter.OnEmitterFinished = () =>
{
    // Burst finished (Loop = false), or Duration-limited emitter expired.
};
```

## State and Diagnostics

```csharp
var emitter = entity.GetComponent<ParticleEmitterComponent>();

int active = emitter.ParticleCount;
int max    = emitter.MaxParticles;

IReadOnlyList<Particle> particles = emitter.ActiveParticles;

// System-wide total (from the registered ParticleSystem service)
int total = _particleSystem.TotalParticleCount;
```

## Sub-Emitters

Sub-emitters spawn secondary bursts at a particle's world position without requiring extra entities. Configure them with `SubEmitterConfig` and assign to the appropriate list.

### Birth and Death Sub-Emitters

```csharp
var deathSparks = new SubEmitterConfig
{
    BurstCount          = 8,
    ParticleLifetime    = 0.4f,
    StartColor          = new Color(255, 220, 100, 255),
    EndColor            = new Color(255, 220, 100,   0),
    StartSize           = 3f,
    EndSize             = 0f,
    InitialVelocity     = Vector2.Zero,
    VelocitySpread      = 360f,  // omnidirectional
    VelocityInheritance = 0.3f,
    Gravity             = new Vector2(0, 300),
    BlendMode           = BlendMode.Additive,
    MaxParticles        = 200,
};

emitter.DeathSubEmitters = new List<SubEmitterConfig> { deathSparks };

// Or at particle birth:
// emitter.BirthSubEmitters = new List<SubEmitterConfig> { ... };
```

### Lifetime-Fraction Sub-Emitters

Fire a burst at a specific point in a particle's life:

```csharp
emitter.LifetimeFractionSubEmitters = new List<LifetimeFractionSubEmitter>
{
    new()
    {
        Fraction = 0.5f,   // fires at 50% of lifetime
        Config   = new SubEmitterConfig
        {
            BurstCount       = 5,
            ParticleLifetime = 0.3f,
            VelocitySpread   = 360f,
            BlendMode        = BlendMode.Additive,
        }
    }
};
```

`SubEmitterConfig` supports the same appearance, physics, rotation, trail, and turbulence properties as `ParticleEmitterComponent`. Sub-particles do not chain further sub-emitters.

## Custom Forces

Implement `IParticleForce` and add instances to `emitter.Forces` to apply arbitrary per-frame velocity changes:

```csharp
public class AttractorForce : IParticleForce
{
    private readonly Vector2 _centre;
    private readonly float _strength;

    public AttractorForce(Vector2 centre, float strength)
    {
        _centre   = centre;
        _strength = strength;
    }

    public Vector2 Evaluate(Vector2 particleWorldPosition, float deltaTime)
    {
        var dir  = _centre - particleWorldPosition;
        var dist = dir.Length();
        if (dist < 0.001f) return Vector2.Zero;
        return Vector2.Normalize(dir) * (_strength / dist) * deltaTime;
    }
}

emitter.Forces = new List<IParticleForce>
{
    new AttractorForce(new Vector2(400, 300), 5000f),
};
```

The returned delta is added to each particle's `BaseVelocity` and is subject to subsequent damping and speed-over-lifetime scaling.

## Preset Effects

### Fire

```csharp
var entity  = _world.CreateEntity("Fire");
entity.AddComponent<TransformComponent>(t => t.Position = new Vector2(400, 300));
entity.AddComponent<ParticleEmitterComponent>();
var emitter = entity.GetComponent<ParticleEmitterComponent>();

emitter.IsEmitting       = true;
emitter.EmissionRate     = 100f;
emitter.MaxParticles     = 200;
emitter.ParticleLifetime = 1.5f;
emitter.Shape            = EmitterShape.Circle;
emitter.SpawnRadius      = 15f;

emitter.StartColor = new Color(255, 200, 0, 255);
emitter.EndColor   = new Color(255,  50, 0,   0);
emitter.StartSize  = 8f;
emitter.EndSize    = 2f;
emitter.BlendMode  = BlendMode.Additive;

emitter.InitialRotation          = 0f;
emitter.RotationSpeed            = 2f;
emitter.InitialRotationVariation = MathF.PI / 2f;

emitter.EnableTrails   = true;
emitter.TrailLength    = 5;
emitter.TrailHeadAlpha = 0.6f;
emitter.TrailTailAlpha = 0.0f;

emitter.InitialVelocity = new Vector2(0, -100);
emitter.VelocitySpread  = 30f;
emitter.Gravity         = new Vector2(0, -20);
```

### Explosion (Burst)

```csharp
entity.AddComponent<ParticleEmitterComponent>();
var emitter = entity.GetComponent<ParticleEmitterComponent>();

emitter.IsBurst          = true;
emitter.BurstCount       = 100;
emitter.MaxParticles     = 100;
emitter.ParticleLifetime = 1f;
emitter.BlendMode        = BlendMode.Additive;

emitter.StartColor = new Color(255, 255, 200, 255);
emitter.EndColor   = new Color(255, 100,   0,   0);
emitter.StartSize  = 12f;
emitter.EndSize    = 2f;

emitter.RotationSpeed            = 5f;
emitter.InitialRotationVariation = MathF.PI;

emitter.InitialVelocity = new Vector2(0, -200);
emitter.VelocitySpread  = 360f;
emitter.Gravity         = new Vector2(0, 500);

emitter.Play();
```

### Smoke

```csharp
emitter.IsEmitting       = true;
emitter.EmissionRate     = 20f;
emitter.MaxParticles     = 100;
emitter.ParticleLifetime = 3f;
emitter.Shape            = EmitterShape.Circle;
emitter.SpawnRadius      = 5f;

emitter.StartColor = new Color( 60,  60,  60, 200);
emitter.EndColor   = new Color(150, 150, 150,   0);
emitter.StartSize  = 4f;
emitter.EndSize    = 12f;
emitter.BlendMode  = BlendMode.Alpha;

emitter.RotationSpeed            = 0.5f;
emitter.InitialRotationVariation = MathF.PI;

emitter.InitialVelocity = new Vector2(0, -30);
emitter.VelocitySpread  = 20f;
emitter.Gravity         = new Vector2(0, -10);
```

### Magic Ring

```csharp
emitter.Shape            = EmitterShape.Circle;
emitter.SpawnRadius      = 40f;
emitter.SpawnOnPerimeter = true;
emitter.IsEmitting       = true;
emitter.EmissionRate     = 60f;
emitter.MaxParticles     = 200;
emitter.ParticleLifetime = 2f;

emitter.StartColor = new Color(150, 100, 255, 255);
emitter.EndColor   = new Color(150, 100, 255,   0);
emitter.StartSize  = 6f;
emitter.EndSize    = 1f;
emitter.BlendMode  = BlendMode.Additive;

emitter.RotationSpeed = 3f;

emitter.EnableTrails   = true;
emitter.TrailLength    = 8;
emitter.TrailHeadAlpha = 0.7f;
emitter.TrailTailAlpha = 0.0f;

emitter.InitialVelocity = new Vector2(-50, 0);
emitter.VelocitySpread  = 10f;
emitter.Gravity         = Vector2.Zero;
```

### Fountain

```csharp
emitter.Shape            = EmitterShape.Cone;
emitter.ConeAngle        = 30f;  // degrees
emitter.SpawnRadius      = 5f;
emitter.IsEmitting       = true;
emitter.EmissionRate     = 80f;
emitter.MaxParticles     = 300;
emitter.ParticleLifetime = 2.5f;

emitter.StartColor = new Color(100, 150, 255, 200);
emitter.EndColor   = new Color(100, 150, 255,   0);
emitter.StartSize  = 4f;
emitter.EndSize    = 2f;
emitter.BlendMode  = BlendMode.Alpha;

emitter.InitialVelocity = new Vector2(0, -300);
emitter.VelocitySpread  = 15f;
emitter.Gravity         = new Vector2(0, 500);
```

## Advanced Techniques

### Layered Particles

A single entity can hold only one `ParticleEmitterComponent`. Use separate entities and `RenderLayer` to control draw order across multiple emitters:

```csharp
public void CreateExplosion(Vector2 position)
{
    // Smoke — drawn first (furthest back)
    var smokeEntity = _world.CreateEntity("ExplosionSmoke");
    smokeEntity.AddComponent<TransformComponent>(t => t.Position = position);
    smokeEntity.AddComponent<ParticleEmitterComponent>();
    var smoke = smokeEntity.GetComponent<ParticleEmitterComponent>();

    smoke.RenderLayer      = 0;
    smoke.IsBurst          = true;
    smoke.BurstCount       = 30;
    smoke.BlendMode        = BlendMode.Alpha;
    smoke.StartColor       = new Color( 60,  60,  60, 200);
    smoke.EndColor         = new Color(120, 120, 120,   0);
    smoke.ParticleLifetime = 3f;
    smoke.StartSize        = 4f;
    smoke.EndSize          = 20f;

    // Fire — drawn on top
    var fireEntity = _world.CreateEntity("ExplosionFire");
    fireEntity.AddComponent<TransformComponent>(t => t.Position = position);
    fireEntity.AddComponent<ParticleEmitterComponent>();
    var fire = fireEntity.GetComponent<ParticleEmitterComponent>();

    fire.RenderLayer      = 1;
    fire.IsBurst          = true;
    fire.BurstCount       = 60;
    fire.BlendMode        = BlendMode.Additive;
    fire.StartColor       = new Color(255, 200, 0, 255);
    fire.EndColor         = new Color(255,  50, 0,   0);
    fire.ParticleLifetime = 1f;
    fire.InitialVelocity  = new Vector2(0, -200);
    fire.VelocitySpread   = 180f;
    fire.Gravity          = new Vector2(0, 400);

    smoke.Play();
    fire.Play();
}
```

### Conditional Emission

```csharp
public class DustTrailSystem : IUpdateSystem
{
    public string Name     => "DustTrailSystem";
    public int UpdateOrder => 100;
    public bool IsEnabled  { get; set; } = true;

    public void Update(GameTime gameTime)
    {
        foreach (var entity in _world.Query<PlayerComponent, VelocityComponent, ParticleEmitterComponent>())
        {
            var vel     = entity.GetComponent<VelocityComponent>();
            var emitter = entity.GetComponent<ParticleEmitterComponent>();
            var speed   = vel.Velocity.Length();

            emitter.IsEmitting   = speed > 80f;
            emitter.EmissionRate = speed * 0.5f;
        }
    }
}
```

### Reusable Pooled Emitter

Use `CaptureDefaultState` + `ResetToDefaultState` to recycle emitters:

```csharp
protected override void OnInitialize()
{
    var entity  = _world.CreateEntity("SparksTemplate");
    entity.AddComponent<TransformComponent>();
    entity.AddComponent<ParticleEmitterComponent>();
    var emitter = entity.GetComponent<ParticleEmitterComponent>();

    emitter.IsBurst          = true;
    emitter.BurstCount       = 20;
    emitter.MaxParticles     = 40;
    emitter.ParticleLifetime = 0.6f;
    emitter.BlendMode        = BlendMode.Additive;
    emitter.StartColor       = new Color(255, 220, 100, 255);
    emitter.EndColor         = new Color(255, 220, 100,   0);
    emitter.VelocitySpread   = 360f;
    emitter.Gravity          = new Vector2(0, 400);

    emitter.CaptureDefaultState();

    // Later, to reuse:
    // emitter.ResetToDefaultState();
    // entity.GetComponent<TransformComponent>().Position = newPosition;
    // emitter.Play();
}
```

## Performance

Particles use object pooling — there are **zero GC allocations** after warm-up.

### Guidelines

| Particle count per emitter | Performance impact |
|---|---|
| < 500 | Excellent |
| 500 – 1 000 | Good |
| > 1 000 | Consider splitting into multiple smaller emitters |

**Tips:**

- Use `MaxParticles` conservatively — the pool is pre-allocated.
- Trails multiply effective particle count (`TrailLength` ghost sprites per particle).
- Pack particle textures into a texture atlas to reduce draw calls.
- Disable distant or off-screen emitters: `emitter.IsEmitting = false`.
- Use `WarmupDuration` to pre-simulate ambient effects instead of starting cold.

### Texture Atlasing

```csharp
var atlas = await AtlasBuilder.BuildAtlasAsync(
    _renderer, _assets,
    new[] { "assets/particles/fire.png", "assets/particles/smoke.png" },
    padding: 2, maxSize: 1024);

var emitter = entity.GetComponent<ParticleEmitterComponent>();
emitter.ParticleAtlasRegion = atlas["assets/particles/fire.png"];
```

### Monitoring

```csharp
var emitter = entity.GetComponent<ParticleEmitterComponent>();
Logger.LogDebug("Active: {Count}/{Max}", emitter.ParticleCount, emitter.MaxParticles);

// System-wide total
Logger.LogDebug("Total particles: {Total}", _particleSystem.TotalParticleCount);
```

## Troubleshooting

### Particles not visible

- Verify `IsEmitting = true` and `IsEnabled = true`.
- Check `EmissionRate > 0` and `ParticleLifetime > 0`.
- Ensure `StartColor` has `alpha > 0`.
- Make sure a `TransformComponent` is on the same entity.
- If using `IsBurst`, call `Play()` to fire — it does not auto-fire on component creation.

### Texture not showing

`ParticleTexture` and `ParticleAtlasRegion` are reference types assigned after loading. There is no `TexturePath` string property:

```csharp
// Load and assign
var tex = await _assets.GetOrLoadTextureAsync("assets/particles/fire.png", cancellationToken: ct);
emitter.ParticleTexture = tex;
```

### Poor performance

1. Lower `MaxParticles` and `TrailLength`.
2. Pack textures into an atlas.
3. Disable emitters outside the camera view.
4. Use `IsBurst` instead of continuous emission for one-shot effects.
5. Watch `TotalParticleCount` via logging or the performance overlay (F3).

### Trails look wrong

- Increase `TrailLength` for smoother ribbons.
- Raise `TrailHeadAlpha` if trails are too faint.
- Increase `EmissionRate` — sparse particles produce gaps in trails.
- For continuous ribbons on untextured particles, use `TrailMode = TrailMode.Lines`.

## See Also

- [Texture Atlasing](texture-atlasing.md)
- [Sprites & Textures](sprites.md)
- [ECS Systems](../ecs/systems.md)
- [Performance Optimization](../performance/optimization.md)