"""Unit tests for misc response models."""

import pytest

from models.data.rest_api.v1.entitybase.response.misc import (
    AliasesResponse,
    BatchAliasesResponse,
    BatchDescriptionsResponse,
    BatchLabelsResponse,
    CleanupOrphanedResponse,
    DeleteResponse,
    DescriptionResponse,
    DescriptionsResponse,
    EntityJsonResponse,
    GeneralStatsResponse,
    LabelResponse,
    LabelsResponse,
    PropertiesResponse,
    RangeStatus,
    RangeStatuses,
    RevisionMetadataResponse,
    SitelinksResponse,
    TermsPerLanguage,
    TermsByType,
    TopEntityByBacklinks,
    TurtleResponse,
    VersionResponse,
    WatchCounts,
)


class TestCleanupOrphanedResponse:
    def test_basic(self):
        r = CleanupOrphanedResponse(cleaned_count=10)
        assert r.cleaned_count == 10

    def test_with_failures(self):
        r = CleanupOrphanedResponse(cleaned_count=10, failed_count=2, errors=["err1"])
        assert r.failed_count == 2
        assert len(r.errors) == 1


class TestRevisionMetadataResponse:
    def test_basic(self):
        r = RevisionMetadataResponse(
            revision_id=1,
            created_at="2024-01-01T00:00:00Z",
            user_id=123,
            edit_summary="Test edit",
        )
        assert r.revision_id == 1
        assert r.user_id == 123


class TestLabelResponse:
    def test_basic(self):
        r = LabelResponse(value="Test Label")
        assert r.value == "Test Label"


class TestDescriptionResponse:
    def test_basic(self):
        r = DescriptionResponse(value="Test Description")
        assert r.value == "Test Description"


class TestAliasesResponse:
    def test_basic(self):
        r = AliasesResponse(aliases=["alias1", "alias2"])
        assert len(r.aliases) == 2


class TestLabelsResponse:
    def test_basic(self):
        r = LabelsResponse(labels={"en": "English", "de": "Deutsch"})
        assert r.labels["en"] == "English"


class TestDescriptionsResponse:
    def test_basic(self):
        r = DescriptionsResponse(descriptions={"en": "English desc"})
        assert "en" in r.descriptions


class TestSitelinksResponse:
    def test_basic(self):
        r = SitelinksResponse(sitelinks={"enwiki": "Article"})
        assert r.sitelinks["enwiki"] == "Article"


class TestPropertiesResponse:
    def test_basic(self):
        r = PropertiesResponse(properties={"P31": {}})
        assert "P31" in r.properties


class TestWatchCounts:
    def test_basic(self):
        r = WatchCounts(entity_count=100, property_count=50)
        assert r.entity_count == 100


class TestRangeStatus:
    def test_basic(self):
        r = RangeStatus(
            current_start=1000,
            current_end=2000,
            next_id=1500,
            ids_used=500,
            utilization=50.0,
        )
        assert r.current_start == 1000


class TestRangeStatuses:
    def test_basic(self):
        rs = RangeStatuses(ranges={"item": RangeStatus(
            current_start=1000,
            current_end=2000,
            next_id=1500,
            ids_used=500,
            utilization=50.0,
        )})
        assert "item" in rs.ranges


class TestTermsPerLanguage:
    def test_basic(self):
        r = TermsPerLanguage(terms={"en": 1000, "de": 500})
        assert r.terms["en"] == 1000


class TestTermsByType:
    def test_basic(self):
        r = TermsByType(counts={"labels": 1000, "descriptions": 500})
        assert r.counts["labels"] == 1000


class TestGeneralStatsResponse:
    def test_basic(self):
        r = GeneralStatsResponse(
            date="2024-01-01",
            total_statements=1000,
            total_qualifiers=500,
            total_references=300,
            total_items=100,
            total_lexemes=50,
            total_properties=20,
            total_sitelinks=200,
            total_terms=1500,
            terms_per_language=TermsPerLanguage(terms={"en": 1000}),
            terms_by_type=TermsByType(counts={"labels": 500}),
        )
        assert r.total_items == 100


class TestTurtleResponse:
    def test_basic(self):
        r = TurtleResponse(turtle="<ex:subject> <ex:predicate> <ex:object> .")
        assert "subject" in r.turtle


class TestEntityJsonResponse:
    def test_basic(self):
        r = EntityJsonResponse(data={"key": "value"})
        assert r.data["key"] == "value"


class TestBatchLabelsResponse:
    def test_basic(self):
        r = BatchLabelsResponse(labels={"hash1": "Label1"})
        assert "hash1" in r.labels


class TestBatchDescriptionsResponse:
    def test_basic(self):
        r = BatchDescriptionsResponse(descriptions={"hash1": "Desc1"})
        assert "hash1" in r.descriptions


class TestBatchAliasesResponse:
    def test_basic(self):
        r = BatchAliasesResponse(aliases={"hash1": ["alias1"]})
        assert "hash1" in r.aliases


class TestDeleteResponse:
    def test_basic(self):
        r = DeleteResponse(success=True)
        assert r.success is True


class TestVersionResponse:
    def test_basic(self):
        r = VersionResponse(api_version="1.0.0", entitybase_version="1.0.0")
        assert r.api_version == "1.0.0"


class TestTopEntityByBacklinks:
    def test_basic(self):
        r = TopEntityByBacklinks(entity_id="Q1", backlink_count=100)
        assert r.entity_id == "Q1"
