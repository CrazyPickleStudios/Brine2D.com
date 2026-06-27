---
title: Dialog
description: UIDialog: modal popup with title bar, message, buttons, and custom children
---

# UIDialog

`UIDialog` is a modal popup. It renders a darkening overlay, a title bar, a message area, and one or more action buttons. Children can be added freely to the content area. The dialog auto-centers when added to a canvas.

Implements `IUIComponent` (not `IAnchoredUIComponent`: centering is handled by the canvas).

---

## Constructor

```csharp
var dialog = new UIDialog("Confirm", "Are you sure you want to delete this?",
	new Vector2(360, 200));
_canvas.Add(dialog);
```

The dialog is centered on screen immediately when added. If `UICanvas.ScreenSize` changes later the dialog is re-centered automatically.

---

## Action buttons

```csharp
dialog.AddButton("Delete", () =>
{
	DeleteItem();
	_canvas.Remove(dialog);
});

dialog.AddButton("Cancel", () => _canvas.Remove(dialog));
```

Buttons are evenly spaced in the button area at the bottom of the dialog. Control button sizing with:

| Property | Type | Default |
|----------|------|---------|
| `ButtonWidth` | `float` | `100` |
| `ButtonHeight` | `float` | `35` |
| `ButtonSpacing` | `float` | `10` |
| `ButtonAreaHeight` | `float` | `60` |

---

## Custom children

Children are positioned relative to the content area below the title bar:

```csharp
dialog.AddChild(new UILabel("Enter a name:", new Vector2(20, 10)));
dialog.AddChild(new UITextInput(new Vector2(20, 36), new Vector2(260, 28)));

IReadOnlyList<IUIComponent> kids = dialog.GetChildren();
dialog.BringChildToFront(myChild);
```

---

## Layout properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Title` | `string` | `""` | Title bar text |
| `Message` | `string` | `""` | Body message text (empty = no message rendered) |
| `TitleBarHeight` | `float` | `40` | Height of the title bar in pixels |
| `Padding` | `float` | `20` | Interior padding around message and content |
| `MessageMaxWidth` | `float` | `0` | Wrap width for the message; `0` = full content width |

---

## Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(50,50,50)` |
| `TitleBarColor` | `Color` | `(70,70,70)` |
| `BorderColor` | `Color` | `(100,100,100)` |
| `TextColor` | `Color` | White |
| `OverlayColor` | `Color` | `(0,0,0,180)` |

---

## Nine-slice textures

```csharp
// Body
dialog.BackgroundTexture       = renderer.LoadTexture("ui/dialog_body.png");
dialog.BackgroundTextureBorder = new NineSliceBorder(12, 12, 12, 12);

// Title bar
dialog.TitleBarTexture         = renderer.LoadTexture("ui/dialog_titlebar.png");
dialog.TitleBarTextureBorder   = new NineSliceBorder(8, 8, 8, 8);
```

When a texture is set it replaces the solid color fill. The border outline is still drawn on top.

---

## Overlay

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ShowOverlay` | `bool` | `true` | Darken the scene behind the dialog |
| `OverlayColor` | `Color` | `(0,0,0,180)` | Overlay fill color |

When multiple dialogs are stacked only the topmost one draws the overlay (the canvas suppresses it for lower dialogs automatically).

---

## Behavior

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AllowEscapeClose` | `bool` | `true` | Fire `OnEscapeDismissed` when Escape is pressed |
| `IsDraggable` | `bool` | `false` | Allow the user to drag the dialog by its title bar |
| `ShowCloseButton` | `bool` | `false` | Show an × button in the title bar corner |
| `CloseButtonColor` | `Color` | `(90,90,90)` | Close button idle color |
| `CloseButtonHoverColor` | `Color` | `(180,60,60)` | Close button hover color |
| `CloseButtonTextColor` | `Color` | White | × glyph color |

### Escape / close button event

```csharp
dialog.OnEscapeDismissed += () =>
{
	_canvas.Remove(dialog);
};
```

---

## Example: confirm dialog

```csharp
var confirm = new UIDialog("Delete Save?",
	"This will permanently delete your save file. This cannot be undone.",
	new Vector2(380, 180))
{
	ShowOverlay      = true,
	AllowEscapeClose = true,
	ShowCloseButton  = true,
};

confirm.AddButton("Delete", () =>
{
	SaveManager.Delete();
	_canvas.Remove(confirm);
});

confirm.AddButton("Cancel", () => _canvas.Remove(confirm));
confirm.OnEscapeDismissed += () => _canvas.Remove(confirm);

_canvas.Add(confirm);
```

## Example: input dialog

```csharp
UITextInput nameInput = null!;

var inputDialog = new UIDialog("Rename", string.Empty, new Vector2(340, 160))
{
	IsDraggable     = true,
	TitleBarColor   = new Color(40, 60, 100),
	ShowCloseButton = true,
};

nameInput = new UITextInput(new Vector2(20, 10), new Vector2(260, 28))
{
	Placeholder = "Enter new name",
};
inputDialog.AddChild(nameInput);

inputDialog.AddButton("OK", () =>
{
	Rename(nameInput.Text);
	_canvas.Remove(inputDialog);
});
inputDialog.AddButton("Cancel", () => _canvas.Remove(inputDialog));
inputDialog.OnEscapeDismissed += () => _canvas.Remove(inputDialog);

_canvas.Add(inputDialog);
```
