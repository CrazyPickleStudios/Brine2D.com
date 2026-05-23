---
title: Animation Demo
description: Animation Demo sample in Brine2D
---

# Animation Demo

The Animation Demo shows the full animation system in action: a character entity driven by a state machine, a 2D directional blend tree, animation layers, and Aseprite-loaded clips with hitbox slices.

## What's Demonstrated

| Feature | Where to look |
|---|---|
| `AnimatorComponent` + `AnimationSystem` ECS wiring | `AnimationDemoScene.cs` |
| `AnimationStateMachine` with trigger and speed transitions | `PlayerAnimationSetup.cs` |
| `AnimationBlendSelector2D` for eight-way directional movement | `PlayerAnimationSetup.cs` |
| `AnimationLayer` for an upper-body attack overlay | `PlayerAnimationSetup.cs` |
| `AsepriteClipLoader` with hitbox slices | `AnimationDemoScene.cs` |
| `ClipEvent` footstep sounds | `PlayerAnimationSetup.cs` |
| Cross-fade transitions | `PlayerAnimationSetup.cs` |

## Running the Demo

```
dotnet run --project samples/FeatureDemos
```

Select **Animation Demo** from the main menu.

## Key Controls

| Key | Action |
|---|---|
| WASD / Arrow keys | Move (drives blend tree) |
| Space | Jump (one-shot, returns to idle) |
| F | Attack (one-shot upper-body layer) |
| 1–3 | Force state (idle / walk / run) |
| Tab | Toggle state machine diagnostic overlay |

---

## Further Reading

- [Animation System Overview](../animation/index.md)
- [State Machine](../animation/state-machine.md)
- [Blend Trees](../animation/blend-trees.md)
- [Layers](../animation/layers.md)
- [Aseprite Integration](../animation/aseprite.md)
