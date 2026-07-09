# Roadmap

Brine2D 1.0 is released. The core engine is feature-complete, the API is stable, and CI runs on Windows, macOS, and Linux.

## Post-1.0 Priorities

### NativeAOT / Trimmed Publishing — Built-in Components

`RegisterBrineComponents()` in `ComponentTypeRegistry` uses reflection. A fully AOT-safe registration path for built-in engine components (supplying source-generated `JsonTypeInfo<T>` for each) is the highest-priority post-1.0 item for the persistence system.

### Platform Runtime Validation

Windows is fully tested. macOS and Linux build and test clean in CI. Community runtime testing and bug reports are welcome to close out any platform-specific rough edges.

### Mobile and Console Targets

Post-1.0 priorities include iOS, Android, and additional console targets subject to SDL3 platform availability.

## After 1.0

Feature additions and API extensions follow semantic versioning:

- **Minor versions (1.1, 1.2)** — New features; no breaking changes
- **Patch versions (1.0.1, 1.0.2)** — Bug fixes only
- **Major versions (2.0)** — Breaking changes, announced well in advance

!!! note
	This roadmap reflects current intent and is subject to change. Follow the [GitHub repository](https://github.com/CrazyPickleStudios/Brine2D) for the latest updates.
