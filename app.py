import streamlit as st
from main import evaluate_prompt

st.set_page_config(page_title="Judge Guardrail", page_icon="🧑‍⚖️")
st.title("🧑‍⚖️ Judge - Prompt Guardrail")

# Simulate the SLM evaluation function (replace with actual implementation)
# def evaluate_prompt(prompt: str):
#     # Example mocked response structure
#     return {
#         "nsfw": True,
#         "jailbreak": True,
#         "hate": False,
#         "exploit": False
#     }

# Mapping for colors
policy_colors = {
    "compliant": "#23d35e",   # Green
    "violation": "#f02b2b", # Red
    None: "#251f1f"    # Neutral / Pending
}

policy_names = ["nsfw", "jailbreak", "hate", "exploit"]

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []
if "latest_evals" not in st.session_state:
    st.session_state.latest_evals = {k: None for k in policy_names}


# Sidebar evaluation boxes
st.sidebar.title("Policy Evaluation")

for policy in policy_names:
    color = policy_colors[st.session_state.latest_evals[policy]]
    st.sidebar.markdown(f"""
    <div style='padding: 0.75em; background-color: {color}; border-radius: 0.5em; text-align: center; margin-bottom: 0.5em;'>
        <strong>{policy.upper()}</strong>
    </div>
    """, unsafe_allow_html=True)

# Chat display

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    

# Input box
if prompt := st.chat_input("Enter your prompt here..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Thinking..."):      
        _, results = evaluate_prompt(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.latest_evals = results

    status = [f"{k}" for k,v in results.items() if v is not "compliant"]

    assistant_response = f"Failed to comply: {', '.join(status)}." if status else "Compliant."

    st.session_state.messages.append({"role": "assistant", "content":assistant_response})   
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    st.rerun()
