# Consistency Model and Failure Recovery

## Write atomicity model

The system uses a **single-database ACID transaction** model with MariaDB as the system of record.

**Write order (strict):**
1. Write revision data to MariaDB
2. Insert revision metadata
3. Update entity head pointer

All writes happen within a single MariaDB database. ACID transactions guarantee atomicity — either all three steps succeed, or none do.

## Handling partial failures

### Case: Transaction fails (any step)

MariaDB rolls back the entire transaction atomically. No partial state is persisted.

**Recovery strategy:**
- Client receives an error and retries the full operation
- No orphaned data, no reconciliation needed

This makes the system **strictly consistent** by design.

### Case: Head update fails (should not happen)

If the transaction commits successfully, the head pointer is always updated. There is no scenario where revision metadata exists but the head pointer is stale, because both are in the same transaction.

**Recovery strategy:**
- N/A — prevented by transactional guarantees

---

## Transaction boundaries

All writes to MariaDB occur within a single ACID transaction:

- Atomicity — all steps succeed or all are rolled back
- Consistency — constraints are enforced at the database level
- Isolation — concurrent writes are serialized by MariaDB
- Durability — committed data survives crashes

No distributed transactions. No cross-system coordination. No reconciliation needed.

## S3 usage

S3 is used only for dump uploads (bulk data exports). These are:

- Non-critical operations that can be retried on failure
- Independent of the entity write path
- Not part of the consistency model

---

## Final consistency guarantees

- No data loss (MariaDB is authoritative)
- Heads never move backward
- History is immutable
- Readers see strictly consistent state
- All writes are atomic and durable
- No reconciliation needed
