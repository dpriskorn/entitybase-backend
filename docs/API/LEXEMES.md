# Lexemes API

> API endpoints for Lexeme entities (L IDs)

Lexemes represent words or phrases in a language, including forms and senses.

---

## POST /v1/entities/lexemes
**Create Lexeme**

Create a new lexeme entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_lexeme_v1_entities_lexemes_post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityCreateRequest](#entitycreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/lexemes/{id}
**Get Lexeme**

Retrieve a lexeme by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_v1_entities_lexemes__id_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{id}` |
| Parameters | `id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Forms

### GET /v1/entities/lexemes/{lexeme_id}/forms
**Get Lexeme Forms**

List all forms for a lexeme, sorted by numeric suffix.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_forms_v1_entities_lexemes__lexeme_id__forms_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{lexeme_id}/forms` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/{lexeme_id}/forms
**Create Lexeme Form**

Create a new form for a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_lexeme_form_v1_entities_lexemes__lexeme_id__forms_post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/{lexeme_id}/forms` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[FormCreateRequest](#formcreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/forms/{form_id}
**Get Form By Id**

Get single form by ID (accepts L42-F1 or F1 format).

| Aspect | Details |
|--------|---------|
| Operation ID | `get_form_by_id_v1_entities_lexemes_forms__form_id__get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/forms/{form_id}` |
| Parameters | `form_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/lexemes/forms/{form_id}
**Delete Form**

Delete a form by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_form_v1_entities_lexemes_forms__form_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/lexemes/forms/{form_id}` |
| Parameters | `form_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/forms/{form_id}/representation
**Get Form Representations**

Get all representations for a form.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_form_representations_v1_entities_lexemes_forms__form_id__representation_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/forms/{form_id}/representation` |
| Parameters | `form_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/forms/{form_id}/representation/{langcode}
**Get Form Representation**

Get representation for a form in specific language.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_form_representation_v1_entities_lexemes_forms__form_id__representation__langcode__get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/forms/{form_id}/representation/{langcode}
**Add Form Representation**

Add a new form representation for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_form_representation_v1_entities_lexemes_forms__form_id__representation__langcode__post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/lexemes/forms/{form_id}/representation/{langcode}
**Update Form Representation**

Update form representation for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_form_representation_v1_entities_lexemes_forms__form_id__representation__langcode__put` |
| Method | `PUT` |
| Path | `/v1/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/lexemes/forms/{form_id}/representation/{langcode}
**Delete Form Representation**

Delete form representation for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_form_representation_v1_entities_lexemes_forms__form_id__representation__langcode__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/lexemes/forms/{form_id}/representation/{langcode}` |
| Parameters | `form_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/forms/{form_id}/statements
**Add Form Statement**

Add a statement to a form.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_form_statement_v1_entities_lexemes_forms__form_id__statements_post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/forms/{form_id}/statements` |
| Parameters | `form_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[AddStatementRequest](#addstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Senses

### GET /v1/entities/lexemes/{lexeme_id}/senses
**Get Lexeme Senses**

List all senses for a lexeme, sorted by numeric suffix.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_senses_v1_entities_lexemes__lexeme_id__senses_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{lexeme_id}/senses` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/{lexeme_id}/senses
**Create Lexeme Sense**

Create a new sense for a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_lexeme_sense_v1_entities_lexemes__lexeme_id__senses_post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/{lexeme_id}/senses` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[SenseCreateRequest](#sensecreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/senses/{sense_id}
**Get Sense By Id**

Get single sense by ID (accepts L42-S1 or S1 format).

| Aspect | Details |
|--------|---------|
| Operation ID | `get_sense_by_id_v1_entities_lexemes_senses__sense_id__get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/senses/{sense_id}` |
| Parameters | `sense_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/lexemes/senses/{sense_id}
**Delete Sense**

Delete a sense by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_sense_v1_entities_lexemes_senses__sense_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/lexemes/senses/{sense_id}` |
| Parameters | `sense_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/senses/{sense_id}/glosses
**Get Sense Glosses**

Get all glosses for a sense.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_sense_glosses_v1_entities_lexemes_senses__sense_id__glosses_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/senses/{sense_id}/glosses` |
| Parameters | `sense_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Get Sense Gloss By Language**

Get gloss for a sense in specific language.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_sense_gloss_by_language_v1_entities_lexemes_senses__sense_id__glosses__langcode__get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Add Sense Gloss**

Add a new sense gloss for a language.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_sense_gloss_v1_entities_lexemes_senses__sense_id__glosses__langcode__post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Update Sense Gloss**

Update sense gloss for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_sense_gloss_v1_entities_lexemes_senses__sense_id__glosses__langcode__put` |
| Method | `PUT` |
| Path | `/v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}
**Delete Sense Gloss**

Delete sense gloss for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_sense_gloss_v1_entities_lexemes_senses__sense_id__glosses__langcode__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/lexemes/senses/{sense_id}/glosses/{langcode}` |
| Parameters | `sense_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/senses/{sense_id}/statements
**Add Sense Statement**

Add a statement to a sense.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_sense_statement_v1_entities_lexemes_senses__sense_id__statements_post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/senses/{sense_id}/statements` |
| Parameters | `sense_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[AddStatementRequest](#addstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Lemmas

### GET /v1/entities/lexemes/{lexeme_id}/lemmas
**Get Lexeme Lemmas**

Get all lemmas for a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_lemmas_v1_entities_lexemes__lexeme_id__lemmas_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lemmas` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Get Lexeme Lemma**

Get lemma for a lexeme in specific language.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_lemma_v1_entities_lexemes__lexeme_id__lemmas__langcode__get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Add Lexeme Lemma**

Add a new lemma for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_lexeme_lemma_v1_entities_lexemes__lexeme_id__lemmas__langcode__post` |
| Method | `POST` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Update Lexeme Lemma**

Update lemma for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_lexeme_lemma_v1_entities_lexemes__lexeme_id__lemmas__langcode__put` |
| Method | `PUT` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}
**Delete Lexeme Lemma**

Delete lemma for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_lexeme_lemma_v1_entities_lexemes__lexeme_id__lemmas__langcode__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lemmas/{langcode}` |
| Parameters | `lexeme_id` (path, Required) `langcode` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Language & Category

### GET /v1/entities/lexemes/{lexeme_id}/language
**Get Lexeme Language**

Get the language of a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_language_v1_entities_lexemes__lexeme_id__language_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{lexeme_id}/language` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/lexemes/{lexeme_id}/language
**Update Lexeme Language**

Update the language of a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_lexeme_language_v1_entities_lexemes__lexeme_id__language_put` |
| Method | `PUT` |
| Path | `/v1/entities/lexemes/{lexeme_id}/language` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[LexemeLanguageRequest](#lexemelanguagerequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/lexemes/{lexeme_id}/lexicalcategory
**Get Lexeme Lexicalcategory**

Get the lexical category of a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_lexeme_lexicalcategory_v1_entities_lexemes__lexeme_id__lexicalcategory_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lexicalcategory` |
| Parameters | `lexeme_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/lexemes/{lexeme_id}/lexicalcategory
**Update Lexeme Lexicalcategory**

Update the lexical category of a lexeme.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_lexeme_lexicalcategory_v1_entities_lexemes__lexeme_id__lexicalcategory_put` |
| Method | `PUT` |
| Path | `/v1/entities/lexemes/{lexeme_id}/lexicalcategory` |
| Parameters | `lexeme_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[LexemeLexicalCategoryRequest](#lexemelexicalcategoryrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Items API](./ITEMS.md)
- [Properties API](./PROPERTIES.md)
- [Entities API](./ENTITIES.md)