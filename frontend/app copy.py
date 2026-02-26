import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Family Knowledge Graph", layout="wide")

# ==================================================
# SESSION STATE
# ==================================================

if "selected_person" not in st.session_state:
    st.session_state.selected_person = None

if "graph_data" not in st.session_state:
    st.session_state.graph_data = None

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = None

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
    .main-title {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-size: 42px;
        font-weight: 600;
        color: #f5c542;
        letter-spacing: 0.06em;
        text-align: center;
        margin-bottom: 4px;
        text-shadow: 0 0 40px rgba(245,197,66,0.3);
    }
    .main-subtitle {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-size: 14px;
        color: #3a5a7a;
        text-align: center;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 32px;
    }
</style>
<div class='main-title'>🌳 Family Knowledge Graph</div>
<div class='main-subtitle'>Explore · Discover · Connect</div>
""", unsafe_allow_html=True)

mode = st.radio("Choose Mode", ["Browse Family", "Ask AI"], horizontal=True)

# ==================================================
# HELPER — field value or "—"
# ==================================================

def val(person, field):
    v = person.get(field)
    if v is None:
        return "—"
    s = str(v).strip()
    if s.lower() in ("", "none", "nan", "null", "n/a", "0"):
        return "—"
    return s

# ==================================================
# HELPER — Person Detail Card
# ==================================================

def render_person_card(person):
    ethnicities = [
        person.get(f"ethnicity_{i}")
        for i in range(1, 5)
        if person.get(f"ethnicity_{i}") and val(person, f"ethnicity_{i}") != "—"
    ]

    gender      = val(person, "gender").lower()
    gender_icon = "&#9794;" if gender == "male" else ("&#9792;" if gender == "female" else "&#9900;")
    avatar_border = "#5eb8ff" if gender == "male" else ("#d97de8" if gender == "female" else "#f5c542")
    avatar_glow   = "rgba(94,184,255,0.3)" if gender == "male" else ("rgba(217,125,232,0.3)" if gender == "female" else "rgba(245,197,66,0.3)")

    maiden_block = ""
    if val(person, "maiden_name") != "—":
        maiden_block = (
            "<div style='font-size:14px;color:#a0b8d0;margin-top:5px;font-style:italic;letter-spacing:0.03em;'>"
            + val(person, "maiden_name") + "</div>"
        )

    pill_colors = [
        ("#ffd580", "#3d2e00", "#7a5c00"),
        ("#f4a8d0", "#3d0028", "#7a0050"),
        ("#80d4f4", "#00263d", "#004d7a"),
        ("#a8f4c8", "#003d20", "#007a40"),
    ]
    ethnicity_pills = ""
    if ethnicities:
        for i, e in enumerate(ethnicities):
            txt, bg, border = pill_colors[i % len(pill_colors)]
            ethnicity_pills += (
                "<span style='display:inline-block;margin:5px 8px 5px 0;padding:7px 18px;"
                "border-radius:24px;background:" + bg + ";border:1.5px solid " + border + ";"
                "color:" + txt + ";font-size:14px;font-weight:600;letter-spacing:0.06em;"
                "box-shadow:0 2px 12px rgba(0,0,0,0.3);'>" + e + "</span>"
            )
    else:
        ethnicity_pills = "<span style='color:#4a6a7a;font-style:italic;font-size:14px;'>Not recorded</span>"

    notes_block = ""
    if val(person, "notes") != "—":
        notes_block = (
            "<div style='height:1px;background:linear-gradient(90deg,transparent,#2a3a5c,transparent);margin:20px 0;'></div>"
            "<div style='margin-bottom:8px;font-size:10px;color:#6a9abf;text-transform:uppercase;letter-spacing:0.16em;font-weight:600;'>Notes</div>"
            "<div style='font-size:14px;color:#a0b8cc;font-style:italic;line-height:1.8;"
            "background:rgba(94,184,255,0.04);border-radius:10px;padding:14px 18px;"
            "border-left:3px solid #2a4a6c;'>" + val(person, "notes") + "</div>"
        )

    def cell(label, value):
        if value == "—":
            val_style = "font-size:18px;color:#3a5a70;font-style:italic;font-weight:400;"
        else:
            val_style = "font-size:18px;color:#e8dcc8;font-weight:600;letter-spacing:0.02em;"
        return (
            "<div style='background:linear-gradient(135deg,rgba(255,255,255,0.04) 0%,rgba(255,255,255,0.01) 100%);"
            "border:1px solid #223050;border-radius:12px;padding:16px 18px;"
            "box-shadow:inset 0 1px 0 rgba(255,255,255,0.05);'>"
            "<div style='font-size:9px;color:#4a7aaa;text-transform:uppercase;"
            "letter-spacing:0.18em;margin-bottom:8px;font-weight:600;'>" + label + "</div>"
            "<div style='" + val_style + "'>" + value + "</div>"
            "</div>"
        )

    def section_label(text):
        return (
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:12px;'>"
            "<div style='height:1px;width:16px;background:#2a4a6c;'></div>"
            "<div style='font-size:9px;color:#4a7aaa;text-transform:uppercase;letter-spacing:0.2em;font-weight:700;'>" + text + "</div>"
            "<div style='height:1px;flex:1;background:linear-gradient(90deg,#2a4a6c,transparent);'></div>"
            "</div>"
        )

    gender_display = val(person, "gender").capitalize() if val(person, "gender") != "—" else "—"

    html = (
        "<!DOCTYPE html><html><head>"
        "<link href='https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap' rel='stylesheet'>"
        "<style>"
        "* {margin:0;padding:0;box-sizing:border-box;}"
        "body {font-family:'Libre Baskerville',Georgia,serif;background:transparent;padding:6px 2px;}"
        "</style></head><body>"
        "<div style='background:linear-gradient(160deg,#0c1a2e 0%,#0a0e1f 50%,#080c18 100%);"
        "border:1px solid #1e3050;border-radius:18px;padding:30px 34px 28px;"
        "box-shadow:0 0 60px rgba(94,184,255,0.05),0 12px 40px rgba(0,0,0,0.5);"
        "position:relative;overflow:hidden;'>"
        "<div style='position:absolute;top:0;left:0;right:0;height:3px;"
        "background:linear-gradient(90deg,transparent 0%,#f5c542 25%,#5eb8ff 60%,#d97de8 85%,transparent 100%);'></div>"
        "<div style='position:absolute;top:0;right:0;width:300px;height:300px;border-radius:50%;"
        "background:radial-gradient(circle,rgba(94,184,255,0.04) 0%,transparent 70%);"
        "transform:translate(100px,-150px);pointer-events:none;'></div>"
        "<div style='display:flex;align-items:flex-start;gap:22px;margin-bottom:28px;'>"
        "<div style='width:66px;height:66px;border-radius:50%;flex-shrink:0;"
        "background:linear-gradient(135deg,#0d1e30 0%,#151530 100%);"
        "border:2.5px solid " + avatar_border + ";display:flex;align-items:center;justify-content:center;"
        "font-size:26px;color:" + avatar_border + ";"
        "box-shadow:0 0 24px " + avatar_glow + ";'>" + gender_icon + "</div>"
        "<div style='flex:1;'>"
        "<div style='font-size:28px;font-weight:700;color:#f0d080;letter-spacing:0.04em;line-height:1.15;'>" + val(person, "full_name") + "</div>"
        + maiden_block +
        ""
        "</div></div>"
        + section_label("Name Details") +
        "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px;'>"
        + cell("First Name",  val(person, "first_name"))
        + cell("Middle Name", val(person, "middle_name"))
        + cell("Last Name",   val(person, "last_name")) +
        "</div>"
        + section_label("Vitals") +
        "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;'>"
        + cell("Born",   val(person, "born_year"))
        + cell("Died",   val(person, "died"))
        + cell("Age",    val(person, "age"))
        + cell("Gender", gender_display) +
        "</div>"
        + section_label("Ethnicity") +
        "<div style='margin-bottom:8px;'>" + ethnicity_pills + "</div>"
        + notes_block +
        "</div></body></html>"
    )

    height = 510 if val(person, "notes") != "—" else 460
    components.html(html, height=height, scrolling=False)


def render_graph(graph):
    st.subheader("🌳 Family Graph")

    col1, col2 = st.columns([2, 1])
    with col1:
        layout_mode = st.radio("Layout", ["Hierarchical (Tree)", "Force-Directed"], horizontal=True)
    with col2:
        show_edge_labels = st.checkbox("Show relationship labels", value=True)

    use_hierarchical = layout_mode == "Hierarchical (Tree)"

    net = Network(height="720px", width="100%", directed=True,
                  bgcolor="#080c14", font_color="#e8dcc8")

    if use_hierarchical:
        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "UD",
              "sortMethod": "directed",
              "levelSeparation": 130,
              "nodeSpacing": 230,
              "treeSpacing": 290,
              "blockShifting": true,
              "edgeMinimization": true,
              "parentCentralization": true
            }
          },
          "physics": { "enabled": false },
          "edges": {
            "smooth": { "type": "cubicBezier", "forceDirection": "vertical", "roundness": 0.3 },
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } }
          },
          "nodes": {
            "shape": "box",
            "widthConstraint": { "minimum": 150, "maximum": 230 },
            "heightConstraint": { "minimum": 44 },
            "margin": 14, "borderWidth": 2,
            "font": { "size": 14, "face": "Libre Baskerville", "bold": true }
          },
          "interaction": { "hover": true, "zoomView": true, "dragView": true, "tooltipDelay": 80 }
        }
        """)
    else:
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -130,
              "centralGravity": 0.01,
              "springLength": 210,
              "springConstant": 0.08,
              "damping": 0.4,
              "avoidOverlap": 1
            },
            "stabilization": { "iterations": 300, "updateInterval": 25 }
          },
          "edges": {
            "smooth": { "type": "dynamic" },
            "arrows": { "to": { "enabled": true, "scaleFactor": 0.6 } }
          },
          "nodes": {
            "shape": "box",
            "widthConstraint": { "minimum": 150, "maximum": 230 },
            "heightConstraint": { "minimum": 44 },
            "margin": 14, "borderWidth": 2,
            "font": { "size": 14, "face": "Libre Baskerville", "bold": true }
          },
          "interaction": { "hover": true, "zoomView": true, "dragView": true, "tooltipDelay": 80 }
        }
        """)

    MALE_STYLE   = {"background": "#0d2137", "border": "#5eb8ff",
                    "highlight": {"background": "#1a3a6e", "border": "#93d5ff"}}
    FEMALE_STYLE = {"background": "#26062e", "border": "#d97de8",
                    "highlight": {"background": "#3f0f50", "border": "#ebb8f5"}}
    ROOT_STYLE   = {"background": "#2a1a00", "border": "#f5c542",
                    "highlight": {"background": "#4a3000", "border": "#ffe680"}}
    OTHER_STYLE  = {"background": "#0d2620", "border": "#4ecb91",
                    "highlight": {"background": "#1a4035", "border": "#82e8be"}}

    root_id = str((st.session_state.selected_person or {}).get("person_id", ""))

    for n in graph["nodes"]:
        nid     = n["id"]
        label   = n["label"]
        gender  = n.get("gender", "").lower()
        is_root = str(nid) == root_id and root_id != ""

        if is_root:
            color, bwidth, font_color = ROOT_STYLE,   3, "#f5c542"
        elif gender == "male":
            color, bwidth, font_color = MALE_STYLE,   2, "#a8d8ff"
        elif gender == "female":
            color, bwidth, font_color = FEMALE_STYLE, 2, "#e8b8f8"
        else:
            color, bwidth, font_color = OTHER_STYLE,  2, "#8ee8c0"

        born    = n.get("born_year", "")
        tooltip = f"<b style='font-size:14px; font-family:'Libre Baskerville',Georgia,serif'>{label}</b>"
        if born:
            tooltip += f"<br><span style='color:#aaa'>Born: {born}</span>"
        if gender:
            tooltip += f"<br><span style='color:#aaa'>{gender.capitalize()}</span>"

        net.add_node(
            nid, label=label, color=color, borderWidth=bwidth,
            title=tooltip,
            font={"size": 13, "color": font_color, "bold": True, "face": "Libre Baskerville"},
            shape="box",
            shadow={"enabled": True, "color": color["border"], "size": 12, "x": 0, "y": 0}
        )

    EDGE_STYLES = {
        "SPOUSE":    {"color": "#e8a87c", "width": 3, "dashes": False},
        "CHILD_OF":  {"color": "#5eb8ff", "width": 2, "dashes": False},
        "PARENT_OF": {"color": "#d97de8", "width": 2, "dashes": False},
        "SIBLING":   {"color": "#4ecb91", "width": 2, "dashes": [6, 4]},
    }

    for e in graph["edges"]:
        rel   = e["type"].upper()
        style = EDGE_STYLES.get(rel, {"color": "#556070", "width": 1, "dashes": False})

        net.add_edge(
            e["source"], e["target"],
            label=rel if show_edge_labels else "",
            color={"color": style["color"], "highlight": "#ffffff", "opacity": 0.9},
            width=style["width"], dashes=style["dashes"],
            font={"size": 10, "color": style["color"],
                  "strokeWidth": 2, "strokeColor": "#080c14", "align": "middle"},
            arrows={"to": {"enabled": True, "scaleFactor": 0.55}}
        )

    html_path = "/tmp/family_graph.html"
    net.save_graph(html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    custom_css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
      body, html { margin: 0; padding: 0;
        background: radial-gradient(ellipse at 30% 20%, #0d1a2e 0%, #080c14 50%, #0a0a0f 100%);
      }
      #mynetwork {
        border: 1px solid #1e2d45; border-radius: 12px;
        background: radial-gradient(ellipse at 30% 20%, #0d1a2e 0%, #080c14 55%, #0a0a0f 100%) !important;
        box-shadow: 0 0 60px rgba(94,184,255,0.06), inset 0 0 80px rgba(0,0,0,0.4);
      }
      .vis-tooltip {
        background: linear-gradient(135deg, #0d1a2e, #1a0d2e) !important;
        border: 1px solid #5eb8ff !important; border-radius: 8px !important;
        color: #e8dcc8 !important;
        font-family: 'Libre Baskerville', Georgia, serif !important;
        font-size: 13px !important; padding: 10px 14px !important;
        box-shadow: 0 4px 24px rgba(94,184,255,0.2) !important;
      }
    </style>
    """
    html_content = html_content.replace("</head>", custom_css + "</head>")
    components.html(html_content, height=740, scrolling=False)

    st.markdown("""
    <div style='display:flex; gap:24px; flex-wrap:wrap; padding:12px 20px; margin-top:10px;
        background: linear-gradient(135deg, #0d1a2e 0%, #0d0d1a 100%);
        border-radius:10px; border:1px solid #1e2d45; font-size:13px;
        font-family:'Libre Baskerville',Georgia,serif; letter-spacing:0.03em;
        box-shadow: 0 2px 20px rgba(0,0,0,0.4);'>
        <span style='color:#f5c542; text-shadow:0 0 8px rgba(245,197,66,0.5)'>★ Selected</span>
        <span style='color:#a8d8ff; text-shadow:0 0 6px rgba(94,184,255,0.4)'>■ Male</span>
        <span style='color:#e8b8f8; text-shadow:0 0 6px rgba(217,125,232,0.4)'>■ Female</span>
        <span style='color:#e8a87c; text-shadow:0 0 6px rgba(232,168,124,0.4)'>── Spouse</span>
        <span style='color:#5eb8ff; text-shadow:0 0 6px rgba(94,184,255,0.4)'>── Child of</span>
        <span style='color:#d97de8; text-shadow:0 0 6px rgba(217,125,232,0.4)'>── Parent of</span>
        <span style='color:#4ecb91; text-shadow:0 0 6px rgba(78,203,145,0.4)'>╌ Sibling</span>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# BROWSE MODE
# ==================================================

if mode == "Browse Family":

    st.header("Search Family Member")
    search_name = st.text_input("Enter name")

    if st.button("Search") and search_name:
        res = requests.get(f"{BACKEND_URL}/family/search", params={"name": search_name})

        if res.status_code != 200:
            st.error(f"API Error {res.status_code}: {res.text}")
        else:
            results = res.json()
            if not isinstance(results, list):
                st.error("Unexpected API response")
                st.write(results)
            elif not results:
                st.warning("No results found.")
                st.session_state.search_results = []
            else:
                st.session_state.search_results  = results
                st.session_state.selected_person = None
                st.session_state.graph_data      = None
                st.session_state.ai_answer       = None

    # ── Search Results ─────────────────────────────────────────────
    if st.session_state.search_results:
        st.success(f"{len(st.session_state.search_results)} result(s) found")

        for i, person in enumerate(st.session_state.search_results):
            born = f" · b.{person.get('born_year')}" if person.get("born_year") else ""
            gender = f" · {person.get('gender', '').capitalize()}" if person.get("gender") else ""
            label  = f"{person['full_name']}"

            if st.button(label, key=f"person_{i}"):
                st.session_state.selected_person = person
                st.session_state.graph_data      = None
                st.session_state.ai_answer       = None
                st.rerun()

    # ── Selected Person ────────────────────────────────────────────
    if st.session_state.selected_person:

        person = st.session_state.selected_person

        # Detail card
        render_person_card(person)

        # Family tree controls
        depth = st.slider("Generations Depth", 1, 4, 2)

        if st.button("🌳 Load Family Tree"):
            with st.spinner("Loading family tree..."):
                res = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": f"Show me family tree of {person['full_name']} {depth} generations"}
                )
                if res.status_code != 200:
                    st.error(res.text)
                else:
                    data = res.json()
                    st.session_state.graph_data = data.get("graph")
                    st.session_state.ai_answer  = data.get("answer")

        if st.session_state.ai_answer:
            st.markdown("""
            <div style='
                background: linear-gradient(135deg, #0a1628, #0d0d1f);
                border: 1px solid #1e2d45; border-radius: 12px;
                padding: 20px 24px; margin: 16px 0;
                font-family: 'Libre Baskerville', Georgia, serif;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            '>
                <div style='font-size:10px; color:#5eb8ff; text-transform:uppercase;
                    letter-spacing:0.14em; margin-bottom:10px;'>AI Summary</div>
            </div>
            """, unsafe_allow_html=True)
            st.write(st.session_state.ai_answer)

# ==================================================
# ASK AI MODE
# ==================================================

elif mode == "Ask AI":

    st.header("Ask a Question About the Family")
    question = st.text_input("Enter your question")

    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            res = requests.post(f"{BACKEND_URL}/ask", json={"question": question})

            if res.status_code != 200:
                st.error(res.text)
            else:
                data = res.json()
                st.session_state.graph_data = data.get("graph")
                st.session_state.ai_answer  = data.get("answer")

    if st.session_state.ai_answer:
        st.subheader("AI Response")
        st.write(st.session_state.ai_answer)

# ==================================================
# GRAPH RENDER (shared by both modes)
# ==================================================

if st.session_state.graph_data:
    render_graph(st.session_state.graph_data)