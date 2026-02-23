from jinja2 import Environment, BaseLoader

jinja_env = Environment(loader=BaseLoader())

CREATE_ANALYSIS_PROMPT = jinja_env.from_string("""
you are tasked with creating a set of AI analysts. please follow the instructions:
1. first review the reseearch topic:
                                                                                           
                                                                                                                                         
                                               
                                                                                             
""")                                                                                    )