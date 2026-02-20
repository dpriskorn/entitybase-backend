# Thanks

Users can thank other users for their contributions to revisions.

## Overview

The **thanks** feature allows users to express appreciation for revisions. When a user thanks another user for a revision, it's recorded in the system.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/entities/{entity_id}/revisions/{revision_id}/thanks` | Get all thanks for a specific revision |
| GET | `/users/{user_id}/thanks/received` | Get thanks received by a user |
| GET | `/users/{user_id}/thanks/sent` | Get thanks sent by a user |

## How It Works

1. A user sends a thank for a specific revision
2. The thank is recorded with the sender and revision info
3. Thanks are aggregated per user (received/sent counts)
4. Users can see who thanked them and for which revision

## Use Cases

- Show appreciation for helpful edits
- Encourage quality contributions
- Track user engagement
