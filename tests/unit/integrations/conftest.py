"""Shared test helpers for integration provider tests."""

import httpx


class FailingClient:
    """Raises httpx.ConnectError immediately. Inject to test error paths without respx."""

    async def get(self, url, **kw):
        raise httpx.ConnectError("stubbed failure")

    async def aclose(self):
        pass
