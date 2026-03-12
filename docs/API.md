# Entitybase Backend API Documentation
**Version**: v1.2026.3.2
**Base URL**: See `/docs` for interactive API explorer

---

## Quick Start: Creating Entities

### Creating an Item

**Note:** Currently, item creation only supports empty items. Use the endpoint below to create an item, then add labels/descriptions using the update endpoints.

```bash
# Create an empty item
curl -X POST https://api.example.com/v1/entitybase/entities/items \
  -H "X-User-ID: 1" \
  -H "X-Edit-Summary: Creating new item"
```

### Creating a Lexeme (with full data)

Lexeme creation supports full entity data in the request body:

```json
{
  "type": "lexeme",
  "language": "Q1860",
  "lexicalCategory": "Q1084",
  "lemmas": {"en": {"language": "en", "value": "test"}},
  "labels": {"en": {"language": "en", "value": "test lexeme"}},
  "forms": [
    {
      "representations": {"en": {"language": "en", "value": "tests"}},
      "grammaticalFeatures": ["Q110786"]
    }
  ],
  "senses": [
    {
      "glosses": {"en": {"language": "en", "value": "a test"}}
    }
  ]
}
```

### Adding Labels and Descriptions to Existing Entities

After creating an entity, add labels using:

```bash
# Add a label
curl -X PUT https://api.example.com/v1/entitybase/entities/Q123/labels/en \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -H "X-Edit-Summary: Adding label" \
  -d '{"language": "en", "value": "My Item"}'
```

### MonolingualText Format

Labels, descriptions, aliases, and other term data use the MonolingualText format:

```json
{
  "language": "en",
  "value": "The text content"
}
```

---

## Authentication
All endpoints requiring modifications (POST, PUT, PATCH, DELETE) require headers:
| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `X-User-ID` | integer | Yes | User ID making the edit |
| `X-Edit-Summary` | string | Yes | Edit summary (1-200 chars) |
| `X-Base-Revision-ID` | integer | No | For optimistic locking |

---

## Items
### POST /v1/entitybase/entities/items
**Create Item**
Create a new empty item entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_item_v1_entitybase_entities_items_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/items` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Properties
### POST /v1/entitybase/entities/properties
**Create Property**
Create a new empty property entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_property_v1_entitybase_entities_properties_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/properties` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entity/{entity_id}/properties/{property_list}
**Get Entity Property Hashes**
Get statement hashes for specified properties in an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_property_hashes_v1_entitybase_entity__entity_id__properties__property_list__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entity/{entity_id}/properties/{property_list}` |
| Parameters | `entity_id` (path, Required) `property_list` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Lexemes
### POST /v1/entitybase/entities/lexemes
**Create Lexeme**
Create a new lexeme entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_lexeme_v1_entitybase_entities_lexemes_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityCreateRequest](#entitycreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "id": "string",
  "type": "string",
  "labels": {},
  "descriptions": {},
  "claims": {},
  "aliases": {},
  "sitelinks": {},
  "forms": [
    {}
  ],
  "senses": [
    {}
  ],
  "lemmas": {},
  "language": "string",
  "lexical_category": "string",
  "is_mass_edit": true,
  "edit_type": null,
  "state": null,
  "is_autoconfirmed_user": true,
  "is_semi_protected": true,
  "is_locked": true,
  "is_archived": true,
  "is_dangling": true,
  "is_mass_edit_protected": true
}
```

---

### DELETE /v1/entitybase/entities/lexemes/forms/{form_id}
**Delete Form**
Delete a form by ID.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_form_v1_entitybase_entities_lexemes_forms__form_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}` |
| Parameters | `form_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/forms/{form_id}
**Get Form By Id**
Get single form by ID (accepts L42-F1 or F1 format).
| Aspect | Details |
|--------|---------|
| Operation ID | `get_form_by_id_v1_entitybase_entities_lexemes_forms__form_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}` |
| Parameters | `form_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/forms/{form_id}/representation
**Get Form Representations**
Get all representations for a form.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_form_representations_v1_entitybase_entities_lexemes_forms__form_id__representation_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}/representation` |
| Parameters | `form_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}
**Delete Form Representation**
Delete form representation for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_form_representation_v1_entitybase_entities_lexemes_forms__form_id__representation__langcode__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}
**Get Form Representation**
Get representation for a form in specific language.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_form_representation_v1_entitybase_entities_lexemes_forms__form_id__representation__langcode__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}
**Add Form Representation**
Add a new form representation for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_form_representation_v1_entitybase_entities_lexemes_forms__form_id__representation__langcode__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### PUT /v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}
**Update Form Representation**
Update form representation for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_form_representation_v1_entitybase_entities_lexemes_forms__form_id__representation__langcode__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### POST /v1/entitybase/entities/lexemes/forms/{form_id}/statements
**Add Form Statement**
Add a statement to a form.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_form_statement_v1_entitybase_entities_lexemes_forms__form_id__statements_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/forms/{form_id}/statements` |
| Parameters | `form_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[AddStatementRequest](#addstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "claim": {}
}
```

---

### DELETE /v1/entitybase/entities/lexemes/senses/{sense_id}
**Delete Sense**
Delete a sense by ID.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_sense_v1_entitybase_entities_lexemes_senses__sense_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}` |
| Parameters | `sense_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/senses/{sense_id}
**Get Sense By Id**
Get single sense by ID (accepts L42-S1 or S1 format).
| Aspect | Details |
|--------|---------|
| Operation ID | `get_sense_by_id_v1_entitybase_entities_lexemes_senses__sense_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}` |
| Parameters | `sense_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/senses/{sense_id}/glosses
**Get Sense Glosses**
Get all glosses for a sense.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_sense_glosses_v1_entitybase_entities_lexemes_senses__sense_id__glosses_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}/glosses` |
| Parameters | `sense_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Delete Sense Gloss**
Delete sense gloss for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_sense_gloss_v1_entitybase_entities_lexemes_senses__sense_id__glosses__langcode__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Get Sense Gloss By Language**
Get gloss for a sense in specific language.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_sense_gloss_by_language_v1_entitybase_entities_lexemes_senses__sense_id__glosses__langcode__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Add Sense Gloss**
Add a new sense gloss for a language.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_sense_gloss_v1_entitybase_entities_lexemes_senses__sense_id__glosses__langcode__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### PUT /v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Update Sense Gloss**
Update sense gloss for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_sense_gloss_v1_entitybase_entities_lexemes_senses__sense_id__glosses__langcode__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### POST /v1/entitybase/entities/lexemes/senses/{sense_id}/statements
**Add Sense Statement**
Add a statement to a sense.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_sense_statement_v1_entitybase_entities_lexemes_senses__sense_id__statements_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/senses/{sense_id}/statements` |
| Parameters | `sense_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[AddStatementRequest](#addstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "claim": {}
}
```

---

### GET /v1/entitybase/entities/lexemes/{lexeme_id}/forms
**Get Lexeme Forms**
List all forms for a lexeme, sorted by numeric suffix.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_forms_v1_entitybase_entities_lexemes__lexeme_id__forms_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/forms` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/lexemes/{lexeme_id}/forms
**Create Lexeme Form**
Create a new form for a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_lexeme_form_v1_entitybase_entities_lexemes__lexeme_id__forms_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/forms` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[FormCreateRequest](#formcreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "representations": {},
  "grammatical_features": [
    "string"
  ],
  "claims": {}
}
```

---

### GET /v1/entitybase/entities/lexemes/{lexeme_id}/language
**Get Lexeme Language**
Get the language of a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_language_v1_entitybase_entities_lexemes__lexeme_id__language_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/language` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### PUT /v1/entitybase/entities/lexemes/{lexeme_id}/language
**Update Lexeme Language**
Update the language of a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_lexeme_language_v1_entitybase_entities_lexemes__lexeme_id__language_put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/language` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[LexemeLanguageRequest](#lexemelanguagerequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string"
}
```

---

### GET /v1/entitybase/entities/lexemes/{lexeme_id}/lemmas
**Get Lexeme Lemmas**
Get all lemmas for a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_lemmas_v1_entitybase_entities_lexemes__lexeme_id__lemmas_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lemmas` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Delete Lexeme Lemma**
Delete lemma for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_lexeme_lemma_v1_entitybase_entities_lexemes__lexeme_id__lemmas__langcode__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Get Lexeme Lemma**
Get lemma for a lexeme in specific language.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_lemma_v1_entitybase_entities_lexemes__lexeme_id__lemmas__langcode__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Add Lexeme Lemma**
Add a new lemma for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_lexeme_lemma_v1_entitybase_entities_lexemes__lexeme_id__lemmas__langcode__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### PUT /v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Update Lexeme Lemma**
Update lemma for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_lexeme_lemma_v1_entitybase_entities_lexemes__lexeme_id__lemmas__langcode__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### GET /v1/entitybase/entities/lexemes/{lexeme_id}/lexicalcategory
**Get Lexeme Lexicalcategory**
Get the lexical category of a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_lexicalcategory_v1_entitybase_entities_lexemes__lexeme_id__lexicalcategory_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lexicalcategory` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### PUT /v1/entitybase/entities/lexemes/{lexeme_id}/lexicalcategory
**Update Lexeme Lexicalcategory**
Update the lexical category of a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_lexeme_lexicalcategory_v1_entitybase_entities_lexemes__lexeme_id__lexicalcategory_put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/lexicalcategory` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[LexemeLexicalCategoryRequest](#lexemelexicalcategoryrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "lexical_category": "string"
}
```

---

### GET /v1/entitybase/entities/lexemes/{lexeme_id}/senses
**Get Lexeme Senses**
List all senses for a lexeme, sorted by numeric suffix.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_senses_v1_entitybase_entities_lexemes__lexeme_id__senses_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/senses` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/lexemes/{lexeme_id}/senses
**Create Lexeme Sense**
Create a new sense for a lexeme.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_lexeme_sense_v1_entitybase_entities_lexemes__lexeme_id__senses_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/lexemes/{lexeme_id}/senses` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[SenseCreateRequest](#sensecreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "glosses": {},
  "claims": {}
}
```

---

## Entities
### DELETE /v1/entitybase/entities/{entity_id}
**Delete Entity**
Delete an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_v1_entitybase_entities__entity_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityDeleteRequest](#entitydeleterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "delete_type": null
}
```

---

### GET /v1/entitybase/entities/{entity_id}
**Get Entity**
Retrieve a single entity by its ID.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_v1_entitybase_entities__entity_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}.json
**Get Entity Data Json**
Get entity data in JSON format.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_data_json_v1_entitybase_entities__entity_id__json_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}.json` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}.ttl
**Get Entity Data Turtle**
Get entity data in Turtle format.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_data_turtle_v1_entitybase_entities__entity_id__ttl_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}.ttl` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/{entity_id}/aliases/{language_code}
**Delete Entity Aliases**
Delete all aliases for entity language.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_aliases_v1_entitybase_entities__entity_id__aliases__language_code__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/aliases/{language_code}
**Get Entity Aliases**
Get entity alias texts for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_aliases_v1_entitybase_entities__entity_id__aliases__language_code__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/{entity_id}/aliases/{language_code}
**Add Entity Alias**
Add a single alias to entity for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_alias_v1_entitybase_entities__entity_id__aliases__language_code__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### PUT /v1/entitybase/entities/{entity_id}/aliases/{language_code}
**Update Entity Aliases**
Update entity aliases for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_entity_aliases_v1_entitybase_entities__entity_id__aliases__language_code__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | Inline schema |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/{entity_id}/archive
**Unarchive Entity**
Unarchive an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `unarchive_entity_v1_entitybase_entities__entity_id__archive_delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/archive` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### POST /v1/entitybase/entities/{entity_id}/archive
**Archive Entity**
Archive an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `archive_entity_v1_entitybase_entities__entity_id__archive_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/archive` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### GET /v1/entitybase/entities/{entity_id}/backlinks
**Get Entity Backlinks**
Get backlinks for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_backlinks_v1_entitybase_entities__entity_id__backlinks_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/backlinks` |
| Parameters | `entity_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/{entity_id}/descriptions/{language_code}
**Delete Entity Description**
Delete entity description for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_description_v1_entitybase_entities__entity_id__descriptions__language_code__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/descriptions/{language_code}
**Get Entity Description**
Get entity description text for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_description_v1_entitybase_entities__entity_id__descriptions__language_code__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/{entity_id}/descriptions/{language_code}
**Add Entity Description**
Add a new description to entity for language (alias for PUT).
| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_description_v1_entitybase_entities__entity_id__descriptions__language_code__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### PUT /v1/entitybase/entities/{entity_id}/descriptions/{language_code}
**Update Entity Description**
Update entity description for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_entity_description_v1_entitybase_entities__entity_id__descriptions__language_code__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### DELETE /v1/entitybase/entities/{entity_id}/labels/{language_code}
**Delete Entity Label**
Delete entity label for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_label_v1_entitybase_entities__entity_id__labels__language_code__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/labels/{language_code}
**Get Entity Label**
Get entity label text for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_label_v1_entitybase_entities__entity_id__labels__language_code__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/{entity_id}/labels/{language_code}
**Add Entity Label**
Add a new label to entity for language (alias for PUT).
| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_label_v1_entitybase_entities__entity_id__labels__language_code__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### PUT /v1/entitybase/entities/{entity_id}/labels/{language_code}
**Update Entity Label**
Update entity label for language.
| Aspect | Details |
|--------|---------|
| Operation ID | `update_entity_label_v1_entitybase_entities__entity_id__labels__language_code__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "language": "string",
  "value": "string"
}
```

---

### DELETE /v1/entitybase/entities/{entity_id}/lock
**Unlock Entity**
Remove lock from an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `unlock_entity_v1_entitybase_entities__entity_id__lock_delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/lock` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### POST /v1/entitybase/entities/{entity_id}/lock
**Lock Entity**
Lock an entity from edits.
| Aspect | Details |
|--------|---------|
| Operation ID | `lock_entity_v1_entitybase_entities__entity_id__lock_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/lock` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### DELETE /v1/entitybase/entities/{entity_id}/mass-edit-protect
**Mass Edit Unprotect Entity**
Remove mass edit protection from an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `mass_edit_unprotect_entity_v1_entitybase_entities__entity_id__mass_edit_protect_delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/mass-edit-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### POST /v1/entitybase/entities/{entity_id}/mass-edit-protect
**Mass Edit Protect Entity**
Add mass edit protection to an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `mass_edit_protect_entity_v1_entitybase_entities__entity_id__mass_edit_protect_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/mass-edit-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### GET /v1/entitybase/entities/{entity_id}/properties
**Get Entity Properties**
Get list of unique property IDs for an entity's head revision.

Returns sorted list of properties used in entity statements.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_properties_v1_entitybase_entities__entity_id__properties_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/properties` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/{entity_id}/properties/{property_id}
**Add Entity Property**
Add claims for a single property to an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_property_v1_entitybase_entities__entity_id__properties__property_id__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/properties/{property_id}` |
| Parameters | `entity_id` (path, Required) `property_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[AddPropertyRequest](#addpropertyrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "claims": [
    {}
  ]
}
```

---

### GET /v1/entitybase/entities/{entity_id}/properties/{property_list}
**Get Entity Property Hashes**
Get entity property hashes for specified properties.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_property_hashes_v1_entitybase_entities__entity_id__properties__property_list__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/properties/{property_list}` |
| Parameters | `entity_id` (path, Required) `property_list` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/property_counts
**Get Entity Property Counts**
Get statement counts per property for an entity's head revision.

Returns dict mapping property ID -> count of statements.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_property_counts_v1_entitybase_entities__entity_id__property_counts_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/property_counts` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/{entity_id}/revert
**Revert Entity**
Revert entity to a previous revision.
| Aspect | Details |
|--------|---------|
| Operation ID | `revert_entity_v1_entitybase_entities__entity_id__revert_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/revert` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityRevertRequest](#entityrevertrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "to_revision_id": 0,
  "watchlist_context": null
}
```

---

### GET /v1/entitybase/entities/{entity_id}/revision/{revision_id}
**Get Entity Revision**
Get a specific revision of an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_revision_v1_entitybase_entities__entity_id__revision__revision_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/revision/{revision_id}` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/revision/{revision_id}/json
**Get Entity Json Revision**
Get JSON representation of a specific entity revision.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_json_revision_v1_entitybase_entities__entity_id__revision__revision_id__json_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/revision/{revision_id}/json` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/revision/{revision_id}/ttl
**Get Entity Ttl Revision**
Get Turtle (TTL) representation of a specific entity revision.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_ttl_revision_v1_entitybase_entities__entity_id__revision__revision_id__ttl_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/revision/{revision_id}/ttl` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) `format` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/revisions
**Get Entity History**
Get the revision history for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_history_v1_entitybase_entities__entity_id__revisions_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/revisions` |
| Parameters | `entity_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/{entity_id}/semi-protect
**Unsemi Protect Entity**
Remove semi-protection from an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `unsemi_protect_entity_v1_entitybase_entities__entity_id__semi_protect_delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/semi-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### POST /v1/entitybase/entities/{entity_id}/semi-protect
**Semi Protect Entity**
Semi-protect an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `semi_protect_entity_v1_entitybase_entities__entity_id__semi_protect_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/semi-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "edit_summary": null
}
```

---

### GET /v1/entitybase/entities/{entity_id}/sitelinks
**Get All Sitelinks**
Get all sitelinks for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_all_sitelinks_v1_entitybase_entities__entity_id__sitelinks_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/sitelinks` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/entities/{entity_id}/sitelinks/{site}
**Delete Entity Sitelink**
Delete a sitelink from an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_sitelink_v1_entitybase_entities__entity_id__sitelinks__site__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/sitelinks/{site}
**Get Entity Sitelink**
Get a single sitelink for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_sitelink_v1_entitybase_entities__entity_id__sitelinks__site__get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/entities/{entity_id}/sitelinks/{site}
**Post Entity Sitelink**
Add a new sitelink for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `post_entity_sitelink_v1_entitybase_entities__entity_id__sitelinks__site__post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[SitelinkData](#sitelinkdata)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "title": "string",
  "badges": [
    "string"
  ]
}
```

---

### PUT /v1/entitybase/entities/{entity_id}/sitelinks/{site}
**Put Entity Sitelink**
Update an existing sitelink for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `put_entity_sitelink_v1_entitybase_entities__entity_id__sitelinks__site__put` |
| Method | `PUT` |
| Path | `/v1/entitybase/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[SitelinkData](#sitelinkdata)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "title": "string",
  "badges": [
    "string"
  ]
}
```

---

### POST /v1/entitybase/entities/{entity_id}/statements
**Add Entity Statement**
Add a single statement to an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_statement_v1_entitybase_entities__entity_id__statements_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/statements` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[AddStatementRequest](#addstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "claim": {}
}
```

---

### DELETE /v1/entitybase/entities/{entity_id}/statements/{statement_hash}
**Remove Entity Statement**
Remove a statement by hash from an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `remove_entity_statement_v1_entitybase_entities__entity_id__statements__statement_hash__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/entities/{entity_id}/statements/{statement_hash}` |
| Parameters | `entity_id` (path, Required) `statement_hash` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[RemoveStatementRequest](#removestatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{}
```

---

### PATCH /v1/entitybase/entities/{entity_id}/statements/{statement_hash}
**Patch Entity Statement**
Replace a statement by hash with new claim data.
| Aspect | Details |
|--------|---------|
| Operation ID | `patch_entity_statement_v1_entitybase_entities__entity_id__statements__statement_hash__patch` |
| Method | `PATCH` |
| Path | `/v1/entitybase/entities/{entity_id}/statements/{statement_hash}` |
| Parameters | `entity_id` (path, Required) `statement_hash` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[PatchStatementRequest](#patchstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "claim": {}
}
```

---

## Statements
### GET /v1/entitybase/statements/batch
**Get Batch Statements**
Get statement hashes for multiple entities.

Query params:
- entity_ids: Comma-separated entity IDs (e.g., Q1,Q2,Q3). Max 20.
- property_ids: Optional comma-separated property IDs to filter (e.g., P31,P279).

Returns dict mapping entity_id → property_id → list of statement hashes.
Entities not found return empty dict for that entity_id.

Example: GET /statements/batch?entity_ids=Q1,Q2&property_ids=P31
Returns: {"Q1": {"P31": [123, 456]}, "Q2": {"P31": [789]}}
| Aspect | Details |
|--------|---------|
| Operation ID | `get_batch_statements_v1_entitybase_statements_batch_get` |
| Method | `GET` |
| Path | `/v1/entitybase/statements/batch` |
| Parameters | `entity_ids` (query, Required) `property_ids` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/statements/cleanup-orphaned
**Cleanup Orphaned Statements**
Clean up orphaned statements that are no longer referenced.
| Aspect | Details |
|--------|---------|
| Operation ID | `cleanup_orphaned_statements_v1_entitybase_statements_cleanup_orphaned_post` |
| Method | `POST` |
| Path | `/v1/entitybase/statements/cleanup-orphaned` |
| Request Body | `[CleanupOrphanedRequest](#cleanuporphanedrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "older_than_days": 0,
  "limit": 0
}
```

---

### GET /v1/entitybase/statements/most_used
**Get Most Used Statements**
Get most used statements based on reference count.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_most_used_statements_v1_entitybase_statements_most_used_get` |
| Method | `GET` |
| Path | `/v1/entitybase/statements/most_used` |
| Parameters | `limit` (query, Optional) `min_ref_count` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/statements/{content_hash}
**Get Statement**
Retrieve a single statement by its content hash.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_statement_v1_entitybase_statements__content_hash__get` |
| Method | `GET` |
| Path | `/v1/entitybase/statements/{content_hash}` |
| Parameters | `content_hash` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Statistics
### GET /v1/entitybase/stats
**Get General Stats**
Get general wiki statistics.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_general_stats_v1_entitybase_stats_get` |
| Method | `GET` |
| Path | `/v1/entitybase/stats` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |


---

## Watchlist
### GET /v1/entitybase/users/{user_id}/watchlist
**Get Watches**
Get user's watchlist.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_watches_v1_entitybase_users__user_id__watchlist_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/watchlist` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/users/{user_id}/watchlist
**Add Watch**
Add a watchlist entry for user.
| Aspect | Details |
|--------|---------|
| Operation ID | `add_watch_v1_entitybase_users__user_id__watchlist_post` |
| Method | `POST` |
| Path | `/v1/entitybase/users/{user_id}/watchlist` |
| Parameters | `user_id` (path, Required) |
| Request Body | `[WatchlistAddRequest](#watchlistaddrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "entity_id": "string",
  "properties": null
}
```

---

### GET /v1/entitybase/users/{user_id}/watchlist/notifications
**Get Notifications**
Get user's recent watchlist notifications.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_notifications_v1_entitybase_users__user_id__watchlist_notifications_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/watchlist/notifications` |
| Parameters | `user_id` (path, Required) `hours` (query, Optional) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### PUT /v1/entitybase/users/{user_id}/watchlist/notifications/{notification_id}/check
**Mark Checked**
Mark a notification as checked.
| Aspect | Details |
|--------|---------|
| Operation ID | `mark_checked_v1_entitybase_users__user_id__watchlist_notifications__notification_id__check_put` |
| Method | `PUT` |
| Path | `/v1/entitybase/users/{user_id}/watchlist/notifications/{notification_id}/check` |
| Parameters | `user_id` (path, Required) `notification_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/users/{user_id}/watchlist/remove
**Remove Watch**
Remove a watchlist entry for user.
| Aspect | Details |
|--------|---------|
| Operation ID | `remove_watch_v1_entitybase_users__user_id__watchlist_remove_post` |
| Method | `POST` |
| Path | `/v1/entitybase/users/{user_id}/watchlist/remove` |
| Parameters | `user_id` (path, Required) |
| Request Body | `[WatchlistRemoveRequest](#watchlistremoverequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "entity_id": "string",
  "properties": null
}
```

---

### GET /v1/entitybase/users/{user_id}/watchlist/stats
**Get Watch Counts**
Get user's watchlist statistics.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_watch_counts_v1_entitybase_users__user_id__watchlist_stats_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/watchlist/stats` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/users/{user_id}/watchlist/{watch_id}
**Remove Watch By Id**
Remove a watchlist entry by ID.
| Aspect | Details |
|--------|---------|
| Operation ID | `remove_watch_by_id_v1_entitybase_users__user_id__watchlist__watch_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/users/{user_id}/watchlist/{watch_id}` |
| Parameters | `user_id` (path, Required) `watch_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Import
### POST /v1/entitybase/import
**Import a single entity (item, property, or lexeme)**
Import a single entity of any type.

This unified endpoint accepts items, properties, and lexemes.
The entity type is determined by the 'type' field in the request.

Supported entity types:
- item: Q-prefixed entities (e.g., Q42)
- property: P-prefixed entities (e.g., P31)
- lexeme: L-prefixed entities (e.g., L123)

Parameters:
- id: Entity ID (required for import, auto-assignment not supported)
- type: Entity type (item, property, lexeme)
- labels: Language-specific labels
- descriptions: Language-specific descriptions
- claims: Statements/claims
- sitelinks: Site links (items only)
- forms: Forms (lexemes only)
- senses: Senses (lexemes only)
- lemmas: Lemmas (lexemes only)
- aliases: Aliases

Returns:
- EntityResponse with created entity data

Errors:
- 409: Entity already exists
- 400: Validation error
| Aspect | Details |
|--------|---------|
| Operation ID | `import_entity_v1_entitybase_import_post` |
| Method | `POST` |
| Path | `/v1/entitybase/import` |
| Request Body | `[EntityCreateRequest](#entitycreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "id": "string",
  "type": "string",
  "labels": {},
  "descriptions": {},
  "claims": {},
  "aliases": {},
  "sitelinks": {},
  "forms": [
    {}
  ],
  "senses": [
    {}
  ],
  "lemmas": {},
  "language": "string",
  "lexical_category": "string",
  "is_mass_edit": true,
  "edit_type": null,
  "state": null,
  "is_autoconfirmed_user": true,
  "is_semi_protected": true,
  "is_locked": true,
  "is_archived": true,
  "is_dangling": true,
  "is_mass_edit_protected": true
}
```

---

## Redirects
### POST /v1/entitybase/entities/{entity_id}/revert-redirect
**Revert Entity Redirect**
| Aspect | Details |
|--------|---------|
| Operation ID | `revert_entity_redirect_v1_entitybase_entities__entity_id__revert_redirect_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/revert-redirect` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[RedirectRevertRequest](#redirectrevertrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "revert_to_revision_id": 0,
  "created_by": "string"
}
```

---

### POST /v1/entitybase/redirects
**Create Entity Redirect**
Create a redirect for an entity.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_entity_redirect_v1_entitybase_redirects_post` |
| Method | `POST` |
| Path | `/v1/entitybase/redirects` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityRedirectRequest](#entityredirectrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "redirect_from_id": "string",
  "redirect_to_id": "string",
  "created_by": "string"
}
```

---

## List
### GET /v1/entitybase/entities
**List Entities**
List entities based on type, status, edit_type, limit, and offset.
| Aspect | Details |
|--------|---------|
| Operation ID | `list_entities_v1_entitybase_entities_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities` |
| Parameters | `entity_type` (query, Optional) `status` (query, Optional) `edit_type` (query, Optional) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/items
**List Items**
List all items (Q-prefixed entities).
| Aspect | Details |
|--------|---------|
| Operation ID | `list_items_v1_entitybase_entities_items_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/items` |
| Parameters | `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/lexemes
**List Lexemes**
List all lexemes (L-prefixed entities).
| Aspect | Details |
|--------|---------|
| Operation ID | `list_lexemes_v1_entitybase_entities_lexemes_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/lexemes` |
| Parameters | `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/properties
**List Properties**
List all properties (P-prefixed entities).
| Aspect | Details |
|--------|---------|
| Operation ID | `list_properties_v1_entitybase_entities_properties_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/properties` |
| Parameters | `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Debug
### GET /v1/entitybase/debug/entity/{entity_id}
**Debug Entity**
Debug endpoint to check entity in database.

This endpoint queries the entity_id_mapping table directly to verify
if an entity exists and what its internal_id is.
| Aspect | Details |
|--------|---------|
| Operation ID | `debug_entity_v1_entitybase_debug_entity__entity_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/debug/entity/{entity_id}` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/debug/entity_head/{entity_id}
**Debug Entity Head**
Debug endpoint to check entity_head table.
| Aspect | Details |
|--------|---------|
| Operation ID | `debug_entity_head_v1_entitybase_debug_entity_head__entity_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/debug/entity_head/{entity_id}` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Health
### GET /health
**Health Check Endpoint**
Health check endpoint for monitoring service status.
| Aspect | Details |
|--------|---------|
| Operation ID | `health_check_endpoint_health_get` |
| Method | `GET` |
| Path | `/health` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |


---

## Version
### GET /version
**Version Endpoint**
Return API and EntityBase versions.
| Aspect | Details |
|--------|---------|
| Operation ID | `version_endpoint_version_get` |
| Method | `GET` |
| Path | `/version` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |


---

## Settings
### GET /settings
**Get Settings**
Get current application settings (excludes sensitive values).
| Aspect | Details |
|--------|---------|
| Operation ID | `get_settings_settings_get` |
| Method | `GET` |
| Path | `/settings` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |


---

## Interactions
### POST /v1/entitybase/entities/{entity_id}/revisions/{revision_id}/thank
**Send Thank Endpoint**
Send a thank for a specific revision.
| Aspect | Details |
|--------|---------|
| Operation ID | `send_thank_endpoint_v1_entitybase_entities__entity_id__revisions__revision_id__thank_post` |
| Method | `POST` |
| Path | `/v1/entitybase/entities/{entity_id}/revisions/{revision_id}/thank` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) `X-User-ID` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/entities/{entity_id}/revisions/{revision_id}/thanks
**Get Revision Thanks Endpoint**
Get all thanks for a specific revision.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_revision_thanks_endpoint_v1_entitybase_entities__entity_id__revisions__revision_id__thanks_get` |
| Method | `GET` |
| Path | `/v1/entitybase/entities/{entity_id}/revisions/{revision_id}/thanks` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### DELETE /v1/entitybase/statements/{statement_hash}/endorse
**Withdraw Endorsement Endpoint**
Withdraw endorsement from a statement.
| Aspect | Details |
|--------|---------|
| Operation ID | `withdraw_endorsement_endpoint_v1_entitybase_statements__statement_hash__endorse_delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/statements/{statement_hash}/endorse` |
| Parameters | `statement_hash` (path, Required) `X-User-ID` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### POST /v1/entitybase/statements/{statement_hash}/endorse
**Endorse Statement Endpoint**
Endorse a statement to signal trust.
| Aspect | Details |
|--------|---------|
| Operation ID | `endorse_statement_endpoint_v1_entitybase_statements__statement_hash__endorse_post` |
| Method | `POST` |
| Path | `/v1/entitybase/statements/{statement_hash}/endorse` |
| Parameters | `statement_hash` (path, Required) `X-User-ID` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/statements/{statement_hash}/endorsements
**Get Statement Endorsements Endpoint**
Get endorsements for a statement.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_statement_endorsements_endpoint_v1_entitybase_statements__statement_hash__endorsements_get` |
| Method | `GET` |
| Path | `/v1/entitybase/statements/{statement_hash}/endorsements` |
| Parameters | `statement_hash` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `include_removed` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/statements/{statement_hash}/endorsements/stats
**Get Statement Endorsement Stats**
Get endorsement statistics for a statement.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_statement_endorsement_stats_v1_entitybase_statements__statement_hash__endorsements_stats_get` |
| Method | `GET` |
| Path | `/v1/entitybase/statements/{statement_hash}/endorsements/stats` |
| Parameters | `statement_hash` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/users/{user_id}/endorsements
**Get User Endorsements Endpoint**
Get endorsements given by a user.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_endorsements_endpoint_v1_entitybase_users__user_id__endorsements_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/endorsements` |
| Parameters | `user_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `include_removed` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/users/{user_id}/endorsements/stats
**Get User Endorsement Stats Endpoint**
Get endorsement statistics for a user.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_endorsement_stats_endpoint_v1_entitybase_users__user_id__endorsements_stats_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/endorsements/stats` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/users/{user_id}/thanks/received
**Get Thanks Received Endpoint**
Get thanks received by user.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_thanks_received_endpoint_v1_entitybase_users__user_id__thanks_received_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/thanks/received` |
| Parameters | `user_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `hours` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/users/{user_id}/thanks/sent
**Get Thanks Sent Endpoint**
Get thanks sent by user.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_thanks_sent_endpoint_v1_entitybase_users__user_id__thanks_sent_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/thanks/sent` |
| Parameters | `user_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `hours` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Users
### POST /v1/entitybase/users
**Create User**
Create a new user.
| Aspect | Details |
|--------|---------|
| Operation ID | `create_user_v1_entitybase_users_post` |
| Method | `POST` |
| Path | `/v1/entitybase/users` |
| Request Body | `[UserCreateRequest](#usercreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "user_id": 0
}
```

---

### GET /v1/entitybase/users/stat
**Get User Stats**
Get user statistics.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_stats_v1_entitybase_users_stat_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/stat` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |


---

### DELETE /v1/entitybase/users/{user_id}
**Delete User**
Delete a user by ID.
| Aspect | Details |
|--------|---------|
| Operation ID | `delete_user_v1_entitybase_users__user_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entitybase/users/{user_id}` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/users/{user_id}
**Get User**
Get user information by MediaWiki user ID.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_v1_entitybase_users__user_id__get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/users/{user_id}/activity
**Get User Activity**
Get user's activity with filtering.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_activity_v1_entitybase_users__user_id__activity_get` |
| Method | `GET` |
| Path | `/v1/entitybase/users/{user_id}/activity` |
| Parameters | `user_id` (path, Required) `type` (query, Optional) `hours` (query, Optional) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### PUT /v1/entitybase/users/{user_id}/watchlist/toggle
**Toggle Watchlist**
Enable or disable watchlist for user.
| Aspect | Details |
|--------|---------|
| Operation ID | `toggle_watchlist_v1_entitybase_users__user_id__watchlist_toggle_put` |
| Method | `PUT` |
| Path | `/v1/entitybase/users/{user_id}/watchlist/toggle` |
| Parameters | `user_id` (path, Required) |
| Request Body | `[WatchlistToggleRequest](#watchlisttogglerequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

**Request Body Example:**
```json
{
  "enabled": true
}
```

---

## Resolve
### GET /v1/entitybase/resolve/aliases/{hashes}
**Get Batch Aliases**
Get batch aliases by hashes.

Supports single hash (e.g., /resolve/aliases/123) or comma-separated batch
(e.g., /resolve/aliases/123,456,789).

Returns dict mapping hash strings to alias text lists. Max 20 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_batch_aliases_v1_entitybase_resolve_aliases__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/aliases/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/descriptions/{hashes}
**Get Batch Descriptions**
Get batch descriptions by hashes.

Supports single hash (e.g., /resolve/descriptions/123) or comma-separated batch
(e.g., /resolve/descriptions/123,456,789).

Returns dict mapping hash strings to description text. Max 20 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_batch_descriptions_v1_entitybase_resolve_descriptions__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/descriptions/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/glosses/{hashes}
**Get Glosses**
Fetch sense glosses by hash(es).

Supports single hash (e.g., /resolve/glosses/123) or comma-separated batch
(e.g., /resolve/glosses/123,456,789).

Returns array of gloss strings in request order; null for missing hashes.
Max 100 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_glosses_v1_entitybase_resolve_glosses__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/glosses/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/labels/{hashes}
**Get Batch Labels**
Get batch labels by hashes.

Supports single hash (e.g., /resolve/labels/123) or comma-separated batch
(e.g., /resolve/labels/123,456,789).

Returns dict mapping hash strings to label text. Max 20 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_batch_labels_v1_entitybase_resolve_labels__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/labels/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/qualifiers/{hashes}
**Get Qualifiers**
Fetch qualifiers by hash(es).

Supports single hash (e.g., /resolve/qualifiers/123) or comma-separated batch
(e.g., /resolve/qualifiers/123,456,789).

Returns array of qualifier dicts in request order; null for missing hashes.
Max 100 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_qualifiers_v1_entitybase_resolve_qualifiers__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/qualifiers/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/references/{hashes}
**Get References**
Fetch references by hash(es).

Supports single hash (e.g., /resolve/references/123) or comma-separated batch
(e.g., /resolve/references/123,456,789).

Returns array of reference dicts in request order; null for missing hashes.
Max 100 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_references_v1_entitybase_resolve_references__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/references/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/representations/{hashes}
**Get Representations**
Fetch form representations by hash(es).

Supports single hash (e.g., /resolve/representations/123) or comma-separated batch
(e.g., /resolve/representations/123,456,789).

Returns array of representation strings in request order; null for missing hashes.
Max 100 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_representations_v1_entitybase_resolve_representations__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/representations/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/sitelinks/{hashes}
**Get Batch Sitelinks**
Get batch sitelink titles by hashes.

Supports single hash (e.g., /resolve/sitelinks/123) or comma-separated batch
(e.g., /resolve/sitelinks/123,456,789).

Returns dict mapping hash strings to sitelink titles. Max 20 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_batch_sitelinks_v1_entitybase_resolve_sitelinks__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/sitelinks/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/snaks/{hashes}
**Get Snaks**
Fetch snaks by hash(es).

Supports single hash (e.g., /resolve/snaks/123) or comma-separated batch
(e.g., /resolve/snaks/123,456,789).

Returns array of snak dicts in request order; null for missing hashes.
Max 100 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_snaks_v1_entitybase_resolve_snaks__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/snaks/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

### GET /v1/entitybase/resolve/statements/{hashes}
**Get Statements**
Fetch statements by hash(es).

Supports single hash (e.g., /resolve/statements/123) or comma-separated batch
(e.g., /resolve/statements/123,456,789).

Returns array of statement dicts in request order; null for missing hashes.
Max 100 hashes per request.
| Aspect | Details |
|--------|---------|
| Operation ID | `get_statements_v1_entitybase_resolve_statements__hashes__get` |
| Method | `GET` |
| Path | `/v1/entitybase/resolve/statements/{hashes}` |
| Parameters | `hashes` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |


---

## Data Models
### AddPropertyRequest
Request model for adding claims to a single property.
| Field | Type | Description |
|-------|------|-------------|
| `claims` | array[object] | List of claim statements for the property. Each claim should be a valid Wikibase statement JSON. *(required)* |

---
### AddStatementRequest
Request model for adding a single statement to an entity, form, or sense.
| Field | Type | Description |
|-------|------|-------------|
| `claim` | object | A valid Wikibase statement JSON. *(required)* |

---
### AliasesResponse
Response model for entity aliases.
| Field | Type | Description |
|-------|------|-------------|
| `aliases` | array[string] | List of alias texts for the specified language *(required)* |

---
### AllSitelinksResponse
Response model for all entity sitelinks.
| Field | Type | Description |
|-------|------|-------------|
| `sitelinks` | object | Dictionary mapping site key to sitelink data *(required)* |

---
### BacklinkResponse
Model representing a backlink from one entity to another.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID that references the target *(required)* |
| `property_id` | string | Property used in the reference *(required)* |
| `rank` | string | Rank of the statement (normal/preferred/deprecated) *(required)* |

---
### BacklinksResponse
Response model for backlinks API.
| Field | Type | Description |
|-------|------|-------------|
| `backlinks` | array[BacklinkResponse] | List of backlinks *(required)* |
| `limit` | integer | Requested limit *(required)* |
| `offset` | integer | Requested offset *(required)* |

---
### BatchAliasesResponse
Response model for batch aliases lookup by hash.
| Field | Type | Description |
|-------|------|-------------|
| `aliases` | object | Dictionary mapping hash strings to alias text lists |

---
### BatchDescriptionsResponse
Response model for batch descriptions lookup by hash.
| Field | Type | Description |
|-------|------|-------------|
| `descriptions` | object | Dictionary mapping hash strings to description text |

---
### BatchLabelsResponse
Response model for batch labels lookup by hash.
| Field | Type | Description |
|-------|------|-------------|
| `labels` | object | Dictionary mapping hash strings to label text |

---
### BatchSitelinksResponse
Response model for batch sitelinks lookup by hash.
| Field | Type | Description |
|-------|------|-------------|
| `sitelinks` | object | Dictionary mapping hash strings to sitelink titles |

---
### BatchStatementsResponse
Response model for batch statements lookup.
| Field | Type | Description |
|-------|------|-------------|
| `statements` | object | Dictionary mapping entity_id → property_id → list of statement hashes |

---
### CleanupOrphanedRequest
| Field | Type | Description |
|-------|------|-------------|
| `older_than_days` | integer | Minimum age in days before cleanup (default 180) |
| `limit` | integer | Maximum number of statements to cleanup (default 1000) |

---
### CleanupOrphanedResponse
| Field | Type | Description |
|-------|------|-------------|
| `cleaned_count` | integer | Number of statements cleaned up from S3 and Vitess *(required)* |
| `failed_count` | integer | Number of statements that failed to clean up |
| `errors` | array[string] | List of error messages for failed cleanups |

---
### DeleteResponse
Response for DELETE operations.
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded. *(required)* |

---
### DeleteType

---
### DescriptionResponse
Response model for entity descriptions.
| Field | Type | Description |
|-------|------|-------------|
| `value` | string | The description text for the specified language *(required)* |

---
### EditType
Enumeration of different types of edits that can be made to entities.

---
### EndorsementListResponse
Response for endorsement list queries.
| Field | Type | Description |
|-------|------|-------------|
| `hash` | integer | Hash of the statement for which endorsements are listed. Example: 12345 |
| `user_id` | integer | ID of the user whose endorsements are listed. Example: 67890 |
| `list` | array[EndorsementResponse] | List of endorsements. Example: [{'id': 1, 'user_id': 123}] *(required)* |
| `count` | integer | Total number of endorsements. Example: 50 *(required)* |
| `more` | boolean | Whether there are more endorsements to fetch. Example: true *(required)* |
| `stats` | any | Statistics for the statement's endorsements |

---
### EndorsementResponse
Response for endorsement operations.
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier for the endorsement. Example: 12345. *(required)* |
| `user_id` | integer | ID of the user who created the endorsement. Example: 67890. *(required)* |
| `hash` | integer | Hash of the endorsed statement. Example: 987654321. *(required)* |
| `created_at` | string | Timestamp when the endorsement was created (ISO format). Example: '2023-01-01T12:00:00Z'. *(required)* |
| `removed_at` | string | Timestamp when the endorsement was removed (ISO format), empty string if active. Example: '2023-12-31T23:59:59Z'. |

---
### EndorsementStatsResponse
Response for endorsement statistics.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | ID of the user for whom statistics are provided. Example: 12345 *(required)* |
| `given` | integer | Total number of endorsements given by the user. Example: 10 *(required)* |
| `active` | integer | Number of active endorsements given by the user. Example: 8 *(required)* |

---
### EntityCreateRequest
Request model for entity creation.
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Entity ID (e.g., Q42) - optional for creation, auto-assigned if not provided |
| `type` | string | Entity type (item, property, lexeme) *(required)* |
| `labels` | object |  |
| `descriptions` | object |  |
| `claims` | object |  |
| `aliases` | object |  |
| `sitelinks` | object |  |
| `forms` | array[object] |  |
| `senses` | array[object] |  |
| `lemmas` | object |  |
| `language` | string | Lexeme language (QID) |
| `lexical_category` | string | Lexeme lexical category (QID) |
| `is_mass_edit` | boolean | Whether this is a mass edit |
| `edit_type` | EditType | Classification of edit type |
| `state` | EntityState | Entity state |
| `is_autoconfirmed_user` | boolean | User is autoconfirmed (not a new/unconfirmed account) |
| `is_semi_protected` | boolean | Whether the entity is semi-protected |
| `is_locked` | boolean | Whether the entity is locked |
| `is_archived` | boolean | Whether the entity is archived |
| `is_dangling` | boolean | Whether the entity is dangling |
| `is_mass_edit_protected` | boolean | Whether the entity is mass edit protected |

---
### EntityDeleteRequest
Request to delete an entity.
| Field | Type | Description |
|-------|------|-------------|
| `delete_type` | DeleteType | Type of deletion |

---
### EntityDeleteResponse
Response model for entity deletion.
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Entity ID. Example: 'Q42'. *(required)* |
| `rev_id` | integer | Revision ID at deletion. Example: 12345. *(required)* |
| `is_deleted` | boolean | Whether entity is deleted. Example: true. *(required)* |
| `del_type` | string | Type of deletion performed. Example: 'soft_delete'. *(required)* |
| `del_status` | string | Status of deletion (soft_deleted/hard_deleted). Example: 'soft_deleted'. *(required)* |

---
### EntityHistoryEntry
Response model for a single entity history entry.
| Field | Type | Description |
|-------|------|-------------|
| `revision_id` | integer | Revision ID. Example: 12345. *(required)* |
| `created_at` | string | Creation timestamp (ISO format). Example: '2023-01-01T12:00:00Z'. |
| `user_id` | integer | User ID who made the change. Example: 67890. |
| `summary` | string | Edit summary text. Example: 'Added label'. |

---
### EntityIdResult
Model for entity creation result with ID and revision.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | The new entity ID (e.g., 'Q123') *(required)* |
| `revision_id` | integer | The revision ID of the created entity *(required)* |

---
### EntityJsonResponse
Response model for JSON format entity data.
| Field | Type | Description |
|-------|------|-------------|
| `data` | object | Entity data in JSON format *(required)* |

---
### EntityListItem
Single entity item in a list response.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID (e.g., 'Q42') *(required)* |
| `head_revision_id` | integer | Current head revision ID *(required)* |

---
### EntityListItemWithEditType
Entity item with edit type and revision information.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID (e.g., 'Q42') *(required)* |
| `head_revision_id` | integer | Current head revision ID *(required)* |
| `edit_type` | string | Edit type classification *(required)* |
| `revision_id` | integer | Specific revision ID *(required)* |

---
### EntityListResponse
Response model for entity list queries.
| Field | Type | Description |
|-------|------|-------------|
| `entities` | array[any] | List of entities with their metadata *(required)* |
| `count` | integer | Total number of entities returned *(required)* |

---
### EntityRedirectRequest
| Field | Type | Description |
|-------|------|-------------|
| `redirect_from_id` | string | Source entity ID to be marked as redirect (e.g., Q59431323) *(required)* |
| `redirect_to_id` | string | Target entity ID (e.g., Q42) *(required)* |
| `created_by` | string | User or system creating redirect |

---
### EntityRedirectResponse
Response model for entity redirect creation.
| Field | Type | Description |
|-------|------|-------------|
| `redirect_from_id` | string | Entity ID being redirected from *(required)* |
| `redirect_to_id` | string | Entity ID being redirected to *(required)* |
| `created_at` | string | Creation timestamp of the redirect *(required)* |
| `revision_id` | integer | Revision ID of the redirect *(required)* |

---
### EntityResponse
Response model for entity data.
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Entity ID. Example: 'Q42'. *(required)* |
| `rev_id` | integer | Revision ID of the entity. Example: 12345. *(required)* |
| `data` | S3RevisionData | Full entity JSON data. Example: {'id': 'Q42', 'type': 'item'}. *(required)* |
| `state` | any | Entity state information (optional, may be None for revisions). |

---
### EntityRevertRequest
Request to revert an entity to a previous revision.
| Field | Type | Description |
|-------|------|-------------|
| `to_revision_id` | integer | Revision ID to revert to *(required)* |
| `watchlist_context` | any | Optional watchlist context |

---
### EntityRevertResponse
Response for entity revert operation.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | ID of the reverted entity. Example: 'Q42'. *(required)* |
| `new_rev_id` | integer | New revision ID after revert. Example: 12345. *(required)* |
| `from_rev_id` | integer | Original revision ID before revert. Example: 67890. *(required)* |
| `reverted_at` | string | Timestamp of the revert. Example: '2023-01-01T12:00:00Z'. *(required)* |

---
### EntityState
Model for entity state information.
| Field | Type | Description |
|-------|------|-------------|
| `sp` | boolean | Whether the entity is semi-protected. Example: true. |
| `locked` | boolean | Whether the entity is locked. Example: false. |
| `archived` | boolean | Whether the entity is archived. Example: false. |
| `dangling` | boolean | Whether the entity is dangling. Example: false. |
| `mep` | boolean | Whether the entity has mass edit protection. Example: true. |
| `deleted` | boolean | Whether the entity is deleted. Example: true. |

---
### EntityStatusRequest
Request model for entity status changes (lock, archive, semi-protect).
| Field | Type | Description |
|-------|------|-------------|
| `edit_summary` | any |  |

---
### EntityStatusResponse
Response model for entity status changes (lock, archive, semi-protect).
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Entity ID. Example: 'Q42'. *(required)* |
| `rev_id` | integer | Revision ID after status change. Example: 12345. *(required)* |
| `status` | string | Status that was set. Example: 'locked', 'unlocked', 'archived', 'unarchived', 'semi_protected', 'unprotected'. *(required)* |
| `idempotent` | boolean | True if entity was already in the target state (no new revision created). |

---
### FormCreateRequest
Request body for creating a new form.
| Field | Type | Description |
|-------|------|-------------|
| `representations` | object | Form representations by language code, e.g. {'en': {'language': 'en', 'value': 'runs'}} *(required)* |
| `grammatical_features` | array[string] | List of grammatical feature item IDs (e.g. ['Q123']) |
| `claims` | object | Optional statements/claims for the form |

---
### FormRepresentationResponse
| Field | Type | Description |
|-------|------|-------------|
| `value` | string |  *(required)* |

---
### FormRepresentationsResponse
| Field | Type | Description |
|-------|------|-------------|
| `representations` | object |  *(required)* |

---
### FormResponse
| Field | Type | Description |
|-------|------|-------------|
| `id` | string |  *(required)* |
| `representations` | object |  *(required)* |
| `grammaticalFeatures` | array[string] |  |
| `claims` | object |  |

---
### FormsResponse
| Field | Type | Description |
|-------|------|-------------|
| `forms` | array[FormResponse] |  *(required)* |

---
### GeneralStatsResponse
API response for general wiki statistics.
| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date of statistics computation. *(required)* |
| `total_statements` | integer | Total number of statements. *(required)* |
| `total_qualifiers` | integer | Total number of qualifiers. *(required)* |
| `total_references` | integer | Total number of references. *(required)* |
| `total_items` | integer | Total number of items. *(required)* |
| `total_lexemes` | integer | Total number of lexemes. *(required)* |
| `total_properties` | integer | Total number of properties. *(required)* |
| `total_sitelinks` | integer | Total number of sitelinks. *(required)* |
| `total_terms` | integer | Total number of terms (labels + descriptions + aliases). *(required)* |
| `terms_per_language` | TermsPerLanguage | Terms count per language. *(required)* |
| `terms_by_type` | TermsByType | Terms count by type (labels, descriptions, aliases). *(required)* |

---
### HTTPValidationError
| Field | Type | Description |
|-------|------|-------------|
| `detail` | array[ValidationError] |  |

---
### HealthCheckResponse
Detailed response model for health check.
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health status *(required)* |
| `s3` | string | S3 service health status. Example: 'healthy'. *(required)* |
| `vitess` | string | Vitess service health status. Example: 'healthy'. *(required)* |
| `timestamp` | string | Timestamp of health check *(required)* |

---
### LabelResponse
Response model for entity labels.
| Field | Type | Description |
|-------|------|-------------|
| `value` | string | The label text for the specified language *(required)* |

---
### LemmaResponse
| Field | Type | Description |
|-------|------|-------------|
| `value` | string |  *(required)* |

---
### LemmasResponse
| Field | Type | Description |
|-------|------|-------------|
| `lemmas` | object |  *(required)* |

---
### LexemeLanguageRequest
Request body for updating a lexeme's language.
| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Lexeme language as QID (e.g., 'Q1860') *(required)* |

---
### LexemeLanguageResponse
Response model for lexeme language endpoint.
| Field | Type | Description |
|-------|------|-------------|
| `language` | string |  *(required)* |

---
### LexemeLexicalCategoryRequest
Request body for updating a lexeme's lexical category.
| Field | Type | Description |
|-------|------|-------------|
| `lexical_category` | string | Lexeme lexical category as QID (e.g., 'Q1084') *(required)* |

---
### LexemeLexicalCategoryResponse
Response model for lexeme lexical category endpoint.
| Field | Type | Description |
|-------|------|-------------|
| `lexical_category` | string |  *(required)* |

---
### MessageResponse
Generic message response.
| Field | Type | Description |
|-------|------|-------------|
| `message` | string |  *(required)* |

---
### MostUsedStatementsResponse
| Field | Type | Description |
|-------|------|-------------|
| `statements` | array[integer] | List of statement hashes sorted by ref_count DESC |

---
### NotificationResponse
Response for user notifications.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer |  *(required)* |
| `notifications` | array[any] |  *(required)* |

---
### OperationResult_EntityIdResult_
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean |  *(required)* |
| `error` | string |  |
| `data` | any |  |

---
### OperationResult_RevisionIdResult_
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean |  *(required)* |
| `error` | string |  |
| `data` | any |  |

---
### PatchStatementRequest
Request model for patching a statement.
| Field | Type | Description |
|-------|------|-------------|
| `claim` | object | The new claim data to replace the existing statement. Must be a valid Wikibase claim JSON. *(required)* |

---
### PropertyCountsResponse
| Field | Type | Description |
|-------|------|-------------|
| `property_counts` | object | Dict mapping property ID -> statement count |

---
### PropertyHashesResponse
| Field | Type | Description |
|-------|------|-------------|
| `property_hashes` | array[integer] | List of statement hashes for specified properties |

---
### PropertyListResponse
| Field | Type | Description |
|-------|------|-------------|
| `properties` | array[string] | List of unique property IDs |

---
### QualifierResponse
Response model for qualifier data.
| Field | Type | Description |
|-------|------|-------------|
| `qualifier` | object | Full qualifier JSON object with reconstructed snaks. Values may be int, str, dict, or list containing reconstructed snaks. *(required)* |
| `hash` | integer | Hash of the qualifier content. Example: 123456789. *(required)* |
| `created_at` | string | Timestamp when qualifier was created. Example: '2023-01-01T12:00:00Z'. *(required)* |

---
### RedirectRevertRequest
| Field | Type | Description |
|-------|------|-------------|
| `revert_to_revision_id` | integer | Revision ID to revert to (e.g., 12340). *(required)* |
| `created_by` | string |  |

---
### ReferenceResponse
Response model for reference data.
| Field | Type | Description |
|-------|------|-------------|
| `reference` | object | Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}. *(required)* |
| `hash` | integer | Hash of the reference content. Example: 123456789. *(required)* |
| `created_at` | string | Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'. *(required)* |

---
### RemoveStatementRequest
Request model for removing a statement.
| Field | Type | Description |
|-------|------|-------------|

---
### RepresentationData
| Field | Type | Description |
|-------|------|-------------|
| `language` | string |  *(required)* |
| `value` | string |  *(required)* |

---
### RevisionIdResult
Model for operations that return a revision ID.
| Field | Type | Description |
|-------|------|-------------|
| `revision_id` | integer | The revision ID of the created/updated entity, or 0 for idempotent operations |

---
### S3RevisionData
Model for revision data stored in S3.
| Field | Type | Description |
|-------|------|-------------|
| `schema` | string | Schema version (MAJOR.MINOR.PATCH). Example: '1.0.0'. *(required)* |
| `revision` | object | Complete revision data including entity and metadata. *(required)* |
| `hash` | integer | Hash of the revision content. Example: 123456789. *(required)* |
| `created_at` | string | Timestamp when revision was created. Example: '2023-01-01T12:00:00Z'. *(required)* |

---
### SenseCreateRequest
Request body for creating a new sense.
| Field | Type | Description |
|-------|------|-------------|
| `glosses` | object | Sense glosses by language code, e.g. {'en': {'language': 'en', 'value': 'to move quickly'}} *(required)* |
| `claims` | object | Optional statements/claims for the sense |

---
### SenseGlossResponse
| Field | Type | Description |
|-------|------|-------------|
| `value` | string |  *(required)* |

---
### SenseGlossesResponse
| Field | Type | Description |
|-------|------|-------------|
| `glosses` | object |  *(required)* |

---
### SenseResponse
| Field | Type | Description |
|-------|------|-------------|
| `id` | string |  *(required)* |
| `glosses` | object |  *(required)* |
| `claims` | object |  |

---
### SensesResponse
| Field | Type | Description |
|-------|------|-------------|
| `senses` | array[SenseResponse] |  *(required)* |

---
### SettingsResponse
Response model for settings endpoint (excludes sensitive values).
| Field | Type | Description |
|-------|------|-------------|
| `s3_endpoint` | string |  *(required)* |
| `s3_references_bucket` | string |  *(required)* |
| `s3_qualifiers_bucket` | string |  *(required)* |
| `s3_sitelinks_bucket` | string |  *(required)* |
| `s3_snaks_bucket` | string |  *(required)* |
| `s3_statements_bucket` | string |  *(required)* |
| `s3_terms_bucket` | string |  *(required)* |
| `s3_revisions_bucket` | string |  *(required)* |
| `s3_snak_version` | string |  *(required)* |
| `s3_sitelink_version` | string |  *(required)* |
| `s3_qualifier_version` | string |  *(required)* |
| `s3_reference_version` | string |  *(required)* |
| `s3_statement_version` | string |  *(required)* |
| `s3_schema_revision_version` | string |  *(required)* |
| `vitess_host` | string |  *(required)* |
| `vitess_port` | integer |  *(required)* |
| `vitess_database` | string |  *(required)* |
| `vitess_pool_size` | integer |  *(required)* |
| `vitess_max_overflow` | integer |  *(required)* |
| `vitess_pool_timeout` | integer |  *(required)* |
| `wikibase_repository_name` | string |  *(required)* |
| `property_registry_path` | string |  *(required)* |
| `log_level` | string |  *(required)* |
| `streaming_enabled` | boolean |  *(required)* |
| `kafka_bootstrap_servers` | string |  *(required)* |
| `kafka_entitychange_json_topic` | string |  *(required)* |
| `kafka_entity_diff_topic` | string |  *(required)* |
| `streaming_entity_change_version` | string |  *(required)* |
| `streaming_endorsechange_version` | string |  *(required)* |
| `streaming_newthank_version` | string |  *(required)* |
| `streaming_entity_diff_version` | string |  *(required)* |
| `entity_version` | string |  *(required)* |
| `dangling_property_id` | string |  *(required)* |
| `api_prefix` | string |  *(required)* |
| `user_agent` | string |  *(required)* |
| `api_description` | string |  *(required)* |
| `backlink_stats_enabled` | boolean |  *(required)* |
| `backlink_stats_schedule` | string |  *(required)* |
| `backlink_stats_top_limit` | integer |  *(required)* |
| `user_stats_enabled` | boolean |  *(required)* |
| `user_stats_schedule` | string |  *(required)* |
| `general_stats_enabled` | boolean |  *(required)* |
| `general_stats_schedule` | string |  *(required)* |
| `json_dump_enabled` | boolean |  *(required)* |
| `json_dump_schedule` | string |  *(required)* |
| `s3_dump_bucket` | string |  *(required)* |
| `json_dump_batch_size` | integer |  *(required)* |
| `json_dump_parallel_workers` | integer |  *(required)* |
| `json_dump_generate_checksums` | boolean |  *(required)* |
| `ttl_dump_enabled` | boolean |  *(required)* |
| `ttl_dump_schedule` | string |  *(required)* |
| `ttl_dump_batch_size` | integer |  *(required)* |
| `ttl_dump_parallel_workers` | integer |  *(required)* |
| `ttl_dump_compression` | boolean |  *(required)* |
| `ttl_dump_generate_checksums` | boolean |  *(required)* |

---
### SingleEndorsementStatsResponse
Response for single statement endorsement statistics.
| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of endorsements for the statement. Example: 15 *(required)* |
| `active` | integer | Number of active endorsements for the statement. Example: 12 *(required)* |
| `withdrawn` | integer | Number of withdrawn endorsements for the statement. Example: 3 *(required)* |

---
### SitelinkData
Data for a single sitelink.
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Page title *(required)* |
| `badges` | array[string] | List of badges |

---
### SnakResponse
Response model for snak data.
| Field | Type | Description |
|-------|------|-------------|
| `snak` | object | Full snak JSON object. Example: {'snaktype': 'value', 'property': 'P31', 'datatype': 'wikibase-item', 'datavalue': {...}}. *(required)* |
| `hash` | integer | Hash of the snak content. Example: 123456789. *(required)* |
| `created_at` | string | Timestamp when snak was created. Example: '2023-01-01T12:00:00Z'. *(required)* |

---
### StatementEndorsementStats
Response for statement endorsement statistics.
| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of endorsements for the statement. Example: 15 *(required)* |
| `active` | integer | Number of active endorsements for the statement. Example: 12 *(required)* |
| `withdrawn` | integer | Number of withdrawn endorsements for the statement. Example: 3 *(required)* |

---
### StatementResponse
Response model for statement data.
| Field | Type | Description |
|-------|------|-------------|
| `schema` | string | Schema version for the statement. Example: '1.0'. *(required)* |
| `hash` | integer | Hash of the statement content. Example: 123456789. *(required)* |
| `statement` | object | Full statement JSON object. Example: {'id': 'P31', 'value': 'Q5'}. *(required)* |
| `created_at` | string | Timestamp when statement was created. Example: '2023-01-01T12:00:00Z'. *(required)* |

---
### TermHashResponse
Response for single term (label/description/alias/lemma) operations.
| Field | Type | Description |
|-------|------|-------------|
| `hash` | integer | Hash of the stored term. *(required)* |

---
### TermHashesResponse
Response for multi-term operations (e.g., aliases PUT).
| Field | Type | Description |
|-------|------|-------------|
| `hashes` | array[integer] | Hashes of the stored terms. *(required)* |

---
### TermUpdateRequest
Request body for updating entity terms (labels, descriptions, representations, glosses).

Matches the Wikidata internal storage format with language and value fields.
| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Language code (e.g., 'en', 'fr') *(required)* |
| `value` | string | Term text value *(required)* |

---
### TermsByType
Model for terms count by type.
| Field | Type | Description |
|-------|------|-------------|
| `counts` | object | Type to count mapping. *(required)* |

---
### TermsPerLanguage
Model for terms count per language.
| Field | Type | Description |
|-------|------|-------------|
| `terms` | object | Language to count mapping. *(required)* |

---
### ThankItemResponse
Individual thank item.
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier for the thank *(required)* |
| `from_user_id` | integer | User ID who sent the thank *(required)* |
| `to_user_id` | integer | User ID who received the thank *(required)* |
| `entity_id` | string | Entity ID associated with the thank *(required)* |
| `revision_id` | integer | Revision ID associated with the thank *(required)* |
| `created_at` | string | Timestamp when the thank was created *(required)* |

---
### ThankResponse
Response for sending a thank.
| Field | Type | Description |
|-------|------|-------------|
| `thank_id` | integer | Thank ID *(required)* |
| `from_user_id` | integer | User ID sending the thank *(required)* |
| `to_user_id` | integer | User ID receiving the thank *(required)* |
| `entity_id` | string | Entity ID *(required)* |
| `revision_id` | integer | Revision ID *(required)* |
| `created_at` | string | Creation timestamp *(required)* |

---
### ThanksListResponse
Response for thanks list queries.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | User ID *(required)* |
| `thanks` | array[ThankItemResponse] | List of thanks *(required)* |
| `total_count` | integer | Total count of thanks *(required)* |
| `has_more` | boolean | Whether there are more thanks available *(required)* |

---
### UserActivityItemResponse
Individual user activity item.
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier for the activity *(required)* |
| `user_id` | integer | User ID who performed the activity *(required)* |
| `activity_type` | UserActivityType | Type of activity performed *(required)* |
| `entity_id` | string | Entity ID associated with the activity |
| `revision_id` | integer | Revision ID associated with the activity |
| `created_at` | string | Timestamp when the activity occurred *(required)* |

---
### UserActivityResponse
Response for user activity query.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | User ID *(required)* |
| `activities` | array[UserActivityItemResponse] | List of user activities *(required)* |

---
### UserActivityType
User activity types for entity operations.

---
### UserCreateRequest
Request to create/register a user.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | MediaWiki user ID *(required)* |

---
### UserCreateResponse
Response for user creation.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer |  *(required)* |
| `created` | boolean |  *(required)* |

---
### UserResponse
User model.
We intentionally don't have auth, nor store the usernames.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer |  *(required)* |
| `created_at` | string |  *(required)* |
| `preferences` | any |  |

---
### UserStatsResponse
API response for user statistics.
| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date of statistics computation. Example: '2023-01-01'. *(required)* |
| `total` | integer | Total number of users. Example: 1000. *(required)* |
| `active` | integer | Number of active users. Example: 500. *(required)* |

---
### ValidationError
| Field | Type | Description |
|-------|------|-------------|
| `loc` | array[any] |  *(required)* |
| `msg` | string |  *(required)* |
| `type` | string |  *(required)* |

---
### VersionResponse
Response model for version endpoint.
| Field | Type | Description |
|-------|------|-------------|
| `api_version` | string | API version *(required)* |
| `entitybase_version` | string | EntityBase version *(required)* |

---
### WatchCounts
Model for user watch counts.
| Field | Type | Description |
|-------|------|-------------|
| `entity_count` | integer | Number of entities watched *(required)* |
| `property_count` | integer | Number of properties watched *(required)* |

---
### WatchlistAddRequest
Request to add a watchlist entry.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID (e.g., Q42) *(required)* |
| `properties` | any | Specific properties to watch, empty for whole entity |

---
### WatchlistRemoveRequest
Request to remove a watchlist entry.
| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID to remove from watchlist *(required)* |
| `properties` | any | Specific properties to stop watching |

---
### WatchlistResponse
Response for listing user's watchlist.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | User ID for whom the watchlist is returned *(required)* |
| `watches` | array[object] | List of watchlist entries with entity_id and properties *(required)* |

---
### WatchlistToggleRequest
Request to enable/disable watchlist for user.
| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean |  *(required)* |

---
### WatchlistToggleResponse
Response for watchlist toggle.
| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer |  *(required)* |
| `enabled` | boolean |  *(required)* |

---
