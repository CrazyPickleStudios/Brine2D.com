---
title: State Machine
description: AnimationStateMachine, AnimationTransition, AnimationParameters, and state callbacks in Brine2D
---

# State Machine

!!! abstract "In this article"
    `AnimationStateMachine` transitions (condition, on-complete, AnyState, trigger), `AnimationParameters`
    (bool, float, int, trigger types and safe consumption), state enter/exit callbacks, forced states,
    and transition diagnostics.

    **Namespace:** `Brine2D.Animation`

`AnimationStateMachine` is a lightweight code-driven state machine that evaluates transition conditions each frame and calls `SpriteAnimator.Play` automatically when one passes. You never manually poll input and call `Play` in `OnUpdate` — the state machine does that for you once you've declared the transitions.

## Overview

```
Transitions are evaluated in descending Priority order.
Within the same priority, insertion order wins.
The first passing condition fires; evaluation stops.

AnyState transitions are evaluated after all regular transitions for the current state.
Non-looping clips block outgoing transitions unless CanInterrupt = true.
```

`AnimationSystem` calls `StateMachine.Update(delta)` before advancing the animator each tick.

---

## Setting a Default State

The default state is the fallback the machine enters when no animation is playing. It is played (or restarted) automatically.

```csharp
var sm = animComp.StateMachine;
sm.SetDefaultState("idle");
```

---

## Adding Transitions

### Condition-based transition

```csharp
sm.AddTransition("idle", "walk", () => speed > 0.1f);
sm.AddTransition("walk", "idle", () => speed <= 0.1f);
sm.AddTransition("walk", "run",  () => speed > 4f);
sm.AddTransition("run",  "walk", () => speed <= 4f);
```

### From any state

```csharp
// Fires regardless of which animation is currently playing
sm.AddAnyTransition("hurt", () => tookDamage, canInterrupt: true);
```

### On-complete transition

Fires when a non-looping clip reaches its natural end:

```csharp
sm.AddOnCompleteTransition("jump", "land");
sm.AddOnCompleteTransition("land", "idle");

// Unconditional AnyState on-complete
sm.AddAnyOnCompleteTransition("idle");
```

### Transition options

All `AddTransition` / `AddAnyTransition` overloads share these optional parameters:

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `canInterrupt` | `bool` | `false` | Allow transition to interrupt a non-looping clip mid-play |
| `crossFadeDuration` | `float` | `0` | Blend over this many seconds instead of hard-cutting |
| `minStateDuration` | `float` | `0` | Source must have been active at least this many seconds |
| `minNormalizedTime` | `float` | `0` | Source must have reached this normalised position `[0, 1]` |
| `priority` | `int` | `0` | Higher values evaluated first within the same list |
| `restartSelf` | `bool` | `false` | Allow a transition from a state back to itself |

```csharp
// Exit-time: don't transition until 80% through the clip
sm.AddTransition("attack", "idle", () => true, minNormalizedTime: 0.8f);

// Cross-fade with a 0.1 s blend
sm.AddTransition("walk", "run", () => speed > 4f, crossFadeDuration: 0.1f);
```

---

## AnimationParameters

`AnimationParameters` is a typed named-parameter store designed for use in transition conditions. It eliminates manual boolean reset bookkeeping.

```csharp
var p = animComp.Parameters;

// In your setup:
sm.AddTransition("idle", "walk",   () => p.GetFloat("speed") > 0.1f);
sm.AddTransition("walk", "idle",   () => p.GetFloat("speed") <= 0.1f);
sm.AddTransition("idle", "attack", () => p.GetBool("isAttacking"));
sm.AddTransition("walk", "attack", () => p.GetBool("isAttacking"));

// In OnUpdate every frame:
p.SetFloat("speed", velocity.Length());
p.SetBool("isAttacking", isAttackButtonHeld);
```

### Four parameter types

| Type | Set | Get | Notes |
|---|---|---|---|
| `Bool` | `SetBool(name, value)` | `GetBool(name)` | Latching; stays set until explicitly cleared |
| `Float` | `SetFloat(name, value)` | `GetFloat(name)` | Continuous value |
| `Int` | `SetInt(name, value)` | `GetInt(name)` | Integer value |
| `Trigger` | `SetTrigger(name)` | `GetTrigger(name)` | Fire-once: returns `true` exactly once then auto-resets |

### Triggers and safe consumption

!!! warning "Trigger short-circuit hazard"
    `GetTrigger` consumes the trigger immediately on read. Do **not** use it in compound conditions
    like `() => p.GetTrigger("attack") && isGrounded` — if `isGrounded` short-circuits to `false`
    first, the trigger is still consumed.

Use `IsTriggerArmed` as the guard and let `AddTriggerTransition` consume it safely via `OnFired`:

```csharp
// Safe trigger transition — uses IsTriggerArmed as condition, ResetTrigger in OnFired
sm.AddTriggerTransition("idle",   "attack", p, "attackPressed");
sm.AddTriggerTransition("walk",   "attack", p, "attackPressed");
sm.AddAnyTriggerTransition("hurt", p, "tookDamage", canInterrupt: true);

// Trigger with on-complete chaining
sm.AddOnCompleteTriggerTransition("attack", "combo2", p, "attackPressed");

// Set the trigger from input
if (inputAttack) p.SetTrigger("attackPressed");
```

### Checking and removing parameters

```csharp
bool hasBool  = p.HasBool("isAttacking");
bool hasFloat = p.HasFloat("speed");

p.RemoveBool("isAttacking");
p.RemoveFloat("speed");
p.ResetTrigger("attackPressed"); // manually consume a trigger
p.ClearAll();                    // remove everything
```

---

## State Callbacks

Register callbacks that fire whenever a named state is entered or exited. Multiple callbacks per state are supported.

```csharp
sm.OnStateEnter("attack", prev =>
{
    audioService.Play("sword_swing");
});

sm.OnStateExit("hurt", next =>
{
    invincibilityTimer = 0.5f;
});
```

Remove a specific callback:

```csharp
Action<string?> onEnterAttack = prev => audioService.Play("sword_swing");
sm.OnStateEnter("attack", onEnterAttack);
// later:
sm.RemoveStateEnterCallback("attack", onEnterAttack);

// Remove all callbacks for a state
sm.RemoveStateEnterCallback("attack");
sm.RemoveStateExitCallback("hurt");
```

The `OnStateChanged` event fires for every state change regardless of name:

```csharp
sm.OnStateChanged += (prev, next) =>
{
    Logger.LogDebug("Transition: {Prev} → {Next}", prev, next);
};
```

---

## Forced Transitions

Bypass condition evaluation and drive the state machine imperatively:

```csharp
sm.ForceState("attack");              // immediate, no restart if already playing
sm.ForceState("attack", restart: true); // always restart from frame 0
sm.ForceStop();                         // stop and clear (fires OnStopped by default = false)
sm.ForceStateQueued("idle");            // queue after current non-looping clip
sm.ForceStateQueuedWithCrossFade("idle", 0.15f);
```

`ForceState` still fires `OnStateChanged` and state enter/exit callbacks. It suppresses the internal play-event loop so the state machine doesn't double-track the change.

---

## Control and Diagnostics

```csharp
sm.IsEnabled = false;  // suspend transition evaluation (animator keeps playing)
sm.IsEnabled = true;   // re-enable

bool inWalk = sm.IsInState("walk");
bool can    = sm.CanTransitionTo("run");

// Last 16 state names (oldest at index 0)
IReadOnlyList<string> history = sm.StateHistory;
sm.ClearStateHistory();

float elapsed = sm.StateTimer; // seconds in the current state

string? current  = sm.CurrentState;
string? previous = sm.PreviousState;
```

### Validation

```csharp
var issues = sm.ValidateTransitions();
foreach (var msg in issues)
    Logger.LogWarning(msg);
```

`ValidateTransitions` checks that every transition's `To` target is registered on the animator. Call it after setup during development.

---

## Removing Transitions

```csharp
// By handle returned from AddTransition
var t = sm.AddTransition("walk", "run", () => speed > 4f);
sm.RemoveTransition(t);

// By source/target
sm.RemoveTransitions("walk", "run");
sm.RemoveAnyTransitions("hurt");
sm.RemoveOnCompleteTransitions("jump", "land");
sm.RemoveAnyOnCompleteTransition("idle");

sm.ClearTransitions(); // remove everything
```

---

## Full Example

```csharp
var p  = animComp.Parameters;
var sm = animComp.StateMachine;

sm.SetDefaultState("idle");

sm.AddTransition("idle", "walk",  () => p.GetFloat("speed") > 0.1f);
sm.AddTransition("walk", "idle",  () => p.GetFloat("speed") <= 0.1f);
sm.AddTransition("walk", "run",   () => p.GetFloat("speed") > 4f);
sm.AddTransition("run",  "walk",  () => p.GetFloat("speed") <= 4f);

sm.AddAnyTriggerTransition("attack", p, "attackPressed", canInterrupt: false);
sm.AddOnCompleteTransition("attack", "idle");

sm.AddAnyTriggerTransition("hurt", p, "tookDamage", canInterrupt: true, crossFadeDuration: 0.05f);
sm.AddOnCompleteTransition("hurt", "idle");

sm.OnStateEnter("attack", _ => audioService.Play("sword_swing"));

// Each frame (e.g. in a Behavior or System):
p.SetFloat("speed", rigidbody.LinearVelocity.Length());
if (attackInput) p.SetTrigger("attackPressed");
if (hitByEnemy)  p.SetTrigger("tookDamage");
```
