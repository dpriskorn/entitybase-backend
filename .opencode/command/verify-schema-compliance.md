---
description: Investigate YAML schema compliance
agent: plan
---
read these and make sure they all fit together.
This is returned to users and contain the revision schema + a few extra fields.
schemas/entitybase/entity/1.0.0/schema.yaml
has content from
schemas/entitybase/s3/revision/4.0.0/schema.yaml
has content from:
schemas/entitybase/s3/sitelink/1.0.0/schema.yaml
schemas/entitybase/s3/statement/1.0.0/schema.yaml
has contents from:
schemas/entitybase/s3/snak/1.0.0/schema.yaml
schemas/entitybase/s3/reference/1.0.0/schema.yaml
schemas/entitybase/s3/qualifier/1.0.0/schema.yaml

So its like a pyramid with 4 levels.