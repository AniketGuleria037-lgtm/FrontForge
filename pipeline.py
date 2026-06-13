import sys
sys.path.append(".")
from langgraph.graph import StateGraph, END
from state import AgentState
from agents.Clarification import clarification_agent
from agents.Planner import planner_agent
from agents.Architect import architect_agent
from agents.Package import package_agent
from agents.Component import component_agent
from agents.Styling import styling_agent
from agents.Reviewer import reviewer_agent

def build_pipeline():
    graph=StateGraph(AgentState)
    graph.add_node("clarification_agent", clarification_agent)
    graph.add_node("planner_agent",planner_agent)
    graph.add_node("architect_agent",architect_agent)
    graph.add_node("component_agent",component_agent)
    graph.add_node("styling_agent",styling_agent)
    graph.add_node("package_agent",package_agent)
    graph.add_node("reviewer_agent",reviewer_agent)

    graph.set_entry_point("clarification_agent")
    graph.add_edge("clarification_agent", "planner_agent")
    graph.add_edge("planner_agent", "architect_agent")
    graph.add_edge("architect_agent", "package_agent")
    graph.add_edge("package_agent", "component_agent")
    graph.add_edge("component_agent", "styling_agent")
    graph.add_edge("styling_agent", "reviewer_agent")
    graph.add_edge("reviewer_agent", END)

    return graph.compile()

if __name__ == "__main__":
    pipeline = build_pipeline()
    print("Pipeline built successfully")
    print(pipeline.get_graph().draw_ascii())
