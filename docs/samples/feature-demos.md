---
title: Samples Overview
description: Complete working examples demonstrating Brine2D features
---

# Samples

Learn by example! The Brine2D samples demonstrate real-world usage of the engine's features. Each sample is a complete, runnable project that showcases specific functionality.

## FeatureDemos

**Location:** `samples/FeatureDemos/`  
**Difficulty:** Beginner to Advanced  
**Topics Covered:** ECS Queries, Particles, Collision, Scene Transitions, UI, Manual Control

The FeatureDemos project is an interactive showcase of Brine2D's major features. Run the project to see a **menu-driven demo selector** where you can explore each feature independently.

```mermaid
graph TD
    A["FeatureDemos Project"] --> B["MainMenuScene"]
    B --> C["Query System Demo"]
    B --> D["Particle System Demo"]
    B --> E["Collision Demo"]
    B --> F["Scene Transitions Demo"]
    B --> G["UI Components Demo"]
    B --> H["Manual Control Demo"]
    
    C --> I["Fluent Query API"]
    C --> J["Cached Queries"]
    C --> K["Complex Filters"]
    
    D --> L["GPU Particles"]
    D --> M["Emitter Systems"]
    D --> N["Performance"]
    
    E --> O["AABB Colliders"]
    E --> P["Circle Colliders"]
    E --> Q["Physics Response"]
    
    F --> R["FadeTransition"]
    F --> S["Loading Screens"]
    F --> T["Scene Chaining"]
    
    G --> U["Complete UI Library"]
    G --> V["Tooltips & Dialogs"]
    G --> W["Input Layers"]
    
    H --> X["Lifecycle Hooks"]
    H --> Y["Manual Pipelines"]
    H --> Z["Power User Features"]

    style A fill:#1e3a5f,stroke:#569cd6,stroke-width:2px,color:#fff
    style B fill:#2d5016,stroke:#4ec9b0,stroke-width:2px,color:#fff
    style C fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style D fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style E fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style F fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style G fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style H fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style I fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style J fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style K fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style L fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style M fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style N fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style O fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style P fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style Q fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style R fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style S fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style T fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style U fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style V fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style W fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style X fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style Y fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
    style Z fill:#3d3d2a,stroke:#dcdcaa,stroke-width:2px,color:#fff
```

### Demo Scenes

| Demo | Description | Key Features | Category |
|------|-------------|--------------|----------|
| **Query System** | Advanced entity queries | Fluent API, cached queries, complex filters | ECS |
| **Particle System** | GPU-accelerated particles | 10,000+ particles, emitters, performance | ECS |
| **Collision Detection** | Physics and collision | AABB/circle colliders, bounce, slide, push | Collision |
| **Scene Transitions** | Smooth scene changes | FadeTransition, loading screens, async loading | Transitions |
| **UI Components** | Complete UI showcase | All 15+ components, tooltips, dialogs, tabs | UI |
| **Manual Control** | Power user features | Opt-out of automatic execution, custom pipelines | Advanced |

---

## Running the Demos

### Prerequisites

- .NET 10 SDK
- Visual Studio 2022 or VS Code
- SDL3 (auto-installed via NuGet)

### Option 1: Run from Visual Studio

1. Open `Brine2D.sln` in Visual Studio
2. Set `FeatureDemos` as startup project
3. Press **F5** to run
4. Select a demo from the menu

### Option 2: Run from Command Line

```bash
cd samples/FeatureDemos
dotnet run
```

### Navigation

- **Use number keys (1-6)** to select a demo
- **ESC** returns to menu from any demo
- **F1/F2** toggle debug options in some demos

---

## Demo Deep Dive

### 1. Query System Demo

**What it demonstrates:**
- Fluent query API for complex entity searches
- Cached queries for performance
- Multiple filter conditions (`With`, `Without`, `Where`)
- Real-time entity statistics

**Controls:**
- **SPACE** - Spawn entities
- **C** - Clear entities
- **ESC** - Return to menu

**Key Code:**

```csharp
// Find low-health enemies near the player
var weakEnemies = _world.Query()
    .With<HealthComponent>()
    .With<TransformComponent>()
    .Without<DeadComponent>()
    .WithTag("Enemy")
    .Where(e => 
    {
        var health = e.GetComponent<HealthComponent>();
        var transform = e.GetComponent<TransformComponent>();
        var distance = Vector2.Distance(transform.Position, playerPos);
        
        return health.CurrentHealth < 50 && distance < 200f;
    })
    .Execute();

// Cached queries (no allocation!)
var movingEntities = _world.CreateCachedQuery<TransformComponent, VelocityComponent>();
foreach (var (transform, velocity) in movingEntities)
{
    transform.Position += velocity.Velocity * deltaTime;
}
```

---

### 2. Particle System Demo

**What it demonstrates:**
- GPU-accelerated particle rendering
- 10,000+ particles at 60 FPS
- Multiple emitter types
- Particle lifetime and physics
- Performance monitoring

**Controls:**
- **SPACE** - Toggle emission
- **1-3** - Change emitter type
- **ESC** - Return to menu

**Key Code:**

```csharp
// Create particle emitter
var emitter = entity.AddComponent<ParticleEmitterComponent>();
emitter.EmissionRate = 100;
emitter.Lifetime = 2f;
emitter.StartColor = Color.Red;
emitter.EndColor = new Color(255, 0, 0, 0);
emitter.StartSpeed = 100f;
emitter.SpreadAngle = MathF.PI / 4;
```

---

### 3. Collision Detection Demo

**What it demonstrates:**
- AABB (box) and circle colliders
- Collision detection with `CollisionSystem`
- Physics response: bounce, slide, push
- Dynamic vs static objects
- Trigger colliders (collectibles)
- Debug visualization

**Controls:**
- **WASD** - Move player
- **R** - Kick ball (when nearby)
- **F1** - Toggle collider visualization
- **F2** - Toggle velocity vectors
- **SPACE** - Reset scene
- **ESC** - Return to menu

**Key Code:**

```csharp
// Player slides along walls
var newPosition = _playerPosition + moveVector;
_playerCollider.Position = newPosition;

var collisions = _collisionSystem.GetCollisions(_playerCollider);
if (collisions.Any(c => _walls.Contains(c)))
{
    // Try sliding along X axis
    var slideX = _playerPosition + new Vector2(moveVector.X, 0);
    _playerCollider.Position = slideX;
    
    if (!_collisionSystem.GetCollisions(_playerCollider).Any())
    {
        _playerPosition = slideX;
    }
}

// Ball bounces with physics
_ballVelocity = CollisionResponse.Bounce(_ballVelocity, penetration, 0.7f);
```

---

### 4. Scene Transitions Demo

**What it demonstrates:**
- `FadeTransition` between scenes
- Custom loading screens with progress bars
- Async scene loading
- Scene chaining (A ? B ? C ? A)
- Transition customization (duration, color)

**Controls:**
- **ENTER** - Go to next scene
- **Number keys** - Jump to specific scene
- **ESC** - Return to menu

**Key Code:**

```csharp
// Fade transition
await _sceneManager.LoadSceneAsync<SceneB>(
    new FadeTransition(duration: 0.5f, color: Color.Black)
);

// Custom loading screen
public class CustomLoadingScreen : LoadingScene
{
    protected override void OnRender(GameTime gameTime)
    {
        _renderer.DrawText($"Loading... {Progress:P0}", 500, 300, Color.White);
        _renderer.DrawRectangleFilled(400, 350, Progress * 400, 20, Color.Green);
    }
}

await _sceneManager.LoadSceneAsync<GameScene>(
    loadingScreen: new CustomLoadingScreen(),
    transition: new FadeTransition(0.5f, Color.Black)
);
```

---

### 5. UI Components Demo

**What it demonstrates:**
- **Complete UI library** - All 15+ components
- Buttons, labels, text inputs
- Sliders, checkboxes, radio buttons
- Progress bars, dropdowns
- Tab containers, scroll views
- Dialogs with multiple buttons
- Tooltips on hover
- Input layer management

**Controls:**
- **Mouse** - Interact with all UI elements
- **TAB** - Navigate between inputs
- **ESC** - Return to menu

**Components Showcased:**

| Component | Demo Feature |
|-----------|--------------|
| `UILabel` | Title, status messages |
| `UIButton` | Click counter, actions |
| `UITextInput` | Name entry with placeholder |
| `UISlider` | Volume control (0-100) |
| `UIProgressBar` | Health bar with +/- buttons |
| `UIDropdown` | Graphics quality selector |
| `UICheckbox` | Sound/VSync toggles |
| `UIRadioButton` | Difficulty selection |
| `UITabContainer` | Settings organization |
| `UIScrollView` | 25-item scrollable list |
| `UIDialog` | Confirmation popups |
| `UITooltip` | Hover help text |
| `UIPanel` | Visual grouping |

**Key Code:**

```csharp
// Button with event
var button = new UIButton("Click Me!", pos, size);
button.OnClick += () => Logger.LogInformation("Clicked!");
_uiCanvas.Add(button);

// Slider with value display
var slider = new UISlider(pos, size)
{
    MinValue = 0f,
    MaxValue = 100f,
    Value = 75f,
    ShowValue = true,
    Tooltip = new UITooltip("Adjust volume")
};
slider.OnValueChanged += (value) => Logger.LogDebug("Volume: {Volume}", value);
_uiCanvas.Add(slider);

// Dialog with multiple buttons
var dialog = new UIDialog("Confirm", "Are you sure?", new Vector2(400, 250));
dialog.AddButton("Yes", () => dialog.Visible = false);
dialog.AddButton("No", () => dialog.Visible = false);
_uiCanvas.Add(dialog);
```

---

### 6. Manual Control Demo

**What it demonstrates:**
- Opt-out of automatic execution
- Manual pipeline control
- Manual frame management
- When and why to use manual control
- Power user scenarios (fixed timestep, conditional execution)

**Controls:**
- **ESC** - Return to menu

**Key Code:**

```csharp
public class ManualControlScene : Scene
{
    public override bool EnableLifecycleHooks => false; // Disable automatic execution
    public override bool EnableAutomaticFrameManagement => false; // Full manual control
    
    protected override void OnUpdate(GameTime gameTime)
    {
        // You control when systems run
        _updatePipeline.Execute(gameTime);
        _world.Update(gameTime);
    }
    
    protected override void OnRender(GameTime gameTime)
    {
        // You control frame management
        Renderer.ClearColor = Color.Black;
        _renderer.BeginFrame();
        
        _renderPipeline.Execute(_renderer);
        
        _renderer.EndFrame();
    }
}
```

See [Lifecycle Hooks Guide](../guides/scenes/lifecycle-hooks.md) for full documentation.

---

## Project Structure

```
FeatureDemos/
+-- Scenes/
¦   +-- MainMenuScene.cs           # Interactive demo selector
¦   +-- DemoSceneBase.cs           # Shared base class
¦   +-- ECS/
¦   ¦   +-- QueryDemoScene.cs      # Query system showcase
¦   ¦   +-- ParticleDemoScene.cs   # Particle effects
¦   +-- Collision/
¦   ¦   +-- CollisionDemoScene.cs  # Physics demo
¦   +-- Transitions/
¦   ¦   +-- TransitionDemoScene.cs # Transition showcase
¦   ¦   +-- SceneA.cs              # Chain scene A
¦   ¦   +-- SceneB.cs              # Chain scene B
¦   ¦   +-- SceneC.cs              # Chain scene C
¦   +-- UI/
¦   ¦   +-- UIDemoScene.cs         # Complete UI showcase
¦   +-- Advanced/
¦       +-- ManualControlScene.cs  # Power user demo
+-- Program.cs                      # Entry point
+-- gamesettings.json               # Configuration
+-- FeatureDemos.csproj             # Project file
```

---

## Configuration

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Brine2D": "Debug"
    }
  },
  "Rendering": {
    "WindowTitle": "Brine2D Feature Demos",
    "WindowWidth": 1280,
    "WindowHeight": 720,
    "VSync": true,
    "Backend": "GPU"
  }
}
```

---

## Dependency Injection Setup

FeatureDemos demonstrates complete service configuration:

```csharp
var builder = GameApplication.CreateBuilder(args);

// Core services
builder.Configure(options =>`n{`n    options.Window.Title = "Brine2D Feature Demos";`n    options.Window.Width = 1280;`n    options.Window.Height = 720;`n    options.Rendering.VSync = true;`n});
// ECS and systems
// Register all demo scenes
builder.AddScene<MainMenuScene>();
builder.AddScene<QueryDemoScene>();
builder.AddScene<ParticleDemoScene>();
builder.AddScene<CollisionDemoScene>();
builder.AddScene<TransitionDemoScene>();
builder.AddScene<UIDemoScene>();
builder.AddScene<ManualControlScene>();

var game = builder.Build();
await game.RunAsync<MainMenuScene>();
```

---

## Learning Path

We recommend exploring the demos in this order:

1. **Query System** - Understand ECS queries (if using ECS)
2. **Collision Detection** - Learn physics and collision response
3. **UI Components** - Master the UI framework
4. **Scene Transitions** - Build polished scene changes
5. **Particle System** - Add visual effects
6. **Manual Control** - Advanced power user techniques

---

## Using Demos as Templates

The demo code is production-ready and designed to be copied:

1. **Copy a scene class** - Use as a starting point
2. **Modify for your game** - Change colors, sizes, behaviors
3. **Extract patterns** - Query builders, UI layouts, collision response
4. **Build on top** - Extend with your own features

---

## Troubleshooting

### Menu doesn't appear?
- Check that `MainMenuScene` is registered
- Verify `game.RunAsync<MainMenuScene>()` is called

### Demo crashes on load?
- Check console for missing dependencies
- Verify all scenes are registered in DI
- Try running from Visual Studio with debugger

### Performance issues?
- Enable VSync in `gamesettings.json`
- Check particle count in Particle Demo (reduce if needed)
- Review logging level (set to `Information`)

---

## Next Steps

After exploring the demos:

- **[Guides](../guides/index.md)** - Deep dive into specific features
- **[Tutorials](../tutorials/index.md)** - Build complete games step-by-step
- **[Lifecycle Hooks](../guides/scenes/lifecycle-hooks.md)** - Advanced manual control
- **[ECS Queries](../guides/ecs/queries.md)** - Master the query system

---

Ready to explore? Clone the repository and run the demos:

```bash
git clone https://github.com/CrazyPickleStudios/Brine2D.git
cd Brine2D/samples/FeatureDemos
dotnet run
```

**Press 1-6 to explore each demo!**

Happy coding!