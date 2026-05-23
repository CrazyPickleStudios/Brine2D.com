---
title: Animator Component
description: ECS setup, SpriteAnimator playback API, cross-fades, and animation queuing in Brine2D
---

# Animator Component

    **Namespaces:** `Brine2D.Animation` Â· `Brine2D.Systems.Animation`

`AnimatorComponent` is the ECS entry point for the animation system. It owns the primary `SpriteAnimator`, an `AnimationStateMachine`, an `AnimationParameters` store, optional blend trees, and any additional `AnimationLayer`s.

## ECS Setup

### 1. Register AnimationSystem

Register the system in your scene builder once. It ticks every `AnimatorComponent` every frame.

```csharp
builder.AddSystem<AnimationSystem>();
```

### 2. Add the Component to an Entity

`AnimatorComponent` is typically paired with `SpriteComponent`. `AnimationSystem` writes the current frame data to `SpriteComponent` each tick.

```csharp
entity
    .AddComponent<SpriteComponent>(s =>
    {
        s.Texture = myTexture;
    })
    .AddComponent<AnimatorComponent>();
```

### 3. Build Clips and Play

```csharp
var anim = entity.GetComponent<AnimatorComponent>()!;

var idle = new AnimationClip("idle") { PlaybackMode = PlaybackMode.Loop };
idle.AddFrame(new SpriteFrame(new Rectangle(0,  0, 32, 32)));
idle.AddFrame(new SpriteFrame(new Rectangle(32, 0, 32, 32)));

anim.Animator.AddAnimation(idle);
anim.Animator.Play("idle");
```

`AnimationSystem` calls `Update` and writes `CurrentFrame` to `SpriteComponent` automatically â€” you do **not** call `animator.Update()` yourself.

---

## SpriteAnimator

`SpriteAnimator` is the engine that actually advances time and selects frames. You interact with it through `AnimatorComponent.Animator`.

### Playing Clips

| Method | Behaviour |
|---|---|
| `Play(name)` | Starts the named clip immediately; no-op if already on the same clip (use `restart: true` to force) |
| `Play(name, restart: true)` | Always restarts from frame 0, even if already playing |
| `PlayWithCrossFade(name, fadeDuration)` | Starts a cross-fade to the named clip over `fadeDuration` seconds |
| `PlayQueued(name)` | Queues the clip to start after the current non-looping clip finishes; starts immediately if nothing is playing |
| `PlayDirect(clip)` | Plays a clip instance not registered on the animator |
| `PlayDirectQueued(clip, fadeDuration?)` | Queues an unregistered clip |
| `Stop(fireCallbacks?)` | Stops playback and clears the current animation |
| `Pause()` | Freezes playback at the current frame |
| `Resume()` | Resumes a paused animation |

```csharp
// Hard cut
animator.Play("run");

// Cross-fade over 0.15 s
animator.PlayWithCrossFade("run", 0.15f);

// Queue "land" after "jump" finishes
animator.Play("jump");
animator.PlayQueued("land");
```

!!! note "Queue depth"
    The queue is capped at `MaxQueueDepth` (default 32). Entries beyond the limit are dropped
    with a warning. Set `animator.MaxQueueDepth` to change the limit.

### State Properties

| Property | Type | Notes |
|---|---|---|
| `CurrentAnimation` | `AnimationClip?` | The active clip, or `null` |
| `CurrentFrameIndex` | `int` | Zero-based index, or `-1` when nothing is playing |
| `CurrentFrame` | `SpriteFrame?` | The current frame, or `null` |
| `CurrentTime` | `float` | Elapsed seconds within the current clip |
| `NormalizedTime` | `float` | `[0, 1]` position within the current clip |
| `TimeRemaining` | `float` | Remaining seconds for non-looping clips; `0` for looping |
| `IsPlaying` | `bool` | `true` when playing and not paused |
| `IsFinished` | `bool` | `true` when a non-looping clip has completed |
| `Speed` | `float` | Playback speed multiplier (default `1.0`) |
| `Reversed` | `bool` | When `true`, the clip plays in reverse |
| `CrossFadeAlpha` | `float` | `[0, 1]` cross-fade progress; `1.0` when no fade is active |

### Speed and Direction

```csharp
animator.Speed    = 2.0f;  // 2Ã— faster
animator.Speed    = 0.5f;  // half speed / slow-motion
animator.Reversed = true;  // play backwards
```

### Animation Registration

```csharp
animator.AddAnimation(clip);
animator.RemoveAnimation("idle");
bool exists = animator.HasAnimation("walk");
```

### Events

| Event | Signature | When it fires |
|---|---|---|
| `OnAnimationStart` | `Action<AnimationClip>` | A clip starts playing |
| `OnAnimationComplete` | `Action<AnimationClip>` | A non-looping clip finishes, or a `RepeatCount` loop limit is hit |
| `OnLoopComplete` | `Action<AnimationClip>` | Each completed pass on a looping clip |
| `OnFrameChanged` | `Action<SpriteFrame>` | The active frame index changes |
| `OnStopped` | `Action<AnimationClip>` | Playback stops entirely (after `OnAnimationComplete` or `Stop()`) |

```csharp
animator.OnAnimationComplete += clip =>
{
    if (clip.Name == "attack")
        animator.Play("idle");
};

animator.OnFrameChanged += frame =>
{
    // react to individual frame changes (e.g. dust particles on footstep frames)
};
```

---

## Cross-Fades

A cross-fade blends the outgoing clip's last frame against the incoming clip's first frames while it ramps up. `AnimationSystem` renders ghost frames via `SpriteComponent.CrossFadeGhosts` so the `SpriteRenderingSystem` issues one draw call per concurrent fade.

```csharp
// Transition initiated manually
animator.PlayWithCrossFade("run", 0.12f);

// Initiated by the state machine
sm.AddTransition("walk", "run", () => speed > 4f, crossFadeDuration: 0.1f);
```

Multiple simultaneous fades (e.g. base layer + an `AnimationLayer`) are fully supported.

---

## AnimatorComponent Properties

| Property | Type | Purpose |
|---|---|---|
| `Animator` | `SpriteAnimator` | Primary animator |
| `StateMachine` | `AnimationStateMachine` | Transition evaluator for the primary animator |
| `Parameters` | `AnimationParameters` | Named parameter store for transition conditions |
| `BlendSelector1D` | `AnimationBlendSelector1D?` | Optional 1D blend tree; takes priority over `BlendSelector2D` |
| `BlendSelector2D` | `AnimationBlendSelector2D?` | Optional 2D blend tree |
| `Layers` | `IReadOnlyList<AnimationLayer>` | Additional animation layers (sorted by priority) |
| `CurrentHitBox` | `Rectangle?` | Primary animator's current frame `HitBox`, or `null` |

```csharp
Rectangle? hitbox = anim.CurrentHitBox;
Rectangle? head   = anim.GetCurrentHitBox("head");
```

---

## Without ECS

`SpriteAnimator` can be used standalone â€” for example in a scene that doesn't use the full ECS, or in unit tests.

```csharp
var animator = new SpriteAnimator();
animator.AddAnimation(walk);
animator.Play("walk");

// In your update loop:
animator.Update(deltaTime);

// In your render loop:
if (animator.CurrentFrame is { } frame)
    renderer.DrawTexture(texture, frame.SourceRect, destRect);
```

!!! warning "Manual update required"
    When using `SpriteAnimator` outside the ECS, you are responsible for calling
    `animator.Update(deltaTime)` every frame. Inside the ECS, `AnimationSystem` handles this.
