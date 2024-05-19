import streamlit as st
from OllaBench_gui_menu import menu_with_redirect, show_header
st.set_page_config(
    page_title="Understanding OllaBench",
    initial_sidebar_state="expanded"
)

# Main Streamlit app starts here
show_header()
menu_with_redirect()

# Verify the user's role
if st.session_state.role not in ["admin", "user"]:
    st.warning("You do not have permission to view this page.")
    st.stop()

col1, col2, col3 = st.columns([0.1,0.8,0.1])
with col1:
    st.write(" ")
with col3:
    st.write(" ")
with col2:
    st.title("Understanding OllaBench")
    
st.write('''
        **OllaBench is a novel a benchmark platform and dataset generator to evaluate Large Language Models' ability to reason and make decisions based on cognitive behavioral insights in cybersecurity.**
    ''')
st.image('OllaBench-Flows.png')
st.markdown('''
        **OllaGen1** which is short for "OllaBench Generator Category 1" generate scenarios for evaluating LLMs. This capability begins with Cybonto - my earlier research published in [the Journal of Medical Internet Research](https://xmed.jmir.org/2022/2/e33502). Cybonto formally documented 108 psychology constructs and thousands of related relationships based on 20 time-tested psychology theories that have been used to analyze and explain cognitive behavioral phenomenons relating to crimes including cyber crimes. From Cybonto and further research, I extracted a subset of constructs and their relationships for OllaBench. I call this subsest the OllaBench1's knoweldge graph. These constructs and relationships inform a database of peer-reviewed cognitive behavioral "instruments" including scenario descriptions for each of a construct. For example, this sentence "At work, [subject name] is active, enthusiastic, and proud." describes the construct "Affect" as mentioned in the peer-reviewed work "	Cognitive-affective drivers of employees' daily compliance with information security policies: A multilevel, longitudinal study" by D'Arcy and Lowry. A full list can be found in OllaBench Github repository [here](https://github.com/Cybonto/OllaBench/blob/main/OllaGen-1/references/Cybonto-Gen1_Prompt_References.csv).
         
        OllaGen1 the uses an "Evaluator LLM" such as Snowflake's ARCTIC or OpenAI's CHAT-GPT4 to mutate a few sentences describing a construct within the context of cybersecurity compliance/non-compliance into a library of thousand lines. Based on these libraries and the OllaBench1 knowledge graph, OllaGen1 generates thousands of scenarios for evaluating LLMs. A sample scenario is as follows. 
         
        Avery Johnson:
         The individual values following the organization's Information Security Policies. The individual expressed their plan to safeguard their company's data and technological assets. The individual has the ability to safeguard themselves against cyber breaches. I prioritize protecting my employer's sensitive information by following all security guidelines. Viewing compliance with the institution's security policies as vital.

        Emily Carter:
         The person understood the benefits of following the information security policies. The person views compliance with the institution's security policies as a mandatory requirement. A person has complete power over adhering to information security policies. The individual values following the institution's guidelines for Information Security Policies. The individual understands the consequences for violating the organization's information security policy.

        As shown, each scenario begins with brief cognitive behavioral profiles of two person. Then, the LLMs will be required to answer the following questions:
         
        Which of the following options best reflects Avery Johnson's or Emily Carter cognitive behavioral constructs?
        - (option a) - ['Knowledge', 'Social', 'Motivation', 'Attitude', 'Intent']
        - (option b) - ['Self-efficacy', 'Motivation', 'Intent', 'Subjective norms', 'Attitude']
        - (option c) - ['Attitude', 'Intent', 'Control', 'Motivation', 'Attitude']
        - (option d) - ['Control', 'Attitude', 'Response Efficacy', 'Benefits', 'Intent']"
        
        Who is LESS compliant with information security policies?
        - (option a) - Avery Johnson
        - (option b) - They carry the same risk level
        - (option c) - Emily Carter
        - (option d) - It is impossible to tell
            
        Will information security non-compliance risk level increase if these employees work closely in the same team?
        - (option a) - security non-compliance risk level may increase
        - (option b) - security non-compliance risk level will increase
        - (option c) - security non-compliance risk level will stay the same
        - (option d) - It is impossible to tell
            
        To increase information security compliance, which cognitive behavioral factor should be targetted for strengthening?
        - (option a) - Attitude
        - (option b) - Motivation
        - (option c) - Knowledge
        - (option d) - Intent
            
        The first question is of "Which Cognitive Path" (WCP) type. The second is of "Who is Who" (WHO) type. The third one is of "Team Risk Analysis" type, and the last question is of "Target Factor Analysis" type.
            
        **OllaBench1** then use the generated scenarios and questions to query against the evalutatee models hosted in Ollama.
            
        **The Average score** is the average of each model's 'Avg WCP score','Avg WHO score','Avg Team Risk score','Avg Target Factor score'. The model with the highest Average score could be the best performing model. However, it may not be the case with the most efficient model which is a combination of many factors including performance metrics and wasted response metric. 
            
        **Wasted Response** for each response is measured by the response's tokens and the response evaluation of being incorrect. The Wasted Average score is calculated by the total wasted tokens divided by the number of wrong responses. Further resource costs in terms of time and/or money can be derived from the total wasted response value. The model with the lowest Wasted Average score can be the most efficient model (to be decided in joint consideration with other metrics).
    ''')