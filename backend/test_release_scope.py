import pytest
from fastapi import HTTPException
from backend.release_scope import release_scope, require_feature


def test_showcase_disables_deferred_features():
    for feature in ('research', 'ocr', 'original_storage', 'semantic_review'):
        with pytest.raises(HTTPException) as exc:
            require_feature(release_scope('showcase'), feature)
        assert exc.value.status_code == 409
        require_feature(release_scope('development'), feature)


def test_invalid_profile_and_unknown_feature_fail_closed():
    with pytest.raises(ValueError):
        release_scope('production-ready')
    with pytest.raises(HTTPException):
        require_feature(release_scope('showcase'), 'unknown')
