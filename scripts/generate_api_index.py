"""
Generates docs/api/index.md by scanning the DefaultDocumentation Directory-factory output.
With the Directory factory, each namespace becomes a folder with its own index.md.
Run after defaultdocumentation and before mkdocs build.
"""

import os

API_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "api")
OUTPUT = os.path.join(API_DIR, "index.md")


def namespace_description(name: str) -> str:
    descriptions = {
        "Brine2D": "Root namespace — SDL3 service extensions and engine entry points",
        "Brine2D.Animation": "Clips, frames, animator component, state machines, blend trees",
        "Brine2D.Assets": "Asset loading, caching, manifests",
        "Brine2D.Audio": "Sound effects, music, spatial audio",
        "Brine2D.Collision": "Collision detection, shapes, events",
        "Brine2D.Common": "Shared utilities and helpers",
        "Brine2D.Core": "GameTime, Color, Rectangle, math helpers",
        "Brine2D.ECS": "Entities, components, systems, queries",
        "Brine2D.ECS.Components": "Built-in ECS components",
        "Brine2D.ECS.Components.Joints": "Physics joint components",
        "Brine2D.ECS.Query": "Query types and filters",
        "Brine2D.ECS.Serialization": "ECS serialization support",
        "Brine2D.ECS.Systems": "Built-in ECS systems",
        "Brine2D.Engine": "Game loop, scene management",
        "Brine2D.Engine.Transitions": "Scene transition effects",
        "Brine2D.Events": "Event bus, window events",
        "Brine2D.Hosting": "Builder pattern, options, DI wiring",
        "Brine2D.Input": "Keyboard, mouse, gamepad, input actions",
        "Brine2D.Performance": "Diagnostics and performance monitoring",
        "Brine2D.Physics": "Physics bodies, joints, simulation",
        "Brine2D.Pooling": "Object pooling utilities",
        "Brine2D.Rendering": "Sprites, cameras, particles, post-processing",
        "Brine2D.Rendering.PostProcessing": "Post-processing pipeline",
        "Brine2D.Rendering.SDL": "SDL3 rendering internals",
        "Brine2D.Rendering.SDL.PostProcessing": "SDL3 post-processing",
        "Brine2D.Rendering.SDL.PostProcessing.Effects": "Built-in post-processing effects",
        "Brine2D.Rendering.SDL.PostProcessing.Shaders": "Post-processing shaders",
        "Brine2D.Rendering.SDL.Shaders": "SDL3 shader support",
        "Brine2D.Rendering.SDL.Shaders.PostProcessing": "Post-processing shader types",
        "Brine2D.Rendering.SDL.TextureAtlas": "SDL3 texture atlas runtime",
        "Brine2D.Rendering.Text": "Text rendering",
        "Brine2D.Rendering.TextureAtlas": "Texture atlas runtime",
        "Brine2D.Systems.AI": "AI controller and behaviors",
        "Brine2D.Systems.Animation": "Animation system",
        "Brine2D.Systems.Audio": "Audio system",
        "Brine2D.Systems.Input": "Input system",
        "Brine2D.Systems.Physics": "Physics system",
        "Brine2D.Systems.Rendering": "Rendering system",
        "Brine2D.Threading": "Threading and async utilities",
        "Brine2D.Tilemap": "Tilemap loading and rendering",
        "Brine2D.UI": "UI components, layout, input handling",
    }
    return descriptions.get(name, "")


def folder_to_namespace(rel_path: str) -> str:
    return rel_path.replace(os.sep, ".").replace("/", ".")


def is_namespace_page(filepath: str) -> bool:
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                if line.startswith("## ") and "Namespace" in line:
                    return True
                if line.startswith("### ") or line.startswith("| "):
                    break  # past the heading area, not a namespace page
    except OSError:
        pass
    return False


def main():
    entries = []

    for dirpath, dirnames, filenames in os.walk(API_DIR):
        dirnames.sort()
        if "index.md" not in filenames:
            continue
        rel = os.path.relpath(dirpath, API_DIR)
        if rel == ".":
            continue
        index_path = os.path.join(dirpath, "index.md")
        if not is_namespace_page(index_path):
            continue
        namespace = folder_to_namespace(rel)
        if not namespace.startswith("Brine2D"):
            continue
        link_path = os.path.join(rel, "index.md").replace(os.sep, "/")
        entries.append((namespace, link_path))

    entries.sort(key=lambda e: e[0])

    rows = []
    for namespace, link_path in entries:
        description = namespace_description(namespace)
        rows.append(f"| [{namespace}]({link_path}) | {description} |")

    # Write index.md
    content = """\
---
title: API Reference
description: Auto-generated API reference for Brine2D, built from XML doc comments in the source code.
---

# API Reference

This reference is generated automatically from the Brine2D source code on every docs build.
All public types, properties, methods, and events are documented here.

Use the search bar at the top of the page to find a specific type or method, or browse by namespace below.

| Namespace | Contents |
|---|---|
"""
    content += "\n".join(rows) + "\n"

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated {OUTPUT} with {len(rows)} namespaces.")

    # Write docs/api/.pages — points awesome-pages at the Brine2D root folder
    api_pages_path = os.path.join(API_DIR, ".pages")
    with open(api_pages_path, "w", encoding="utf-8") as f:
        f.write("nav:\n  - index.md\n  - Brine2D\n")
    print(f"Generated {api_pages_path}.")

    # Write docs/api/Brine2D/.pages — lists only namespace-level folders in order
    brine2d_dir = os.path.join(API_DIR, "Brine2D")
    if os.path.isdir(brine2d_dir):
        # Namespace folders are immediate children of Brine2D/ that have an index.md
        # and are namespace pages (e.g. Animation/, Core/) — not type folders
        ns_folders = sorted(
            d for d in os.listdir(brine2d_dir)
            if os.path.isdir(os.path.join(brine2d_dir, d))
            and is_namespace_page(os.path.join(brine2d_dir, d, "index.md"))
        )
        brine2d_pages_path = os.path.join(brine2d_dir, ".pages")
        with open(brine2d_pages_path, "w", encoding="utf-8") as f:
            f.write("nav:\n  - index.md\n")
            for folder in ns_folders:
                f.write(f"  - {folder}\n")
        print(f"Generated {brine2d_pages_path} with {len(ns_folders)} namespace folders.")


if __name__ == "__main__":
    main()
