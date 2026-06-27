---
title: Tab Container
description: UITabContainer: tabbed panels with scrollable tab bar and per-tab children
---

# UITabContainer

`UITabContainer` organises content into switchable tabs. The tab bar renders horizontally above a content area. When there are too many tabs to fit, the bar becomes scrollable via arrow buttons.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var tabs = new UITabContainer(new Vector2(20, 50), new Vector2(500, 350));
_canvas.Add(tabs);
```

---

## Adding and managing tabs

```csharp
tabs.AddTab("General");
tabs.AddTab("Audio");
tabs.AddTab("Graphics");

// Remove a tab by index
tabs.RemoveTab(1);

// Rename
tabs.RenameTab(0, "Options");

int count = tabs.TabCount;
string? title = tabs.GetTabTitle(0);
```

---

## Adding components to a tab

Component positions inside a tab are **content-origin-relative**: `(0, 0)` is the top-left corner of the content area directly below the tab bar.

```csharp
// By index
tabs.AddComponentToTab(0, new UILabel("Resolution", new Vector2(10, 10)));

// By title
tabs.AddComponentToTab("Audio", new UISlider(new Vector2(10, 10), new Vector2(200, 18)));

// Read all components in a tab
IReadOnlyList<IUIComponent> components = tabs.GetTabComponents(0);

// Remove a component
tabs.RemoveComponentFromTab(0, myLabel);
```

---

## Selection

```csharp
// Set active tab programmatically
tabs.SelectedTabIndex = 2;

// Navigate
tabs.SelectNextTab();
tabs.SelectPreviousTab();

int current = tabs.SelectedTabIndex;
```

---

## Tab bar styling

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TabHeight` | `float` | `30` | Height of the tab bar in pixels |
| `TabBackgroundColor` | `Color` | `(60,60,60)` | Inactive tab fill |
| `ActiveTabColor` | `Color` | `(80,80,80)` | Active (selected) tab fill |
| `HoverTabColor` | `Color` | `(70,70,70)` | Hovered tab fill |
| `TextColor` | `Color` | White | Tab label color |
| `BorderColor` | `Color` | `(100,100,100)` | Tab and content border |
| `FocusColor` | `Color` | `(120,180,255)` | Focus ring around the tab bar |

## Content area styling

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ContentBackgroundColor` | `Color` | `(50,50,50)` | Content area fill |
| `ContentBackgroundTexture` | `ITexture?` | `null` | Nine-slice texture for the content area |
| `ContentBackgroundTextureBorder` | `NineSliceBorder` | `default` | Nine-slice insets |
| `ContentBackgroundTextureTint` | `Color` | White | Tint applied to the content texture |

## Tab button texture

```csharp
tabs.TabTexture       = renderer.LoadTexture("ui/tab.png");
tabs.TabTextureBorder = new NineSliceBorder(6, 6, 6, 6);
// Per-state tints are taken from ActiveTabColor, HoverTabColor, TabBackgroundColor
```

When `TabTexture` is set it replaces the solid color fills. The per-state colors become tints applied on top of the texture.

---

## Scrollable tab bar

When tabs are too narrow to fit at `MinTabWidth` the bar automatically adds left/right arrow buttons:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MinTabWidth` | `float` | `80` | Minimum tab width before scrolling activates; `0` = never scroll |
| `TabArrowWidth` | `float` | `20` | Width of each arrow button |

---

## Events

| Event | Signature | Fires when |
|-------|-----------|-----------|
| `OnTabChanged` | `Action<int, string>` | Selected tab changes |
| `OnFocusGained` | `Action` | Container receives keyboard focus |
| `OnFocusLost` | `Action` | Container loses keyboard focus |

```csharp
tabs.OnTabChanged += (index, title) => Debug.Log($"Switched to {title}");
```

---

## Keyboard navigation

When focused, Left/Right arrows cycle through tabs.

---

## Content origin helper

If you need to convert a content-relative position to absolute screen coordinates (e.g. for debug hit-tests):

```csharp
Vector2 origin = tabs.GetContentOrigin();
```

---

## Example: settings screen

```csharp
var settings = new UITabContainer(new Vector2(60, 60), new Vector2(560, 400))
{
	TabHeight            = 32f,
	ActiveTabColor       = new Color(40, 80, 140),
	ContentBackgroundColor = new Color(25, 25, 35, 240),
};

settings.AddTab("Graphics");
settings.AddTab("Audio");
settings.AddTab("Controls");

// Graphics tab
settings.AddComponentToTab("Graphics", new UILabel("Resolution", new Vector2(12, 12)));
settings.AddComponentToTab("Graphics", new UIDropdown(new Vector2(120, 8), new Vector2(180, 28)));

// Audio tab
settings.AddComponentToTab("Audio", new UILabel("Master Volume", new Vector2(12, 12)));
settings.AddComponentToTab("Audio", new UISlider(new Vector2(160, 12), new Vector2(200, 18))
{
	MinValue = 0f, MaxValue = 1f, Value = 0.8f
});

settings.OnTabChanged += (i, title) => Debug.Log($"Tab: {title}");
_canvas.Add(settings);
```
