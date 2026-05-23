---
title: Performance Monitoring
description: Monitor and profile your game's performance in Brine2D
---

# Performance Monitoring

Learn how to use Brine2D's built-in performance overlay and profiling tools to identify bottlenecks and optimize your game.

## Overview

Brine2D includes a comprehensive performance monitoring system that provides real-time metrics without impacting game performance. The overlay displays FPS, frame time, memory usage, rendering statistics, and more.

```mermaid
graph LR
    A[Game Loop] --> B[PerformanceMonitor]
    B --> C[FPS Tracking]
    B --> D[Frame Time History]
    B --> E[Memory Stats]
    B --> F[Rendering Stats]
    C --> G[PerformanceOverlay]
    D --> G
    E --> G
    F --> G
    G --> H[On-Screen Display]
```

---

## Quick Start

### Enable Performance Monitoring

Add performance monitoring to your game builder:

```csharp
using Brine2D.Hosting;
using Brine2D.Rendering.Performance;

var builder = GameApplication.CreateBuilder(args);

// Add performance monitoring with default settings
builder.Services.AddPerformanceMonitoring(options =>
{
    options.EnableOverlay = true;
    options.ShowFPS = true;
    options.ShowFrameTime = true;
    options.ShowMemory = true;
});

var game = builder.Build();
await game.RunAsync<GameScene>();
```

That's it! The performance overlay will now appear in your game.

---

## Keyboard Shortcuts

Control the performance overlay with these hotkeys:

| Hotkey | Action |
|--------|--------|
| `F1` | Toggle overlay visibility (on/off) |
| `F3` | Toggle detailed stats (includes frame time graph and memory) |

**Tip:** Try the **Performance Benchmark** demo to see the overlay in action with 10,000+ sprites!

```bash
cd samples/FeatureDemos
dotnet run
# Select "Performance Benchmark" from menu
```

---

## Performance Metrics

### FPS Counter

The FPS counter tracks frames per second with historical data:

**Displayed Metrics:**
- **Current FPS** - Real-time frame rate
- **Min FPS** - Lowest FPS recorded (since startup)
- **Max FPS** - Highest FPS recorded
- **Average FPS** - Rolling average (last 60 frames)

**Color Coding:**
- ? **Green** - 60+ FPS (excellent)
- ?? **Yellow** - 30-59 FPS (acceptable)
- ?? **Red** - Below 30 FPS (poor)

```csharp
// Access FPS metrics programmatically
var monitor = serviceProvider.GetRequiredService<PerformanceMonitor>();

var currentFPS = monitor.CurrentFPS;
var minFPS = monitor.MinFPS;
var maxFPS = monitor.MaxFPS;
var avgFPS = monitor.AverageFPS;

Logger.LogInformation("FPS: {Current:F1} (Min: {Min:F0}, Max: {Max:F0}, Avg: {Avg:F1})",
    currentFPS, minFPS, maxFPS, avgFPS);
```

---

### Frame Time

Frame time measures how long each frame takes to render (in milliseconds):

**Key Metrics:**
- **Current Frame Time** - Time for the last frame
- **Frame Time Graph** - Visual history of last 60 frames
- **Target Line** - 16.67ms line (60 FPS target)

**Interpreting Frame Time:**
- **< 16.67ms** - Running at 60+ FPS ?
- **16.67-33.33ms** - Running at 30-60 FPS ??
- **> 33.33ms** - Below 30 FPS ?

```csharp
// Access frame time metrics
var frameTime = monitor.CurrentFrameTime;
var minFrameTime = monitor.MinFrameTime;
var maxFrameTime = monitor.MaxFrameTime;

Logger.LogDebug("Frame Time: {FrameTime:F2}ms", frameTime);
```

**Frame Time Graph:**

The graph shows a rolling 60-frame history, with spikes indicating frame drops. Green bars indicate frames under the 60 FPS target (16.67ms), while red bars show slower frames.

---

### Memory Statistics

Track managed memory usage and garbage collection:

**Displayed Metrics:**
- **Total Memory (MB)** - Current managed heap size
- **GC Gen 0/1/2** - Collection counts per generation

**Understanding GC Generations:**
- **Gen 0** - Short-lived objects (frequent, cheap)
- **Gen 1** - Medium-lived objects (less frequent)
- **Gen 2** - Long-lived objects (rare, expensive!)

```csharp
// Access memory metrics
var memoryMB = monitor.TotalMemoryMB;
var gen0 = monitor.Gen0Collections;
var gen1 = monitor.Gen1Collections;
var gen2 = monitor.Gen2Collections;

Logger.LogInformation("Memory: {Memory:F2} MB | GC: {Gen0}/{Gen1}/{Gen2}",
    memoryMB, gen0, gen1, gen2);
```

**Warning:** Frequent Gen 2 collections indicate memory pressure. Consider using object pooling (see [Optimization Guide](optimization.md)).

---

### Rendering Statistics

Monitor sprite rendering performance:

**Displayed Metrics:**
- **Entity Count** - Total entities in the world
- **Sprite Count** - Sprites rendered this frame
- **Culled Sprites** - Off-screen sprites skipped
- **Draw Calls** - Number of render batches
- **Batch Efficiency** - Average sprites per batch

```csharp
// Update rendering stats each frame
monitor.UpdateRenderStats(
    drawCalls: 5,
    entityCount: 1000,
    spriteCount: 850,
    culledSprites: 150,
    batchCount: 5
);

// Access rendering stats
var drawCalls = monitor.DrawCalls;
var spriteCount = monitor.SpriteCount;
var batchEfficiency = monitor.BatchEfficiency; // sprites per batch

Logger.LogDebug("Rendered {Sprites} sprites in {Calls} batches ({Efficiency:F1}x efficiency)",
    spriteCount, drawCalls, batchEfficiency);
```

**Batch Efficiency:**
- **1x** - No batching (poor) ??
- **5-10x** - Moderate batching (acceptable) ??
- **10+x** - Excellent batching ?

---

## Configuration Options

### Basic Configuration

```csharp
builder.Services.AddPerformanceMonitoring(options =>
{
    // Toggle overlay visibility
    options.EnableOverlay = true;
    
    // Choose which stats to display
    options.ShowFPS = true;
    options.ShowFrameTime = true;
    options.ShowMemory = true;
});
```

---

### Advanced Configuration

```csharp
// Access overlay at runtime for customization
public class GameScene : Scene
{
    private readonly PerformanceOverlay _perfOverlay;
    
    public GameScene(
        PerformanceOverlay perfOverlay,
        ILogger<GameScene> logger)
    {
        _perfOverlay = perfOverlay;
        
        // Change overlay position
        _perfOverlay.Position = OverlayPosition.TopLeft;
        
        // Adjust update frequency (default: 0.25 seconds = 4 updates/sec)
        _perfOverlay.DisplayUpdateInterval = 0.5; // Update twice per second
        
        // Start with detailed stats visible
        _perfOverlay.ShowDetailedStats = true;
    }
}
```

**Overlay Positions:**
- `OverlayPosition.TopRight` (default)
- `OverlayPosition.TopLeft`
- `OverlayPosition.BottomLeft`
- `OverlayPosition.BottomRight`

---

## Programmatic Access

### Manual Frame Timing

Track custom operations:

```csharp
public class GameScene : Scene
{
    private readonly PerformanceMonitor _monitor;
    
    public GameScene(
        PerformanceMonitor monitor,
        ILogger<GameScene> logger)
    {
        _monitor = monitor;
    }
    
    protected override void OnUpdate(GameTime gameTime)
    {
        // Monitor tracks frames automatically, but you can reset stats
        if (_input.IsKeyPressed(Key.R))
        {
            _monitor.Reset(); // Clear min/max/average stats
            Logger.LogInformation("Performance stats reset!");
        }
    }
}
```

---

### Custom Profiling Regions

Profile specific code sections:

```csharp
using System.Diagnostics;

public class AISystem : IUpdateSystem
{
    private readonly Stopwatch _stopwatch = new();
    
    public string Name => "AISystem";
    public int UpdateOrder => 20;
    
    public void Update(GameTime gameTime)
    {
        _stopwatch.Restart();
        
        // Your AI logic here
        ProcessEnemyAI();
        
        _stopwatch.Stop();
        
        if (_stopwatch.ElapsedMilliseconds > 5)
        {
            Logger.LogWarning("AI system took {Ms}ms (> 5ms budget!)",
                _stopwatch.ElapsedMilliseconds);
        }
    }
}
```

---

## Performance Targets

### 60 FPS Target

Target specifications for smooth gameplay:

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| **FPS** | 60+ | 30-59 | < 30 |
| **Frame Time** | < 16.67ms | 16.67-33.33ms | > 33.33ms |
| **Gen 2 GC** | 0/sec | < 1/sec | > 1/sec |
| **Batch Efficiency** | 10+x | 5-10x | < 5x |

---

### Platform-Specific Targets

Adjust expectations based on platform:

```csharp
using System.Runtime.InteropServices;

// Desktop: Target 60 FPS
// Mobile: Target 30 FPS (optional)
// Web: Target 30-60 FPS depending on device

var targetFPS = RuntimeInformation.IsOSPlatform(OSPlatform.Windows) ? 60 : 30;
Logger.LogInformation("Target FPS: {Target}", targetFPS);
```

---

## Troubleshooting

### Problem: High Frame Time (Low FPS)

**Symptom:** FPS consistently below 60, frame time spikes above 16.67ms.

**Common Causes:**
1. **Too many entities** - Reduce entity count or use culling
2. **Expensive queries** - Cache queries, avoid complex predicates
3. **Allocations** - Use object pooling (see [Optimization Guide](optimization.md))
4. **Draw calls** - Enable sprite batching

**Solutions:**

```csharp
// 1. Enable frustum culling (automatic with SpriteRenderingSystem)
var spriteSystem = world.GetSystem<SpriteRenderingSystem>();
var (rendered, culled) = spriteSystem.GetCullingStats();
Logger.LogInformation("Rendered: {Rendered}, Culled: {Culled}", rendered, culled);

// 2. Use cached queries
var enemies = world.CreateCachedQuery<EnemyComponent, TransformComponent>();

// 3. Check batch efficiency
var (spriteCount, drawCalls) = spriteSystem.GetBatchStats();
var efficiency = (float)spriteCount / drawCalls;
if (efficiency < 5f)
{
    Logger.LogWarning("Low batch efficiency: {Efficiency:F1}x", efficiency);
}
```

---

### Problem: Frequent GC Collections

**Symptom:** Gen 2 collections increasing rapidly, frame time spikes during collections.

**Common Causes:**
1. **LINQ in hot paths** - Use `for` loops instead
2. **String concatenation** - Use `StringBuilder` or string interpolation
3. **New allocations** - Use object pooling

**Solutions:**

```csharp
// ? Bad - creates garbage
var results = world.Query()
    .With<EnemyComponent>()
    .Execute()
    .ToList(); // Allocation!

foreach (var enemy in results)
{
    var message = "Enemy: " + enemy.Name; // Allocation!
}

// ? Good - zero allocation
var enemies = world.CreateCachedQuery<EnemyComponent>();

foreach (var enemy in enemies.Execute())
{
    Logger.LogDebug("Enemy: {Name}", enemy.Name); // Interpolation is optimized
}
```

See [Performance Optimization](optimization.md) for detailed guidance.

---

### Problem: Low Batch Efficiency

**Symptom:** Batch efficiency < 5x, high draw call count.

**Common Causes:**
1. **Many different textures** - Use texture atlases
2. **Frequent layer changes** - Group sprites by layer

**Solutions:**

```csharp
// Group sprites by texture and layer
var sprites = world.Query()
    .With<SpriteComponent>()
    .OrderBy(e => e.GetComponent<SpriteComponent>().Layer)
    .ThenBy(e => e.GetComponent<SpriteComponent>().TexturePath)
    .Execute();
```

---

## Best Practices

### DO

1. **Enable monitoring during development**
   ```csharp
   #if DEBUG
   builder.Services.AddPerformanceMonitoring(options =>
   {
       options.EnableOverlay = true;
       options.ShowDetailedStats = true;
   });
   #endif
   ```

2. **Profile before optimizing**
   ```csharp
   // ? Good - measure first, optimize second
   // Don't guess where bottlenecks are!
   ```

3. **Set performance budgets**
   ```csharp
   // ? Good - define acceptable performance
   const float MAX_FRAME_TIME = 16.67f; // 60 FPS
   
   if (monitor.CurrentFrameTime > MAX_FRAME_TIME)
   {
       Logger.LogWarning("Frame time exceeded budget: {Time:F2}ms",
           monitor.CurrentFrameTime);
   }
   ```

4. **Monitor Gen 2 collections**
   ```csharp
   // ? Good - track expensive GC events
   var gen2Count = monitor.Gen2Collections;
   if (gen2Count > _lastGen2Count + 1)
   {
       Logger.LogWarning("Gen 2 GC occurred! ({Count} total)", gen2Count);
   }
   _lastGen2Count = gen2Count;
   ```

5. **Use profiling in context**
   ```csharp
   // ? Good - profile specific scenarios
   // Profile during heavy action scenes, not just menus!
   ```

### DON'T

1. **Don't optimize prematurely**
   ```csharp
   // ? Bad - optimizing without measuring
   // Profile first to identify actual bottlenecks
   ```

2. **Don't leave overlay enabled in production**
   ```csharp
   // ? Bad - always on
   options.EnableOverlay = true;
   
   // ? Good - only in debug builds
   #if !RELEASE
   options.EnableOverlay = true;
   #endif
   ```

3. **Don't ignore Gen 2 collections**
   ```csharp
   // ? Bad - ignoring memory pressure
   // Frequent Gen 2 GCs indicate serious memory problems
   ```

4. **Don't profile with overlay rendering**
   ```csharp
   // ? Bad - overlay adds overhead
   // Disable overlay when benchmarking actual performance
   ```

5. **Don't trust single-frame measurements**
   ```csharp
   // ? Bad - one frame isn't representative
   var fps = monitor.CurrentFPS;
   
   // ? Good - use averages
   var avgFPS = monitor.AverageFPS;
   ```

---

## Performance Monitoring Checklist

Use this checklist when profiling your game:

**Before Optimizing:**
- [ ] Enable performance overlay (`F1`)
- [ ] Enable detailed stats (`F3`)
- [ ] Note current FPS and frame time
- [ ] Check Gen 2 collection frequency
- [ ] Verify batch efficiency

**During Testing:**
- [ ] Test worst-case scenarios (max entities)
- [ ] Monitor frame time graph for spikes
- [ ] Watch for GC collection pauses
- [ ] Check draw call count
- [ ] Verify culling is working

**After Optimizing:**
- [ ] Compare before/after FPS
- [ ] Verify frame time reduced
- [ ] Check Gen 2 collections decreased
- [ ] Confirm batch efficiency improved
- [ ] Test on target hardware

---

## Summary

**Performance overlay:**

| Hotkey | Action |
|--------|--------|
| `F1` | Toggle overlay on/off |
| `F3` | Toggle detailed stats |

**Key metrics:**

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **FPS** | 60+ | 30-59 | < 30 |
| **Frame Time** | < 16.67ms | 16.67-33.33ms | > 33.33ms |
| **Gen 2 GC** | 0/sec | < 1/sec | > 1/sec |
| **Batch Efficiency** | 10+x | 5-10x | < 5x |

**Common issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| **Low FPS** | Too many entities | Culling, pooling |
| **Frame spikes** | GC collections | Reduce allocations |
| **High draw calls** | Many textures | Texture atlases |
| **Memory growth** | Memory leaks | Use object pools |

---

## Next Steps

- **[Optimization Guide](optimization.md)** - Learn zero-allocation patterns
- **[Sprite Batching](../rendering/sprites.md)** - Minimize draw calls
- **[Object Pooling](optimization.md#object-pooling)** - Reduce allocations
- **[GPU Renderer](../rendering/gpu-renderer.md)** - High-performance rendering

---

## Quick Reference

```csharp
// Enable performance monitoring
builder.Services.AddPerformanceMonitoring(options =>
{
    options.EnableOverlay = true;
    options.ShowFPS = true;
    options.ShowFrameTime = true;
    options.ShowMemory = true;
});

// Access metrics programmatically
public class GameScene : Scene
{
    private readonly PerformanceMonitor _monitor;
    
    public GameScene(PerformanceMonitor monitor, ...) : base(...)
    {
        _monitor = monitor;
    }
    
    protected override void OnUpdate(GameTime gameTime)
    {
        // Get current metrics
        var fps = _monitor.CurrentFPS;
        var frameTime = _monitor.CurrentFrameTime;
        var memoryMB = _monitor.TotalMemoryMB;
        
        // Check performance budget
        if (frameTime > 16.67f)
        {
            Logger.LogWarning("Frame time exceeded: {Time:F2}ms", frameTime);
        }
        
        // Monitor GC
        var gen2 = _monitor.Gen2Collections;
        if (gen2 > _lastGen2Count)
        {
            Logger.LogWarning("Gen 2 GC occurred!");
            _lastGen2Count = gen2;
        }
        
        // Reset stats
        if (_input.IsKeyPressed(Key.R))
        {
            _monitor.Reset();
        }
    }
}

// Update rendering stats
monitor.UpdateRenderStats(
    drawCalls: drawCallCount,
    entityCount: totalEntities,
    spriteCount: renderedSprites,
    culledSprites: culledCount,
    batchCount: batchCount
);

// Custom profiling
var sw = Stopwatch.StartNew();
ExpensiveOperation();
sw.Stop();

if (sw.ElapsedMilliseconds > 5)
{
    Logger.LogWarning("Operation took {Ms}ms", sw.ElapsedMilliseconds);
}
```

---

**Remember:** Measure first, optimize second! ??