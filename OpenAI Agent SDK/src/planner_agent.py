"""Planner agent configuration and output schemas for search planning."""

from pydantic import BaseModel, Field
from agents import Agent

# Keep this centralized so prompt and expected output size stay aligned.
HOW_MANY_SEARCHES = 5

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."


class WebSearchItem(BaseModel):
    """Single planned web search with rationale.

    Attributes:
        reason: Why this search contributes to answering the user query.
        query: Concrete term to pass to the web search tool.
    """

    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    """Collection of searches to execute for one research request.

    Attributes:
        searches: Ordered list of planned searches for evidence gathering.
    """

    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")


# Configure a structured-output agent so downstream code can rely on typed planning data.
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)