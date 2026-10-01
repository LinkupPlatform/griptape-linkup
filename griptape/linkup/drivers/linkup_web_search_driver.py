from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from attrs import define, field

from griptape.artifacts import JsonArtifact, ListArtifact
from griptape.drivers.web_search import BaseWebSearchDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from linkup import LinkupClient, LinkupSearchResults, LinkupSourcedAnswer


@define
class LinkupWebSearchDriver(BaseWebSearchDriver):
    """Web Search Driver for the Linkup API (https://docs.linkup.so).

    Attributes:
        api_key: Linkup API key. Falls back to the `LINKUP_API_KEY` environment variable when not set.
        depth: Search depth. `"standard"` for most queries, `"deep"` for complex multi-step questions.
        output_type: `"searchResults"` returns one artifact per source, `"sourcedAnswer"` returns a single
            artifact with an answer and the sources it cites.
        params: Additional parameters passed to `LinkupClient.search`, e.g. `include_domains` or `from_date`.
    """

    api_key: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    depth: Literal["fast", "standard", "deep"] = field(
        default="standard", kw_only=True, metadata={"serializable": True}
    )
    output_type: Literal["searchResults", "sourcedAnswer"] = field(
        default="searchResults", kw_only=True, metadata={"serializable": True}
    )
    params: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})
    _client: LinkupClient | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> LinkupClient:
        return import_optional_dependency("linkup").LinkupClient(api_key=self.api_key)

    def search(self, query: str, **kwargs) -> ListArtifact[JsonArtifact]:
        response = self.client.search(
            query,
            depth=self.depth,
            output_type=self.output_type,
            max_results=self.results_count,
            **self.params,
            **kwargs,
        )

        if self.output_type == "sourcedAnswer":
            answer = cast("LinkupSourcedAnswer", response)
            sources = [
                {"title": source.name, "url": source.url, "snippet": source.snippet} for source in answer.sources
            ]
            return ListArtifact([JsonArtifact({"answer": answer.answer, "sources": sources})])

        results = [
            {"type": result.type, "title": result.name, "url": result.url, "content": getattr(result, "content", None)}
            for result in cast("LinkupSearchResults", response).results
        ]
        return ListArtifact([JsonArtifact(result) for result in results])
