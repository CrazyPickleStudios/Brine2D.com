---
title: Drag & Drop
description: UIDropTarget, IDragPayload, and UICanvas drag-and-drop APIs
---

# Drag & Drop

Brine2D's drag-and-drop system is canvas-managed. Any `IUIComponent` can be a drag source; drop zones are `UIDropTarget` components. The payload is any type that implements `IDragPayload`.

---

## IDragPayload

`IDragPayload` is a plain marker interface. Create one record or class per payload type:

```csharp
public record InventoryItemPayload(InventoryItem Item) : IDragPayload;
public record CardPayload(Card Card, int SourceSlot) : IDragPayload;
```

---

## Registering a drag source

Any `IUIComponent` already on the canvas can be made draggable:

```csharp
var itemIcon = new UIImage(itemTexture, new Vector2(100, 200), new Vector2(48, 48));
_canvas.Add(itemIcon);

_canvas.RegisterDraggable(itemIcon, new InventoryItemPayload(myItem));
```

The canvas begins a drag when the user holds the left mouse button and moves more than 6 pixels (the drag threshold). During the drag it renders a ghost copy of the source component following the cursor.

### Canvas drag events

```csharp
_canvas.OnDragStarted   += (source, payload) => Debug.Log("Drag started");
_canvas.OnDragCancelled += (source, payload) => Debug.Log("Dropped on nothing");
```

`OnDragCancelled` fires when the user releases over no registered drop target.

---

## Registering a drop target

```csharp
var slot = new UIDropTarget
{
	Position      = new Vector2(300, 200),
	Size          = new Vector2(64, 64),
	IdleColor     = new Color(80, 80, 80, 60),
	HoverColor    = new Color(100, 180, 255, 100),
	BorderColor   = new Color(120, 180, 255, 180),
	BorderThickness = 2f,
};
_canvas.Add(slot);
_canvas.RegisterDropTarget(slot);

slot.OnDrop += payload =>
{
	if (payload is InventoryItemPayload p)
		EquipItem(p.Item);
};
```

### Filtering accepted payloads

```csharp
slot.AcceptsPayload = payload => payload is InventoryItemPayload;
```

When `AcceptsPayload` is `null` (the default) the target accepts all payload types. When it returns `false` the cursor does not change to "drop" over that target and `OnDrop` will not fire.

---

## UIDropTarget properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IdleColor` | `Color` | `(80,80,80,60)` | Background when no drag is over it |
| `HoverColor` | `Color` | `(100,180,255,100)` | Background while a compatible payload hovers |
| `BorderColor` | `Color` | `(120,180,255,180)` | Border around the zone; set alpha to 0 to hide |
| `BorderThickness` | `float` | `2` | Border width in pixels |
| `IsHovered` | `bool` | `false` | Read-only: set by the canvas during drag |
| `AcceptsPayload` | `Func<IDragPayload, bool>?` | `null` | Optional filter; `null` = accept all |

---

## Querying drag state

```csharp
bool           dragging = _canvas.IsDragging;
IUIComponent?  source   = _canvas.DragSource;
```

---

## Full example: inventory drag and drop

```csharp
// Payload
public record SlotPayload(int SlotIndex, InventoryItem Item) : IDragPayload;

// Source slots
for (int i = 0; i < inventory.Slots.Count; i++)
{
	int slotIndex = i;
	var item      = inventory.Slots[i];

	var icon = new UIImage(item.Icon, new Vector2(10 + i * 56, 10), new Vector2(48, 48));
	_canvas.Add(icon);
	_canvas.RegisterDraggable(icon, new SlotPayload(slotIndex, item));
}

// Drop targets
for (int i = 0; i < equipment.Slots.Count; i++)
{
	int slotIndex = i;

	var target = new UIDropTarget
	{
		Position  = new Vector2(300, 10 + i * 56),
		Size      = new Vector2(48, 48),
		HoverColor = new Color(60, 180, 120, 140),
	};
	target.AcceptsPayload = p => p is SlotPayload sp && equipment.Accepts(slotIndex, sp.Item);
	target.OnDrop += payload =>
	{
		if (payload is SlotPayload sp)
			equipment.Equip(slotIndex, sp.Item, sp.SlotIndex);
	};

	_canvas.Add(target);
	_canvas.RegisterDropTarget(target);
}

// Listen for cancelled drags (dropped on nothing)
_canvas.OnDragCancelled += (_, _) => Debug.Log("Drag cancelled");
```

---

## Notes

- The canvas renders the drag ghost automatically using the source component's `Render` method at the current cursor position.
- Drag sources must be added to the canvas with `Add` before calling `RegisterDraggable`.
- Drop targets must also be added with `Add` before calling `RegisterDropTarget`.
- There is no built-in multi-select; handle that at the payload level if needed.
