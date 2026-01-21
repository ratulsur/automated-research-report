from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

search = TavilySearchResults()

search.invoke("who is Lionel Messi?")