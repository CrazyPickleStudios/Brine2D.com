---
title: Tree View
description: UITreeView and UITreeNode: hierarchical expand/collapse tree widget
---

# UITreeView

`UITreeView` renders a hierarchical tree of `UITreeNode` items with expand/collapse toggles, single-row selection, keyboard navigation, alternating row colors, and a virtual scrollbar.

Implements `IUIComponent` and `IAnchoredUIComponent`.

---

## Constructor

```csharp
var tree = new UITreeView(new Vector2(20, 60), new Vector2(320, 400));
_canvas.Add(tree);
```

---

## Building the tree

### UITreeNode

```csharp
var node = new UITreeNode("Entities", tag: null, isExpanded: true);

// Fluent child API: Add returns the parent node for chaining
node.Add("Player")
	.Add("Camera")
	.Add("LightSource");

// Or add pre-built children
var enemy = new UITreeNode("Enemy", tag: myEnemy);
enemy.Add("Sprite").Add("Collider");
node.Add(enemy);
```

| Property | Type | Description |
|----------|------|-------------|
| `Text` | `string` | Display text |
| `Tag` | `object?` | Arbitrary application data |
| `IsExpanded` | `bool` | Whether the node's children are visible |
| `Children` | `IReadOnlyList<UITreeNode>` | Child nodes |
| `HasChildren` | `bool` | `true` when the node has at least one child |

```csharp
// Modify later
node.Text       = "Root (3)";
node.IsExpanded = false;

node.Remove(enemy);
node.ClearChildren();
```

### Adding roots to the tree view

```csharp
// Add one at a time
tree.AddRoot(node);

// Or replace all roots at once (resets scroll and selection)
tree.SetRoots(new[] { rootA, rootB });

// Clear everything
tree.ClearRoots();

IReadOnlyList<UITreeNode> roots = tree.Roots;
```

---

## Selection

```csharp
int            index = tree.SelectedIndex; // -1 = none; index into the flattened visible list
UITreeNode?    node  = tree.SelectedNode;

tree.OnSelectionChanged += selectedNode =>
{
	if (selectedNode?.Tag is MyEntity e)
		InspectEntity(e);
};
```

---

## Expand / collapse events

```csharp
tree.OnNodeToggled += node =>
{
	Debug.Log($"{node.Text} is now {(node.IsExpanded ? "expanded" : "collapsed")}");
};
```

---

## Scrolling

```csharp
float offset = tree.ScrollOffsetY;
tree.ScrollToTop();
tree.ScrollToBottom();
```

---

## Geometry

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `RowHeight` | `float` | `22` | Row height in pixels |
| `IndentWidth` | `float` | `16` | Indent added per depth level |
| `ScrollbarWidth` | `float` | `10` | Scrollbar track width |
| `MinThumbSize` | `float` | `10` | Minimum scrollbar thumb height |

---

## Colors

| Property | Type | Default |
|----------|------|---------|
| `BackgroundColor` | `Color` | `(28,28,28)` |
| `RowColor` | `Color` | `(38,38,38)` |
| `AlternateRowColor` | `Color` | `(42,42,42)` |
| `HoverColor` | `Color` | `(65,80,110)` |
| `SelectionColor` | `Color` | `(55,95,175)` |
| `BorderColor` | `Color` | `(80,80,80)` |
| `FocusBorderColor` | `Color` | `(120,180,255)` |
| `TextColor` | `Color` | White |
| `DisabledTextColor` | `Color` | `(130,130,130)` |
| `ExpanderColor` | `Color` | `(180,180,180)` |
| `ScrollbarTrackColor` | `Color` | `(50,50,50)` |
| `ScrollbarThumbColor` | `Color` | `(100,100,100)` |
| `ScrollbarThumbHoverColor` | `Color` | `(140,140,140)` |

---

## Keyboard navigation

When focused:

| Key | Action |
|-----|--------|
| Up / Down | Move selection |
| Left | Collapse selected node (or move to parent) |
| Right | Expand selected node |
| Page Up / Down | Scroll by one viewport height |
| Home / End | Jump to first / last visible row |

---

## Focus events

```csharp
tree.TabIndex       = 0;
tree.OnFocusGained += () => { };
tree.OnFocusLost   += () => { };
```

---

## Example: scene hierarchy panel

```csharp
var hierarchy = new UITreeView(new Vector2(0, 28), new Vector2(240, 600))
{
	RowHeight     = 22f,
	IndentWidth   = 14f,
	SelectionColor = new Color(40, 80, 150),
	TabIndex      = 0,
};

var sceneRoot = new UITreeNode("Scene", isExpanded: true);
foreach (var entity in _scene.Entities)
{
	var entityNode = new UITreeNode(entity.Name, tag: entity, isExpanded: false);
	foreach (var comp in entity.Components)
		entityNode.Add(comp.GetType().Name, tag: comp);
	sceneRoot.Add(entityNode);
}
hierarchy.AddRoot(sceneRoot);

hierarchy.OnSelectionChanged += node =>
{
	_inspector.Target = node?.Tag;
};

_canvas.Add(hierarchy);
```
