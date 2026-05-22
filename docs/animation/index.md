---
title: Animation System
description: Overview of Brine2D's animation system — clips, the state machine, blend trees, layers, and Aseprite integration
---

# Animation System

!!! abstract "In this section"
    Sprite animation from individual frames and clips through to a full layered state machine with
    blend trees, Aseprite loading, and time-offset event callbacks.

    **Namespaces:** `Brine2D.Animation` · `Brine2D.Systems.Animation`

Brine2D's animation system is built around a small set of composable types that work together to drive sprite playback. You can use as much or as little of the system as your game needs — from a single looping clip to a full layered state machine with 2D blend trees.

## Architecture at a Glance

```
AnimatorComponent  (ECS component)
├── SpriteAnimator          ← plays AnimationClips, fires events
├── AnimationStateMachine   ← evaluates transitions each frame
├── AnimationParameters     ← named parameter store (bool/float/int/trigger)
├── BlendSelector1D?        ← drives clip selection from one float
├── BlendSelector2D?        ← drives clip selection from two floats
└── AnimationLayer[]        ← additional independent tracks
     ├── SpriteAnimator
     ├── AnimationStateMachine
     ├── AnimationParameters
     └── BlendSelector1D/2D?
```

`AnimationSystem` (registered in the scene) ticks all of this every frame and writes the result to the entity's `SpriteComponent`.

## Core Concepts

| Concept | What it does |
|---|---|
| [`AnimationClip`](clips-and-frames.md) | An ordered list of `SpriteFrame`s with a `PlaybackMode` |
| [`SpriteFrame`](clips-and-frames.md#spriteframe) | One frame: source rect, duration, origin, hitboxes, optional texture/tint/flip overrides |
| [`SpriteAnimator`](animator-component.md#spriteanimator) | Advances time through a clip, fires events, exposes current frame |
| [`AnimationStateMachine`](state-machine.md) | Code-driven transitions between named clips |
| [`AnimationParameters`](state-machine.md#animationparameters) | Typed named parameters evaluated in transition conditions |
| [`AnimationBlendSelector1D`](blend-trees.md#1d-blend-tree) | Selects and speeds a clip based on one float |
| [`AnimationBlendSelector2D`](blend-trees.md#2d-blend-tree) | Selects a clip based on a 2D position (nearest-neighbor) |
| [`AnimationLayer`](layers.md) | An independent animator + state machine running in parallel |
| [`AsepriteClipLoader`](aseprite.md) | Loads clips directly from Aseprite JSON exports |
| [`ClipEvent`](clip-events.md) | A named time-offset callback fired during playback |

## Quick Start (ECS)

```csharp
// 1. Register the system in your scene builder
builder.AddSystem<AnimationSystem>();

// 2. Add the component to an entity
var animator = entity
    .AddComponent<SpriteComponent>()
    .AddComponent<AnimatorComponent>()
    .GetComponent<AnimatorComponent>();

// 3. Build a clip
var idle = new AnimationClip("idle") { PlaybackMode = PlaybackMode.Loop };
idle.AddFrame(new SpriteFrame(new Rectangle(0, 0, 32, 32)));
idle.AddFrame(new SpriteFrame(new Rectangle(32, 0, 32, 32)));

// 4. Register and play
animator.Animator.AddAnimation(idle);
animator.Animator.Play("idle");
```

`AnimationSystem` handles all ticking and writes `CurrentFrame` to the entity's `SpriteComponent` automatically.

## Pages in This Section

- [Clips & Frames](clips-and-frames.md) — building `AnimationClip`s and `SpriteFrame`s manually
- [Animator Component](animator-component.md) — ECS setup, `SpriteAnimator` playback API, cross-fades, queuing
- [State Machine](state-machine.md) — transitions, parameters, callbacks, forced states
- [Blend Trees](blend-trees.md) — 1D and 2D clip selection from continuous parameters
- [Layers](layers.md) — independent parallel animation tracks and blending
- [Aseprite Integration](aseprite.md) — loading clips from Aseprite JSON exports
- [Clip Events](clip-events.md) — time-offset callbacks fired during playback
