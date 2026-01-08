# Guiding principles for new wikibase-backend

- Keep it simple, stupid 
- Less is more
- MVP first, non-core features can come later
- Avoid premature optimizations. Caching can wait, let's build something that scales to 1bn+ items accessible for 1 user first, then scale to 100k+ users.
- Keep discrete components small and apart
- Use Python Pydantic and FastAPI framework 
- All code is Pydantic classes except main.py in every service
- Start small and simple, iterate in small steps
- No threat model, everybody is playing nice
- Start with 1 shard until we get MVP working
- Ask user before editing
- Don't run docker commands
- Never pass unparsed json around between methods - use json.loads as soon as possible
- All api endpoints return JSON
- /raw/ endpoint returns full revision schema, /entity/ endpoint extracts nested entity
- after each edit lets use ./run-linters.sh to check for ruff, dead code, mypy errors
- do this before running pytest:  export PYTHONPATH=/home/dpriskorn/src/python/wikibase-backend/src:$PYTHONPATH && source .venv/bin/activate
- after each edit with new tests lets use pytest to check that new tests pass
- generally one class per file for all classes with at least 1 method
- no relative imports
- no __future__ imports
- no strings in code - everything is enums
- no passing tuples or dicts between methods, use pydantic basemodels
- avoid websearch, everything we need is in the repo already just ask where to find what you need
- we don't expose internal_id outside the VitessClient class
- no backward compability

# Current task
add validation to all json input 

# todo
fix failing tests using get-docker-logs.sh
fix ruff, vulture and mypy warnings
move entity endpoints out of main.py
fix failing tests
