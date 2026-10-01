import pytest
from griptape.artifacts import TextArtifact
from griptape.loaders import WebLoader

from griptape.linkup.drivers import LinkupWebScraperDriver


class TestLinkupWebScraperDriver:
    @pytest.fixture()
    def mock_linkup_client(self, mocker):
        mock_client = mocker.patch("linkup.LinkupClient")
        mock_client.return_value.fetch.return_value = mocker.Mock(markdown="# foo")
        return mock_client

    @pytest.fixture()
    def driver(self, mock_linkup_client):
        return LinkupWebScraperDriver(api_key="test")

    def test_client_uses_api_key(self, driver, mock_linkup_client):
        assert driver.client is mock_linkup_client.return_value
        mock_linkup_client.assert_called_once_with(api_key="test")

    def test_fetch_url(self, driver, mock_linkup_client):
        assert driver.fetch_url("https://example.com") == "# foo"
        mock_linkup_client.return_value.fetch.assert_called_once_with("https://example.com", render_js=False)

    def test_fetch_url_with_params(self, mock_linkup_client):
        driver = LinkupWebScraperDriver(api_key="test", render_js=True, params={"mode": "pro"})

        driver.fetch_url("https://example.com")

        mock_linkup_client.return_value.fetch.assert_called_once_with("https://example.com", render_js=True, mode="pro")

    def test_extract_page(self, driver):
        artifact = driver.extract_page("# foo")

        assert isinstance(artifact, TextArtifact)
        assert artifact.value == "# foo"

    def test_scrape_url(self, driver):
        artifact = driver.scrape_url("https://example.com")

        assert isinstance(artifact, TextArtifact)
        assert artifact.value == "# foo"

    def test_fetch_url_raises_error(self, driver, mock_linkup_client):
        mock_linkup_client.return_value.fetch.side_effect = Exception("test_error")
        with pytest.raises(Exception, match="test_error"):
            driver.fetch_url("https://example.com")

    def test_web_loader(self, driver):
        artifact = WebLoader(web_scraper_driver=driver).load("https://example.com")

        assert isinstance(artifact, TextArtifact)
        assert artifact.value == "# foo"
