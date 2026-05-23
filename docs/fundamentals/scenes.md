---
title: Scene Management
description: How scenes organize your Brine2D game into distinct states
---

# Scene Management

Scenes are the building blocks of your game. Each scene represents a distinct screen or state - menu, gameplay, pause, game over.

## How Scenes Work

Brine2D's scene system follows the same patterns as ASP.NET Core:

| ASP.NET Core | Brine2D | Purpose |
|--------------|---------|---------|
| Controller | Scene | Handles a section of your app/game |
| Request scope | Scene scope | Services scoped to the current scene |
| Middleware | ECS Systems | Automatic processing pipeline |
| `ILogger<T>` | `Logger` property | Structured logging |

## Scene Types

| Base Class | Has World (ECS) | Use For |
|-----------|:---------------:|---------|
| `Scene` | :white_check_mark: | Gameplay with entities |
| `SceneBase` | :x: | Lightweight scenes (menus) |
| `LoadingScene` | :x: | Loading screen display |

## Quick Example

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;

    public GameScene(IAssetLoader assets) => _assets = assets;

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        _texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
    }

    protected override void OnEnter()
    {
        var player = World.CreateEntity("Player");
        player.AddComponent<TransformComponent>().Position = new Vector2(400, 300);
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyDown(Key.W))
        {
            var transform = _player.GetComponent<TransformComponent>()!;
            transform.Position += new Vector2(0, -200f * (float)gameTime.DeltaTime);
        }
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Score: " + _score, 10, 10, Color.White);
    }
}
```

## What's Automatic

| Feature | Manual? | Automatic? |
|---------|---------|------------|
| Frame management (clear/begin/end) | :x: | :white_check_mark: |
| ECS system execution | :x: | :white_check_mark: |
| World cleanup on scene unload | :x: | :white_check_mark: |
| Asset release (scoped IAssetLoader) | :x: | :white_check_mark: |
| Framework property injection | :x: | :white_check_mark: |

## Learn More

For the complete lifecycle reference, framework property availability, transitions, and patterns:

[:octicons-arrow-right-24: Scenes - Full Guide](../scenes/index.md)

[:octicons-arrow-right-24: Scene Transitions](../scenes/transitions.md)