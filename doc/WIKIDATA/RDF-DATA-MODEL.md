# RDF DATA MODEL
This page describes the RDF dump and export format produced by Wikidata and used for export and indexing purposes.

While it is close to the format used by Wikidata Toolkit, it is not the same code and not the same format. While divergence is kept to a minimum, there may be differences; documentation should be used only for the format actually being consumed.

This document describes the RDF dump as downloaded from the Wikimedia dump source. While it can be used to create queries for the Wikidata Query Service (WDQS), the service can have small differences in how the data looks. See the *WDQS data differences* chapter for details.

* **Ontology URI:** [http://wikiba.se/ontology](http://wikiba.se/ontology)
* **Current version:** [http://wikiba.se/ontology-1.0.owl](http://wikiba.se/ontology-1.0.owl)

Changes to the RDF mapping are subject to the Stable Interface Policy.

---

## Data model

![The data used in the description of a single item](Rdf%20mapping-vector.svg)

The RDF format is a binding for the Wikibase data model and represents an export format for it. If the data model changes, the export format changes accordingly, and this document will be updated.

This RDF binding is based on the one designed for the Wikidata Toolkit by Denny Vrandecic and Markus Krötzsch.

Prefixes are used to describe IRIs; all examples are in **Turtle** format.

---

## Versions

The data model version is specified by `schema:softwareVersion` on the `schema:Dataset` node.

**Released versions**

| Version | Description                                                     |
| ------- | --------------------------------------------------------------- |
| 0.0.1   | Initial version                                                 |
| 0.0.2   | Changed WKT coordinate order                                    |
| 0.0.3   | Added page props option to `wdata:`                             |
| 0.0.4   | Added unit conversion & normalisation                           |
| 0.0.5   | Added quantities without bounds                                 |
| 0.1.0   | Changed link encoding                                           |
| 1.0.0   | Removed `-beta` from ontology prefix; mapping considered stable |

---

## Header

The RDF dump contains a header node `wikibase:Dump` with license, generator version, and dump date.

```turtle
wikibase:Dump a schema:Dataset ;
    cc:license <http://creativecommons.org/publicdomain/zero/1.0/> ;
    schema:softwareVersion "1.0.1" ;
    schema:dateModified "2015-03-21T06:03:55Z"^^xsd:dateTime .
```

* `cc:license`: IRI of the license applying to the RDF document
* `schema:softwareVersion`: dump format version (semantic versioning)
* `schema:dateModified`: date of data validity

---

## Entity representation

Each entity is described by two nodes:

* **Data node:** e.g. `wdata:Q1`
* **Entity node:** e.g. `wd:Q1`

The data node (`schema:Dataset`) contains metadata:

* Revision number (`schema:version`)
* Last modification time (`schema:dateModified`)
* Link to entity node (`schema:about`)

```turtle
wdata:Q2 schema:version "59"^^xsd:integer ;
    schema:dateModified "2015-03-18T22:38:36Z"^^xsd:dateTime ;
    a schema:Dataset ;
    schema:about wd:Q2 .
```

The entity node has type `wikibase:Item` or `wikibase:Property`.

### Entity contents

* Labels (`schema:name`, `rdfs:label`, `skos:prefLabel`)
* Aliases (`skos:altLabel`)
* Descriptions (`schema:description`)
* Truthy statements
* Links to full statements

```turtle
wd:Q3 a wikibase:Item ;
    rdfs:label "The Universe"@en ;
    skos:prefLabel "The Universe"@en ;
    schema:name "The Universe"@en ;
    schema:description "The Universe is big"@en ;
    skos:altLabel "everything"@en ;
    wdt:P2 wd:Q3 ;
    wdt:P7 "value1", "value2" ;
    p:P2 wds:Q3-4cc1f2d1-490e-c9c7-4560-46c3cce05bb7 ;
    p:P7 wds:Q3-24bf3704-4c5d-083a-9b59-1881f82b6b37,
         wds:Q3-45abf5ca-4ebf-eb52-ca26-811152eb067c .
```

---

## Page properties

Entities may include page properties such as counts of statements, identifiers, and sitelinks.

```turtle
wdata:Q42 a schema:Dataset ;
    schema:about wd:Q42 ;
    wikibase:statements "275"^^xsd:integer ;
    wikibase:identifiers "206"^^xsd:integer ;
    wikibase:sitelinks "116"^^xsd:integer .
```

---

## Items and Properties

### Items

Items may have sitelinks.

### Properties

Properties include `wikibase:propertyType` and links to derived predicates.

```turtle
wd:P22 a wikibase:Property ;
    rdfs:label "Item property"@en ;
    wikibase:propertyType wikibase:WikibaseItem ;
    wikibase:directClaim wdt:P22 ;
    wikibase:claim p:P22 ;
    wikibase:statementProperty ps:P22 ;
    wikibase:statementValue psv:P22 ;
    wikibase:qualifier pq:P22 ;
    wikibase:qualifierValue pqv:P22 ;
    wikibase:reference pr:P22 ;
    wikibase:referenceValue prv:P22 ;
    wikibase:novalue wdno:P22 .
```

Predicate types depend on whether values are literals or IRIs.

---

## Lexemes

Lexemes are represented according to the Lexeme RDF mapping.

```turtle
wd:L64723 a ontolex:LexicalEntry ;
    wikibase:lemma "hard"@en ;
    dct:language wd:Q1860 ;
    wikibase:lexicalCategory wd:Q34698 ;
    wdt:P2 wd:Q3 ;
    wdt:P7 "value1" , "value2" ;
    ontolex:lexicalForm wd:L64723-F1 ;
    ontolex:sense wd:L64723-S1 .
```

---

## MediaInfo

MediaInfo entities follow the MediaInfo RDF mapping.

```turtle
sdcdata:M6661797 a schema:Dataset ;
    schema:about sdc:M6661797 ;
    cc:license <http://creativecommons.org/publicdomain/zero/1.0/> ;
    schema:softwareVersion "1.0.0" ;
    schema:version "407884644"^^xsd:integer ;
    schema:dateModified "2020-03-29T15:25:01Z"^^xsd:dateTime .
```

---

## Statement types

### Truthy statements

Best non-deprecated statements per property, using `wdt:` predicates. Qualifiers are ignored.

### Full statements

Represented as separate nodes (`wds:`) linked via `p:` predicates.

---

## Statement representation

> **Warning**
> Statements may refer to properties or items that no longer exist.

Statements include rank, value, qualifiers, and references.

```turtle
wds:Q3-24bf3704-4c5d-083a-9b59-1881f82b6b37 a wikibase:Statement, wikibase:BestRank ;
    ps:P2 wd:Q3 ;
    wikibase:rank wikibase:PreferredRank ;
    pq:P8 "-13000000000-01-01T00:00:00Z"^^xsd:dateTime ;
    pqv:P8 wdv:382603eaa501e15688076291fc47ae54 ;
    prov:wasDerivedFrom wdref:87d0dc1c7847f19ac0f19be978015dfb202cf59a .
```

---

## References

References are nodes (`wdref:`) of type `wikibase:Reference`.

```turtle
wdref:d95dde070543a0e0115c8d5061fce6754bb82280 a wikibase:Reference ;
    pr:P7 "Some data" ;
    pr:P8 "1976-01-12T00:00:00Z"^^xsd:dateTime ;
    prv:P8 wdv:b74072c03a5ced412a336ff213d69ef1 .
```

---

## Value representation

Values have **simple** and **full** forms.

Example full value (time):

```turtle
wdv:b74072c03a5ced412a336ff213d69ef1 a wikibase:TimeValue ;
    wikibase:timeValue "+1976-01-12T00:00:00Z"^^xsd:dateTime ;
    wikibase:timePrecision "11"^^xsd:integer ;
    wikibase:timeTimezone "0"^^xsd:integer ;
    wikibase:timeCalendarModel <http://www.wikidata.org/entity/Q1985727> .
```

Supported value types include:

* String
* Commons media
* URL
* External ID
* Wikibase entity ID
* Monolingual text
* Globe coordinate
* Quantity
* Time

---

## Normalised values

Some values (quantities, external IDs) have normalised forms for unified processing.

```turtle
wds:Q3-24bf3704-4c5d-083a-9b59-1881f82b6b37
    ps:P8 "123"^^xsd:decimal ;
    psv:P8 wdv:382603eaa501e15688076291fc47ae54 ;
    psn:P8 wdv:85374998f22bda54efb44a5617d76e51 .
```

---

## Special values

### Somevalue

Unknown values are represented as blank nodes.

### Novalue

Represented as classes with `wdno:` prefix.

```turtle
wd:Q3 a wikibase:Item, wdno:P7 .
```

---

## Sitelinks

Sitelinks are `schema:Article` nodes linked via `schema:about`.

```turtle
<https://en.wikipedia.org/wiki/Duck> a schema:Article ;
    schema:about wd:Q3 ;
    schema:inLanguage "en" ;
    schema:isPartOf <https://en.wikipedia.org/> ;
    schema:name "Duck"@en ;
    wikibase:badge wd:Q5 .
```

---

## Redirects

Redirects use `owl:sameAs`.

```turtle
wd:Q6 owl:sameAs wd:Q1 .
```

---

## Prefixes used

### Standard prefixes

| Prefix | Full URL                                                                                   |
| ------ | ------------------------------------------------------------------------------------------ |
| rdf    | [http://www.w3.org/1999/02/22-rdf-syntax-ns#](http://www.w3.org/1999/02/22-rdf-syntax-ns#) |
| rdfs   | [http://www.w3.org/2000/01/rdf-schema#](http://www.w3.org/2000/01/rdf-schema#)             |
| xsd    | [http://www.w3.org/2001/XMLSchema#](http://www.w3.org/2001/XMLSchema#)                     |
| owl    | [http://www.w3.org/2002/07/owl#](http://www.w3.org/2002/07/owl#)                           |
| skos   | [http://www.w3.org/2004/02/skos/core#](http://www.w3.org/2004/02/skos/core#)               |
| schema | [http://schema.org/](http://schema.org/)                                                   |
| prov   | [http://www.w3.org/ns/prov#](http://www.w3.org/ns/prov#)                                   |
| geo    | [http://www.opengis.net/ont/geosparql#](http://www.opengis.net/ont/geosparql#)             |

---

## Ontology

This section compiles objects and predicates internal to the format.

### Objects

| Name              | Usage             | Context               |
| ----------------- | ----------------- | --------------------- |
| wikibase:Item     | Wikibase item     | Type for `wd:Q123`    |
| wikibase:Property | Wikibase property | Type for `wd:P123`    |
| wikibase:Lexeme   | Wikibase lexeme   | Type for `wd:L123`    |
| wikibase:Form     | Lexeme form       | Type for `wd:L123-F1` |
| wikibase:Sense    | Lexeme sense      | Type for `wd:L123-S1` |

