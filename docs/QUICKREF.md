# Quick Reference ⚡

> One-page reference for common Entitybase operations. Print it, bookmark it, love it! 📄

---

## Base URL

```
http://localhost:8000/v1/entitybase
```

---

## Health Check 🏥

```bash
curl http://localhost:8000/health
```

---

## Items (Q IDs) 🍕

| Action | Method | Endpoint | Example |
|--------|--------|----------|---------|
| Create | POST | `/entities/items` | [See tutorial](TUTORIAL.md) |
| Read | GET | `/entities/items/{id}` | `GET /entities/items/Q1` |
| Update | PUT | `/entities/items/{id}` | `PUT /entities/items/Q1` |
| Delete | DELETE | `/entities/items/{id}` | `DELETE /entities/items/Q1` |
| List | GET | `/entities` | `?entity_type=item` |
| JSON format | GET | `/entities/items/{id}.json` | `GET /entities/items/Q1.json` |
| Terms only | GET | `/entities/items/{id}/terms` | Labels, descriptions, aliases |

**Headers:** `X-User-ID: 1`, `X-Edit-Summary: your message`

---

## Properties (P IDs) 🏗️

| Action | Method | Endpoint |
|--------|--------|----------|
| Create | POST | `/entities/properties` |
| Read | GET | `/entities/properties/{id}` |
| Update | PUT | `/entities/properties/{id}` |
| Delete | DELETE | `/entities/properties/{id}` |

---

## Revisions 📦

| Action | Method | Endpoint |
|--------|--------|----------|
| List all | GET | `/entities/{type}/{id}/revisions` |
| Get one | GET | `/entities/{type}/{id}/revisions/{rev_id}` |
| Get latest | GET | `/entities/{type}/{id}/revisions/latest` |

---

## Statements 📝

| Action | Method | Endpoint |
|--------|--------|----------|
| Add/Update | PUT | `/entities/{type}/{id}` (include `statements` in body) |
| Delete | PATCH | `/entities/{type}/{id}` (use `statements` with empty array) |

---

## Search 🔍

```bash
# Search items by label
curl "http://localhost:8000/v1/entitybase/entities?entity_type=item&search=pizza"

# Filter by property
curl "http://localhost:8000/v1/entitybase/entities?entity_type=item&property=P1&value=Q1000000"
```

---

## Terms (Labels, Descriptions, Aliases) 🏷️

| Action | Method | Endpoint |
|--------|--------|----------|
| Get terms | GET | `/entities/{type}/{id}/terms` |
| Update labels | PUT | `/entities/{type}/{id}` |
| Update descriptions | PUT | `/entities/{type}/{id}` |
| Update aliases | PUT | `/entities/{type}/{id}` |
| Delete term | DELETE | `/entities/{type}/{id}/terms/{language}/{term_type}/{term_value}` |

---

## Entity Protection 🔒

| Action | Method | Endpoint |
|--------|--------|----------|
| Lock | POST | `/entities/{id}/lock` |
| Unlock | DELETE | `/entities/{id}/lock` |
| Archive | POST | `/entities/{id}/archive` |
| Unarchive | DELETE | `/entities/{id}/archive` |
| Semi-protect | POST | `/entities/{id}/semi-protect` |
| Unprotect | DELETE | `/entities/{id}/semi-protect` |

---

## Users 👤

| Action | Method | Endpoint |
|--------|--------|----------|
| Create | POST | `/users` |
| Get | GET | `/users/{id}` |
| Get watchlist | GET | `/users/{id}/watchlist` |
| Add to watchlist | POST | `/users/{id}/watchlist` |
| Remove from watchlist | DELETE | `/users/{id}/watchlist/{entity_id}` |

---

## RDF Export 🐢

```bash
# Get entity as Turtle
curl "http://localhost:8000/v1/entitybase/entities/items/Q1.ttl"

# Get all entities as Turtle (careful, this can be huge!)
curl "http://localhost:8000/v1/entitybase/rdf/entities.ttl"
```

---

## Common curl Headers 📋

```bash
-H "Content-Type: application/json" \
-H "X-User-ID: 1" \
-H "X-Edit-Summary: Adding info about pizza" \
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## Environment Variables ⚙️

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_HOST` | localhost | Vitess host |
| `DATABASE_PORT` | 33306 | Vitess port |
| `DATABASE_USER` | root | Database user |
| `DATABASE_PASSWORD` | password | Database password |
| `DATABASE_NAME` | wikibase | Database name |
| `S3_BUCKET` | — | S3 bucket name |
| `AWS_ACCESS_KEY_ID` | — | AWS key |
| `AWS_SECRET_ACCESS_KEY` | — | AWS secret |
| `API_HOST` | 0.0.0.0 | API listen address |
| `API_PORT` | 8000 | API port |

---

## Make Commands 🛠️

| Command | What it does |
|---------|--------------|
| `make api` | Start full stack (Docker + API) |
| `make stop` | Stop everything |
| `make test-unit` | Run unit tests |
| `make test-integration` | Run integration tests |
| `make test-e2e` | Run e2e tests |
| `make lint` | Run all linters |
| `make coverage` | Run tests with coverage |
| `make help` | See all commands |

---

## Ports 🚢

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |
| Vitess Admin | http://localhost:15100 |

---

## S3 Buckets 🪣

| Bucket | What it stores |
|--------|---------------|
| `terms` | Labels, descriptions, aliases |
| `statements` | Statement content (deduplicated) |
| `references` | Reference data |
| `qualifiers` | Qualifier data |
| `revisions` | Revision snapshots |
| `sitelinks` | Site links |
| `snaks` | Snak data |
| `wikibase-dumps` | Entity exports |

---

## Status Codes ✅

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized |
| 404 | Not found |
| 409 | Conflict (e.g., revision mismatch) |
| 500 | Server error |

---

## Debugging Tips 🐛

```bash
# See exactly what the server returns
curl -v http://localhost:8000/v1/entitybase/entities/items/Q1

# Check revision history when things go wrong
curl http://localhost:8000/v1/entitybase/entities/items/Q1/revisions

# Get entity in Wikidata JSON format (easier to compare)
curl http://localhost:8000/v1/entitybase/entities/items/Q1.json
```

---

## Related Docs 📚

- [Tutorial](TUTORIAL.md) — Step-by-step walkthrough
- [Getting Started](GETTING_STARTED.md) — Initial setup
- [Glossary](GLOSSARY.md) — Domain terms
- [Architecture](ARCHITECTURE/ARCHITECTURE.md) — Deep dive
- [API Endpoints](features/ENDPOINTS.md) — All endpoints
