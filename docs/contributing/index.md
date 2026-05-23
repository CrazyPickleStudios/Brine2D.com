---
title: Contributing
description: Help make Brine2D better - contribute code, documentation, or feedback
---

# Contributing to Brine2D

Brine2D is an open-source project and welcomes contributions from the community. Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated!

---

## Quick Links

- ðŸ› [Report a Bug](https://github.com/CrazyPickleStudios/Brine2D/issues/new?template=bug_report.md)
- ðŸ’¡ [Request a Feature](https://github.com/CrazyPickleStudios/Brine2D/issues/new?template=feature_request.md)
- ðŸ’¬ [Ask Questions](https://github.com/CrazyPickleStudios/Brine2D/discussions)
- ðŸ“ [Submit Documentation](https://github.com/CrazyPickleStudios/Brine2D-Documentation)
- ðŸ¤ [Pull Requests](https://github.com/CrazyPickleStudios/Brine2D/pulls)

---

## Ways to Contribute

### 1. Report Bugs ðŸ›

**Found a bug?** Help us fix it!

**Before reporting:**
- âœ… Search [existing issues](https://github.com/CrazyPickleStudios/Brine2D/issues)
- âœ… Check if bug exists in latest version
- âœ… Try to reproduce consistently

**Include in your report:**
- Brine2D version (v0.9.0-beta)
- .NET version (`dotnet --version`)
- Operating system (Windows 11, macOS 14, Ubuntu 22.04)
- Minimal reproduction code
- Expected vs actual behavior
- Screenshots/logs if relevant

**Template:**
```
**Brine2D Version:** 0.9.0-beta
**OS:** Windows 11
**Reproduction:**
```csharp
var builder = GameApplication.CreateBuilder();
// Minimal code that reproduces the bug
```

**Expected:** Window opens at 800x600
**Actual:** Window opens at 1024x768
```

[:octicons-arrow-right-24: Report a Bug](https://github.com/CrazyPickleStudios/Brine2D/issues/new?template=bug_report.md)

---

### 2. Request Features ðŸ’¡

**Have an idea?** We'd love to hear it!

**Good feature requests:**
- âœ… Solve a real problem
- âœ… Include use case examples
- âœ… Consider alternatives
- âœ… Respect project scope

**Template:**
```
**Feature:** Add sprite animation blending

**Use Case:** Smooth transitions between walk/run animations

**Proposed API:**
```csharp
animator.BlendTo("Run", duration: 0.3f);
```

**Alternatives Considered:**
- Manual frame interpolation (too complex)
- Instant switching (not smooth enough)
```

[:octicons-arrow-right-24: Request a Feature](https://github.com/CrazyPickleStudios/Brine2D/issues/new?template=feature_request.md)

---

### 3. Improve Documentation ðŸ“

**Documentation is code!** Help make it better.

**What needs documentation:**
- Missing API docs (XML comments)
- Tutorial improvements
- Code examples
- Troubleshooting guides
- Best practices

**How to contribute docs:**

```bash
# Clone documentation repo
git clone https://github.com/CrazyPickleStudios/Brine2D-Documentation
cd Brine2D-Documentation

# Edit markdown files
code docs/

# Preview locally
mkdocs serve

# Submit PR
git checkout -b improve-collision-docs
git commit -am "Add collision detection examples"
git push origin improve-collision-docs
```

[:octicons-arrow-right-24: Documentation Repo](https://github.com/CrazyPickleStudios/Brine2D-Documentation)

---

### 4. Write Code ðŸ’»

**Ready to code?** Here's how to get started.

#### First Time Setup

```bash
# Fork on GitHub (click Fork button)

# Clone your fork
git clone https://github.com/YOUR_USERNAME/Brine2D
cd Brine2D

# Add upstream remote
git remote add upstream https://github.com/CrazyPickleStudios/Brine2D

# Create branch
git checkout -b feature/my-awesome-feature
```

#### Building the Project

```bash
# Restore dependencies
dotnet restore

# Build
dotnet build

# Run tests
dotnet test

# Run sample
cd samples/BasicGame
dotnet run
```

#### Making Changes

```bash
# Make your changes
code src/Brine2D/

# Build and test
dotnet build
dotnet test

# Commit with clear message
git commit -am "Add spatial audio distance falloff"

# Push to your fork
git push origin feature/my-awesome-feature
```

#### Submit Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the PR template
4. Wait for review

---

## Code Guidelines

### C# Style

**Follow .NET conventions:**

```csharp
// âœ… Good
public class AudioService
{
    private readonly IAudioDevice _device;
    
    public float MasterVolume { get; set; }
    
    public async Task<SoundEffect> LoadSoundAsync(string path, CancellationToken ct)
    {
        // Implementation
    }
}

// âŒ Bad
public class audioservice  // lowercase class name
{
    private IAudioDevice device;  // missing underscore
    
    public float masterVolume;  // field instead of property
    
    public SoundEffect LoadSound(string path)  // not async
    {
        // Implementation
    }
}
```

**Key rules:**
- PascalCase for public members
- camelCase with `_` prefix for private fields
- Use `async/await` for I/O operations
- Add XML documentation comments
- Keep methods under 50 lines

---

### Project Structure

```
Brine2D/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ Brine2D/           # Core framework
â”‚   â””â”€â”€ Brine2D.SDL/       # SDL3 backend (being merged)
â”œâ”€â”€ tests/
â”‚   â””â”€â”€ Brine2D.Tests/     # Unit tests
â”œâ”€â”€ samples/
â”‚   â””â”€â”€ BasicGame/         # Sample projects
â””â”€â”€ docs/                  # Inline documentation
```

**Where to add code:**
- Core features â†’ `src/Brine2D/`
- SDL3 implementations â†’ `src/Brine2D.SDL/` (temporary)
- Tests â†’ `tests/Brine2D.Tests/`
- Samples â†’ `samples/NewSample/`

---

### Testing

**All new features need tests:**

```csharp
using Xunit;
using Brine2D.Audio;

public class AudioServiceTests
{
    [Fact]
    public void SetMasterVolume_ClampsBetweenZeroAndOne()
    {
        var audio = new AudioService();
        
        audio.MasterVolume = 1.5f;
        
        Assert.Equal(1.0f, audio.MasterVolume);
    }
    
    [Fact]
    public async Task LoadSoundAsync_ReturnsValidSound()
    {
        var audio = new AudioService();
        
        var sound = await audio.LoadSoundAsync("test.wav", CancellationToken.None);
        
        Assert.NotNull(sound);
        Assert.True(sound.IsLoaded);
    }
}
```

**Run tests:**
```bash
dotnet test
```

---

### Documentation Comments

**All public APIs need XML docs:**

```csharp
/// <summary>
/// Plays a sound effect with optional volume and panning.
/// </summary>
/// <param name="sound">The sound to play.</param>
/// <param name="volume">Volume override (0.0 to 1.0), or null to use default.</param>
/// <param name="pan">Stereo panning (-1.0 = left, 0 = center, 1.0 = right).</param>
/// <example>
/// <code>
/// var jumpSound = await audio.LoadSoundAsync("jump.wav");
/// audio.PlaySound(jumpSound, volume: 0.8f);
/// </code>
/// </example>
public void PlaySound(SoundEffect sound, float? volume = null, float pan = 0f)
{
    // Implementation
}
```

**Include:**
- `<summary>` - Brief description
- `<param>` - Parameter explanations
- `<returns>` - Return value description (if any)
- `<example>` - Code example (for complex APIs)

---

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/descriptive-name
```

**Branch naming:**
- `feature/spatial-audio` - New feature
- `fix/collision-bug` - Bug fix
- `docs/improve-quickstart` - Documentation
- `perf/optimize-rendering` - Performance

---

### 2. Make Changes

**Best practices:**
- âœ… Small, focused PRs (easier to review)
- âœ… One logical change per commit
- âœ… Clear commit messages
- âœ… Add tests for new code
- âœ… Update documentation

**Commit messages:**
```bash
# âœ… Good
git commit -m "Add spatial audio distance attenuation"
git commit -m "Fix collision detection for rotated rectangles"

# âŒ Bad
git commit -m "stuff"
git commit -m "WIP"
git commit -m "asdf"
```

---

### 3. Sync with Upstream

```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch
git rebase upstream/main

# Force push (if already pushed)
git push --force-with-lease origin feature/my-feature
```

---

### 4. Submit PR

**PR Template:**
```
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Unit tests added/updated
- [ ] Manually tested on Windows/macOS/Linux
- [ ] Sample project works

## Breaking Changes
List any breaking changes (if applicable)

## Related Issues
Closes #123
Related to #456
```

---

### 5. Code Review

**Expect feedback!** We review all PRs for:
- Code quality
- Test coverage
- Documentation
- Performance
- API design

**Respond to feedback:**
```bash
# Make requested changes
code src/

# Commit changes
git commit -am "Address review feedback"

# Push update
git push origin feature/my-feature
```

**PR automatically updates!**

---

## Development Setup

### Prerequisites

```bash
# .NET 10 SDK
dotnet --version  # Should be 10.0.x

# Git
git --version

# IDE (pick one)
# - Visual Studio 2022 (recommended)
# - JetBrains Rider
# - Visual Studio Code
```

---

### IDE Setup

#### Visual Studio 2022

```
1. Open Brine2D.sln
2. Set Brine2D as startup project
3. Install extensions:
   - CodeMaid (code cleanup)
   - Roslynator (code analysis)
4. Enable Editor Guidelines (Tools > Options)
```

#### Rider

```
1. Open Brine2D.sln
2. File > Settings > Editor > Code Style > C#
3. Import .editorconfig
4. Enable code inspections
```

#### VS Code

```
1. Install extensions:
   - C# Dev Kit
   - .NET Core Test Explorer
2. Open workspace: Brine2D.code-workspace
3. Press F5 to debug
```

---

### Debug Build

```bash
# Build in Debug mode
dotnet build -c Debug

# Run with debugger attached
dotnet run --project samples/BasicGame -c Debug

# Or use IDE debugger (F5)
```

---

### Release Build

```bash
# Build optimized
dotnet build -c Release

# Run release build
dotnet run --project samples/BasicGame -c Release
```

---

## Contribution Checklist

**Before submitting PR:**

- [ ] Code compiles without warnings
- [ ] All tests pass (`dotnet test`)
- [ ] Added tests for new features
- [ ] Updated XML documentation comments
- [ ] Updated markdown docs (if needed)
- [ ] Ran code cleanup (CodeMaid/Rider)
- [ ] Follows C# conventions
- [ ] No merge conflicts with main
- [ ] PR description filled out
- [ ] Linked related issues

---

## Community Guidelines

### Be Respectful

- âœ… Constructive feedback
- âœ… Patient with newcomers
- âœ… Assume good intentions
- âŒ Personal attacks
- âŒ Harassment
- âŒ Discrimination

---

### Stay On Topic

**GitHub Issues:** Bug reports and feature requests only

**GitHub Discussions:** Questions, ideas, show & tell

**Discord:** Real-time chat (coming soon)

---

### Search First

Before posting:
1. Search existing issues
2. Read documentation
3. Check troubleshooting guides

Save everyone's time!

---

## Recognition

**Contributors are credited:**
- ðŸŽ–ï¸ Listed in CONTRIBUTORS.md
- ðŸŽ–ï¸ Mentioned in release notes
- ðŸŽ–ï¸ GitHub contributions graph

**Top contributors may receive:**
- Collaborator access
- Input on roadmap decisions
- Swag (coming soon!)

---

## Questions?

**Need help contributing?**

- ðŸ’¬ [GitHub Discussions](https://github.com/CrazyPickleStudios/Brine2D/discussions)
- ðŸ“§ Email: contribute@brine2d.dev (coming soon)
- ðŸ¦ Twitter: [@Brine2D](https://twitter.com/Brine2D) (coming soon)

**We're here to help!** Don't be shy - even small contributions matter.

---

## License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

See [LICENSE](https://github.com/CrazyPickleStudios/Brine2D/blob/main/LICENSE) for details.

---

**Thank you for making Brine2D better!** ðŸŽ®âœ¨