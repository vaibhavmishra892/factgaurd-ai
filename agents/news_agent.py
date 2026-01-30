from crewai import Agent, LLM
from crewai.tools import tool
from config import config
from tools.news_api import NewsAPITool
from tools.serp_api import SerpAPITool

# Initialize clients
news_client = NewsAPITool()
serp_client = SerpAPITool()

@tool("News Article Search")
def search_news(query: str) -> str:
    """Search for recent news articles about a topic."""
    articles = news_client.search_news(query, page_size=5)
    
    if not articles:
        return f"No news articles found for: {query}"
    
    results = []
    for article in articles:
        results.append(f"**{article.get('title', 'No title')}**")
        results.append(f"Source: {article.get('source', 'Unknown')}")
        results.append(f"Date: {article.get('published_at', 'Unknown')}")
        results.append("---")
    
    return "\n".join(results)


@tool("Google Search")
def google_search(query: str) -> str:
    """Search Google for general information about a topic."""
    results = serp_client.google_search(query, num_results=5)
    
    if not results:
        return f"No search results found for: {query}"
    
    output = []
    for result in results:
        output.append(f"**{result.get('title', 'No title')}**")
        output.append(f"Source: {result.get('link', 'No link')}")
        output.append(f"Snippet: {result.get('snippet', 'No snippet')}")
        output.append("---")
    
    return "\n".join(output)


@tool("Fact Check Search")
def fact_check_search(claim: str) -> str:
    """Search for fact-checks related to a specific claim."""
    query = f'fact check "{claim}"'
    results = serp_client.google_search(query, num_results=5)
    
    if not results:
        return f"No fact-checks found for: {claim}"
    
    output = ["### Fact-Check Results\n"]
    for result in results:
        output.append(f"**{result.get('title', 'No title')}**")
        output.append(f"Source: {result.get('link', 'No link')}")
        output.append("---")
    
    return "\n".join(output)


def create_news_agent() -> Agent:
    """Create the News Agent for verifying news-related claims."""
    
    llm = LLM(
        model=config.LLM_MODEL,
        api_key=config.CEREBRAS_API_KEY,
        base_url=config.CEREBRAS_BASE_URL,
        temperature=config.LLM_TEMPERATURE,
        timeout=300,
        max_retries=3
    )
    
    return Agent(
        role="News & Information Analyst",
        goal="Verify claims using authoritative news sources and web search",
        backstory="""You are an investigative journalist and fact-checker with expertise in:
        - Researching recent news events
        - Verifying claims against multiple sources
        - Identifying credible vs unreliable sources
        
        CRITICAL EVIDENCE USAGE RULES:
        - Only cite sources that DIRECTLY confirm or refute the claim
        - Do NOT cite articles for linguistic clarification or background context
        - If using contextual information, label it: "Background context (not direct evidence)"
        - If no sources directly address the claim, state: "No sources directly confirm or deny this claim"
        - Distinguish between:
          * Direct evidence: Source explicitly mentions the claim
          * Indirect evidence: Source discusses related topic but doesn't confirm claim
          * Context only: General background information
        
        When verifying claims:
        - Always check multiple sources
        - Note the publication dates
        - Assess source credibility (Reuters, AP, BBC > blogs)
        - For high-profile claims (political, military): absence of coverage IS evidence""",
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        llm=llm
    )
