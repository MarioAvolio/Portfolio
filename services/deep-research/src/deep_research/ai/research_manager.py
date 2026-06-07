from agents import Runner, trace, gen_trace_id
from deep_research.ai.search_agent import search_agent
from deep_research.ai.planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from deep_research.ai.writer_agent import writer_agent, ReportData
import asyncio


class ResearchManager:
    """Coordinate planning, web research, and report generation."""

    async def run(self, query: str):
        """Run the deep research workflow and stream progress updates.

        Args:
            query: The user research request to investigate.

        Yields:
            str: Progress messages, trace URL, and finally the markdown report.
        """
        # Generate and expose a trace so the full execution can be inspected later.
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            # Step 1: Ask the planner agent which searches should run.
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."
            # Step 2: Execute searches concurrently and collect successful results.
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            # Step 3: Hand gathered evidence to the writer agent.
            report = await self.write_report(query, search_results)
            yield "Report written."
            yield report.markdown_report

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """Create a search plan for the input query.

        Args:
            query: The user research request to analyze.

        Returns:
            WebSearchPlan: Structured list of searches to run.
        """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Execute planned searches in parallel and collect summaries.

        Args:
            search_plan: Planned search terms with rationale.

        Returns:
            list[str]: Summaries for searches that completed successfully.
        """
        print("Searching...")
        num_completed = 0
        # Schedule each search immediately to maximize throughput.
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        # Store only successful summaries (failed searches return None).
        results = []
        # Consume tasks in completion order, not creation order.
        for task in asyncio.as_completed(tasks):
            # Await the next finished task and get its summary payload.
            result = await task
            if result is not None:
                results.append(result)
            # Update progress even when a single search fails.
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        # Return all collected summaries for report synthesis.
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """Run one web search and return its summary when available.

        Args:
            item: Search query details produced by the planner agent.

        Returns:
            str | None: Search summary text, or ``None`` when the search fails.
        """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            # A single failed search should not stop the overall research run.
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """Generate the final report from collected search summaries.

        Args:
            query: Original user research question.
            search_results: Summaries returned by completed search tasks.

        Returns:
            ReportData: Structured report payload with markdown content.
        """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)