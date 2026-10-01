import pytest
from griptape.artifacts import ErrorArtifact, JsonArtifact, ListArtifact
from griptape.tools import WebSearchTool

from griptape.linkup.drivers import LinkupWebSearchDriver


class TestLinkupWebSearchDriver:
    @pytest.fixture()
    def mock_linkup_client(self, mocker):
        return mocker.patch("linkup.LinkupClient")

    def mock_text_result(self, mocker):
        result = mocker.MagicMock(type="text", url="bar", content="baz")
        result.name = "foo"
        return result

    def mock_image_result(self, mocker):
        result = mocker.MagicMock(spec=["type", "name", "url"], type="image", url="qux.png")
        result.name = "image"
        return result

    @pytest.fixture()
    def driver(self, mock_linkup_client, mocker):
        mock_response = mocker.Mock()
        mock_response.results = [self.mock_text_result(mocker), self.mock_text_result(mocker)]
        mock_linkup_client.return_value.search.return_value = mock_response
        return LinkupWebSearchDriver(api_key="test")

    def test_client_uses_api_key(self, driver, mock_linkup_client):
        assert driver.client is mock_linkup_client.return_value
        mock_linkup_client.assert_called_once_with(api_key="test")

    def test_search_returns_results(self, driver, mock_linkup_client):
        results = driver.search("test")
        assert isinstance(results, ListArtifact)
        assert all(isinstance(result, JsonArtifact) for result in results)
        output = [result.value for result in results]
        assert len(output) == 2
        assert output[0] == {"type": "text", "title": "foo", "url": "bar", "content": "baz"}
        mock_linkup_client.return_value.search.assert_called_once_with(
            "test", depth="standard", output_type="searchResults", max_results=5
        )

    def test_search_returns_image_results(self, driver, mock_linkup_client, mocker):
        mock_linkup_client.return_value.search.return_value.results = [self.mock_image_result(mocker)]

        output = [result.value for result in driver.search("test", include_images=True)]

        assert output == [{"type": "image", "title": "image", "url": "qux.png", "content": None}]

    def test_search_sourced_answer(self, mock_linkup_client, mocker):
        source = mocker.MagicMock(url="bar", snippet="baz")
        source.name = "foo"
        mock_linkup_client.return_value.search.return_value = mocker.Mock(answer="qux", sources=[source])
        driver = LinkupWebSearchDriver(api_key="test", depth="deep", output_type="sourcedAnswer", results_count=3)

        results = driver.search("test")

        assert len(results) == 1
        assert results[0].value == {"answer": "qux", "sources": [{"title": "foo", "url": "bar", "snippet": "baz"}]}
        mock_linkup_client.return_value.search.assert_called_once_with(
            "test", depth="deep", output_type="sourcedAnswer", max_results=3
        )

    def test_search_raises_error(self, driver, mock_linkup_client):
        mock_linkup_client.return_value.search.side_effect = Exception("test_error")
        with pytest.raises(Exception, match="test_error"):
            driver.search("test")

    def test_search_with_params(self, driver, mock_linkup_client):
        driver.params = {"include_domains": ["example.com"]}
        driver.search("test", from_date="2026-01-01")

        mock_linkup_client.return_value.search.assert_called_once_with(
            "test",
            depth="standard",
            output_type="searchResults",
            max_results=5,
            include_domains=["example.com"],
            from_date="2026-01-01",
        )

    def test_web_search_tool(self, driver):
        tool = WebSearchTool(web_search_driver=driver)

        result = tool.search({"values": {"query": "test"}})

        assert isinstance(result, ListArtifact)
        assert len(result) == 2

    def test_web_search_tool_error(self, driver, mock_linkup_client):
        mock_linkup_client.return_value.search.side_effect = Exception("test_error")
        tool = WebSearchTool(web_search_driver=driver)

        result = tool.search({"values": {"query": "test"}})

        assert isinstance(result, ErrorArtifact)
        assert "test_error" in result.value
