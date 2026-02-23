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
[No feedback given. Us eyour own discretion]
{% endif %}

3. 

                                                                                                                                        
                                                                                                                                         
                                               
                                                                                             
""")                                                                                    )