"""
Entity Diff Worker - Computes diffs between RDF versions of Wikibase entities
"""

import time
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional

from pydantic import Field
from pyld import jsonld  # type: ignore[import-untyped]

from models.infrastructure.stream.producer import StreamProducerClient
from models.data.rest_api.v1.response import RDFChangeEvent
from models.workers.entity_diff.entity_diff_request import EntityDiffRequest
from models.workers.entity_diff.entity_diff_response import EntityDiffResponse
from models.workers.entity_diff.enums import CanonicalizationMethod
from models.workers.entity_diff.rdf_cannonicalizer import RDFCanonicalizer
from models.workers.entity_diff.rdf_serializer import RDFSerializer
from models.workers.worker import Worker

Triple = Tuple[str, str, str]  # (subject, predicate, object)


class EntityDiffWorker(Worker):
    """Worker for computing entity diffs."""

    canonicalization_method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015
    rdf_stream_producer: Optional[StreamProducerClient] = Field(default=None)
    serializer: RDFSerializer = RDFSerializer()

    @property
    def canonicalizer(self) -> RDFCanonicalizer:
        return RDFCanonicalizer(method=self.canonicalization_method)

    async def compute_diff_from_rdf(
        self, entity_id: str, rdf_v1: str, rdf_v2: str, format_: str = "turtle"
    ) -> EntityDiffResponse:
        """Compute diff from RDF content strings."""
        request = EntityDiffRequest(
            entity_id=entity_id,
            rdf_content_v1=rdf_v1,
            rdf_content_v2=rdf_v2,
            format=format_,
            canonicalization_method=self.canonicalizer.method,
        )
        return await self.compute_diff(request)

    async def compute_diff_from_entity_data(
        self,
        entity_id: str,
        entity_data_v1: dict,
        entity_data_v2: dict,
        format_: str = "turtle",
    ) -> EntityDiffResponse:
        """Compute diff from Wikibase entity data dictionaries."""
        rdf_v1 = self.serializer.entity_data_to_rdf(entity_data_v1, format_)
        rdf_v2 = self.serializer.entity_data_to_rdf(entity_data_v2, format_)

        return await self.compute_diff_from_rdf(entity_id, rdf_v1, rdf_v2, format_)

    async def compute_diff(self, request: EntityDiffRequest) -> EntityDiffResponse:
        """Compute diff between two RDF versions of an entity."""
        start_time = time.time()

        # Canonicalize both versions
        triples_v1 = self.canonicalizer.canonicalize(
            request.rdf_content_v1, request.format
        )
        triples_v2 = self.canonicalizer.canonicalize(
            request.rdf_content_v2, request.format
        )

        # Compute set differences
        added = triples_v2 - triples_v1
        removed = triples_v1 - triples_v2

        processing_time = int((time.time() - start_time) * 1000)

        response = EntityDiffResponse(
            entity_id=request.entity_id,
            added_triples=sorted(list(added)),
            removed_triples=sorted(list(removed)),
            canonicalization_method=request.canonicalization_method.value,
            processing_time_ms=processing_time,
            triple_count_v1=len(triples_v1),
            triple_count_v2=len(triples_v2),
        )

        # Optionally publish to stream
        if self.rdf_stream_producer is not None:
            await self._publish_rdf_change_event(request, response)

        return response

    async def _publish_rdf_change_event(
        self, request: EntityDiffRequest, response: EntityDiffResponse
    ) -> None:
        """Publish RDF change event to stream following MediaWiki recentchange schema."""
        if not self.rdf_stream_producer:
            return

        # Create event following MediaWiki recentchange schema
        event = RDFChangeEvent(
            # Required schema fields
            meta={
                "dt": datetime.now(timezone.utc).isoformat() + "Z",
                "stream": "wikibase.entity_diff",
                "id": f"{request.entity_id}-{response.triple_count_v2}",
                "domain": "wikibase.org",  # TODO: Make configurable
                "uri": f"https://www.wikidata.org/wiki/{request.entity_id}",
            },
            # Wikibase-specific fields
            entity_id=request.entity_id,
            revision_id=response.triple_count_v2,  # Using triple count as revision for now
            from_revision_id=request.from_revision_id,
            # RDF diff data
            added_triples=response.added_triples,
            removed_triples=response.removed_triples,
            method=response.canonicalization_method,
            triple_count_diff=len(response.added_triples)
            - len(response.removed_triples),
            # MediaWiki recentchange schema fields
            title=request.entity_id,
            user="system",  # TODO: Get from request context
            timestamp=int(time.time()),
            comment=f"RDF diff: +{len(response.added_triples)} -{len(response.removed_triples)} triples",
            # Revision info
            revision={"new": response.triple_count_v2, "old": response.triple_count_v1},
            # Length info (using triple counts)
            length={"new": response.triple_count_v2, "old": response.triple_count_v1},
            # Server info
            server_name="wikibase-backend",
            server_url="https://wikibase-backend.example.com",  # TODO: Make configurable
            wiki="wikidatawiki",  # TODO: Make configurable
            # Required field
            patrolled=False,
        )

        await self.rdf_stream_producer.publish_change(event)


# Convenience functions for testing
async def diff_rdf_content(
    rdf_v1: str,
    rdf_v2: str,
    format_: str = "turtle",
    method: CanonicalizationMethod = CanonicalizationMethod.URDNA2015,
) -> Dict[str, Any]:
    """Compute diff between two RDF strings."""
    worker = EntityDiffWorker(canonicalization_method=method)

    request = EntityDiffRequest(
        entity_id="test",
        rdf_content_v1=rdf_v1,
        rdf_content_v2=rdf_v2,
        format=format_,
        canonicalization_method=method,
    )

    response = await worker.compute_diff(request)

    return {
        "added": response.added_triples,
        "removed": response.removed_triples,
        "canonicalization_method": response.canonicalization_method,
        "processing_time_ms": response.processing_time_ms,
        "triple_count_v1": response.triple_count_v1,
        "triple_count_v2": response.triple_count_v2,
    }
