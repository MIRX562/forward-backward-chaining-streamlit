import streamlit as st
import json
from io import StringIO
from graphviz import Digraph

st.set_page_config(page_title="Expert System", layout="wide")
st.title("Forward/Backward Chaining Expert System")

# ---------- Sidebar Settings ----------
st.sidebar.header("Settings")
method = st.sidebar.selectbox("Chaining Method", ["Forward Chaining", "Backward Chaining"])

# ---------- Initialize Session State ----------
if "rules" not in st.session_state:
    st.session_state.rules = [
        {"if": ["A"], "then": "B"},
        {"if": ["B"], "then": "C"},
        {"if": ["C"], "then": "D"},
    ]
if "facts" not in st.session_state:
    st.session_state.facts = ["A"]

# ---------- Load Rules from File ----------
st.sidebar.subheader("Import/Export Rules")
uploaded_file = st.sidebar.file_uploader("Import Rules (JSON)", type="json")
if uploaded_file:
    try:
        data = json.load(uploaded_file)
        st.session_state.rules = data["rules"]
        st.sidebar.success("Rules imported successfully!")
    except Exception as e:
        st.sidebar.error(f"Failed to import rules: {e}")

if st.sidebar.button("Export Rules as JSON"):
    rules_data = {"rules": st.session_state.rules}
    json_data = json.dumps(rules_data, indent=2)
    st.sidebar.download_button("Download Rules", json_data, file_name="rules.json")

# ---------- Facts Input ----------
st.subheader("Known Facts")
fact_inputs = []
cols = st.columns([6, 1])
with cols[0]:
    for i, fact in enumerate(st.session_state.facts):
        new_fact = st.text_input(f"Fact #{i+1}", value=fact, key=f"fact_{i}")
        fact_inputs.append(new_fact.strip())
with cols[1]:
    if st.button("➕ Add Fact"):
        st.session_state.facts.append("")

# ---------- Rules Input ----------
st.subheader("Rules")
cols = st.columns([8, 1])
with cols[0]:
    for i, rule in enumerate(st.session_state.rules):
        if_part = st.text_input(f"IF part #{i+1}", value=", ".join(rule["if"]), key=f"if_{i}")
        then_part = st.text_input(f"THEN part #{i+1}", value=rule["then"], key=f"then_{i}")
        st.session_state.rules[i] = {
            "if": [item.strip() for item in if_part.split(",") if item.strip()],
            "then": then_part.strip()
        }
with cols[1]:
    if st.button("➕ Add Rule"):
        st.session_state.rules.append({"if": [], "then": ""})

# ---------- Reasoning Functions ----------
def forward_chaining(facts, rules):
    derived = set(facts)
    trace = []
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if all(f in derived for f in rule["if"]) and rule["then"] not in derived:
                derived.add(rule["then"])
                trace.append(f"Applied: IF {rule['if']} THEN {rule['then']}")
                changed = True
    return derived, trace

def backward_chaining(goal, facts, rules, trace=None):
    if trace is None:
        trace = []
    if goal in facts:
        trace.append(f"Goal '{goal}' is already known.")
        return True, trace
    for rule in rules:
        if rule["then"] == goal:
            trace.append(f"Trying rule: IF {rule['if']} THEN {goal}")
            satisfied = all(backward_chaining(fact, facts, rules, trace)[0] for fact in rule["if"])
            if satisfied:
                facts.append(goal)
                trace.append(f"Goal '{goal}' proved.")
                return True, trace
    trace.append(f"Goal '{goal}' cannot be proven.")
    return False, trace

# ---------- Reasoning Execution ----------
st.divider()
if method == "Forward Chaining":
    st.subheader("Forward Chaining Result")
    derived, trace = forward_chaining(fact_inputs, st.session_state.rules)
    st.markdown("**Derived Facts:**")
    st.write(sorted(derived))
    st.markdown("**Trace:**")
    for step in trace:
        st.text(step)

elif method == "Backward Chaining":
    goal = st.text_input("Enter Goal to Prove", "D")
    if goal:
        st.subheader("Backward Chaining Result")
        success, trace = backward_chaining(goal.strip(), fact_inputs.copy(), st.session_state.rules)
        st.markdown("**Result:**")
        st.write("✅ Proved!" if success else "❌ Cannot be proven.")
        st.markdown("**Trace:**")
        for step in trace:
            st.text(step)

# ---------- Rule Graph Visualization ----------
st.divider()
st.subheader("Rule Visualization")

def draw_graph(rules):
    dot = Digraph()
    for rule in rules:
        for premise in rule["if"]:
            dot.edge(premise, rule["then"])
    return dot

graph = draw_graph(st.session_state.rules)
st.graphviz_chart(graph)
