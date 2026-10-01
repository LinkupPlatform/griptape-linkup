from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.drivers.web_scraper import BaseWebScraperDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from linkup import LinkupClient


@define
class LinkupWebScraperDriver(BaseWebScraperDriver):
    """Web Scraper Driver that uses the Linkup fetch endpoint (https://docs.linkup.so) to get a page as markdown.

    Attributes:
        api_key: Linkup API key. Falls back to the `LINKUP_API_KEY` environment variable when not set.
        render_js: If `True`, Linkup renders the page's JavaScript before extracting its content.
        params: Additional parameters passed to `LinkupClient.fetch`, e.g. `mode` or `timeout`.
    """

    api_key: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    render_js: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    params: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})
    _client: LinkupClient | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> LinkupClient:
        return import_optional_dependency("linkup").LinkupClient(api_key=self.api_key)

    def fetch_url(self, url: str) -> str:
        response = self.client.fetch(url, render_js=self.render_js, **self.params)

        return response.markdown

    def extract_page(self, page: str) -> TextArtifact:
        return TextArtifact(page)
