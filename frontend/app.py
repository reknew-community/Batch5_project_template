import html
import streamlit as st
import requests
from pyvis.network import Network
import streamlit.components.v1 as components
import re

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Family Knowledge Graph", layout="wide")

# ==================================================
# SESSION STATE INIT
# ==================================================

defaults = {
    "selected_person": None,
    "graph_data": None,
    "search_results": [],
    "ai_answer": None,
    "queried_person_ids": [],
    "question_input": "",
    "prefill_question": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================================================
# GLOBAL CSS
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
    .ai-response-card {
        background: linear-gradient(135deg, #0a1628 0%, #0d0820 100%);
        border: 1px solid #2a3d5c;
        border-left: 4px solid #f5c542;
        border-radius: 12px;
        padding: 22px 28px;
        margin: 16px 0 8px 0;
        font-family: 'Libre Baskerville', Georgia, serif;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4), 0 0 40px rgba(245,197,66,0.04);
        color: #d0c4b0;
        font-size: 15px;
        line-height: 1.8;
    }
     .ai-response-content {
        color: #c8bca8;
        line-height: 1.85;
        font-size: 14.5px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: pre-wrap;
        width: 100%;
    }
    .breadcrumb-bar {
        background: linear-gradient(135deg, #080f1c, #0a0d1a);
        border: 1px solid #1e2d45;
        border-radius: 10px;
        padding: 12px 20px;
        margin: 10px 0 16px 0;
        font-family: 'Libre Baskerville', Georgia, serif;
        font-size: 13px;
        color: #8ab4cc;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
    }
    .stButton > button {
        font-family: 'Libre Baskerville', Georgia, serif !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class='main-title'>🌳 Family Knowledge Graph</div>
<div class='main-subtitle'>Explore · Discover · Connect</div>
""", unsafe_allow_html=True)

mode = st.radio("Choose Mode", ["Browse Family", "Ask AI"], horizontal=True)

# ==================================================
# HELPERS
# ==================================================

def val(person, field):
    v = person.get(field)
    if v is None:
        return "—"
    s = str(v).strip()
    if s.lower() in ("", "none", "nan", "null", "n/a", "0"):
        return "—"
    return s


def extract_relationship_label(answer_text):
    if not answer_text:
        return None
    patterns = [
        r'\b(first cousins? once removed)\b',
        r'\b(second cousins? once removed)\b',
        r'\b(first cousins?)\b',
        r'\b(second cousins?)\b',
        r'\b(third cousins?)\b',
        r'\b(siblings?)\b',
        r'\b(parent and child)\b',
        r'\b(grandparent and grandchild)\b',
        r'\b(great-grandparent and great-grandchild)\b',
        r'\b(aunt(?: or uncle)?)\b',
        r'\b(uncle(?: or aunt)?)\b',
        r'\b(nephew(?: or niece)?)\b',
        r'\b(niece(?: or nephew)?)\b',
        r'\b(husband and wife|spouses?|married)\b',
        r'\b(great-uncle|great-aunt)\b',
        r'\b(not directly related)\b',
    ]
    for pat in patterns:
        m = re.search(pat, answer_text, re.IGNORECASE)
        if m:
            return m.group(0).strip().title()
    return None


def render_breadcrumb(graph):
    if not graph:
        return
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not nodes or not edges:
        return

    node_map = {n["id"]: n for n in nodes}
    chain = [edges[0]["source"]]
    for e in edges:
        chain.append(e["target"])

    rel_map = {(e["source"], e["target"]): e["type"] for e in edges}
    rel_display = {
        "CHILD_OF": "child of",
        "SPOUSE": "spouse of",
        "PARENT_OF": "parent of",
        "SIBLING": "sibling of",
    }

    parts_html = ""
    for i, nid in enumerate(chain):
        node = node_map.get(nid, {})
        name = node.get("label") or str(nid)
        parts_html += f"<span style='color:#e8dcc8;font-weight:600;'>{name}</span>"
        if i < len(chain) - 1:
            next_nid = chain[i + 1]
            rel = rel_map.get((nid, next_nid), "")
            rel_label = rel_display.get(rel.upper(), rel.lower())
            parts_html += "<span style='color:#2a4a6c;margin:0 6px;font-size:16px;'>›</span>"
            parts_html += f"<span style='color:#5eb8ff;font-size:11px;font-style:italic;'>({rel_label})</span>"
            parts_html += "<span style='color:#2a4a6c;margin:0 6px;font-size:16px;'>›</span>"

    


def render_ai_response(answer, graph=None):
    if not answer:
        return
    safe_answer = html.escape(answer)
    rel_label = extract_relationship_label(answer)
    badge_html = ""
    
    st.html(f"""
    <div style='
        background: linear-gradient(135deg, #0a1628 0%, #0d0820 100%);
        border: 1px solid #2a3d5c;
        border-left: 4px solid #f5c542;
        border-radius: 12px;
        padding: 22px 28px;
        margin: 16px 0 8px 0;
        font-family: "Libre Baskerville", Georgia, serif;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    '>
        <div style='font-size:9px;color:#f5c542;text-transform:uppercase;
            letter-spacing:0.22em;font-weight:700;margin-bottom:12px;'>✦ &nbsp;AI Response</div>
        {badge_html}
        <div style='
            color: #c8bca8;
            line-height: 1.85;
            font-size: 14.5px;
            word-wrap: break-word;
            overflow-wrap: break-word;
            white-space: pre-wrap;
            width: 100%;
        '>{safe_answer}</div>
    </div>
    """)

    if graph:
        render_breadcrumb(graph)


def render_example_chips():
    examples = [
        "How is Prathyusha related to Samba Siva?",
        "Who are the children of Kanthamma?",
        "How are Leela and Chandra Shekhar related?",
        "Show ancestors of Anusha",
    ]
    st.markdown("""
    <div style='font-size:11px;color:#4a6a8a;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:8px;font-family:"Libre Baskerville",Georgia,serif;'>
        Try asking
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(len(examples))
    for i, (col, ex) in enumerate(zip(cols, examples)):
        with col:
            if st.button(ex, key=f"chip_{i}", use_container_width=True):
                st.session_state["question_input"] = ex
                st.rerun()


# ==================================================
# PERSON CARD
# ==================================================

def render_person_card(person):
    ethnicities = [
        person.get(f"ethnicity_{i}")
        for i in range(1, 5)
        if person.get(f"ethnicity_{i}") and val(person, f"ethnicity_{i}") != "—"
    ]
    gender        = val(person, "gender").lower()
    gender_icon   = "&#9794;" if gender == "male" else ("&#9792;" if gender == "female" else "&#9900;")
    avatar_border = "#5eb8ff" if gender == "male" else ("#d97de8" if gender == "female" else "#f5c542")
    avatar_glow   = "rgba(94,184,255,0.3)" if gender == "male" else ("rgba(217,125,232,0.3)" if gender == "female" else "rgba(245,197,66,0.3)")

    maiden_block = ""
    if val(person, "maiden_name") != "—":
        maiden_block = (
            "<div style='font-size:14px;color:#a0b8d0;margin-top:5px;"
            "font-style:italic;letter-spacing:0.03em;'>" + val(person, "maiden_name") + "</div>"
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
            "<div style='height:1px;background:linear-gradient(90deg,transparent,#2a3a5c,transparent);"
            "margin:20px 0;'></div>"
            "<div style='margin-bottom:8px;font-size:10px;color:#6a9abf;text-transform:uppercase;"
            "letter-spacing:0.16em;font-weight:600;'>Notes</div>"
            "<div style='font-size:14px;color:#a0b8cc;font-style:italic;line-height:1.8;"
            "background:rgba(94,184,255,0.04);border-radius:10px;padding:14px 18px;"
            "border-left:3px solid #2a4a6c;'>" + val(person, "notes") + "</div>"
        )

    def cell(label, value):
        val_style = ("font-size:18px;color:#3a5a70;font-style:italic;font-weight:400;"
                     if value == "—" else
                     "font-size:18px;color:#e8dcc8;font-weight:600;letter-spacing:0.02em;")
        return (
            "<div style='background:linear-gradient(135deg,rgba(255,255,255,0.04) 0%,"
            "rgba(255,255,255,0.01) 100%);border:1px solid #223050;border-radius:12px;"
            "padding:16px 18px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.05);'>"
            "<div style='font-size:9px;color:#4a7aaa;text-transform:uppercase;"
            "letter-spacing:0.18em;margin-bottom:8px;font-weight:600;'>" + label + "</div>"
            "<div style='" + val_style + "'>" + value + "</div></div>"
        )

    def section_label(text):
        return (
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:12px;'>"
            "<div style='height:1px;width:16px;background:#2a4a6c;'></div>"
            "<div style='font-size:9px;color:#4a7aaa;text-transform:uppercase;"
            "letter-spacing:0.2em;font-weight:700;'>" + text + "</div>"
            "<div style='height:1px;flex:1;background:linear-gradient(90deg,#2a4a6c,transparent);'></div>"
            "</div>"
        )

    gender_display = val(person, "gender").capitalize() if val(person, "gender") != "—" else "—"

    html = (
        "<!DOCTYPE html><html><head>"
        "<link href='https://fonts.googleapis.com/css2?family=Libre+Baskerville:"
        "ital,wght@0,400;0,700;1,400&display=swap' rel='stylesheet'>"
        "<style>* {margin:0;padding:0;box-sizing:border-box;} "
        "body {font-family:'Libre Baskerville',Georgia,serif;background:transparent;padding:6px 2px;}"
        "</style></head><body>"
        "<div style='background:linear-gradient(160deg,#0c1a2e 0%,#0a0e1f 50%,#080c18 100%);"
        "border:1px solid #1e3050;border-radius:18px;padding:30px 34px 28px;"
        "box-shadow:0 0 60px rgba(94,184,255,0.05),0 12px 40px rgba(0,0,0,0.5);"
        "position:relative;overflow:hidden;'>"
        "<div style='position:absolute;top:0;left:0;right:0;height:3px;"
        "background:linear-gradient(90deg,transparent 0%,#f5c542 25%,#5eb8ff 60%,"
        "#d97de8 85%,transparent 100%);'></div>"
        "<div style='display:flex;align-items:flex-start;gap:22px;margin-bottom:28px;'>"
        "<div style='width:66px;height:66px;border-radius:50%;flex-shrink:0;"
        "background:linear-gradient(135deg,#0d1e30 0%,#151530 100%);"
        "border:2.5px solid " + avatar_border + ";"
        "display:flex;align-items:center;justify-content:center;"
        "font-size:26px;color:" + avatar_border + ";"
        "box-shadow:0 0 24px " + avatar_glow + ";'>" + gender_icon + "</div>"
        "<div style='flex:1;'>"
        "<div style='font-size:28px;font-weight:700;color:#f0d080;"
        "letter-spacing:0.04em;line-height:1.15;'>" + val(person, "full_name") + "</div>"
        + maiden_block +
        "</div></div>"
        + section_label("Name Details") +
        "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px;'>"
        + cell("First Name",  val(person, "first_name"))
        + cell("Middle Name", val(person, "middle_name"))
        + cell("Last Name",   val(person, "last_name"))
        + "</div>"
        + section_label("Vitals") +
        "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;'>"
        + cell("Born",   val(person, "born_year"))
        + cell("Died",   val(person, "died"))
        + cell("Age",    val(person, "age"))
        + cell("Gender", gender_display)
        + "</div>"
        + section_label("Ethnicity") +
        "<div style='margin-bottom:8px;'>" + ethnicity_pills + "</div>"
        + notes_block
        + "</div></body></html>"
    )

    height = 510 if val(person, "notes") != "—" else 460
    components.html(html, height=height, scrolling=False)


# ==================================================
# GRAPH RENDER
# ==================================================

def render_graph(graph, queried_ids=None):
    if not graph:
        return
    if queried_ids is None:
        queried_ids = []

    st.subheader("🌳 Family Graph")

    col1, col2 = st.columns([2, 1])
    with col1:
        layout_mode = st.radio("Layout", ["Hierarchical (Tree)", "Force-Directed"], horizontal=True)
    with col2:
        show_edge_labels = st.checkbox("Show relationship labels", value=True)

    use_hierarchical = layout_mode == "Hierarchical (Tree)"

    node_count    = len(graph.get("nodes", []))
    canvas_height = max(420, min(700, 260 + node_count * 60))

    net = Network(height=f"{canvas_height}px", width="100%", directed=True,
                  bgcolor="#080c14", font_color="#e8dcc8")

    if use_hierarchical:
        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "direction": "DU",
              "sortMethod": "directed",
              "levelSeparation": 140,
              "nodeSpacing": 240,
              "treeSpacing": 300,
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
                    "highlight": {"background": "#1a3a6e", "border": "#93d5ff"},
                    "hover": {"background": "#1a3a6e", "border": "#93d5ff"}}
    FEMALE_STYLE = {"background": "#26062e", "border": "#d97de8",
                    "highlight": {"background": "#3f0f50", "border": "#ebb8f5"},
                    "hover":{"background": "#3f0f50", "border": "#ebb8f5"}}
    OTHER_STYLE  = {"background": "#0d2620", "border": "#4ecb91",
                    "highlight": {"background": "#1a4035", "border": "#82e8be"}}

    QUERIED_MALE_STYLE   = {"background": "#0a2a50", "border": "#00c8ff",
                            "highlight": {"background": "#1040a0", "border": "#60e0ff"},
                            "hover": {"background": "#1040a0", "border": "#60e0ff"}}
    QUERIED_FEMALE_STYLE = {"background": "#3a0050", "border": "#ff50ff",
                            "highlight": {"background": "#600080", "border": "#ff90ff"},
                            "highlight": {"background": "#600080", "border": "#ff90ff"}}
    QUERIED_OTHER_STYLE  = {"background": "#2a2000", "border": "#f5c542",
                            "highlight": {"background": "#4a3800", "border": "#ffe680"},
                            "highlight": {"background": "#4a3800", "border": "#ffe680"}}

    queried_ids_str = [str(q) for q in queried_ids]

    for n in graph["nodes"]:
        nid        = n["id"]
        label      = n["label"]
        gender     = n.get("gender", "").lower()
        is_queried = str(nid) in queried_ids_str

        if is_queried:
            color       = (QUERIED_MALE_STYLE if gender == "male"
                           else QUERIED_FEMALE_STYLE if gender == "female"
                           else QUERIED_OTHER_STYLE)
            bwidth      = 4
            font_color  = "#ffffff"
            shadow_size = 18
        else:
            color       = (MALE_STYLE if gender == "male"
                           else FEMALE_STYLE if gender == "female"
                           else OTHER_STYLE)
            bwidth      = 2
            font_color  = ("#a8d8ff" if gender == "male"
                           else "#e8b8f8" if gender == "female"
                           else "#8ee8c0")
            shadow_size = 10

        born    = n.get("born_year", "")
        gender_display = gender.capitalize() if gender else ""
        tooltip_parts = [label]
        if born:
            tooltip_parts.append(f"Born: {born}")
        if gender_display:
            tooltip_parts.append(gender_display)
        if is_queried:
            tooltip_parts.append("★ Queried Person")

        tooltip = "\n".join(tooltip_parts)

        net.add_node(
            nid, label=label, color=color, borderWidth=bwidth,
            title=tooltip,
            font={"size": 13, "color": font_color, "bold": True, "face": "Libre Baskerville"},
            shape="box",
            shadow={"enabled": True, "color": color["border"], "size": shadow_size, "x": 0, "y": 0}
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
                  "strokeWidth": 2, "strokeColor": "#080c14", "align": "horizontal"},
            arrows={"to": {"enabled": True, "scaleFactor": 0.55}}
        )

    html_path = "/tmp/family_graph.html"
    net.save_graph(html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    custom_css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');
      body, html { margin:0; padding:0;
        background: radial-gradient(ellipse at 30% 20%, #0d1a2e 0%, #080c14 50%, #0a0a0f 100%);
      }
      #mynetwork {
        border: 1px solid #1e2d45; border-radius: 12px; position: relative;
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
      #fit-btn {
        position: absolute; top: 12px; right: 12px; z-index: 9999;
        background: linear-gradient(135deg, #0a1628, #0d0d1f);
        border: 1px solid #2a3d5c; border-radius: 8px;
        color: #7ab0cc; font-size: 12px; padding: 8px 16px;
        cursor: pointer;
        font-family: 'Libre Baskerville', Georgia, serif;
        letter-spacing: 0.06em;
        box-shadow: 0 2px 16px rgba(0,0,0,0.5);
        transition: all 0.2s;
      }
      #fit-btn:hover { border-color: #f5c542; color: #f5c542; }
    </style>
    """

    fit_button_js = """
<script>
// Wait for vis.js network to be initialized then expose it globally
var fitCheckInterval = setInterval(function() {
    // pyvis stores the network in a variable called 'network'
    // We need to wait until it's defined on the window
    if (typeof network !== 'undefined') {
        clearInterval(fitCheckInterval);
        window._visNetwork = network;
        
        // Auto fit on load
        network.fit({ animation: { duration: 800, easingFunction: 'easeInOutQuad' } });
    }
}, 100);

function fitGraph() {
    if (window._visNetwork) {
        window._visNetwork.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
    }
}
</script>
<button onclick="fitGraph()" style="
    position: absolute;
    top: 14px;
    right: 14px;
    z-index: 9999;
    background: linear-gradient(135deg, #0a1628, #0d0d1f);
    border: 1px solid #2a3d5c;
    border-radius: 8px;
    color: #7ab0cc;
    font-size: 12px;
    padding: 8px 16px;
    cursor: pointer;
    font-family: 'Libre Baskerville', Georgia, serif;
    letter-spacing: 0.06em;
    box-shadow: 0 2px 16px rgba(0,0,0,0.5);
    transition: all 0.2s;
" onmouseover="this.style.borderColor='#f5c542';this.style.color='#f5c542';"
  onmouseout="this.style.borderColor='#2a3d5c';this.style.color='#7ab0cc';">
    ⊡ Fit View
</button>
"""

    html_content = html_content.replace("</head>", custom_css + "</head>")
    html_content = html_content.replace("</body>", fit_button_js + "</body>")

    components.html(html_content, height=canvas_height + 20, scrolling=False)

    st.markdown("""
    <div style='display:flex;gap:24px;flex-wrap:wrap;padding:12px 20px;margin-top:10px;
        background:linear-gradient(135deg,#0d1a2e 0%,#0d0d1a 100%);
        border-radius:10px;border:1px solid #1e2d45;font-size:13px;
        font-family:"Libre Baskerville",Georgia,serif;letter-spacing:0.03em;
        box-shadow:0 2px 20px rgba(0,0,0,0.4);'>
        <span style='color:#00c8ff;text-shadow:0 0 8px rgba(0,200,255,0.6)'>★ Queried</span>
        <span style='color:#a8d8ff;text-shadow:0 0 6px rgba(94,184,255,0.4)'>■ Male</span>
        <span style='color:#e8b8f8;text-shadow:0 0 6px rgba(217,125,232,0.4)'>■ Female</span>
        <span style='color:#e8a87c;text-shadow:0 0 6px rgba(232,168,124,0.4)'>── Spouse</span>
        <span style='color:#5eb8ff;text-shadow:0 0 6px rgba(94,184,255,0.4)'>── Child of</span>
        <span style='color:#d97de8;text-shadow:0 0 6px rgba(217,125,232,0.4)'>── Parent of</span>
        <span style='color:#4ecb91;text-shadow:0 0 6px rgba(78,203,145,0.4)'>╌ Sibling</span>
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# BROWSE MODE
# ==================================================

if mode == "Browse Family":

    st.header("Search Family Member")
    search_name = st.text_input("Enter name", key="browse_search")

    if st.button("Search", key="browse_search_btn"):
        if not search_name.strip():
            st.warning("Please enter a name to search.")
        else:
            with st.spinner("Searching..."):
                try:
                    res = requests.get(
                        f"{BACKEND_URL}/family/search",
                        params={"name": search_name},
                        timeout=15
                    )
                    if res.status_code != 200:
                        st.error(f"API Error {res.status_code}: {res.text}")
                    else:
                        results = res.json()
                        if not isinstance(results, list):
                            st.error("Unexpected API response")
                        elif not results:
                            st.warning("No results found.")
                            st.session_state.search_results = []
                        else:
                            st.session_state.search_results  = results
                            st.session_state.selected_person = None
                            st.session_state.graph_data      = None
                            st.session_state.ai_answer       = None
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend at " + BACKEND_URL + ". Is it running?")
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.search_results:
        st.success(f"{len(st.session_state.search_results)} result(s) found")
        for i, person in enumerate(st.session_state.search_results):
            if st.button(person["full_name"], key=f"person_{i}"):
                st.session_state.selected_person    = person
                st.session_state.graph_data         = None
                st.session_state.ai_answer          = None
                st.session_state.queried_person_ids = [person.get("person_id", "")]
                st.rerun()

    if st.session_state.selected_person:
        person = st.session_state.selected_person
        render_person_card(person)

        depth = st.slider("Generations Depth", 1, 4, 2)

        if st.button("🌳 Load Family Tree", key="load_tree_btn"):
            with st.spinner("Loading family tree..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": f"Show me family tree of {person['full_name']} {depth} generations"},
                        timeout=30
                    )
                    if res.status_code != 200:
                        st.error(res.text)
                    else:
                        data = res.json()
                        st.session_state.graph_data         = data.get("graph")
                        st.session_state.ai_answer          = data.get("answer")
                        st.session_state.queried_person_ids = [person.get("person_id", "")]
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend at " + BACKEND_URL + ". Is it running?")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.ai_answer:
            render_ai_response(st.session_state.ai_answer, st.session_state.graph_data)

# ==================================================
# ASK AI MODE
# ==================================================

elif mode == "Ask AI":

    st.header("Ask a Question About the Family")

    render_example_chips()

    question = st.text_input(
        "Enter your question",
        key="question_input",
        placeholder="e.g. How is Prathyusha related to Samba Siva?"
    )

    if st.button("Ask", key="ask_btn"):
        current_question = st.session_state.get("question_input", "").strip()
        if not current_question:
            st.warning("Please enter a question.")
        else:
            with st.spinner("✦ Consulting the family records..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/ask",
                        json={"question": current_question},
                        timeout=30
                    )
                    if res.status_code != 200:
                        st.error(f"API Error {res.status_code}: {res.text}")
                    else:
                        data = res.json()
                        st.session_state.graph_data = data.get("graph")
                        st.session_state.ai_answer  = data.get("answer")

                        graph = data.get("graph")
                        if graph and graph.get("nodes") and len(graph["nodes"]) >= 2:
                            nodes = graph["nodes"]
                            st.session_state.queried_person_ids = [
                                nodes[0]["id"], nodes[-1]["id"]
                            ]
                        else:
                            st.session_state.queried_person_ids = []

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend at " + BACKEND_URL + ". Is it running?")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. The backend took too long to respond.")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    if st.session_state.ai_answer:
        render_ai_response(st.session_state.ai_answer, st.session_state.graph_data)

# ==================================================
# GRAPH RENDER — shared by both modes
# ==================================================

if st.session_state.graph_data:
    render_graph(
        st.session_state.graph_data,
        queried_ids=st.session_state.get("queried_person_ids", [])
    )
