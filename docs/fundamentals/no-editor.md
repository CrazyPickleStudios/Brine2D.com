# Why No Editor?

Brine2D ships without a built-in editor. That is a deliberate choice, not a gap waiting to be filled.

## The problem with built-in editors

Most game engines include an editor because their runtime is not easily scriptable — a visual tool is the primary way to build a scene and wire things together. That works well for a lot of people, and the big engines have invested heavily in making those editors good.

The tradeoff is that the editor becomes the interface to everything. Animation tools, tilemap editors, and asset importers are all built in to the engine, and you work within whatever quality and feature set shipped in that version. When a built-in tool is missing something you need, your options are to wait, work around it, or use an external tool and write your own importer.

Brine2D takes a different position: everything is code, so a visual tool is never required. That also means you are free to use whichever tools you already know and trust for content creation.

## The tools Brine2D supports

The goal is direct support for tools that are already widely used, well-documented, and excellent at what they do — with no custom import step or format conversion required. You work in the tool, export in its native format, and Brine2D reads it directly.

### Aseprite

[Aseprite](https://www.aseprite.org/) is one of the most widely used pixel art and sprite animation tools in indie game development. It is available for purchase or can be compiled for free from source. It has a mature animation timeline, tag-based clip management, onion skinning, and exports a standard JSON format alongside the sprite sheet.

Brine2D reads that JSON export directly via `AsepriteClipLoader`. Your tags become `AnimationClip` objects, frame durations are preserved, ping-pong and reverse playback are handled automatically, and per-frame user data maps to clip events. You define your animations in Aseprite and they arrive in the engine as-is — no re-entry, no mapping file.

See [Aseprite Integration](../animation/aseprite.md) for the full workflow.

### Tiled

[Tiled](https://www.mapeditor.org/) is a free, open-source tile map editor that has been actively developed for over fifteen years. It supports orthogonal, isometric, and hexagonal maps; object layers; custom tile properties; and exports standard TMX/JSON formats.

Brine2D loads Tiled maps at runtime without any intermediate conversion step. Collision shapes, spawn points, object layers, and custom properties come through directly. Tiled has a large community and extensive documentation of its own — if you already know it, there is nothing new to learn on the Brine2D side.

See [Loading Tilemaps](../tilemaps/loading.md) for the full workflow.

### TexturePacker

[TexturePacker](https://www.codeandweb.com/texturepacker) is a commercial sprite atlas packing tool with a free tier. It packs sprites efficiently, handles trim, rotation, extrusion, and padding, and exports atlases alongside a descriptor file in multiple formats.

Brine2D supports TexturePacker's output directly. Proper atlas packing reduces draw calls and texture memory, and TexturePacker gives you precise control over the result.

Brine2D also has a built-in runtime atlas builder, and the two serve different stages of development. While your assets are still changing — early prototyping, iterating on art, adding and removing sprites — the built-in packer is the practical choice. There is no export step and no file to regenerate every time a sprite changes. Once your assets are settled, swapping in a TexturePacker atlas is straightforward and gives you tighter packing, better control over padding and trim, and predictable output you can tune for performance. Think of it as: build with the engine's packer, ship with TexturePacker.

See [Texture Atlasing](../rendering/texture-atlasing.md) for the full workflow.

## What this means in practice

None of these tools are Brine2D-specific. Aseprite, Tiled, and TexturePacker all have their own tutorials, communities, and years of history. If you already use any of them, you bring that knowledge directly into Brine2D. If you learn them for a Brine2D project, that knowledge carries to any other engine that supports the same formats — which most do.

Your assets stay in open, standard formats: JSON, PNG, TMX. They are easy to version control, easy to share with artists who never touch the engine, and not tied to any proprietary project file.

The tradeoff is honest: you configure and compose in code rather than in a visual viewport. If you are reading this documentation, that is probably already where you are comfortable.
