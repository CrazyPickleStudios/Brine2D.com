---
title: Scene Transitions
description: Smooth visual effects and loading screens when transitioning between scenes
---

# Scene Transitions

Scene transitions provide **visual feedback** during scene changes, making your game feel polished and professional. Brine2D supports **fade transitions** and **custom loading screens**.

## Overview

| Feature | Purpose | Use For |
|---------|---------|---------|
| **ISceneTransition** | Visual effect during transition | Fade in/out, wipes, crossfades |
| **LoadingScene** | Progress indication | Long loads, asset loading |
| **Combined** | Transition + loading screen | Best user experience |

---

## Basic Scene Transitions

### Without Transition (Instant)

```csharp
// Instant scene change (no transition)
_sceneManager.LoadScene<GameScene>();
```

---

### With Fade Transition

```csharp
using Brine2D.Engine.Transitions;

// Fade to black and back (1 second)
_sceneManager.LoadScene<GameScene>(
    new FadeTransition(duration: 1f));

// Fade to white (2 seconds)
_sceneManager.LoadScene<GameScene>(
    new FadeTransition(duration: 2f, color: Color.White));
```

---

## The ISceneTransition Interface

```csharp
public interface ISceneTransition
{
    float Duration { get; }
    bool IsComplete { get; }
    float Progress { get; }
    void Begin();
    void Update(GameTime gameTime);
    void Render(IRenderer renderer);
}
```

---

## Loading Screens

### The LoadingScene Class

`LoadingScene` extends `SceneBase` (not `Scene`) - it does NOT have a `World`. Loading screens are visual-only and render between scene scopes.

```csharp
public abstract class LoadingScene : SceneBase
{
    protected float LoadingProgress { get; }
    protected string LoadingMessage { get; }
    public void UpdateProgress(float progress, string? message = null);
    protected virtual void OnRenderLoading(GameTime gameTime);
}
```

**Key features:**
- :white_check_mark: Progress tracking (0.0 to 1.0)
- :white_check_mark: Status messages
- :white_check_mark: Thread-safe progress updates
- :white_check_mark: No EntityWorld - visual-only

---

### Using Loading Screens

```csharp
// Load with custom loading screen
_sceneManager.LoadScene<GameScene, MyLoadingScreen>();

// With transition AND loading screen
_sceneManager.LoadScene<GameScene, MyLoadingScreen>(
    new FadeTransition(1f));
```

---

### Basic Loading Screen

```csharp
public class SimpleLoadingScreen : LoadingScene
{
    // Default implementation shows:
    // - "Loading..." text
    // - Progress bar
    // - Percentage
    // No need to override anything!
}
```

---

### Custom Loading Screen

```csharp
public class CustomLoadingScreen : LoadingScene
{
    protected override void OnRenderLoading(GameTime gameTime)
    {
        var centerX = Renderer.Width / 2f;
        var centerY = Renderer.Height / 2f;

        Renderer.DrawText("Loading Game...", centerX - 80, centerY - 100, Color.Cyan);

        // Progress bar
        var barWidth = 400f;
        var barHeight = 30f;
        var barX = centerX - barWidth / 2f;
        var barY = centerY + 20;

        Renderer.DrawRectangleFilled(barX, barY, barWidth, barHeight, Color.FromArgb(40, 40, 40));
        Renderer.DrawRectangleFilled(barX, barY, barWidth * LoadingProgress, barHeight, Color.FromArgb(50, 150, 255));
        Renderer.DrawRectangleOutline(barX, barY, barWidth, barHeight, Color.White, 2f);

        Renderer.DrawText(LoadingMessage, centerX - 60, centerY + 70, Color.FromArgb(200, 200, 200));
        Renderer.DrawText($"{(int)(LoadingProgress * 100)}%", centerX - 20, centerY - 10, Color.White);
    }
}
```

---

## Scene with Loading Screen

```csharp
public class GameScene : Scene
{
    private readonly IAssetLoader _assets;

    public GameScene(IAssetLoader assets)
    {
        _assets = assets;
    }

    protected override async Task OnLoadAsync(CancellationToken ct, IProgress<float>? progress = null)
    {
        progress?.Report(0.2f);

        _playerTexture = await _assets.GetOrLoadTextureAsync("assets/images/player.png", cancellationToken: ct);
        progress?.Report(0.5f);

        _bgMusic = await _assets.GetOrLoadMusicAsync("assets/audio/theme.ogg", ct);
        progress?.Report(0.8f);

        // Or use AssetManifest for parallel preloading:
        // await _assets.PreloadAsync(_manifest, progress: ..., cancellationToken: ct);

        progress?.Report(1.0f);
    }
}
```

---

## Transition from Any Scene

```csharp
public class MenuScene : Scene
{
    private readonly ISceneManager _sceneManager;

    public MenuScene(ISceneManager sceneManager)
    {
        _sceneManager = sceneManager;
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyPressed(Key.Enter))
        {
            // Simple transition
            _sceneManager.LoadScene<GameScene>(
                new FadeTransition(duration: 0.5f));
        }

        if (Input.IsKeyPressed(Key.Space))
        {
            // With loading screen
            _sceneManager.LoadScene<GameScene, CustomLoadingScreen>(
                new FadeTransition(duration: 0.5f));
        }
    }
}
```

---

## ISceneManager API

```csharp
public interface ISceneManager
{
    Scene? CurrentScene { get; }
    event EventHandler<SceneLoadFailedEventArgs>? SceneLoadFailed;

    // Fire-and-forget transitions (void return)
    void LoadScene<TScene>(ISceneTransition? transition = null, CancellationToken ct = default)
        where TScene : Scene;

    void LoadScene<TScene, TLoadingScene>(ISceneTransition? transition = null, CancellationToken ct = default)
        where TScene : Scene
        where TLoadingScene : LoadingScene;

    void LoadScene(Type sceneType, ISceneTransition? transition = null, LoadingScene? loadingScreen = null, CancellationToken ct = default);

    void LoadScene<TScene>(Func<IServiceProvider, TScene> sceneFactory, ISceneTransition? transition = null, LoadingScene? loadingScreen = null, CancellationToken ct = default)
        where TScene : Scene;
}
```

**Important:** `LoadScene` is fire-and-forget. It queues a transition for the end of the current frame. React to the transition in the target scene's `OnEnter()` or handle failures via the `SceneLoadFailed` event.

---

## Best Practices

1. **Use transitions for all player-visible scene changes**
2. **Use loading screens for scenes with heavy asset loading**
3. **Report progress** via the `IProgress<float>?` parameter in `OnLoadAsync`
4. **Use `AssetManifest`** for parallel asset preloading in complex scenes

---

## Next Steps

- **[Scene Lifecycle](lifecycle-hooks.md)** - Scene lifecycle in depth
- **[Scenes Overview](index.md)** - Scene concepts
