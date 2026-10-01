# Griptape Linkup Extension

## Overview

This extension adds [Linkup](https://www.linkup.so) to the [Griptape framework](https://github.com/griptape-ai/griptape):

- `LinkupWebSearchDriver`, a [Web Search Driver](https://docs.griptape.ai/stable/griptape-framework/drivers/web-search-drivers/) for real-time web search with citable sources, for use with `WebSearchTool`.
- `LinkupWebScraperDriver`, a [Web Scraper Driver](https://docs.griptape.ai/stable/griptape-framework/drivers/web-scraper-drivers/) that fetches any URL as clean markdown through Linkup, for use with `WebLoader` and `WebScraperTool`.

## Installation

```bash
pip install griptape-linkup
```

Or with uv:

```bash
uv add griptape-linkup
```

To install directly from the repository:

```bash
pip install git+https://github.com/LinkupPlatform/griptape-linkup.git
```

## Configuration

Get an API key from the [Linkup dashboard](https://app.linkup.so) and either export it:

```bash
export LINKUP_API_KEY=your-api-key
```

or pass it explicitly with `api_key=...` to either driver.

## Quickstart

### Web Search Driver

```python
from griptape.structures import Agent
from griptape.tools import WebSearchTool

from griptape.linkup.drivers import LinkupWebSearchDriver

agent = Agent(tools=[WebSearchTool(web_search_driver=LinkupWebSearchDriver())])

agent.run("What are the latest Griptape framework releases? Cite your sources.")
```

The driver can also be used on its own:

```python
from griptape.linkup.drivers import LinkupWebSearchDriver

driver = LinkupWebSearchDriver(results_count=5)

for artifact in driver.search("griptape ai framework"):
    print(artifact.value["title"], artifact.value["url"])
```

By default, `search` returns a `ListArtifact` with one `JsonArtifact` per source, each with the keys
`type`, `title`, `url` and `content`.

| Attribute | Default | Description |
| --- | --- | --- |
| `api_key` | `None` | Linkup API key. Falls back to the `LINKUP_API_KEY` environment variable. |
| `depth` | `"standard"` | `"fast"`, `"standard"` for most queries, or `"deep"` for complex multi-step questions. |
| `output_type` | `"searchResults"` | `"searchResults"` for a list of sources, or `"sourcedAnswer"` for an answer with its sources. |
| `results_count` | `5` | Maximum number of results to return. |
| `params` | `{}` | Extra arguments for the Linkup search API, e.g. `include_domains`, `exclude_domains`, `from_date`, `to_date`, `include_images`. |

With `output_type="sourcedAnswer"`, `search` returns a `ListArtifact` with a single `JsonArtifact` containing
`answer` and `sources` (each with `title`, `url` and `snippet`):

```python
driver = LinkupWebSearchDriver(depth="deep", output_type="sourcedAnswer")
answer = driver.search("Who maintains the Griptape framework?")[0].value
print(answer["answer"])
```

### Web Scraper Driver

```python
from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import WebScraperTool

from griptape.linkup.drivers import LinkupWebScraperDriver

agent = Agent(
    tools=[WebScraperTool(web_loader=WebLoader(web_scraper_driver=LinkupWebScraperDriver()))],
)

agent.run("Summarize https://docs.griptape.ai")
```

| Attribute | Default | Description |
| --- | --- | --- |
| `api_key` | `None` | Linkup API key. Falls back to the `LINKUP_API_KEY` environment variable. |
| `render_js` | `False` | Render the page's JavaScript before extracting its content. |
| `params` | `{}` | Extra arguments for the Linkup fetch API, e.g. `mode`, `extract_images`, `timeout`. |

More examples are in the [examples/drivers](examples/drivers) folder. See the
[Linkup documentation](https://docs.linkup.so) for the full list of API parameters.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
make install   # Install all dependencies and pre-commit hooks
make test      # Run unit tests
make check     # Run format, lint, type and spelling checks
make format    # Format code
```

To run an example (the Agent examples also need `OPENAI_API_KEY`):

```bash
cp .env.example .env  # then fill in your keys
uv run --env-file .env python examples/drivers/example_agent.py
```

## License

[MIT](LICENSE)
