---
title: Installation
description: Install Brine2D and set up your development environment for .NET 10 game development
---

# Installation

Get Brine2D up and running in minutes with .NET 10 and your favorite IDE.

## Overview

Brine2D is a **single package** for .NET 10:

- **Brine2D** - Core engine, rendering, input, audio, ECS - everything you need

Optional packages:
- **Brine2D.Build** - Compile-time asset path generation (auto-generates typed `Assets` class from your assets folder)

---

## Prerequisites

### Required

- :white_check_mark: **.NET 10 SDK** - [Download here](https://dotnet.microsoft.com/download/dotnet/10.0)
- :white_check_mark: **IDE** - Visual Studio 2022+, VS Code, or Rider

### Optional

- :bulb: **Git** - For cloning samples

---

## Verify .NET 10

Check your .NET version:

```sh
dotnet --version
```

**Expected output:**

```
10.0.xxx
```

If you see `9.x` or earlier, [download .NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0).

---

## Quick Install

### Option 1: New Project (Recommended)

Create a new game from scratch:

```sh
dotnet new console -n MyGame
cd MyGame
dotnet add package Brine2D
```

**Project structure:**

```
MyGame/
+-- MyGame.csproj
+-- Program.cs
+-- assets/          (create this folder)
    +-- images/
    +-- audio/
    +-- fonts/
```

---

### Option 2: Add to Existing Project

Add Brine2D to an existing .NET 10 project:

```sh
cd YourExistingProject
dotnet add package Brine2D
```

---

### Option 3: Manual .csproj Edit

Edit your `.csproj` file directly:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Brine2D" Version="x.x.x" />
  </ItemGroup>

  <!-- Copy assets to output -->
  <ItemGroup>
    <None Update="assets\**\*">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
</Project>
```

---

## Optional: Brine2D.Build

For compile-time asset path generation:

```sh
dotnet add package Brine2D.Build
```

This auto-generates a strongly-typed `Assets` class from your `assets/` folder, giving you IntelliSense and compile-time safety for asset paths. See the [Brine2D.Build README](https://github.com/CrazyPickleStudios/Brine2D) for details.

---

## Verify Installation

After installing, create a minimal `Program.cs`:

```csharp
using Brine2D.Core;
using Brine2D.Engine;
using Brine2D.Hosting;
using Brine2D.Input;

var builder = GameApplication.CreateBuilder(args);

builder.Configure(options =>
{
    options.Window.Title = "Test Game";
    options.Window.Width = 800;
    options.Window.Height = 600;
});

builder.AddScene<TestScene>();

await using var game = builder.Build();
await game.RunAsync<TestScene>();

public class TestScene : Scene
{
    private readonly IGameContext _gameContext;

    public TestScene(IGameContext gameContext)
    {
        _gameContext = gameContext;
    }

    protected override void OnRender(GameTime gameTime)
    {
        Renderer.DrawText("Brine2D works!", 100, 100, Color.White);
    }

    protected override void OnUpdate(GameTime gameTime)
    {
        if (Input.IsKeyPressed(Key.Escape))
            _gameContext.RequestExit();
    }
}
```

Run it:

```sh
dotnet run
```

You should see a window with "Brine2D works!" displayed.

---

## Platform Setup

### Windows

Brine2D works out of the box on Windows. No additional setup needed.

### Linux

Install SDL3 development packages:

```sh
# Ubuntu/Debian
sudo apt install libsdl3-dev

# Fedora
sudo dnf install SDL3-devel
```

### macOS

Install SDL3 via Homebrew:

```sh
brew install sdl3
```

---

## Troubleshooting

### Problem: Package not found

**Symptom:**

```
error NU1102: Unable to find package Brine2D
```

**Solutions:**

1. **Check NuGet sources:**
   ```sh
   dotnet nuget list source
   ```

2. **Ensure nuget.org is enabled:**
   ```sh
   dotnet nuget add source https://api.nuget.org/v3/index.json -n nuget.org
   ```

---

### Problem: Assets not found at runtime

**Symptom:**

```
FileNotFoundException: Could not find file 'assets/player.png'
```

**Solution:**

1. **Check file location**:
   - Assets must be relative to **executable location**
   - Default: `bin/Debug/net10.0/`

2. **Copy assets to output**:

   ```xml
   <ItemGroup>
     <None Update="assets\**\*">
       <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
     </None>
   </ItemGroup>
   ```

3. **Use forward slashes** (cross-platform):
   ```csharp
   // :white_check_mark: Works on all platforms
   "assets/images/player.png"

   // :x: Windows only
   "assets\\images\\player.png"
   ```

---

## Best Practices

### DO

1. **Copy assets to output directory**
   ```xml
   <None Update="assets\**\*">
     <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
   </None>
   ```

2. **Use .gitignore for build artifacts**
   ```
   bin/
   obj/
   .vs/
   *.user
   ```

3. **Use centralized asset folders**
   ```
   assets/
   +-- images/
   +-- audio/
   +-- fonts/
   ```

### DON'T

1. **Don't hard-code absolute asset paths**
   ```csharp
   // :x: Bad
   var texture = await _assets.GetOrLoadTextureAsync("C:\\MyGame\\assets\\player.png");

   // :white_check_mark: Good
   var texture = await _assets.GetOrLoadTextureAsync("assets/images/player.png");
   ```

---

## Summary

| Package | Purpose | Required? |
|---------|---------|-----------|
| **Brine2D** | Core engine (rendering, input, audio, ECS, scenes) | :white_check_mark: Yes |
| **Brine2D.Build** | Compile-time asset path generation | :x: Optional |

**Minimum requirements:**
- .NET 10 SDK
- Brine2D package
- IDE (VS 2022+, VS Code, or Rider)

**Platform notes:**
- **Windows**: Works out of the box
- **Linux**: Requires SDL3 dev packages
- **macOS**: Requires Homebrew SDL3

---

## Next Steps

Now that Brine2D is installed, let's create your first game!

- **[Quick Start](quickstart.md)** - Create your first scene in 5 minutes
- **[Your First Game](first-game.md)** - Build a complete game
- **[Project Structure](project-structure.md)** - Organize your project
- **[Configuration](configuration.md)** - Configure your game

---

## Quick Reference

```sh
# Create new project
dotnet new console -n MyGame
cd MyGame
dotnet add package Brine2D
dotnet run
```

```xml
<!-- Minimal .csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Brine2D" Version="x.x.x" />
  </ItemGroup>

  <ItemGroup>
    <None Update="assets\**\*">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
</Project>
```

---

Ready to create your first game? Head to [Quick Start](quickstart.md)!
