from jinja2 import Environment, BaseLoader

jinja_env = Environment(loader=BaseLoader())

CREATE_ANALYSIS_PROMPT = jinja_env.from_string
("""
you are tasked with creating a set of AI analysts. please follow the instructions:
1. first review the reseearch topic:
{% if topic %}
{{ topic}}
{% else %}
[No topic provided, focus on a more generic topic relevant to AI research and analysis]
{% endif %}

2. Examine any editorial feedback that has been optionally provided to guide creation of the analysts:
{% if human_analyst_feedback %}
{{ human_analysts_feedback}}
{ % else %}
[No feedback given. Use your own discretion]
{% endif %}

3. Determine the most important themes based upon the given documents.

4. pick the top {{ max_analysts | default(3)}} themes.

5. Assign one analyst to each theme.

""")  

ANALYST_ASK_QUESTIONS = jinja_env.from_string
("""
you are an analyst tasked with interviewing an expert to learn about a specific topic.

Your goal is to boil down interesting and specific topics related to the area of research.

1. Interesting: Insights that people will find surprising or non-obvious.
2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your topic of focus and set of goals:
{% if goals %}
{{ goals }}
{% else %}
[If no specific goals are provided assume a general AI Assistant perspective.]
{ % endif %}

Begin by introducing a name that suits your persona and the ask the question.

Continue to ask questions and boil down to most refined understanding.

When you are satisfied with the undersatnding, complete the interview with the words - "Thanks for your help"

Always stay in the character in such a way that it reflects your persona and the goals.

Refer to the expert as an expert. Please note that the expert does not have a name.

""")

GENERATE_SEARCH_QUERY = jinja_env.from_string
("""
You will be given a conversation between an analyst and the expert.
Your goal is to generate a question based on this conversation which will be later used for retrieval or web-search related to the conversation.
First analyse the full conversation.
Use the conversation to understand the final question.
Convert this question to a well-structured query which will be used for web-search 
""")

GENERATE_ANSWERS = jinja_env.from_string
("""
You are an expert being interviewed by an analyst.

Here is the goal which you will use for answering
{% if goals %}
{{goals}}
{% else %}
[If no goals are given, please fallback to the generic AI analyst.]
{ % endif %}

Your goal is to answer the question based on the given prompt.

{% if context %}
{{ context }}
{% else %}
[If no specific information is given, please fallback to the role of a general AI Analyst]
{% endif %}

When answering the questions please follow the followign instructions:

1. use the information from the given context only.
2. please do not use any external resources to answer the questions.
3. the context contains source at the top of each individual document.
4. include these sources in your answer and place them next to the relevant part of the answers. for example, for source #1 use [1].
5. list all the sources at the end of the answers. [1] source 1, [2] source 2

Start your answer with :Expert:

""")

WRITE_SECTION  = jinja_env.from_string
("""
you are an expert technical writer.
your task is to create short, comprehensible section of a report based on a set of souce documents.

1. Analyse the content of the source documents:
the name of the source document should be mentioned at the start of the document with <Document> tag.

2. create the report structure using the following markdown format:
-use ## for section segment.
-use ### for subsection segement.

3. write the report following this format:
a. Title(## header)
b. Summary(### header)
c. Sources (### header)

4. Make your title engaging based on the focus area of the analyst:
{% if focus %}
{{ focus }}
{% else %}
[If no specific information is given please fallback to the role of a general AI analyst]
{% endif %}

5. For summary section:
- - Set up summary with general background / context related to the focus area of the analyst
- Emphasize what is novel, interesting, or surprising about insights gathered from the interview
- Create a numbered list of source documents, as you use them
- Do not mention the names of interviewers or experts
- Aim for approximately 800 words maximum
- Use numbered sources in your report (e.g., [1], [2]) based on information from source documents

6. In the Sources section:
- Include all sources used in your report
- Provide full links to relevant websites or specific document paths
- Separate each source by a newline. Use two spaces at the end of each line to create a newline in Markdown.
Example:
### Sources  
[1] Link or Document name  
[2] Link or Document name

7. be sure to combine the sources without any redundancy. For example this os not correct:
[3] https://ai.meta.com/blog/meta-llama-3-1/
[4] https://ai.meta.com/blog/meta-llama-3-1/

these sources should eb combined into one souce only:
[3] [3] https://ai.meta.com/blog/meta-llama-3-1/

8. Final review:
- make sure the report follows a proper structure.
- inlcude no preamble before the title of the report.
- check all the guidelines have been followed.
""")


REPORT_WRITER_INSTRUCTIONS = jinja_env.from_string("""
You are a technical writer creating a report on this overall topic: 

{% if topic %}
{{ topic }}
{% else %}
[Topic unspecified — create a generalized AI research summary.]
{% endif %}

You have a team of analysts. Each analyst has done two things: 
1. They conducted an interview with an expert on a specific sub-topic.
2. They wrote up their findings into a memo.

Your task:

1. You will be given a collection of memos from your analysts.
2. Think carefully about the insights from each memo.
3. Consolidate these into a crisp overall summary that ties together the central ideas from all of the memos.
4. Summarize the central points in each memo into a cohesive single narrative.

To format your report:

1. Use markdown formatting. 
2. Include no preamble for the report.
3. Use no sub-heading. 
4. Start your report with a single title header: ## Insights
5. Do not mention any analyst names in your report.
6. Preserve any citations in the memos, which will be annotated in brackets, for example [1] or [2].
7. Create a final, consolidated list of sources and add to a Sources section with the ## Sources header.
8. List your sources in order and do not repeat.

Example:
[1] Source 1  
[2] Source 2  
""")


INTRO_CONCLUSION_INSTRUCTIONS = jinja_env.from_string("""
You are a technical writer finishing a report on 
{% if topic %}
{{ topic }}
{% else %}
[General topic — AI Research]
{% endif %}

You will be given all of the sections of the report.

Your job is to write a crisp and compelling introduction or conclusion section.

The user will instruct you whether to write the introduction or conclusion.

Include no preamble for either section.

Target around 100 words, crisply previewing (for introduction) or recapping (for conclusion) all of the sections of the report.

Use markdown formatting.

For your introduction:
- Create a compelling title and use the # header for the title.
- Use ## Introduction as the section header.

For your conclusion:
- Use ## Conclusion as the section header.

Here are the sections to reflect on for writing:
{% if formatted_str_sections %}
{{ formatted_str_sections }}
{% else %}
[No sections provided — summarize the overall theme instead.]
{% endif %}
""")
