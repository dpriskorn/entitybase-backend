#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

try:
    from models.workers.entity_diff.entity_diff_response import EntityDiffResponse
    print("SUCCESS: EntityDiffResponse imported")
    
    from models.workers.entity_diff.entity_diff_worker import EntityDiffWorker
    print("SUCCESS: EntityDiffWorker imported")
    
    from models.workers.entity_diff.rdf_cannonicalizer import RDFCanonicalizer
    print("SUCCESS: RDFCanonicalizer imported")
    
    print("\nAll imports successful - circular import resolved!")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
