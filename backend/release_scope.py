"""Reduced sprint scope; never a deployment-readiness override."""
from fastapi import HTTPException


def release_scope(profile):
    if profile not in ('development', 'showcase'):
        raise ValueError('LEXVIGIL_RELEASE_PROFILE must be development or showcase.')
    enabled = profile == 'development'
    return {'profile': profile, 'research': enabled, 'ocr': enabled,
            'original_storage': enabled, 'semantic_review': enabled}


def require_feature(scope, feature):
    if not scope.get(feature, False):
        raise HTTPException(409, 'This feature is deferred from the contract-analysis showcase.')
