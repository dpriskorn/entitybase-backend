# FAQ
## What is the unique selling point?
Entitybase scales the Wikibase data model to enable storing the sum of human knowledge in a single system. 

## Why build a new backend for the Wikibase data model?
Wikibase is built as an extension to the legacy PHP MediaWiki project. 
MediaWiki is using a not that scalable mysql backend as storage and the table layout is not scaling very well.
Rewriting MediaWiki from scratch is probably a good idea if the Wikimedia movement really want to pursue the goal of curating and sharing in the sum of all knowledge. 
Currently no plans exist to rewrite MW, thus sharing in the sum of all knowledge is currently not possible.

Wikidata has had multiple issues related to the sheer size of the Wikicite data being uploaded by users.
Also the rate of changes has proven difficult to keep up with for the Blazegraph backend (Wikidata Query Service).

WMF tasked a small team called Wikidata platform team in august 2025 to 
begin planning and executing a migration away from Blazegraph and that work is currently ongoing.

# Does it output data in the Wikibase data model?
Yes, `/entities/{entity_id}.json` is designed to output deduplicated entity data in JSON format. 
It can be expanded to the format used by Wikibase by looking up all the hashes 
but you probably rarely need to look up all at once.

# Which version of the Wikibase data model is supported?
The latest official one here The latest official one here https://www.wikidata.org/wiki/Wikidata:Data_model

# Can I set up a QLever instance that follows the changes in the Entitybase backend
Perhaps :)

The system is designed to output RDF change events just like Wikidata 
does using the same schema as WMF currently use in production, but that feature is currently experimental. 
See doc/ARCHITECTURE/CHANGE-STREAMING/CONTINUOUS-RDF-CHANGE-STREAMER.md

# How can Entitybase scale better than Wikibase Suite?
A few design choices of the Wikibase system make it unsuitable for storing 1 trillion statements. 
The most limiting design flaw is not deduplicating 
the content in any way and just storing a blob of JSON for each revision.

Entitybase is deduplicating everything sent to it effectively reducing disk space perhaps >50% (unverified yet). 

On the trillion statement, billion entity scale reducing 
storage costs is very important to approach O(n) and not have exponential 
growth like the current Wikibase Suite does (each revision is storing duplication of all the data which 
works ok for a 7M page Wikipedia, but not for 1 billion entities with a mean of 10+ revisions).

# Is Entitybase a drop-in replacement for Wikibase? 
No. It does not support any of the current tooling around Wikidata/Wikibase.
It does not yet have a frontend either.

The reason for broken compatibility is that Entitybase does not currently allow 
entity update that updates non-atomically. 
Say both adding a new lemma and a new form in one operation. 
That's not supported. 
It has to be broken down in 2 operations: first adding a lemma and then adding a new form.

Thus Entitybase is not compatible with the Wikibase REST API nor the MediaWiki APIs.

# Does it have a search backend?
No, not currently. Search is very important but currently not in scope of the project. 
Feel free to send a PR! :D

# Does it have a frontend?
No, not currently. A frontend is very important but currently not in scope of the project. 
Feel free to write one! :D

# Who developed Entitybase backend
[Q111016131](https://www.wikidata.org/wiki/Q111016131)

# Is it stable
No, the backend is currently in alpha state. You get to keep all the parts if it breaks :D

# Can I help
Yes! Please feel free to open issues, write PRs, or share what you need 
from a scalable Wikibase data model compatible backend.

# How was it built?
Development started in december 2025. 
It has been build using mostly GLM4.7 and opencode. 
First the architecture was written and then implementation in Python started.
Some parts have been fixed manually when GLM did not get the job done.

# Are there tests that verify the features work as expected?
Yes! See STATISTICS.md