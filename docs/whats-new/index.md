---
title: What's New in Brine2D
description: Release history, changelogs, and version information for Brine2D
---

# What's New in Brine2D

Release history and version information for Brine2D.

---

## Latest Release

### [v1.0](v-1.0.md) — 2026

**First stable release.** The core engine is feature-complete and the API is locked.

[:octicons-arrow-right-24: Release notes](v-1.0.md)

---

## Release History

| Version | Release Date | Highlights |
|---------|--------------|------------|
| **[v1.0](v-1.0.md)** | 2026 | Entity persistence, AOT serialization, Brine2D.Build, cross-platform CI |
| **[v0.9.7-beta](v-0.9.7-beta.md)** | 2026 | Input actions, Box2D physics, kinematic character |
| **[v0.9.6-beta](v-0.9.6-beta.md)** | 2026 | Complete audio overhaul, post-processing effects |
| **[v0.9.5-beta](v-0.9.5-beta.md)** | 2026 | Single package, framework properties, asset pipeline |
| **[v0.9.0-beta](v-0.9.0-beta.md)** | Jan 2026 | Package separation, track-based audio, .NET 10 |
| **[v0.8.0-beta](v-0.8.0-beta.md)** | Dec 2025 | Particle textures, spatial audio, texture atlasing |
| **[v0.7.0-beta](v-0.7.0-beta.md)** | Nov 2025 | GPU renderer, post-processing, EventBus |
| **[v0.6.0-beta](v-0.6.0-beta.md)** | Oct 2025 | Scene transitions, UI framework, collision system |

---

## Version Support

| Version | Status | .NET |
|---------|--------|------|
| **v1.0** | ✅ Latest (stable) | .NET 10 |
| **v0.9.7-beta** | ⚠️ Maintenance | .NET 10 |
| **v0.9.6-beta** | ❌ End of life | .NET 10 |
| **v0.9.5-beta** | ❌ End of life | .NET 10 |
| **v0.9.0-beta** | ❌ End of life | .NET 10 |
| **v0.8.0 and earlier** | ❌ End of life | — |

---

## Breaking Changes Log

### v1.0

No breaking changes. v1.0 is the first stable release.

### v0.9.7

- **Physics:** Old manual `CollisionSystem` / `Collider` / `SpatialGrid` removed — use `PhysicsBodyComponent` + `Box2DPhysicsSystem`
- **Input layers:** `InputLayerManager.CreateLayer()` removed — implement `IInputLayer` and call `RegisterLayer()` / `UnregisterLayer()`
- **Input enum:** `Key.Return` corrected to `Key.Enter`

### v0.9.6

- **Audio:** `PlaySound()` now returns `nint` track handle (was `int` channel)
- **Audio:** `StopChannel(int)` → `StopTrack(nint)`, `PauseChannel(int)` → `PauseTrack(nint)`, `IsChannelPlaying(int)` → `IsTrackAlive(nint)`

### v0.9.5

- **Packages:** Consolidated into single `Brine2D` package (no more `Brine2D.SDL`)
- **Builder:** `AddSDL3Rendering()` / `AddSDL3Input()` / `AddSDL3Audio()` → `builder.Configure()`
- **Scenes:** `IRenderer`, `IInputContext`, `IAudioPlayer` removed from constructors — use framework properties
- **Lifecycle:** `OnInitializeAsync` removed — use `OnLoadAsync`
- **Input enum:** `Keys` → `Key`
- **Component:** `OnUpdate(GameTime)` removed — use `Behavior`
- **Entity.Id:** `Guid` → `long`
- **Scene transition:** `LoadSceneAsync` → `LoadScene` (void, fire-and-forget)

### v0.9.0

- **Audio:** `PlaySound()` returns `nint` (from `int`)
- **Packages:** Split into `Brine2D` and `Brine2D.SDL`

### v0.8.0

- **Scenes:** Constructor injection changed — `Logger`, `World`, `Renderer` now properties
- **ECS:** `World` is a framework property, not injected

### v0.7.0

- **Rendering:** `SDL3GPURenderer` introduced as a separate backend
- **EventBus:** Moved from `Brine2D.ECS` to `Brine2D.Core`

---

## Release Philosophy

Brine2D follows **Semantic Versioning**:

- **Major (1.0, 2.0)** — Breaking changes
- **Minor (0.9, 0.10)** — New features, may include breaking changes in beta
- **Patch (0.9.1, 0.9.2)** — Bug fixes only, no breaking changes

### Stable Phase (Current — v1.0+)

- **No breaking changes** without a major version bump
- Deprecations announced one minor version before removal
- Long-term support for each major version
- Predictable release schedule
- Production-ready stability

---

## Get Notified

- 🔔 **Watch on GitHub** — [Star the repo](https://github.com/CrazyPickleStudios/Brine2D) for notifications
- 💡 **Request features** — [Open an issue](https://github.com/CrazyPickleStudios/Brine2D/issues/new)
- 🐛 **Report bugs** — [Bug report template](https://github.com/CrazyPickleStudios/Brine2D/issues/new?template=bug_report.md)
- 🤝 **Contribute** — [Contributing guide](../contributing/index.md)
- 💬 **Discussions** — [GitHub Discussions](https://github.com/CrazyPickleStudios/Brine2D/discussions)

---

**See a specific version:** [v0.9.7](v-0.9.7-beta.md) | [v0.9.6](v-0.9.6-beta.md) | [v0.9.5](v-0.9.5-beta.md) | [v0.9.0](v-0.9.0-beta.md) | [v0.8.0](v-0.8.0-beta.md) | [v0.7.0](v-0.7.0-beta.md) | [v0.6.0](v-0.6.0-beta.md)