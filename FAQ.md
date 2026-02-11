# FAQ
## What is the unique selling point?
Entitybase scales the Wikibase data model to enable storing the sum of human knowledge in a single system. See [VALUE_PROPOSITION.md](VALUE_PROPOSITION.md).

## Why build a new backend for the Wikibase data model?
Wikibase is built as an extension to the legacy PHP MediaWiki project. 
MediaWiki is using a MySQL-based backend that is not highly scalable as storage and the table layout is not designed to scale beyond 500M "pages"/entities with multiple revisions each.
Rewriting MediaWiki from scratch is probably a good idea if the Wikimedia movement really wants to pursue the goal of curating and sharing in the sum of all knowledge. 
Currently no plans exist to rewrite MW, thus sharing in the sum of all knowledge is currently not possible.

Wikidata has had multiple issues related to the sheer size of the Wikicite data being uploaded by users.
Also the rate of changes has proven difficult to keep up with for the Blazegraph backend (Wikidata Query Service).

WMF tasked a small team called Wikidata platform team in August 2025 to 
begin planning and executing a migration away from Blazegraph and that work is currently ongoing.

## Does it output data in the Wikibase data model?
Yes, `/entities/{entity_id}.json` is designed to output deduplicated entity data in JSON format. 
It can be expanded to the format used by Wikibase by looking up all the hashes 
but you probably rarely need to look up all at once.

## Which version of the Wikibase data model is supported?
The latest official one, https://www.mediawiki.org/w/index.php?title=Wikibase/DataModel&oldid=7684672

## Can I set up a QLever instance that follows the changes in the Entitybase backend?
Yes, it should work.

The system is designed to output RDF change events just like Wikidata
does using the same schema as WMF currently uses in production, but that feature is currently experimental. 
See doc/ARCHITECTURE/CHANGE-STREAMING/CONTINUOUS-RDF-CHANGE-STREAMER.md

## How can Entitybase scale better than Wikibase Suite?
A few design choices of the Wikibase system make it unsuitable for storing 1 trillion statements. 
The most limiting design flaw is not deduplicating 
the content in any way and just storing a blob of JSON for each revision.

Entitybase is deduplicating everything sent to it effectively reducing disk space estimated >50% (not yet verified). 

On the trillion statement, billion entity scale reducing 
storage costs is very important to approach O(n) and not have exponential 
growth like the current Wikibase Suite does (each revision is storing duplication of all the data which 
works ok for a 7M page Wikipedia, but not for 1 billion entities with a mean of 10+ revisions).

## Is Entitybase a drop-in replacement for Wikibase? 
No. It does not support any of the current tooling around Wikidata/Wikibase.
It does not yet have a frontend either.

The reason for broken compatibility is that Entitybase does not currently allow
entity update that updates non-atomically.
For example, both adding a new lemma and a new form in one operation is not supported.
It has to be broken down in 2 operations: first adding a lemma and then adding a new form.

Thus Entitybase is not compatible with the Wikibase REST API nor the MediaWiki APIs.

## Can I upload the latest Wikidata dump to Entitybase?
Yes, this should work. It has yet to be tested. Be bold and try it. See the dedicated endpoint and worker.

## How can I export data from Entitybase?
JSON dump export is planned but not yet implemented. The Dump Worker will support JSONL entity dumps in the future.

## Does it have a search backend?
No, not currently. All features are experimental. Search is very important but currently not in scope of the project. Feel free to send a PR!

## Does it have a frontend?
No, not currently. All features are experimental. A frontend is very important but currently not in scope of the project. Feel free to write one!

## Who developed Entitybase backend?
[Nizo Priskorn](https://www.wikidata.org/wiki/Q111016131)

## Is it stable?
No, the backend is currently in alpha state. All features are experimental. Data loss may occur. You get to keep all the parts if it breaks.

## Can I help?
Yes! Please feel free to open issues, write PRs, or share what you need 
from a scalable Wikibase data model compatible backend.

## How was it built?
Development started in December 2025. 
It has been built using mostly [GLM4.7](https://www.wikidata.org/wiki/Q138133653) and [opencode](https://opencode.ai/). 

First the architecture documents were written and discussed with the community in various Telegram channels then implementation in Python started.
Some parts have been fixed manually when GLM did not get the job done.

## Are there tests that verify the features work as expected?
Yes! See [STATISTICS.md](STATISTICS.md)

## What license is this project under?
GPLv3+. See the LICENSE file for details.

## How do I install and run Entitybase?
See [README.md](README.md) for getting started instructions. The quick start is:
```bash
docker-compose up -d
```
The API will be available at http://localhost:8000.

## What are the system requirements?
System requirements depend on the number of entities and statements you plan to store. For development, Docker and ~8GB RAM are sufficient. For production with billions of entities, you will need scalable S3-compatible storage and Vitess database infrastructure. See [README.md](README.md) for scaling characteristics.