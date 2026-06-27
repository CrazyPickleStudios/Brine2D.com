---
title: UI Components â€” Quick Reference
description: All built-in UI components in Brine2D at a glance
---

# UI Components â€” Quick Reference

All 25+ built-in components organized by category. Follow the links for full property tables, styling, and examples.

---

## Text & Display

| Component | Page | Description |
|-----------|------|-------------|
| `UILabel` | [Label & Rich Text](label.md) | Static or dynamic text |
| `UIRichTextLabel` | [Label & Rich Text](label.md) | BBCode-formatted text with alignment, shadows, and wrapping |
| `UIImage` | [Image](image.md) | Texture with tint, rotation, source rect, and optional animation |

---

## Interactive

| Component | Page | Description |
|-----------|------|-------------|
| `UIButton` | [Button](button.md) | Clickable button with per-state colors and nine-slice textures |
| `UICheckbox` | [Checkbox & Radio](selection.md) | Toggle on/off with label |
| `UIRadioButton` | [Checkbox & Radio](selection.md) | Exclusive selection within a `UIRadioButtonGroup` |
| `UIDropdown` | [Dropdown](dropdown.md) | Selection menu with optional scrolling and keyboard navigation |

---

## Input

| Component | Page | Description |
|-----------|------|-------------|
| `UITextInput` | [Text Input & Area](text-input.md) | Single-line text field with selection, undo/redo, and password mode |
| `UITextArea` | [Text Input & Area](text-input.md) | Multi-line editor with selection, scrolling, and undo/redo |
| `UISlider` | [Slider & SpinBox](slider.md) | Horizontal or vertical value slider with step snapping |
| `UISpinBox` | [Slider & SpinBox](slider.md) | Numeric field with increment/decrement buttons |

---

## Progress & Feedback

| Component | Page | Description |
|-----------|------|-------------|
| `UIProgressBar` | [Progress Bar](progress.md) | Directional fill bar with optional label and custom text provider |
| `UITooltip` | [Tooltip & Toast](tooltip-toast.md) | Hover information attached to any component |
| `UIToast` | [Tooltip & Toast](tooltip-toast.md) | Timed fade-in/out notification |

---

## Layout & Containers

| Component | Page | Description |
|-----------|------|-------------|
| `UIPanel` | [Panel, Stack & Grid](layout.md) | Background container with optional nine-slice texture and child clipping |
| `UIStackPanel` | [Panel, Stack & Grid](layout.md) | Auto-stacks children vertically or horizontally |
| `UIGrid` | [Panel, Stack & Grid](layout.md) | Fixed-column grid layout |
| `UIScrollView` | [Scroll View](scroll-view.md) | Scrollable container with horizontal/vertical scrollbars |
| `UITabContainer` | [Tab Container](tab-container.md) | Tabbed interface with scrollable tab bar |

---

## Dialogs & Menus

| Component | Page | Description |
|-----------|------|-------------|
| `UIDialog` | [Dialog](dialog.md) | Modal popup with title bar, message, buttons, and custom children |
| `UIContextMenu` | [Menus](menus.md) | Right-click overlay with items and separators |
| `UIMenuBar` | [Menus](menus.md) | Horizontal menu bar with dropdown submenus |

---

## Advanced

| Component | Page | Description |
|-----------|------|-------------|
| `UIVirtualList<T>` | [Virtual List](virtual-list.md) | High-performance virtualized scrolling list |
| `UITreeView` | [Tree View](tree-view.md) | Hierarchical tree with expand/collapse and keyboard navigation |
| `UIDropTarget` | [Drag & Drop](drag-drop.md) | Drop zone for the canvas drag-and-drop system |
| `UIWorldLabel` | [World Labels](world-labels.md) | World-space text projected to screen coordinates |

---

## Animation

| Component | Page | Description |
|-----------|------|-------------|
| `UITween` | [Animation & Tweens](animation.md) | Animates a `float` property with easing and loop modes |
| `UITweenSequence` | [Animation & Tweens](animation.md) | Chains tweens so each starts after the previous completes |
| `UIEasing` | [Animation & Tweens](animation.md) | Standard easing functions (Linear, Cubic, Bounce, Elastic, â€¦) |

---

## Common Properties

Every `IUIComponent` exposes:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Position` | `Vector2` | `(0, 0)` | Screen-space top-left in pixels |
| `Size` | `Vector2` | varies | Width and height in pixels |
| `Visible` | `bool` | `true` | Whether the component is rendered |
| `Enabled` | `bool` | `true` | Whether the component receives input |
| `ZOrder` | `int` | `0` | Render/input priority â€” higher = on top |
| `TabIndex` | `int` | `int.MaxValue` | Keyboard tab order â€” lower = focused first |
| `Tooltip` | `UITooltip?` | `null` | Hover tooltip |
| `Name` | `string?` | `null` | Name for `UICanvas.FindByName` lookup |

Components implementing `IAnchoredUIComponent` additionally expose:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Anchor` | `UIAnchor` | `TopLeft` | Screen anchor point |
| `AnchorOffset` | `Vector2` | `(0, 0)` | Pixel offset from the resolved anchor |

[:octicons-arrow-right-24: Positioning & Anchoring guide](positioning.md)
