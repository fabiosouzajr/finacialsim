import pytest

from app.integrations.base import Err, Ok, Provider, ProviderChain


class FakeProvider:
    def __init__(self, name: str, should_succeed: bool, payload: str = "ok"):
        self.name = name
        self.should_succeed = should_succeed
        self.payload = payload
        self.calls = 0

    async def fetch(self, query):
        self.calls += 1
        if self.should_succeed:
            return Ok(self.payload)
        return Err(f"{self.name} failed")


async def test_chain_first_provider_wins():
    p1 = FakeProvider("p1", True, "from-p1")
    p2 = FakeProvider("p2", True, "from-p2")
    chain = ProviderChain([p1, p2])
    result = await chain.fetch({"q": 1})
    assert result.is_ok
    assert result.value == "from-p1"
    assert p1.calls == 1
    assert p2.calls == 0


async def test_chain_falls_back_to_second():
    p1 = FakeProvider("p1", False)
    p2 = FakeProvider("p2", True, "from-p2")
    chain = ProviderChain([p1, p2])
    result = await chain.fetch({"q": 1})
    assert result.is_ok
    assert result.value == "from-p2"
    assert p1.calls == 1
    assert p2.calls == 1


async def test_chain_all_fail_returns_err():
    p1 = FakeProvider("p1", False)
    p2 = FakeProvider("p2", False)
    chain = ProviderChain([p1, p2])
    result = await chain.fetch({"q": 1})
    assert result.is_err
