# Tutorial: Hello Entitybase! 🌍

> A hands-on walkthrough to get you familiar with Entitybase. By the end, you'll have created items, properties, statements, and seen the revision history in action!

**Time needed:** ~10 minutes  
**Prerequisites:** Running instance (see [Getting Started](GETTING_STARTED.md))

---

## What You'll Learn 🧑‍🏫

1. ✅ Create your first item with labels and descriptions
2. ✅ Add properties and statements  
3. ✅ Query entities back
4. ✅ See revision history
5. ✅ Create a property (the building block of statements)

---

## Step 0: Check That Everything's Running 🏃

```bash
# Should return {"status":"ok"}
curl http://localhost:8000/health

# API docs are at http://localhost:8000/docs 📚
```

---

## Step 1: Create Your First Item 🎉

Let's create an item about... pizza! 🍕

```bash
curl -X POST http://localhost:8000/v1/entitybase/entities/items \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "labels": {
      "en": {"value": "Pizza", "language": "en"}
    },
    "descriptions": {
      "en": {"value": "Italian dish made of dough, tomato sauce, and cheese", "language": "en"}
    }
  }'
```

**What you get back:**

```json
{
  "entity_id": "Q1",
  "entity_type": "item",
  "labels": {"en": {"value": "Pizza", "language": "en"}},
  "descriptions": {"en": {"value": "Italian dish...", "language": "en"}},
  "revision_id": "1700000000000001",
  "modified": "2026-02-20T10:30:00Z"
}
```

> 🎯 **Congratulations!** You just created item **Q1**! The `revision_id` is your first immutable snapshot.

---

## Step 2: Add an Alias 🗣️

Aliases are alternative names for an item:

```bash
curl -X PUT http://localhost:8000/v1/entitybase/entities/items/Q1 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -H "X-Edit-Summary: Adding Italian name" \
  -d '{
    "labels": {
      "en": {"value": "Pizza", "language": "en"}
    },
    "aliases": {
      "en": [{"value": "Pizzetta"}, {"value": "Italian pizza"}]
    }
  }'
```

> 💡 **Notice the `X-Edit-Summary` header!** This is stored in the revision, making it easy to understand what changed.

---

## Step 3: Create a Property First 🏗️

Before adding statements, you need a property to describe *what* the statement is about:

```bash
curl -X POST http://localhost:8000/v1/entitybase/entities/properties \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "labels": {
      "en": {"value": "has ingredient", "language": "en"}
    },
    "descriptions": {
      "en": {"value": "food ingredient used in preparation", "language": "en"}
    },
    "data_type": "item"
  }'
```

**Response:**

```json
{
  "entity_id": "P1",
  "entity_type": "property",
  "labels": {"en": {"value": "has ingredient", "language": "en"}},
  "data_type": "item",
  "revision_id": "1700000000000002"
}
```

> 🎯 You created **P1** (property "has ingredient")! Properties define *what* kind of statement you can make.

---

## Step 4: Add a Statement to Your Item 🍕

Now let's say our pizza "has ingredient" cheese 🧀:

```bash
curl -X PUT http://localhost:8000/v1/entitybase/entities/items/Q1 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "labels": {
      "en": {"value": "Pizza", "language": "en"}
    },
    "statements": {
      "P1": [
        {
          "value": {
            "entity_type": "item",
            "numeric_id": 1000000,
            "id": "Q1000000"
          },
          "rank": "normal",
          "references": [
            {
              "hash": "abc123",
              "snaks": {
                "P16": [{"snaktype": "value", "property": "P16", "datavalue": {"value": "2024", "type": "string"}}]
              }
            }
          ]
        }
      ]
    }
  }'
```

> 📝 **What's happening here?**
> - `P1` is our property (has ingredient)
> - The value is another item (Q1000000 - let's pretend it's "mozzarella")
> - We added a reference (where this info came from)

---

## Step 5: Query Your Item Back 🔍

Get the full entity:

```bash
curl http://localhost:8000/v1/entitybase/entities/items/Q1
```

Get just the JSON (Wikidata format):

```bash
curl http://localhost:8000/v1/entitybase/entities/items/Q1.json
```

Get just the labels:

```bash
curl http://localhost:8000/v1/entitybase/entities/items/Q1/terms
```

---

## Step 6: See Revision History 📜

Here's the magic of immutable revisions:

```bash
curl http://localhost:8000/v1/entitybase/entities/items/Q1/revisions
```

**Response:**

```json
{
  "revisions": [
    {
      "revision_id": "1700000000000003",
      "timestamp": "2026-02-20T10:35:00Z",
      "user_id": "1",
      "comment": "Adding ingredient statement"
    },
    {
      "revision_id": "1700000000000002",
      "timestamp": "2026-02-20T10:32:00Z", 
      "user_id": "1",
      "comment": "Adding Italian name"
    },
    {
      "revision_id": "1700000000000001",
      "timestamp": "2026-02-20T10:30:00Z",
      "user_id": "1",
      "comment": "Created item"
    }
  ]
}
```

> 🔒 **Notice:** Every edit creates a NEW revision. The old ones are still there! This is the "immutable snapshots" magic.

---

## Step 7: Get a Specific Revision 📦

Want to see what Q1 looked like at a specific point in time?

```bash
curl http://localhost:8000/v1/entitybase/entities/items/Q1/revisions/1700000000000001
```

This is incredibly useful for:
- Debugging what changed
- Rolling back mistakes
- Auditing who did what

---

## Step 8: Try a Property Query 🔎

Find all items with a specific property:

```bash
curl "http://localhost:8000/v1/entitybase/entities?entity_type=item&property=P1&value=Q1000000"
```

---

## What Just Happened? 🎊

Here's what you built:

```
Q1 (Pizza) ──statement──▶ P1 (has ingredient) ──value──▶ Q1000000 (mozzarella)
                         │
                         └──reference──▶ P16 (publication date: 2024)
```

And every step was saved as an immutable revision!

---

## Next Steps 🚀

Now that you've got the basics, explore:

- [⚡ Quick Reference](QUICKREF.md) — Common commands at a glance
- [🔍 Glossary](GLOSSARY.md) — Learn the domain terms
- [🏗️ Architecture](ARCHITECTURE/ARCHITECTURE.md) — Deep dive into how it works
- [✨ Features](Features/ENDPOINTS.md) — All the API endpoints

---

## Python Example 📘

Here's the same workflow in Python:

```python
import httpx

async def main():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create item
        r = await client.post(
            "/v1/entitybase/entities/items",
            json={"labels": {"en": {"value": "Pizza", "language": "en"}}},
            headers={"X-User-ID": "1"}
        )
        print(f"Created: {r.json()}")
        
        # Get it back
        r = await client.get("/v1/entitybase/entities/items/Q1")
        print(f"Retrieved: {r.json()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

**Happy hacking!** 🎉 If you get stuck, check the [FAQ](../../FAQ.md) or open an issue on GitHub.
