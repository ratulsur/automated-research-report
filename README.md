# Autonomous Multi-Agent Research Report Generator

A LangGraph multi-agent system that autonomously produces structured research reports on any
topic — generating analyst personas, running parallel AI-interview workflows with live web
retrieval, and synthesizing the results into a validated, multi-section report.

## What it does

Given a topic, the system spins up a set of distinct **analyst personas**, each of which
interviews an AI domain expert in parallel. Every interview is grounded in live web search
(Tavily), and the responses are captured as **schema-validated structured output**. A synthesis
step then composes the individual analyses into a single coherent research report. The whole
flow is orchestrated as a LangGraph state machine, so steps run concurrently where possible and
state is passed cleanly between nodes.

## Architecture

```
Topic
  │
  ▼
Analyst-persona generation        ← create N distinct analyst viewpoints
  │
  ▼
Parallel AI interviews            ← each analyst interviews an AI expert
  │   └── Tavily web retrieval     grounds each turn in live sources
  │   └── Pydantic structured output + retry logic
  ▼
Synthesis                         ← merge analyses into one narrative
  │
  ▼
Structured research report
```

LangGraph orchestrates the nodes and manages state; the parallel interviews are the core of the
multi-agent design.

## Stack

Python · LangGraph · LangChain · GPT-4o (OpenAI) · Tavily Search · Pydantic

## Engineering notes

The interview responses are parsed into Pydantic models for reliable downstream use. LLM
structured output fails in practical ways — truncated JSON when a response runs long, malformed
fields — so generation is wrapped in **validation-plus-retry logic** that re-prompts on a parse
failure rather than crashing the pipeline. This keeps multi-agent runs robust over many calls,
where a single unhandled malformed response would otherwise abort the whole report.

## Run it

```bash
git clone https://github.com/ratulsur/<repo>.git
cd <repo>
pip install -r requirements.txt

# Set credentials (this project reads them from a .env file, which is gitignored)
cp .env.example .env        # then add your keys:
#   OPENAI_API_KEY=...
#   TAVILY_API_KEY=...

python main.py              # NOTE: replace main.py with your actual entry file if different
```

## Output

The system produces a structured, multi-section research report synthesized from the parallel
analyst interviews, with content grounded in retrieved web sources. _(Add a sample report or a
short run snippet here to show reviewers the output without running the code.)_

## Possible extensions

- Configurable number of analysts and interview depth.
- Pluggable retrieval backends beyond Tavily.
- Export to PDF / Markdown, or a lightweight UI over the pipeline.
