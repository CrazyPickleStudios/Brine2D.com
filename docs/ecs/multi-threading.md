---
title: ECS Multi-Threading
description: Safely use multi-threading and parallel processing in Brine2D's ECS
---

# ECS Multi-Threading

Learn how to safely use multi-threading and parallel processing with Brine2D's Entity Component System.

## Overview

Multi-threading can significantly improve performance when processing large numbers of entities:

- **Parallel Systems** - Process entities across multiple threads
- **Job System** - Queue and execute work asynchronously
- **Thread Safety** - Avoid race conditions and data corruption
- **Synchronization** - Coordinate work between threads
- **Performance** - When to use (and when not to use) threading

**Important:** Multi-threading adds complexity. Only use it when single-threaded performance is insufficient.

---

## Threading Model

```mermaid
graph TB
    A[Main Thread] --> B[Update Systems]
    B --> C{Parallel Safe?}
    
    C -->|Yes| D[Parallel Processing]
    C -->|No| E[Single-Threaded]
    
    D --> F[Worker Thread 1]
    D --> G[Worker Thread 2]
    D --> H[Worker Thread N]
    
    F --> I[Process Entities]
    G --> I
    H --> I
    
    I --> J[Synchronization Point]
    J --> K[Continue Main Thread]
    
    E --> K
    
    style A fill:#2d5016,stroke:#4ec9b0,stroke-width:2px,color:#fff
    style D fill:#4a2d4a,stroke:#c586c0,stroke-width:2px,color:#fff
    style J fill:#1e3a5f,stroke:#569cd6,stroke-width:2px,color:#fff
```

**Key concepts:**

1. **Main Thread** - Game loop, rendering, input
2. **Worker Threads** - Entity processing, physics
3. **Synchronization** - Ensure all work completes before continuing
4. **Thread Safety** - Prevent concurrent access to shared data

---

## Thread Safety Basics

### Read vs Write Access

```csharp
public class ThreadSafetyExample
{
    // ✅ SAFE: Multiple threads reading same data
    public void ReadOnlyOperation()
    {
        var entities = world.QueryEntities()
            .With<TransformComponent>();
        
        Parallel.ForEach(entities, entity =>
        {
            var transform = entity.GetComponent<TransformComponent>();
            var position = transform.Position; // Reading is safe
            ProcessPosition(position);
        });
    }
    
    // ❌ UNSAFE: Multiple threads writing same data
    public void WriteOperation()
    {
        var entities = world.QueryEntities()
            .With<TransformComponent>();
        
        Parallel.ForEach(entities, entity =>
        {
            var transform = entity.GetComponent<TransformComponent>();
            transform.Position += Vector2.One; // Writing is NOT SAFE!
        });
    }
    
    // ✅ SAFE: Each thread writes to different data
    public void IsolatedWriteOperation()
    {
        var entities = world.QueryEntities()
            .With<TransformComponent>();
        
        Parallel.ForEach(entities, entity =>
        {
            var transform = entity.GetComponent<TransformComponent>();
            // Each entity is separate, so this is safe
            transform.Position += Vector2.One;
        });
    }
}
```

**Rules:**

| Access Pattern | Thread Safety | Example |
|----------------|---------------|---------|
| **Multiple reads** | ✅ Safe | Reading positions |
| **Single write** | ✅ Safe | One thread updates |
| **Multiple writes to different data** | ✅ Safe | Each entity separate |
| **Multiple writes to same data** | ❌ Unsafe | Shared counter |

---

## Parallel Entity Processing

### Basic Parallel ForEach

Process entities in parallel:

```csharp
using System.Threading.Tasks;

public class ParallelMovementSystem : IUpdateSystem
{
    private readonly World _world;
    
    public string Name => "ParallelMovementSystem";
    public int UpdateOrder => 100;
    
    public ParallelMovementSystem(World world)
    {
        _world = world;
    }
    
    public void Update(GameTime gameTime)
    {
        var deltaTime = (float)gameTime.DeltaTime;
        
        // Get entities
        var entities = _world.QueryEntities()
            .With<TransformComponent>()
            .With<VelocityComponent>()
            .ToList(); // Important: materialize query
        
        // Process in parallel
        Parallel.ForEach(entities, entity =>
        {
            var transform = entity.GetComponent<TransformComponent>();
            var velocity = entity.GetComponent<VelocityComponent>();
            
            if (transform != null && velocity != null)
            {
                // Safe: Each entity's data is independent
                transform.Position += velocity.Velocity * deltaTime;
            }
        });
    }
}
```

**Important:** Always materialize the query (`.ToList()`) before parallel processing!

---

### Parallel Options

Control parallelism degree:

```csharp
public class ConfigurableParallelSystem : IUpdateSystem
{
    private readonly World _world;
    private readonly ParallelOptions _parallelOptions;
    
    public ConfigurableParallelSystem(World world)
    {
        _world = world;
        
        // Configure parallel options
        _parallelOptions = new ParallelOptions
        {
            MaxDegreeOfParallelism = Environment.ProcessorCount,
            // Or limit threads: MaxDegreeOfParallelism = 4
        };
    }
    
    public void Update(GameTime gameTime)
    {
        var entities = _world.QueryEntities()
            .With<TransformComponent>()
            .ToList();
        
        // Use configured options
        Parallel.ForEach(entities, _parallelOptions, entity =>
        {
            ProcessEntity(entity);
        });
    }
}
```

---

## Synchronization

### Thread-Safe Collections

Use concurrent collections for shared data:

```csharp
using System.Collections.Concurrent;

public class CollisionDetectionSystem : IUpdateSystem
{
    private readonly World _world;
    private readonly ConcurrentBag<Collision> _collisions = new();
    
    public string Name => "CollisionDetectionSystem";
    public int UpdateOrder => 150;
    
    public void Update(GameTime gameTime)
    {
        // Clear previous collisions
        _collisions.Clear();
        
        var entities = _world.QueryEntities()
            .With<TransformComponent>()
            .With<ColliderComponent>()
            .ToList();
        
        // Check collisions in parallel
        Parallel.ForEach(entities, entity1 =>
        {
            foreach (var entity2 in entities)
            {
                if (entity1 == entity2) continue;
                
                if (CheckCollision(entity1, entity2))
                {
                    // Thread-safe add
                    _collisions.Add(new Collision(entity1, entity2));
                }
            }
        });
        
        // Process collisions on main thread
        ProcessCollisions();
    }
    
    private void ProcessCollisions()
    {
        foreach (var collision in _collisions)
        {
            HandleCollision(collision);
        }
    }
}
```

**Concurrent collections:**

| Collection | Use Case | Performance |
|------------|----------|-------------|
| `ConcurrentBag<T>` | Unordered additions | Fast |
| `ConcurrentQueue<T>` | FIFO order | Fast |
| `ConcurrentDictionary<K,V>` | Key-value lookup | Good |
| `ConcurrentStack<T>` | LIFO order | Fast |

---

### Lock-Based Synchronization

Use locks for complex shared state:

```csharp
public class ScoreSystem : IUpdateSystem
{
    private readonly World _world;
    private readonly object _scoreLock = new();
    private int _totalScore = 0;
    
    public string Name => "ScoreSystem";
    public int UpdateOrder => 200;
    
    public void Update(GameTime gameTime)
    {
        var enemies = _world.QueryEntities()
            .With<EnemyComponent>()
            .With<HealthComponent>()
            .ToList();
        
        // Process enemies in parallel
        Parallel.ForEach(enemies, enemy =>
        {
            var health = enemy.GetComponent<HealthComponent>();
            
            if (health != null && health.IsDead)
            {
                // Lock when modifying shared state
                lock (_scoreLock)
                {
                    _totalScore += 10;
                }
            }
        });
    }
    
    public int GetScore()
    {
        lock (_scoreLock)
        {
            return _totalScore;
        }
    }
}
```

**Warning:** Locks can reduce parallelism. Use sparingly!

---

### Interlocked Operations

Atomic operations without locks:

```csharp
using System.Threading;

public class CounterSystem : IUpdateSystem
{
    private readonly World _world;
    private int _entityCount = 0;
    
    public void Update(GameTime gameTime)
    {
        var entities = _world.QueryEntities()
            .With<TransformComponent>()
            .ToList();
        
        // Reset counter
        _entityCount = 0;
        
        // Count in parallel (atomic)
        Parallel.ForEach(entities, entity =>
        {
            if (IsActive(entity))
            {
                Interlocked.Increment(ref _entityCount);
            }
        });
        
        Logger.LogDebug("Active entities: {Count}", _entityCount);
    }
}
```

**Interlocked operations:**

| Operation | Method | Use Case |
|-----------|--------|----------|
| **Increment** | `Interlocked.Increment(ref x)` | Counters |
| **Decrement** | `Interlocked.Decrement(ref x)` | Counters |
| **Add** | `Interlocked.Add(ref x, value)` | Accumulators |
| **Exchange** | `Interlocked.Exchange(ref x, value)` | Swap values |
| **CompareExchange** | `Interlocked.CompareExchange(...)` | Conditional update |

---

## Common Patterns

### Parallel Physics Simulation

```csharp
public class ParallelPhysicsSystem : IUpdateSystem
{
    private readonly World _world;
    private const float Gravity = 980f;
    
    public string Name => "ParallelPhysicsSystem";
    public int UpdateOrder => 50;
    
    public void Update(GameTime gameTime)
    {
        var deltaTime = (float)gameTime.DeltaTime;
        
        var entities = _world.QueryEntities()
            .With<RigidbodyComponent>()
            .ToList();
        
        // Apply forces in parallel (each entity independent)
        Parallel.ForEach(entities, entity =>
        {
            var rigidbody = entity.GetComponent<RigidbodyComponent>();
            
            if (rigidbody != null)
            {
                // Apply gravity
                if (rigidbody.UseGravity)
                {
                    rigidbody.Velocity.Y += Gravity * deltaTime;
                }
                
                // Apply drag
                rigidbody.Velocity *= (1.0f - rigidbody.Drag * deltaTime);
            }
        });
    }
}
```

---

### Parallel Pathfinding

```csharp
public class ParallelPathfindingSystem : IUpdateSystem
{
    private readonly World _world;
    
    public string Name => "ParallelPathfindingSystem";
    public int UpdateOrder => 30;
    
    public void Update(GameTime gameTime)
    {
        var entities = _world.QueryEntities()
            .With<AIComponent>()
            .With<TransformComponent>()
            .ToList();
        
        // Calculate paths in parallel
        Parallel.ForEach(entities, entity =>
        {
            var ai = entity.GetComponent<AIComponent>();
            var transform = entity.GetComponent<TransformComponent>();
            
            if (ai != null && transform != null && ai.NeedsPath)
            {
                // Each pathfinding operation is independent
                var path = CalculatePath(
                    transform.Position, 
                    ai.TargetPosition);
                
                ai.CurrentPath = path;
                ai.NeedsPath = false;
            }
        });
    }
    
    private List<Vector2> CalculatePath(Vector2 start, Vector2 end)
    {
        // A* or other pathfinding algorithm
        // This can be expensive, so parallel processing helps
        return new List<Vector2>();
    }
}
```

---

### Parallel Particle Updates

```csharp
public class ParallelParticleSystem : IUpdateSystem
{
    private readonly World _world;
    
    public string Name => "ParallelParticleSystem";
    public int UpdateOrder => 170;
    
    public void Update(GameTime gameTime)
    {
        var deltaTime = (float)gameTime.DeltaTime;
        
        var particles = _world.QueryEntities()
            .With<ParticleComponent>()
            .ToList();
        
        if (particles.Count < 100)
        {
            // Not worth parallelizing for small counts
            UpdateParticlesSingleThreaded(particles, deltaTime);
            return;
        }
        
        // Parallel for large particle counts
        Parallel.ForEach(particles, particle =>
        {
            var particleComp = particle.GetComponent<ParticleComponent>();
            
            if (particleComp != null)
            {
                // Update lifetime
                particleComp.Lifetime -= deltaTime;
                
                // Update physics
                var transform = particle.GetComponent<TransformComponent>();
                if (transform != null)
                {
                    transform.Position += particleComp.Velocity * deltaTime;
                    particleComp.Velocity += particleComp.Acceleration * deltaTime;
                }
            }
        });
    }
}
```

---

## Performance Considerations

### When to Use Parallelism

```csharp
public class SmartParallelSystem : IUpdateSystem
{
    private readonly World _world;
    private const int ParallelThreshold = 1000;
    
    public void Update(GameTime gameTime)
    {
        var entities = _world.QueryEntities()
            .With<TransformComponent>()
            .ToList();
        
        // Only parallelize if enough work
        if (entities.Count < ParallelThreshold)
        {
            // Single-threaded for small counts
            foreach (var entity in entities)
            {
                ProcessEntity(entity);
            }
        }
        else
        {
            // Parallel for large counts
            Parallel.ForEach(entities, entity =>
            {
                ProcessEntity(entity);
            });
        }
    }
}
```

**Guidelines:**

| Entity Count | Recommendation | Reason |
|--------------|----------------|--------|
| **< 100** | Single-threaded | Overhead > benefit |
| **100-1000** | Test both | Depends on work per entity |
| **> 1000** | Parallel | Significant benefit |

---

### Measuring Parallelism Benefit

```csharp
using System.Diagnostics;

public class ParallelismBenchmark
{
    public void BenchmarkSystem(World world, int iterations = 100)
    {
        var entities = world.QueryEntities()
            .With<TransformComponent>()
            .ToList();
        
        // Benchmark single-threaded
        var singleThreaded = Stopwatch.StartNew();
        for (int i = 0; i < iterations; i++)
        {
            foreach (var entity in entities)
            {
                ProcessEntity(entity);
            }
        }
        singleThreaded.Stop();
        
        // Benchmark parallel
        var parallel = Stopwatch.StartNew();
        for (int i = 0; i < iterations; i++)
        {
            Parallel.ForEach(entities, entity =>
            {
                ProcessEntity(entity);
            });
        }
        parallel.Stop();
        
        // Compare
        var speedup = (double)singleThreaded.ElapsedMilliseconds / 
                     parallel.ElapsedMilliseconds;
        
        Logger.LogInformation(
            "Single: {Single}ms, Parallel: {Parallel}ms, Speedup: {Speedup:F2}x",
            singleThreaded.ElapsedMilliseconds,
            parallel.ElapsedMilliseconds,
            speedup);
    }
}
```

---

## Unsafe Patterns

### Race Conditions

```csharp
public class RaceConditionExample
{
    private int _counter = 0;
    
    // ❌ BAD: Race condition!
    public void UnsafeIncrement()
    {
        var entities = world.QueryEntities()
            .With<EnemyComponent>()
            .ToList();
        
        Parallel.ForEach(entities, entity =>
        {
            // Multiple threads read-modify-write _counter
            // Lost updates! Final value will be incorrect
            _counter++;
        });
    }
    
    // ✅ GOOD: Use Interlocked
    public void SafeIncrement()
    {
        var entities = world.QueryEntities()
            .With<EnemyComponent>()
            .ToList();
        
        Parallel.ForEach(entities, entity =>
        {
            Interlocked.Increment(ref _counter);
        });
    }
    
    // ✅ GOOD: Use lock
    public void SafeIncrementWithLock()
    {
        var lockObj = new object();
        var entities = world.QueryEntities()
            .With<EnemyComponent>()
            .ToList();
        
        Parallel.ForEach(entities, entity =>
        {
            lock (lockObj)
            {
                _counter++;
            }
        });
    }
}
```

---

### Shared Component Access

```csharp
public class SharedComponentExample
{
    // ❌ BAD: Multiple threads modifying same component
    public void UnsafeSharedAccess()
    {
        var playerEntity = GetPlayer();
        var playerTransform = playerEntity.GetComponent<TransformComponent>();
        
        var enemies = world.QueryEntities()
            .With<EnemyComponent>()
            .ToList();
        
        Parallel.ForEach(enemies, enemy =>
        {
            // Multiple threads writing to playerTransform!
            playerTransform.Position += Vector2.One; // UNSAFE!
        });
    }
    
    // ✅ GOOD: Accumulate changes, apply on main thread
    public void SafeSharedAccess()
    {
        var playerEntity = GetPlayer();
        var forces = new ConcurrentBag<Vector2>();
        
        var enemies = world.QueryEntities()
            .With<EnemyComponent>()
            .ToList();
        
        // Parallel: Calculate forces
        Parallel.ForEach(enemies, enemy =>
        {
            var force = CalculateForce(enemy, playerEntity);
            forces.Add(force); // Thread-safe collection
        });
        
        // Main thread: Apply forces
        var playerTransform = playerEntity.GetComponent<TransformComponent>();
        foreach (var force in forces)
        {
            playerTransform.Position += force;
        }
    }
}
```

---

## Best Practices

### DO

1. **Materialize queries before parallel processing**
   ```csharp
   // ✅ Good - materialize first
   var entities = world.QueryEntities()
       .With<TransformComponent>()
       .ToList(); // Important!
   
   Parallel.ForEach(entities, entity => { ... });
   ```

2. **Use concurrent collections for shared data**
   ```csharp
   // ✅ Good - thread-safe collection
   var results = new ConcurrentBag<Result>();
   
   Parallel.ForEach(entities, entity =>
   {
       results.Add(ProcessEntity(entity));
   });
   ```

3. **Benchmark before and after parallelization**
   ```csharp
   // ✅ Good - measure actual improvement
   var stopwatch = Stopwatch.StartNew();
   // ... parallel code
   stopwatch.Stop();
   Logger.LogDebug("Parallel time: {Ms}ms", stopwatch.ElapsedMilliseconds);
   ```

4. **Use threshold checks**
   ```csharp
   // ✅ Good - only parallelize when beneficial
   if (entities.Count > 1000)
   {
       Parallel.ForEach(entities, ProcessEntity);
   }
   else
   {
       foreach (var entity in entities)
           ProcessEntity(entity);
   }
   ```

5. **Keep work per entity substantial**
   ```csharp
   // ✅ Good - expensive operation per entity
   Parallel.ForEach(entities, entity =>
   {
       var path = CalculateExpensivePath(entity); // Worth parallelizing
   });
   ```

### DON'T

1. **Don't query during parallel processing**
   ```csharp
   // ❌ Bad - query during parallel processing
   Parallel.ForEach(entities, entity =>
   {
       var nearby = world.QueryEntities() // UNSAFE!
           .With<EnemyComponent>()
           .ToList();
   });
   
   // ✅ Good - query before parallel processing
   var entities = world.QueryEntities().With<Component>().ToList();
   var nearby = world.QueryEntities().With<EnemyComponent>().ToList();
   
   Parallel.ForEach(entities, entity => { ... });
   ```

2. **Don't modify shared state without synchronization**
   ```csharp
   // ❌ Bad - race condition
   int counter = 0;
   Parallel.ForEach(entities, entity =>
   {
       counter++; // UNSAFE!
   });
   
   // ✅ Good - use Interlocked
   int counter = 0;
   Parallel.ForEach(entities, entity =>
   {
       Interlocked.Increment(ref counter);
   });
   ```

3. **Don't parallelize small workloads**
   ```csharp
   // ❌ Bad - too few entities
   var entities = world.QueryEntities().Take(10).ToList();
   Parallel.ForEach(entities, ProcessEntity); // Overhead > benefit
   
   // ✅ Good - use single-threaded
   foreach (var entity in entities)
   {
       ProcessEntity(entity);
   }
   ```

4. **Don't create/destroy entities in parallel**
   ```csharp
   // ❌ Bad - modifying world structure
   Parallel.ForEach(entities, entity =>
   {
       world.CreateEntity(); // UNSAFE!
       world.DestroyEntity(entity); // UNSAFE!
   });
   
   // ✅ Good - collect entities to destroy, process on main thread
   var toDestroy = new ConcurrentBag<Entity>();
   
   Parallel.ForEach(entities, entity =>
   {
       if (ShouldDestroy(entity))
       {
           toDestroy.Add(entity);
       }
   });
   
   // Main thread
   foreach (var entity in toDestroy)
   {
       world.DestroyEntity(entity);
   }
   ```

5. **Don't use excessive locking**
   ```csharp
   // ❌ Bad - lock every iteration
   var lockObj = new object();
   Parallel.ForEach(entities, entity =>
   {
       lock (lockObj) // Serializes all work!
       {
           ProcessEntity(entity);
       }
   });
   
   // ✅ Good - minimize locked sections
   Parallel.ForEach(entities, entity =>
   {
       var result = ProcessEntity(entity); // Parallel
       
       lock (lockObj) // Only lock when necessary
       {
           AddResult(result);
       }
   });
   ```

---

## Troubleshooting

### Problem: No performance improvement

**Symptom:** Parallel version no faster than single-threaded.

**Solutions:**

1. **Check entity count:**
   ```csharp
   Logger.LogDebug("Entity count: {Count}", entities.Count);
   // Need at least 100-1000 entities for benefit
   ```

2. **Increase work per entity:**
   ```csharp
   // Too little work
   entity.GetComponent<TransformComponent>().Position += Vector2.One;
   
   // More substantial work
   CalculateComplexPathfinding(entity);
   ```

3. **Check CPU cores:**
   ```csharp
   Logger.LogInformation("CPU cores: {Count}", 
       Environment.ProcessorCount);
   // Need multiple cores for parallelism
   ```

---

### Problem: Race condition / data corruption

**Symptom:** Random crashes, incorrect values, inconsistent state.

**Solutions:**

1. **Use thread-safe collections:**
   ```csharp
   // Replace List<T> with ConcurrentBag<T>
   var results = new ConcurrentBag<Result>();
   ```

2. **Add synchronization:**
   ```csharp
   lock (_syncObject)
   {
       // Protect shared state
   }
   ```

3. **Remove shared state:**
   ```csharp
   // Best: Ensure each thread works on independent data
   ```

---

### Problem: Deadlock

**Symptom:** Application hangs, threads waiting forever.

**Solutions:**

1. **Avoid nested locks:**
   ```csharp
   // ❌ Bad - potential deadlock
   lock (lockA)
   {
       lock (lockB) { ... }
   }
   
   // ✅ Good - consistent lock ordering
   // Always acquire locks in same order
   ```

2. **Use timeouts:**
   ```csharp
   if (Monitor.TryEnter(lockObj, TimeSpan.FromSeconds(5)))
   {
       try
       {
           // Critical section
       }
       finally
       {
           Monitor.Exit(lockObj);
       }
   }
   ```

---

### Problem: Poor CPU utilization

**Symptom:** CPU cores not fully utilized.

**Solutions:**

1. **Increase MaxDegreeOfParallelism:**
   ```csharp
   var options = new ParallelOptions
   {
       MaxDegreeOfParallelism = Environment.ProcessorCount
   };
   
   Parallel.ForEach(entities, options, entity => { ... });
   ```

2. **Check work distribution:**
   ```csharp
   // Ensure entities have similar processing time
   // Avoid some entities taking much longer than others
   ```

---

## Summary

**When to parallelize:**

| Entity Count | Work Per Entity | Recommendation |
|--------------|-----------------|----------------|
| **< 100** | Any | Single-threaded |
| **100-1000** | Light | Single-threaded |
| **100-1000** | Heavy | Parallel |
| **> 1000** | Any | Parallel |

**Thread safety:**

| Pattern | Safe? | Notes |
|---------|-------|-------|
| **Multiple reads** | ✅ Yes | No synchronization needed |
| **Isolated writes** | ✅ Yes | Each entity independent |
| **Shared writes** | ❌ No | Need synchronization |
| **World modifications** | ❌ No | Main thread only |

**Synchronization tools:**

| Tool | Use Case | Performance |
|------|----------|-------------|
| `ConcurrentBag<T>` | Collect results | Fast |
| `lock` statement | Protect shared state | Moderate |
| `Interlocked` | Atomic operations | Very Fast |
| `Monitor` | Complex synchronization | Moderate |

**Best practices:**

- ✅ Materialize queries before parallelization
- ✅ Use concurrent collections
- ✅ Benchmark performance
- ✅ Keep work substantial per entity
- ✅ Minimize shared state
- ❌ Don't modify world structure in parallel
- ❌ Don't query during parallel processing
- ❌ Don't parallelize small workloads
- ❌ Don't use excessive locking

---

## Next Steps

- **[Systems Guide](systems.md)** - Learn about ECS systems
- **[Performance Optimization](../performance/optimization.md)** - Optimize game performance
- **[Queries](queries.md)** - Entity query patterns
- **[Components](components.md)** - Component design

---

## Quick Reference

```csharp
// Basic parallel processing
var entities = world.QueryEntities()
    .With<TransformComponent>()
    .ToList(); // Important: materialize first!

Parallel.ForEach(entities, entity =>
{
    var transform = entity.GetComponent<TransformComponent>();
    // Process entity (safe: independent data)
});

// Thread-safe collection
var results = new ConcurrentBag<Result>();

Parallel.ForEach(entities, entity =>
{
    var result = ProcessEntity(entity);
    results.Add(result); // Thread-safe
});

// Atomic counter
int counter = 0;

Parallel.ForEach(entities, entity =>
{
    if (IsActive(entity))
    {
        Interlocked.Increment(ref counter);
    }
});

// Lock for shared state
var lockObj = new object();

Parallel.ForEach(entities, entity =>
{
    var result = ProcessEntity(entity);
    
    lock (lockObj)
    {
        AddToSharedState(result);
    }
});

// Conditional parallelization
if (entities.Count > 1000)
{
    // Parallel for large counts
    Parallel.ForEach(entities, ProcessEntity);
}
else
{
    // Single-threaded for small counts
    foreach (var entity in entities)
    {
        ProcessEntity(entity);
    }
}

// Configure parallel options
var options = new ParallelOptions
{
    MaxDegreeOfParallelism = Environment.ProcessorCount
};

Parallel.ForEach(entities, options, ProcessEntity);
```

---

**Remember:** Only parallelize when single-threaded performance is insufficient. Measure first!