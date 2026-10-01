from griptape.loaders import WebLoader
from griptape.structures import Agent
from griptape.tools import WebScraperTool, WebSearchTool

from griptape.linkup.drivers import LinkupWebScraperDriver, LinkupWebSearchDriver

agent = Agent(
    tools=[
        WebSearchTool(web_search_driver=LinkupWebSearchDriver()),
        WebScraperTool(web_loader=WebLoader(web_scraper_driver=LinkupWebScraperDriver())),
    ]
)

agent.run("Find the Griptape documentation home page and summarize what it says about Drivers.")
