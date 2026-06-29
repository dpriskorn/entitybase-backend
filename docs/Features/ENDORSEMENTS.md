# Endorsements

Endorse statements to indicate agreement or validation.

## Overview

The **endorsements** feature allows users to endorse statements they agree with or consider valid. This is useful for community curation and quality assurance.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/statements/{statement_hash}/endorse` | Endorse a statement |
| DELETE | `/statements/{statement_hash}/endorse` | Withdraw endorsement from a statement |
| GET | `/statements/{statement_hash}/endorsements` | Get endorsements for a statement |
| GET | `/statements/{statement_hash}/endorsements/stats` | Get endorsement statistics |
| GET | `/users/{user_id}/endorsements` | Get endorsements given by a user |
| GET | `/users/{user_id}/endorsements/stats` | Get endorsement statistics for a user |

## How It Works

1. A user endorses a statement by its hash
2. The endorsement is recorded with the user and timestamp
3. Users can withdraw their endorsement
4. Statistics track total endorsements per statement and user

## Use Cases

- Community validation of statements
- Quality control for factual claims
- Prioritizing trusted information
- Track user expertise through endorsements
