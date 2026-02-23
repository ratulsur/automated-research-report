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

Here 
""")