---
title: Post-Processing Effects
description: Add screen-space effects like blur and grayscale to your Brine2D games
---

# Post-Processing Effects

Post-processing effects are applied to the entire screen after the main scene is rendered. Brine2D includes a GPU-accelerated pipeline that handles render target management and texture ping-ponging automatically.

**Built-in effects:**

- **Grayscale** — adjustable intensity desaturation
- **Blur** — two-pass Gaussian blur (horizontal + vertical)

**Custom effects** are supported via the `ISDL3PostProcessEffect` interface.

---

## How It Works

```mermaid
graph LR
    A[Scene] --> B[Main Render Target]
    B --> C[Effect 1]
    C --> D[Effect 2]
    D --> E[Effect N]
    E --> F[Swapchain]

    style B fill:#2d5016,stroke:#4ec9b0,stroke-width:2px,color:#fff
    style C fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style D fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style E fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style F fill:#1e3a5f,stroke:#569cd6,stroke-width:2px,color:#fff
```

1. The scene renders to an off-screen render target instead of the swapchain
2. The pipeline runs each enabled effect in order, ping-ponging between textures
3. The final effect writes directly to the swapchain

The pipeline manages the render targets and ping-pong buffers — you don't need to create or manage them yourself.

---

## Setup

### 1. Register Post-Processing

In `Program.cs`, call `AddPostProcessing` and enable it:

```csharp
builder.Services.AddPostProcessing(options =>
{
    options.Enabled = true;
});
```

### 2. Add Effects

Chain effect registration after `AddPostProcessing`:

```csharp
builder.Services.AddPostProcessing(options =>
{
    options.Enabled = true;
});

builder.Services.AddGrayscaleEffect(intensity: 0.8f);
builder.Services.AddBlurEffect(blurRadius: 2.0f);
```

That's it. The pipeline picks up registered effects automatically when the first frame renders.

---

## Built-in Effects

### Grayscale

Desaturates the image using luminance weighting (0.299R + 0.587G + 0.114B).

```csharp
builder.Services.AddGrayscaleEffect(intensity: 1.0f);
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `width` | 1280 | Initial render width (updated on resize) |
| `height` | 720 | Initial render height (updated on resize) |
| `intensity` | 1.0f | 0.0 = original color, 1.0 = full grayscale |

`Intensity` can be changed at runtime via the effect instance.

### Blur

Two-pass Gaussian blur — horizontal then vertical — using a single shader with direction uniforms.

```csharp
builder.Services.AddBlurEffect(blurRadius: 3.0f);
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `width` | 1280 | Initial render width (updated on resize) |
| `height` | 720 | Initial render height (updated on resize) |
| `blurRadius` | 2.0f | 1.0 = subtle, 5.0 = heavy blur |

`BlurRadius` can be changed at runtime via the effect instance.

---

## Effect Ordering

Effects execute in ascending `Order` value. Both built-in effects default to `Order = 0`, so they run in registration order. Set `Order` on the effect instance to control sequencing when you have multiple effects.

---

## Custom Effects

Implement `ISDL3PostProcessEffect` to write your own GPU shader effect:

```csharp
public class MyCustomEffect : ISDL3PostProcessEffect, IDisposable
{
    public int Order { get; set; } = 100;
    public string Name => "MyEffect";
    public bool Enabled { get; set; } = true;

    private int _width;
    private int _height;

    public MyCustomEffect(int width, int height)
    {
        _width = width;
        _height = height;
        // Create your GPU pipeline, shaders, samplers here
    }

    public void SetDimensions(int width, int height)
    {
        _width = width;
        _height = height;
        // Recreate any dimension-dependent resources
    }

    public void Apply(IRenderer renderer, nint sourceTexture, nint targetTexture, nint commandBuffer)
    {
        // Render a full-screen quad with your shader,
        // reading from sourceTexture and writing to targetTexture.
        // See GrayscaleEffect or BlurEffect for reference.
    }

    public void Dispose()
    {
        // Release GPU resources
    }
}
```

Register it via DI:

```csharp
builder.Services.AddSingleton<IPostProcessEffect>(sp =>
{
    return new MyCustomEffect(1280, 720);
});
```

The pipeline resolves all `IPostProcessEffect` registrations on first use.

### Factory Registration

For effects that need the GPU device to be initialized first, use the factory pattern on `SDL3PostProcessPipeline`:

```csharp
pipeline.AddEffectFactory(() => new MyCustomEffect(1280, 720));
```

Factories are called lazily the first time the pipeline executes.

---

## Runtime Control

Effects can be toggled and adjusted at runtime:

```csharp
// Disable/enable the whole pipeline
postProcessingOptions.Enabled = false;

// Toggle individual effects
grayscaleEffect.Enabled = false;

// Adjust parameters
grayscaleEffect.Intensity = 0.5f;
blurEffect.BlurRadius = 4.0f;
```

---

## Configuration Options

`PostProcessingOptions` controls pipeline-level settings:

| Property | Default | Description |
|----------|---------|-------------|
| `Enabled` | `false` | Master toggle — when disabled, the scene renders directly to the swapchain |
| `RenderTargetFormat` | `null` | Texture format override; `null` uses the swapchain format |

```csharp
builder.Services.AddPostProcessing(options =>
{
    options.Enabled = true;
    options.RenderTargetFormat = SDL3.SDL.GPUTextureFormat.R8G8B8A8Unorm; // optional
});
```

---

## Window Resize

The pipeline handles resize automatically. When the renderer recreates its render targets, it calls `SetEffectDimensions` on all effects and rebuilds the ping-pong buffers. Effects that own dimension-dependent GPU resources (like the blur effect's intermediate render target) recreate them in `SetDimensions`.

---

## Performance

- Each effect is one or more GPU render passes — keep the total pass count low
- Blur is two passes (horizontal + vertical) plus the pipeline's own source/target management
- Effects use pre-compiled SPIR-V / DXIL / DXBC / MSL shaders — no runtime compilation
- Render targets are created once and reused; they're only recreated on resize
- Disable effects you aren't using — disabled effects are skipped entirely (zero cost)

### Resolution Scaling

For expensive effects, render at lower resolution:

```csharp
var scale = 0.5f;
var w = (int)(1280 * scale);
var h = (int)(720 * scale);
builder.Services.AddBlurEffect(width: w, height: h, blurRadius: 3.0f);
```

The GPU blit to the swapchain handles upscaling with linear filtering.

---

## Troubleshooting

### Black screen after enabling post-processing

1. **Check `Enabled = true`** — `PostProcessingOptions.Enabled` defaults to `false`
2. **Check effect registration order** — `AddPostProcessing()` must come before `AddGrayscaleEffect()` / `AddBlurEffect()`
3. **Check logs** — the pipeline logs effect initialization and errors at Info/Error levels

### Effects not visible

1. **Check `effect.Enabled`** — effects default to enabled, but verify nothing is toggling them off
2. **Check effect parameters** — `Intensity = 0` or `BlurRadius = 0` produces no visible change

### Artifacts or incorrect colors

1. **Check render target format** — mismatched formats between the pipeline and effect shaders can cause issues. Leave `RenderTargetFormat` as `null` unless you have a reason to override it

---

## Next Steps

- **[GPU Renderer](gpu-renderer.md)** — Render targets, scissor rects, blend modes
- **[Sprites](sprites.md)** — Sprite rendering
- **[Cameras](cameras.md)** — Camera follow, zoom, and shake
- **[Performance](../performance/optimization.md)** — Rendering optimization
