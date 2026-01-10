# Hash Collision Risk

## Overview
Term strings (labels, descriptions, aliases) are deduplicated using 64-bit rapidhash values. This creates a small risk of hash collisions where different strings produce identical hashes.

## Probability
- 64-bit hash space: ~1.84 × 10^19 possible values
- Collision probability with 1 trillion terms: ~100% (birthday paradox)
- However, rapidhash has excellent distribution; collisions are extremely rare in practice

## Impact
If collision occurs, different term strings would be treated as identical, potentially causing incorrect terms to display for entities.

## Mitigation
- Accept the minimal risk given the scale benefits
- Monitor for anomalies in term data
- Could upgrade to 128-bit hashes if needed

## Alternatives Considered
- Storing full strings (eliminates deduplication benefits)
- Content verification on load (adds complexity without full protection)