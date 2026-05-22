---
title: Animation System Tutorial
description: Learn Brine2D's animation system — clips, the state machine, and Aseprite loading
---

# Animation Tutorial

**Difficulty:** Beginner–Intermediate | **Time:** 25 minutes

This tutorial walks through building an animated ECS character from scratch, covering sprite sheet setup, the `AnimatorComponent`, a code-driven state machine, and optionally loading clips from Aseprite.

## Prerequisites

- Completed [Moving Sprites](moving-sprites.md) tutorial  
- A sprite sheet image, or use the placeholder approach shown below  
- Familiarity with the ECS basics ([ECS Getting Started](../ecs/getting-started.md))

---

## What You'll Build

A player entity that:

- Plays different animation clips for idle, walk, and run
- Automatically transitions between them using a state machine
- Triggers a one-shot jump clip that returns to the previous state when done

---

## Understanding Sprite Sheets

A sprite sheet is a single image containing multiple animation frames in a grid. You load it once and reference sub-rectangles for each frame.

```
character.png  (256 × 96)
?????????????????????????????????????????????????????????
?  0   ?  1   ?  2   ?  3   ?  4   ?  5   ?  6   ?  7   ?  ? idle row (y = 0)
?????????????????????????????????????????????????????????
?????????????????????????????????????????????????????????
?  8   ?  9   ? 10   ? 11   ? 12   ? 13   ? 14   ? 15   ?  ? run  row (y = 32)
?????????????????????????????????????????????????????????
??????????????????????
? 16   ? 17   ? 18   ?                                      ? jump row (y = 64)
??????????????????????
```

Each frame is 32 × 32 pixels.

---

## Step 1: Scene Setup

```csharp
using Brine2D.Animation;
using Brine2D.Assets;
using Brine2D.Core;
using Brine2D.ECS;
using Brine2D.Engine;
using Brine2D.Input;
using Brine2D.Rendering;
using Brine2D.Systems.Animation;
using Brine2D.Systems.Rendering;
using Microsoft.Extensions.Logging;
using System.Numerics;

namespace MyGame;

public class AnimationScene : SceneBase
{
    private readonly IAssetLoader _assets;
    private readonly IInputContext _input;
    private readonly ILogger<AnimationScene> _logger;

    private Entity _player;
    private ITexture? _texture;

    public AnimationScene(
        IAssetLoader assets,
        IInputContext input,
        ILogger<AnimationScene> logger)
    {
        _assets = assets;
        _input  = input;
        _logger = logger;
    }

    protected override void ConfigureWorld(SceneWorldConfiguration config)
    {
        // AnimationSystem ticks every AnimatorComponent each frame
        config.AddSystem<AnimationSystem>();
        config.AddSystem<SpriteRenderingSystem>();
    }

    protected override async Task OnLoadAsync(IEntityWorld world, CancellationToken cancellationToken)
    {
        _texture = await _assets.GetOrLoadTextureAsync(
            "assets/sprites/character.png",
            TextureScaleMode.Nearest,
            cancellationToken);

        _player = CreatePlayer(world, _texture);
    }

    protected override Task OnUnloadAsync(CancellationToken cancellationToken)
    {
        if (_texture != null)
            _assets.Release(_texture);
        return Task.CompletedTask;
    }
}
```

---

## Step 2: Building Clips

Build `AnimationClip`s from the sprite sheet grid. `AddFrame` returns `this` for fluent chaining:

```csharp
private static (AnimationClip idle, AnimationClip run, AnimationClip jump) BuildClips()
{
    const int fw = 32, fh = 32;

    var idle = new AnimationClip("idle") { PlaybackMode = PlaybackMode.Loop };
    for (int i = 0; i < 8; i++)
        idle.AddFrame(new SpriteFrame(new Rectangle(i * fw, 0, fw, fh), 0.15f));

    var run = new AnimationClip("run") { PlaybackMode = PlaybackMode.Loop };
    for (int i = 0; i < 8; i++)
        run.AddFrame(new SpriteFrame(new Rectangle(i * fw, fh, fw, fh), 0.08f));

    // OnceHoldLast: plays once and freezes on the last frame
    var jump = new AnimationClip("jump") { PlaybackMode = PlaybackMode.OnceHoldLast };
    for (int i = 0; i < 3; i++)
        jump.AddFrame(new SpriteFrame(new Rectangle(i * fw, fh * 2, fw, fh), 0.1f));

    return (idle, run, jump);
}
```

!!! note "PlaybackMode"
    `Loop` repeats indefinitely. `OnceHoldLast` plays once and freezes on the last frame — ideal
    for a jump that holds its peak frame until the state machine transitions away. See
    [Clips & Frames](../animation/clips-and-frames.md) for all six modes.

---

## Step 3: Creating the Player Entity

```csharp
private Entity CreatePlayer(IEntityWorld world, ITexture texture)
{
    var (idle, run, jump) = BuildClips();

    var entity = world.CreateEntity();

    entity
        .AddComponent<TransformComponent>(t => t.Position = new Vector2(400, 300))
        .AddComponent<SpriteComponent>(s =>
        {
            s.Texture = texture;
            s.Scale   = new Vector2(2f, 2f);
        })
        .AddComponent<AnimatorComponent>();

    var anim = entity.GetComponent<AnimatorComponent>()!;

    anim.Animator.AddAnimation(idle);
    anim.Animator.AddAnimation(run);
    anim.Animator.AddAnimation(jump);

    SetupStateMachine(anim);

    return entity;
}
```

---

## Step 4: State Machine

Declare transitions once instead of polling input and calling `Play` manually every frame:

```csharp
private static void SetupStateMachine(AnimatorComponent anim)
{
    var p  = anim.Parameters;
    var sm = anim.StateMachine;

    // Fallback state entered automatically when nothing else is playing
    sm.SetDefaultState("idle");

    // Speed-driven movement transitions
    sm.AddTransition("idle", "run",  () => p.GetFloat("speed") > 0.5f);
    sm.AddTransition("run",  "idle", () => p.GetFloat("speed") <= 0.5f);

    // Jump: fire-once trigger from any state, return to idle on completion
    sm.AddAnyTriggerTransition("jump", p, "jumpPressed", canInterrupt: false);
    sm.AddOnCompleteTransition("jump", "idle");
}
```

`AnimationSystem` calls `StateMachine.Update(delta)` automatically — you never call it yourself.

---

## Step 5: Driving Parameters Each Frame

Set parameters in `OnUpdate`. The state machine reads them that same tick:

```csharp
protected override void OnUpdate(GameTime gameTime)
{
    var anim      = _player.GetComponent<AnimatorComponent>()!;
    var transform = _player.GetComponent<TransformComponent>()!;

    var dir = Vector2.Zero;
    if (_input.IsKeyDown(Key.A)) dir.X -= 1;
    if (_input.IsKeyDown(Key.D)) dir.X += 1;
    if (_input.IsKeyDown(Key.W)) dir.Y -= 1;
    if (_input.IsKeyDown(Key.S)) dir.Y += 1;

    const float moveSpeed = 150f;
    if (dir != Vector2.Zero)
    {
        dir = Vector2.Normalize(dir) * moveSpeed;
        transform.Position += dir * (float)gameTime.DeltaTime;
    }

    anim.Parameters.SetFloat("speed", dir.Length());

    if (_input.IsKeyPressed(Key.Space))
        anim.Parameters.SetTrigger("jumpPressed");
}
```

The state machine fires the correct transition, `AnimationSystem` advances the frame, and `SpriteRenderingSystem` draws it — `OnUpdate` only sets values.

---

## Optional: Loading from Aseprite

If you design animations in Aseprite, export via **File ? Export Sprite Sheet** with *JSON Data* and *Frame Tags* enabled, then replace `BuildClips` with:

```csharp
var loader = new AsepriteClipLoader();
var clips  = await loader.LoadAsync("assets/sprites/character.json", cancellationToken);
loader.ConfigureAnimator(anim.Animator, clips);
```

Every Aseprite tag becomes a named `AnimationClip`. Frame durations, hitbox slices, trim offsets, and user data fields are all loaded automatically. See [Aseprite Integration](../animation/aseprite.md).

---

## What You Learned

- `AnimationClip` and `SpriteFrame` — the raw building blocks  
- `PlaybackMode` — looping vs. one-shot behaviour  
- `AnimatorComponent` + `AnimationSystem` — zero-boilerplate ECS wiring  
- `AnimationStateMachine` + `AnimationParameters` — declarative transitions  
- Trigger parameters and on-complete transition chaining

## Next Steps

- [Clips & Frames](../animation/clips-and-frames.md) — all `SpriteFrame` properties and `PlaybackMode` values  
- [State Machine](../animation/state-machine.md) — full transition API, priorities, and diagnostics  
- [Blend Trees](../animation/blend-trees.md) — continuous 1D/2D clip selection  
- [Layers](../animation/layers.md) — upper/lower body splits and effect layers  
- [Clip Events](../animation/clip-events.md) — footstep sounds, hitbox toggles, and more  
- [Building a Platformer](platformer.md) — animation combined with physics