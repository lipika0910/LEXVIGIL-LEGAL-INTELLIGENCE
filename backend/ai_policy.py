"""Live AI is unavailable until a free, India-only route is verified.

API keys and environment labels are not evidence of price or processing location.
This guard must be replaced by reviewed provider eligibility and dispatch, not an
operator switch that silently restores the legacy paid/global provider path.
"""

UNAVAILABLE = (
    'Live AI is unavailable: no free provider with verified India-only processing '
    'is enabled. No text was sent to an AI provider. Local contract analysis and '
    'OCR remain available.'
)


class AIUnavailable(RuntimeError):
    pass


def require_live_ai():
    raise AIUnavailable(UNAVAILABLE)


def status():
    return {'available': False, 'code': 'NO_ELIGIBLE_INDIA_FREE_PROVIDER',
            'processing_region': 'India only', 'paid_fallback_allowed': False,
            'reason': UNAVAILABLE}
