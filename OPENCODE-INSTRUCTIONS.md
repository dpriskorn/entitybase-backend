# Guiding principles for new wikibase-backend

- Keep it simple, stupid 
- Less is more
- MVP first, non-core features can come later
- Use Python Pydantic and FastAPI framework to create a backend API that can replace Mediawiki/Wikibase/mariadb as backend.
- Avoid premature optimizations. Caching can wait, let's build something that scales to 1bn+ items accessible for 1 user first, then scale to 100k+ users.
- All code is Pydantic classes except main.py in every service
- Start small and simple, iterate in small steps