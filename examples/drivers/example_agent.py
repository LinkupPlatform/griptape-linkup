from griptape.structures import Agent
from griptape.tools import WebSearchTool

from griptape.linkup.drivers import LinkupWebSearchDriver

agent = Agent(tools=[WebSearchTool(web_search_driver=LinkupWebSearchDriver())])

agent.run("What are the latest Griptape framework releases? Cite your sources.")
