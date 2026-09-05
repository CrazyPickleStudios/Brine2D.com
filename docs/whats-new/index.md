---
title: What's New in Brine2D
description: Release history, changelogs, and version information for Brine2D
---

# What's New in Brine2D

Release history and version information for Brine2D.

---

## Latest Release

### [v1.1](v-1.1.md) — 2026

Physics on by default, lazy sprite texture loading, a first-class letterbox/pillarbox post-processing effect, and a documentation pass covering events, default systems, and asset tooling.

[:octicons-arrow-right-24: Release notes](v-1.1.md)

---

## Release History

| Version | Release Date | Highlights |
|---------|--------------|------------|
| **[v1.1](v-1.1.md)** | 2026 | Physics on by default, lazy sprite loading, letterbox effect |
| **[v1.0](v-1.0.md)** | 2026 | Entity persistence, AOT serialization, Brine2D.Build, cross-platform CI |

---

## Version Support

| Version | Status | .NET |
|---------|--------|------|
| **v1.1** | ✅ Latest (stable) | .NET 10 |
| **v1.0** | ⚠️ Maintenance | .NET 10 |

---

## Breaking Changes Log

### v1.1

Two narrowly-scoped exceptions to the "no breaking changes without a major bump" policy — see [Release Philosophy](#release-philosophy) below for why, and the [v1.1 release notes](v-1.1.md#breaking-changes) for migration details.

- **UI anchors:** `UIAnchorResolver` is now size-aware for `Center`/`Right`/`Bottom` anchors — remove any manual compensating `AnchorOffset`
- **Behavior:** `Behavior.Entity` is now non-nullable and throws `InvalidOperationException` instead of returning `null` after detachment

### v1.0

No breaking changes. v1.0 is the first stable release.

---

## Release Philosophy

Brine2D follows **Semantic Versioning**:

- **Major (1.0, 2.0)** — Breaking changes
- **Minor (1.1, 1.2)** — New features, no breaking changes (with rare, narrowly-scoped exceptions — see below)
- **Patch (1.1.1, 1.1.2)** — Bug fixes only, no breaking changes

### Stable Phase (Current — v1.0+)

- **No breaking changes** without a major version bump, *except* for small, mechanical fixes to
  genuine bugs discovered during real project use (e.g. v1.1's `UIAnchorResolver`/`Behavior.Entity`
  fixes) — these are called out explicitly in the Breaking Changes Log above with a migration note,
  rather than held until a major release
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