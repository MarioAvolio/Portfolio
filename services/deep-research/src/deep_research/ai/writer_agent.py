"""Writer agent configuration and typed report output schema."""

from pydantic import BaseModel, Field
from agents import Agent

# Instruct the model to produce long-form, publication-ready markdown.
INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 2-3 pages of content, at least 500 words."
)


class ReportData(BaseModel):
    """Structured report payload returned by the writer agent.

    Attributes:
        short_summary: Brief synthesis of key findings.
        markdown_report: Full markdown report body.
        follow_up_questions: Additional research directions.
    """

    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


# Enforce typed output so the manager can safely consume each report field.
writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)