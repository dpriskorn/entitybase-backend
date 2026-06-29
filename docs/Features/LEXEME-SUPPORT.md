# Lexeme Support

Full support for lexical entries — words, forms, senses, and glosses.

## Overview

Entitybase supports the complete Wikibase lexeme data model, enabling storage and management of lexical data including words, phrases, and their grammatical forms.

## Components

### Lexeme (L)
A lexical entry representing a word or phrase in a language.

**Example:** L1 = "cat" (English noun)

### Lemma
The base form of a word.

**Example:** "run" (not "running" or "ran")

### Lexical Category
The grammatical category — noun, verb, adjective, etc.

### Form
A specific variation of a lexeme (e.g., plural, conjugation).

**Example:**
- L1-F1: "cats" (plural form of L1 "cat")
- L2-F1: "running" (present participle of L2 "run")

### Sense
A meaning or definition of a lexeme.

**Example:** L1-S1: "feline animal" (first sense of "cat")

### Gloss
A brief definition in a specific language.

## API Endpoints

| Entity | Endpoints |
|--------|-----------|
| Lexeme | Create, read, update, delete |
| Form | Create, read, update, delete |
| Sense | Create, read, update, delete |
| Lemma | Add, update, delete |
| Gloss | Add, update, delete |

## Use Cases

- Building dictionaries and glossaries
- Multilingual vocabulary databases
- Linguistic research and analysis
- Language learning applications
