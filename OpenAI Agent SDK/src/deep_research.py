"""Gradio entrypoint for running the deep research workflow."""

import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)


async def run(query: str):
    """Stream progress and report chunks for a research query.

    Args:
        query: Topic or question to investigate.

    Yields:
        str: Incremental status updates and final markdown output.
    """
    # Forward each yielded chunk so the UI updates progressively.
    async for chunk in ResearchManager().run(query):
        yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")

    # Trigger research from either the button click or Enter in the textbox.
    run_button.click(fn=run, inputs=query_textbox, outputs=report)
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)

# Launch browser automatically for local interactive usage.
ui.launch(inbrowser=True)
