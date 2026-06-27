---
title: Custom UI
description: Implement your own UI components in Brine2D
---

# Custom UI

Build custom UI elements by implementing `IUIComponent`: the same interface used by every built-in component.

---

## IUIComponent

Every UI component must implement `IUIComponent`:

```csharp
public interface IUIComponent
{
    string?   Name     { get; }
    Vector2   Position { get; set; }
    Vector2   Size     { get; set; }
    bool      Visible  { get; set; }
    bool      Enabled  { get; set; }
    int       TabIndex { get; set; }
    int       ZOrder   { get; set; }
    UITooltip? Tooltip { get; set; }

    void Update(float deltaTime);
    void Render(IRenderer renderer);
    bool Contains(Vector2 screenPosition);
}
```

| Member | Purpose |
|--------|---------|
| `Update(deltaTime)` | Called each frame. Advance animations, timers, or internal state. |
| `Render(renderer)` | Called each frame. Draw the component using the renderer. |
| `Contains(pos)` | Returns `true` if `pos` is inside this component's hit area. |

---

## Minimal Example

A colored rectangle that fires a click event:

```csharp
using Brine2D.Core;
using Brine2D.Rendering;
using Brine2D.UI;
using System.Numerics;

public class ColorBox : IUIComponent
{
    public string?    Name     { get; set; }
    public Vector2    Position { get; set; }
    public Vector2    Size     { get; set; }
    public bool       Visible  { get; set; } = true;
    public bool       Enabled  { get; set; } = true;
    public int        TabIndex { get; set; } = int.MaxValue;
    public int        ZOrder   { get; set; } = 0;
    public UITooltip? Tooltip  { get; set; }

    public Color Color { get; set; } = Color.White;

    public event Action? OnClick;

    public ColorBox(Vector2 position, Vector2 size)
    {
        Position = position;
        Size     = size;
    }

    public void Update(float deltaTime) { }

    public void Render(IRenderer renderer)
    {
        if (!Visible) return;
        renderer.DrawRectangleFilled(Position.X, Position.Y, Size.X, Size.Y, Color);
    }

    public bool Contains(Vector2 pos)
        => pos.X >= Position.X && pos.X <= Position.X + Size.X
        && pos.Y >= Position.Y && pos.Y <= Position.Y + Size.Y;

    // Called by UICanvas when a click is confirmed inside Contains()
    internal void Click()
    {
        if (Enabled) OnClick?.Invoke();
    }
}
```

Add it to a canvas:

```csharp
var box = new ColorBox(new Vector2(100, 100), new Vector2(80, 80))
{
    Color = new Color(100, 150, 255)
};

_canvas.Add(box);
```

!!! note
    `UICanvas` handles general input routing (Update / Render loop, tooltip display, ZOrder sorting, and anchor resolution). For clicks and other interaction events, the canvas checks `Contains` and calls internal methods on known built-in types. If you need the canvas to route clicks to a custom component, the simplest approach is to check `Input.IsMouseButtonPressed` inside your own `Update`.

---

## Adding Anchor Support

Implement `IAnchoredUIComponent` to let the canvas position your component relative to a screen anchor. This is the same interface all built-in components use.

```csharp
public class AnchoredColorBox : IUIComponent, IAnchoredUIComponent
{
    // IUIComponent members ...
    public string?    Name     { get; set; }
    public Vector2    Position { get; set; }
    public Vector2    Size     { get; set; }
    public bool       Visible  { get; set; } = true;
    public bool       Enabled  { get; set; } = true;
    public int        TabIndex { get; set; } = int.MaxValue;
    public int        ZOrder   { get; set; } = 0;
    public UITooltip? Tooltip  { get; set; }

    // IAnchoredUIComponent members
    public UIAnchor Anchor       { get; set; } = UIAnchor.TopLeft;
    public Vector2  AnchorOffset { get; set; }

    public Color Color { get; set; } = Color.White;

    public AnchoredColorBox(Vector2 size)
    {
        Size = size;
    }

    public void Update(float deltaTime) { }

    public void Render(IRenderer renderer)
    {
        if (!Visible) return;
        renderer.DrawRectangleFilled(Position.X, Position.Y, Size.X, Size.Y, Color);
    }

    public bool Contains(Vector2 pos)
        => pos.X >= Position.X && pos.X <= Position.X + Size.X
        && pos.Y >= Position.Y && pos.Y <= Position.Y + Size.Y;
}
```

`UICanvas` resolves the anchor automatically before calling `Render`, so `Position` in your `Render` method already holds the resolved screen coordinate: no extra work needed.

```csharp
var indicator = new AnchoredColorBox(new Vector2(20, 20))
{
    Anchor       = UIAnchor.BottomRight,
    AnchorOffset = new Vector2(-30, -30),
    Color        = Color.Red
};

_canvas.Add(indicator);
```

---

## Rendering Primitives

`IRenderer` provides the drawing methods your component will use:

```csharp
// Filled and outlined rectangles
renderer.DrawRectangleFilled(x, y, w, h, color);
renderer.DrawRectangleOutline(x, y, w, h, color, thickness);

// Lines and circles
renderer.DrawLine(x1, y1, x2, y2, color, thickness);
renderer.DrawCircleFilled(cx, cy, radius, color);
renderer.DrawCircleOutline(cx, cy, radius, color, thickness);

// Text
renderer.DrawText("Hello", x, y);
renderer.DrawText("Hello", x, y, new TextRenderOptions { Color = Color.White, Font = myFont });
var size = renderer.MeasureText("Hello");

// Textures and nine-slice
renderer.DrawTexture(texture, x, y, w, h);
renderer.DrawNineSlice(texture, new Rectangle(x, y, w, h), border, tint);
```

---

## Clipping

Use `PushScissorRect` / `PopScissorRect` to restrict rendering to a region. This is how `UIScrollView` and `UIPanel` clip their children:

```csharp
public void Render(IRenderer renderer)
{
    if (!Visible) return;

    renderer.DrawRectangleFilled(Position.X, Position.Y, Size.X, Size.Y, BackgroundColor);

    var clip = new Rectangle(Position.X, Position.Y, Size.X, Size.Y);
    renderer.PushScissorRect(clip);

    // Anything rendered here is clipped to `clip`
    foreach (var child in _children)
        child.Render(renderer);

    renderer.PopScissorRect();
}
```

---

## Composite Components

Custom components can contain other `IUIComponent` instances. Manage their `Update` and `Render` calls manually, and offset their positions relative to your own:

```csharp
public class LabeledSlider : IUIComponent, IAnchoredUIComponent
{
    public string?    Name     { get; set; }
    public Vector2    Position { get; set; }
    public Vector2    Size     { get; set; }
    public bool       Visible  { get; set; } = true;
    public bool       Enabled  { get; set; } = true;
    public int        TabIndex { get; set; } = int.MaxValue;
    public int        ZOrder   { get; set; } = 0;
    public UITooltip? Tooltip  { get; set; }
    public UIAnchor   Anchor       { get; set; } = UIAnchor.TopLeft;
    public Vector2    AnchorOffset { get; set; }

    private readonly UILabel  _label;
    private readonly UISlider _slider;

    public float Value => _slider.Value;
    public event Action<float>? OnValueChanged;

    public LabeledSlider(string labelText, Vector2 position, Vector2 sliderSize)
    {
        Position = position;
        Size     = new Vector2(sliderSize.X, sliderSize.Y + 20f);

        _label  = new UILabel(labelText, Vector2.Zero);
        _slider = new UISlider(new Vector2(0, 20), sliderSize);
        _slider.OnValueChanged += v => OnValueChanged?.Invoke(v);
    }

    public void Update(float deltaTime)
    {
        _label.Update(deltaTime);
        _slider.Update(deltaTime);
    }

    public void Render(IRenderer renderer)
    {
        if (!Visible) return;

        _label.Position  = Position;
        _slider.Position = Position + new Vector2(0, 20);

        _label.Render(renderer);
        _slider.Render(renderer);
    }

    public bool Contains(Vector2 pos)
        => pos.X >= Position.X && pos.X <= Position.X + Size.X
        && pos.Y >= Position.Y && pos.Y <= Position.Y + Size.Y;
}
```

!!! tip
    For complex composites where children need full input routing (hover, focus, drag), consider putting them directly on the `UICanvas` and managing their positions manually, rather than wrapping them in a composite component.

---

## World-Space Components

For labels or indicators that track world-space positions, implement `IUIWorldComponent` instead of (or in addition to) `IUIComponent`:

```csharp
public interface IUIWorldComponent : IUIComponent
{
    Vector2 WorldPosition    { get; set; }
    Vector2 ScreenOffset     { get; set; }
    bool    CullWhenOffScreen { get; set; }
}
```

Add to the canvas with `AddWorldComponent`. The canvas projects `WorldPosition` through `UICanvas.WorldCamera` to screen space each frame and assigns the result to `Position` before calling `Render`.

```csharp
public class DamageNumber : IUIWorldComponent
{
    // ... IUIComponent members ...
    public Vector2 WorldPosition    { get; set; }
    public Vector2 ScreenOffset     { get; set; } = new Vector2(-20, -40);
    public bool    CullWhenOffScreen { get; set; } = true;

    public string Text    { get; set; } = "0";
    public Color  Color   { get; set; } = Color.Red;
    private float _elapsed;

    public void Update(float deltaTime)
    {
        _elapsed += deltaTime;
        WorldPosition += new Vector2(0, -30f * deltaTime);  // Float upward
    }

    public void Render(IRenderer renderer)
    {
        if (!Visible) return;
        float alpha = Math.Max(0f, 1f - _elapsed);
        renderer.DrawText(Text, Position.X, Position.Y,
            new TextRenderOptions { Color = Color with { A = (byte)(alpha * 255) } });
    }

    public bool Contains(Vector2 pos) => false;  // Not interactive
}
```

---

## Related Topics

- [UI Components](components.md): complete component reference
- [UI Framework Overview](index.md): setup, best practices, and troubleshooting

