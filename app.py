import json
import os
from datetime import date

import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="PathPilot | AI Learning Roadmap",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(135deg, #f7f9ff 0%, #eef3ff 55%, #f8faff 100%); }
    [data-testid="stSidebar"] { background: #101828; }
    [data-testid="stSidebar"] * { color: #f4f7ff !important; }
    .hero {
        padding: 2rem 2.2rem; border-radius: 24px; color: white;
        background: linear-gradient(120deg, #4338ca, #2563eb 60%, #0891b2);
        box-shadow: 0 12px 32px rgba(37, 99, 235, .18);
    }
    .hero h1 { color: white; font-size: 2.35rem; margin: 0; }
    .hero p { color: #eaf1ff; margin: .65rem 0 0 0; font-size: 1.05rem; }
    .small-note { color: #667085; font-size: .88rem; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #e6eaf2; padding: 1rem; border-radius: 16px; }
    div[data-testid="stExpander"] { border-radius: 14px; border: 1px solid #e5eaf3; background: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- API configuration ----------
def get_api_key():
    """Read the Gemini key from Streamlit Secrets or local environment."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def make_client(api_key: str):
    return genai.Client(api_key=api_key)


def roadmap_prompt(profile: dict) -> str:
    return f"""
You are an expert learning-plan designer. Build a realistic, personalized learning roadmap.
Use the user's inputs below. Do not claim that resources or URLs were verified live.
Prefer well-known, free resources and provide a resource name plus a URL only when you are confident
it is correct. If unsure, provide the resource name and say "search for this resource" instead.

USER PROFILE
{json.dumps(profile, ensure_ascii=False, indent=2)}

Return ONLY valid JSON with this exact top-level structure:
{{
  "roadmap_title": "short motivating title",
  "summary": "2-4 sentence overview",
  "total_duration": "duration estimate",
  "weekly_hours": number,
  "milestones": [
    {{"name": "milestone name", "target_week": 1, "outcome": "measurable outcome"}}
  ],
  "weeks": [
    {{
      "week": 1,
      "theme": "weekly theme",
      "goal": "specific weekly outcome",
      "estimated_hours": number,
      "topics": [
        {{"name": "topic", "duration": "time estimate", "description": "plain-language explanation"}}
      ],
      "practice": ["exercise"],
      "project": {{"name": "project name", "brief": "what to build", "deliverables": ["deliverable"]}},
      "resources": [
        {{"name": "resource name", "url": "URL or empty string", "type": "course/video/docs/article", "why": "why it helps"}}
      ],
      "checkpoint": "how the learner can check understanding"
    }}
  ],
  "study_tips": ["tip"],
  "next_steps": ["action"]
}}

Requirements:
- Adapt roadmap depth and pace to the stated skill level, interests, and time availability.
- Include a sensible number of weeks (normally 4-16, adjusted to available time and goal scope).
- Keep week-to-week progression logical; include beginner foundations where needed.
- Make every week actionable and include topics, practice, a small project, resources, and checkpoint.
- Be encouraging but realistic. Avoid guaranteeing mastery or job readiness.
- Do not invent certifications, resource titles, or links.
"""


def parse_json_response(text: str) -> dict:
    """Parse model JSON, allowing a surrounding markdown code fence."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    return json.loads(cleaned)


def generate_roadmap(profile: dict, api_key: str, model: str) -> dict:
    client = make_client(api_key)
    response = client.models.generate_content(
        model=model,
        contents=roadmap_prompt(profile),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.6,
        ),
    )
    if not response.text:
        raise ValueError("The model returned an empty response. Please try again.")
    return parse_json_response(response.text)


# ---------- Interface ----------
st.markdown(
    """
    <div class="hero">
      <h1>🧭 PathPilot</h1>
      <p>Your goals. Your pace. A learning roadmap built with AI.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")
st.write("Tell PathPilot what you want to learn. It will organize your journey into practical weekly steps.")

with st.sidebar:
    st.markdown("## Your learning profile")
    st.caption("More specific inputs help produce a more useful plan.")
    goal = st.text_area(
        "What do you want to learn?",
        placeholder="Example: Learn machine learning and build beginner AI projects",
        height=100,
    )
    skill_level = st.selectbox("Current skill level", ["Beginner", "Intermediate", "Advanced"])
    interests = st.text_input(
        "Interests (optional)",
        placeholder="Example: healthcare, cars, creative apps",
    )
    weekly_hours = st.slider("Hours available each week", min_value=1, max_value=30, value=6)
    duration_weeks = st.slider("Roadmap length", min_value=4, max_value=16, value=8)
    learning_style = st.selectbox(
        "Preferred learning style",
        ["A mix of videos, reading, and practice", "Mostly hands-on projects", "Mostly videos", "Mostly reading"],
    )
    language = st.selectbox("Roadmap language", ["English", "Simple English"])
    model = st.text_input("Gemini model", value="gemini-3.8-flash", help="Use a Gemini model enabled for your API key.")
    generate = st.button("✨ Generate my roadmap", type="primary", use_container_width=True)

st.markdown("### What you'll get")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**🗓️ Weekly plan**")
    st.caption("Topics and estimated study time.")
with c2:
    st.markdown("**🛠️ Practice projects**")
    st.caption("Build skills by doing.")
with c3:
    st.markdown("**🎯 Milestones**")
    st.caption("Check your progress as you learn.")

if generate:
    if not goal.strip():
        st.warning("Please enter a learning goal first.")
    else:
        api_key = get_api_key()
        if not api_key:
            st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets or your local environment.")
        else:
            profile = {
                "learning_goal": goal.strip(),
                "current_skill_level": skill_level,
                "interests": interests.strip() or "Not specified",
                "hours_per_week": weekly_hours,
                "roadmap_length_weeks": duration_weeks,
                "preferred_learning_style": learning_style,
                "language": language,
                "start_date": str(date.today()),
            }
            with st.spinner("PathPilot is organizing your learning journey…"):
                try:
                    result = generate_roadmap(profile, api_key, model.strip())
                    st.session_state["roadmap"] = result
                    st.session_state["profile"] = profile
                except json.JSONDecodeError:
                    st.error("The AI response was not valid JSON. Please try again.")
                except Exception as exc:
                    st.error(f"Could not generate the roadmap: {exc}")
                    st.caption("Check your API key, model availability, internet connection, and API quota.")

if "roadmap" in st.session_state:
    data = st.session_state["roadmap"]
    profile = st.session_state.get("profile", {})
    st.divider()
    st.markdown(f"## 🎓 {data.get('roadmap_title', 'Your Learning Roadmap')}")
    st.write(data.get("summary", ""))
    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated duration", data.get("total_duration", f"{profile.get('roadmap_length_weeks', '—')} weeks"))
    m2.metric("Study time / week", f"{data.get('weekly_hours', profile.get('hours_per_week', '—'))} hours")
    m3.metric("Weeks planned", len(data.get("weeks", [])))

    milestones = data.get("milestones", [])
    if milestones:
        st.markdown("### 🏁 Milestones")
        for milestone in milestones:
            st.markdown(
                f"- **Week {milestone.get('target_week', '?')} — {milestone.get('name', 'Milestone')}**: "
                f"{milestone.get('outcome', '')}"
            )

    st.markdown("### 🗓️ Your week-by-week plan")
    weeks = data.get("weeks", [])
    for week in weeks:
        week_num = week.get("week", "?")
        with st.expander(f"Week {week_num}: {week.get('theme', 'Learning week')}", expanded=(week_num == 1)):
            st.markdown(f"**Weekly goal:** {week.get('goal', '—')}")
            st.caption(f"Estimated time: {week.get('estimated_hours', '—')} hours")
            topics = week.get("topics", [])
            if topics:
                st.markdown("**Topics to learn**")
                for topic in topics:
                    st.markdown(
                        f"- **{topic.get('name', 'Topic')}** ({topic.get('duration', 'time not specified')}): "
                        f"{topic.get('description', '')}"
                    )
            practice = week.get("practice", [])
            if practice:
                st.markdown("**Practice**")
                for item in practice:
                    st.markdown(f"- {item}")
            project = week.get("project", {})
            if project:
                st.markdown(f"**🛠️ Mini-project: {project.get('name', 'Project')}**")
                st.write(project.get("brief", ""))
                for deliverable in project.get("deliverables", []):
                    st.markdown(f"- {deliverable}")
            resources = week.get("resources", [])
            if resources:
                st.markdown("**📚 Resources**")
                for resource in resources:
                    name = resource.get("name", "Resource")
                    url = resource.get("url", "")
                    label = f"[{name}]({url})" if url.startswith(("https://", "http://")) else name
                    st.markdown(f"- {label} — {resource.get('type', 'resource')}. {resource.get('why', '')}")
            if week.get("checkpoint"):
                st.info(f"**Checkpoint:** {week['checkpoint']}")

    for section, heading in [("study_tips", "💡 Study tips"), ("next_steps", "🚀 Next steps")]:
        items = data.get(section, [])
        if items:
            st.markdown(f"### {heading}")
            for item in items:
                st.markdown(f"- {item}")

    export_json = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button(
        "⬇️ Download roadmap (JSON)",
        data=export_json,
        file_name="my_learning_roadmap.json",
        mime="application/json",
    )
    st.caption("AI-generated guidance can contain mistakes. Check resource links and adjust the plan to your pace.")
else:
    st.info("Your roadmap will appear here after you generate it.")
