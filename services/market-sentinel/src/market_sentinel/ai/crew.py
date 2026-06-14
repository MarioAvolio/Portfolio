"""CrewAI crew definition for market-sentinel.

Heavy imports (crewai, crewai_tools) are deferred inside run() so the
webserver layer remains importable without the ML stack.
"""

from pathlib import Path

_CONFIG_DIR = Path(__file__).parent / "config"


class SentinelCrew:
    """Two-agent sequential crew that produces a SWOT report."""

    def __init__(self, openai_model: str = "gpt-4o-mini") -> None:
        """Stores the LLM model name used by both agents.

        Args:
            openai_model: OpenAI model identifier passed to CrewAI agents.
        """
        self._model = openai_model

    def run(self, product: str, competitors: list[str]) -> str:
        """Executes the crew synchronously and returns the SWOT report.

        Called via asyncio.to_thread from the async background task.

        Args:
            product: Product name to analyse.
            competitors: List of competitor names.

        Returns:
            Markdown SWOT report as a string.

        Raises:
            Exception: Any CrewAI or network failure propagates to the caller.
        """
        import yaml
        from crewai import Agent, Crew, Process, Task
        from crewai_tools import SerperDevTool

        agents_cfg: dict = yaml.safe_load((_CONFIG_DIR / "agents.yaml").read_text())
        tasks_cfg: dict = yaml.safe_load((_CONFIG_DIR / "tasks.yaml").read_text())

        competitors_str = ", ".join(competitors)

        def _fmt(text: str) -> str:
            return (
                text.replace("{product}", product)
                .replace("{competitors}", competitors_str)
                .replace("{openai_model}", self._model)
            )

        researcher = Agent(
            role=agents_cfg["market_researcher"]["role"],
            goal=_fmt(agents_cfg["market_researcher"]["goal"]),
            backstory=_fmt(agents_cfg["market_researcher"]["backstory"]),
            tools=[SerperDevTool()],
            llm=self._model,
            verbose=False,
        )
        analyst = Agent(
            role=agents_cfg["strategic_analyst"]["role"],
            goal=_fmt(agents_cfg["strategic_analyst"]["goal"]),
            backstory=_fmt(agents_cfg["strategic_analyst"]["backstory"]),
            tools=[],
            llm=self._model,
            verbose=False,
        )
        research_task = Task(
            description=_fmt(tasks_cfg["research_task"]["description"]),
            expected_output=_fmt(tasks_cfg["research_task"]["expected_output"]),
            agent=researcher,
        )
        analysis_task = Task(
            description=_fmt(tasks_cfg["analysis_task"]["description"]),
            expected_output=_fmt(tasks_cfg["analysis_task"]["expected_output"]),
            agent=analyst,
            context=[research_task],
        )
        crew = Crew(
            agents=[researcher, analyst],
            tasks=[research_task, analysis_task],
            process=Process.sequential,
            verbose=False,
        )
        result = crew.kickoff(inputs={"product": product, "competitors": competitors_str})
        return result.raw
