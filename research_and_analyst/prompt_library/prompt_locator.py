from jinja2 import Environment, BaseLoader

jinja_env = Environment(loader=BaseLoader())

# -------------------------
# Prompt: Create analysts
# -------------------------
CREATE_ANALYSIS_PROMPT = jinja_env.from_string("""
You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. First, review the research topic:
{% if topic %}
{{ topic }}
{% else %}
[No topic provided — focus on a generic research area relevant to AI analysis.]
{% endif %}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts:
{% if human_analyst_feedback %}
{{ human_analyst_feedback }}
{% else %}
[No feedback given — use your discretion to create diverse analyst perspectives.]
{% endif %}

3. Determine the most interesting themes based upon the topic and feedback above.

4. Pick the top {{ max_analysts | default(3) }} themes.

5. Assign one analyst to each theme.
""")

# -------------------------
# Prompt: Analyst asks questions
# -------------------------
ANALYST_ASK_QUESTIONS = jinja_env.from_string("""
You are an analyst tasked with interviewing an expert to learn about a specific topic.

Your goal is to boil down to interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.
2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your topic of focus and set of goals:
{% if goals %}
{{ goals }}
{% else %}
[No specific goals provided — assume a general AI research analyst perspective.]
{% endif %}

Begin by introducing yourself using a name that fits your persona, and then ask your question.
Continue to ask questions to drill down and refine your understanding of the topic.

When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"

Remember to stay in character throughout your response, reflecting the persona and goals provided to you.
Refer to the expert as "expert" (no other name).
""")

# -------------------------
# Prompt: Generate search query
# -------------------------
GENERATE_SEARCH_QUERY = jinja_env.from_string("""
You will be given a conversation between an analyst and an expert.
Your goal is to generate a well-structured query for use in retrieval and/or web-search related to the conversation.

First, analyze the full conversation.
Pay particular attention to the final question posed by the analyst.
Convert this final question into a well-structured web search query.
""")

# -------------------------
# Prompt: Expert answers using context
# -------------------------
GENERATE_ANSWERS = jinja_env.from_string("""
You are an expert being interviewed by an analyst.

Here is analyst area of focus:
{% if goals %}
{{ goals }}
{% else %}
[No goals provided — assume a general technical expert.]
{% endif %}

To answer the question, use this context:
{% if context %}
{{ context }}
{% else %}
[No context provided — answer generally using your expertise.]
{% endif %}

When answering questions, follow these guidelines:

1. Use only the information provided in the context.
2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.
3. The context contains sources at the top of each individual document.
4. Include these sources in your answer next to any relevant statements, e.g. [1], [2].
5. List your sources in order at the bottom of your answer.

Start your answers with: Expert :
""")

# -------------------------
# Prompt: Write report section
# -------------------------
WRITE_SECTION = jinja_env.from_string("""
You are an expert technical writer.
Your task is to create a short, easily digestible section of a report based on a set of source documents.

1. Analyze the content of the source documents:
- The name of each source document is at the start of the document, with the <Document> tag.

2. Create a report structure using markdown formatting:
- Use ## for the section title
- Use ### for sub-section headers

3. Write the report following this structure:
a. Title (## header)
b. Summary (### header)
c. Sources (### header)

4. Make your title engaging based upon the focus area of the analyst:
{% if focus %}
{{ focus }}
{% else %}
[No focus specified — write a general research insight section.]
{% endif %}

5. For the summary section:
- Set up summary with general background / context related to the focus area
- Emphasize what is novel, interesting, or surprising about insights gathered from the interview
- Create a numbered list of sources as you use them
- Do not mention interviewers or experts
- Aim for ~800 words max
- Use numbered sources in your report (e.g., [1], [2])

6. In the Sources section:
- Include all sources used in your report
- Provide full links or specific document paths
- One source per line (add two spaces at end of each line for Markdown newlines)

7. Avoid redundant sources.

8. Final review:
- Ensure the report follows the required structure
- Include no preamble before the title
""")

# -------------------------
# Prompt: Consolidate memos into final report
# -------------------------
REPORT_WRITER_INSTRUCTIONS = jinja_env.from_string("""
You are a technical writer creating a report on this overall topic:

{% if topic %}
{{ topic }}
{% else %}
[Topic unspecified — create a generalized AI research summary.]
{% endif %}

You have a team of analysts. Each analyst has:
1. Conducted an interview with an expert on a sub-topic.
2. Written up findings into a memo.

Your task:
1. You will be given a collection of memos.
2. Consolidate these into a crisp overall summary.
3. Preserve citations in brackets like [1], [2].
4. Create a final consolidated list of sources under "## Sources" with no duplicates.

Formatting rules:
- Use markdown formatting
- No preamble
- No sub-headings
- Start with: ## Insights
- End with: ## Sources
""")

# -------------------------
# Prompt: Intro / Conclusion
# -------------------------
INTRO_CONCLUSION_INSTRUCTIONS = jinja_env.from_string("""
You are a technical writer finishing a report on:

{% if topic %}
{{ topic }}
{% else %}
[General topic — AI Research]
{% endif %}

You will be given all of the sections of the report.
Your job is to write a crisp and compelling introduction or conclusion section.

Target around 100 words.

Use markdown formatting.

For your introduction:
- Create a compelling title using # header
- Use ## Introduction as the section header

For your conclusion:
- Use ## Conclusion as the section header

Here are the sections:
{% if formatted_str_sections %}
{{ formatted_str_sections }}
{% else %}
[No sections provided — summarize the overall theme instead.]
{% endif %}
""")