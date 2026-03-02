"""Unit tests for EntityUpdateTermsMixin."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.handlers.entity.update_terms import (
    EntityUpdateTermsMixin,
)


class TestEntityUpdateTermsMixin:
    """Unit tests for EntityUpdateTermsMixin._decrement_term_ref_count."""

    def _create_mixin_with_mocks(self):
        """Create a mixin with mocked dependencies."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_s3_client = MagicMock()
        mock_state.s3_client = mock_s3_client

        mixin = EntityUpdateTermsMixin(state=mock_state)

        return mixin, mock_vitess, mock_s3_client

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_handles_none_data(
        self, mock_terms_repo_class
    ) -> None:
        """Test handling when result.data is None - treats as orphaned (deletes)."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = None
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        mock_terms_repo.decrement_ref_count.assert_called_once_with(12345)

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_deletes_when_zero(
        self, mock_terms_repo_class
    ) -> None:
        """Test that term is Vitess and S3 deleted when ref_count hits 0."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = 0
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        mock_terms_repo.decrement_ref_count.assert_called_once_with(12345)
        mock_terms_repo.delete_term.assert_called_once_with(12345)
        mock_s3._delete_metadata.assert_called()

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_handles_failure(
        self, mock_terms_repo_class
    ) -> None:
        """Test graceful failure handling when decrement fails."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "DB error"
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        mock_terms_repo.decrement_ref_count.assert_called_once_with(12345)
        mock_terms_repo.delete_term.assert_not_called()
        mock_s3._delete_metadata.assert_not_called()

    @patch("models.rest_api.entitybase.v1.handlers.entity.update_terms.TermsRepository")
    def test_decrement_term_ref_count_deletes_all_metadata_types(
        self, mock_terms_repo_class
    ) -> None:
        """Test that all three metadata types are cleaned up when ref_count hits 0."""
        mixin, mock_vitess, mock_s3 = self._create_mixin_with_mocks()

        mock_terms_repo = MagicMock()
        mock_terms_repo_class.return_value = mock_terms_repo
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = 0
        mock_terms_repo.decrement_ref_count.return_value = mock_result

        mixin._decrement_term_ref_count(12345)

        assert mock_s3._delete_metadata.call_count == 3
