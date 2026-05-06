import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="RINGS — Year by Year", layout="centered")
st.title("RINGS — Year by Year")
st.write("Hi there! My name is Irina, and I'm a creative digital artist. Here's a fun project you can try — and see a tangible outcome of my art touched by your own data. Feel free to download your final personalised infographic. We can also print it for you on beautiful textured paper and send it straight to you. Enjoy!")
st.write("The concept: Each line represents a year of your life, inspired by the quiet rings inside a tree. This is your foundation. The rest reveals itself.")

# Pastel colors with friendly names
PASTELS = {
    "Rose":        "#F4A7B9",
    "Peach":       "#F7C6A3",
    "Lemon":       "#FAE29A",
    "Sage":        "#B8E4A8",
    "Sky":         "#A8D8EA",
    "Lavender":    "#C3B1E1",
    "Pink":        "#F2B5D4",
    "Mint":        "#A8E6CF",
    "Apricot":     "#FFD3B6",
    "Dusty Rose":  "#D4A5A5",
    "Seafoam":     "#B5D5C5",
    "Sand":        "#E8C5A0",
    "Lilac":       "#C5B4E3",
    "Powder Blue": "#A0C4D8",
    "Blush":       "#F0C9C0",
    "Ice Blue":    "#D6EAF8",
    "Pale Green":  "#D5F5E3",
    "Cream":       "#FDEBD0",
    "Ballet":      "#F9EBEA",
    "Wisteria":    "#E8DAEF",
}


# --- Detect number of children from event label ---
def detect_children(label):
    label_lower = label.lower()
    if "quadruplets" in label_lower:
        return 4
    if "triplets" in label_lower:
        return 3
    if "twins" in label_lower:
        return 2
    if any(k in label_lower for k in ["baby", "child", "deliver kid", "born", "daughter", "son", "kid"]):
        return 1
    return 0


# --- Top row: age slider and  personality type ---

col_age, = st.columns(1)
with col_age:
    st.markdown("**Your age**")
    age = st.slider("", min_value=1, max_value=100, value=20, label_visibility="collapsed")


col_personality, = st.columns(1)
with col_personality:
    st.markdown("**What is your personality type?**")
    personality_type = st.radio("", ["Phlegmatic", "Melancholic", "Choleric", "Sanguine"],
                         index=0,
                         horizontal=True, label_visibility="collapsed")
    personality_type = personality_type.lower()

st.markdown("---")

# --- Life events section ---
ev_col1, ev_col2 = st.columns([4, 2])

with ev_col1:
    st.markdown("**Major life events**")
    event_label = st.text_input(
        " ", placeholder="e.g. Got married, had a baby…", label_visibility="collapsed"
    )

with ev_col2:
    st.markdown("**I was**", unsafe_allow_html=True)
    event_age = st.number_input(
        "", min_value=1, max_value=100, value=20, label_visibility="collapsed"
    )

# --- Color picker ---
color_col1, color_col2, ev_col3 = st.columns([4, 1, 1])

with color_col1:
    st.markdown("**Pick the color of each major event**")
    selected_name = st.selectbox(
        "Color",
        options=list(PASTELS.keys()),
        index=0,
        label_visibility="collapsed",
    )

selected_hex = PASTELS[selected_name]

with color_col2:
    st.markdown("&nbsp;", unsafe_allow_html=True)  # matches the label height above
    st.markdown(
        f"""
        <div style="margin-top: 6px;">
            <div style="
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: {selected_hex};
                border: 1px solid #ccc;
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with ev_col3:
    st.markdown("&nbsp;", unsafe_allow_html=True)  # matches the label height above
    add_clicked = st.button("+ Add", key="add_event")
    
# --- Events state ---
if "events" not in st.session_state:
    st.session_state.events = []

if add_clicked and event_label:
    st.session_state.events.append({
        "label":    event_label,
        "age":      int(event_age),
        "color":    selected_hex,
        "children": detect_children(event_label),
    })

# Show added events with remove button
for idx, ev in enumerate(st.session_state.events):
    c1, c2 = st.columns([6, 1])
    with c1:
        child_tag = ""
        if ev.get("children", 0) > 0:
            names = {1: "👶 child", 2: "👶👶 twins", 3: "👶👶👶 triplets", 4: "👶👶👶👶 quadruplets"}
            child_tag = f" · <em>{names.get(ev['children'], '')}</em>"
        st.markdown(
            f"<span style='color:{ev['color']};font-size:18px;'>●</span> "
            f"<strong>Age {ev['age']}</strong> — {ev['label']}{child_tag}",
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("×", key=f"del_{idx}"):
            st.session_state.events.pop(idx)
            st.rerun()

st.markdown("---")


# --- Helper: hex to RGB 0-1 float ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


# --- Draw a single ring ---
def draw_ring(ax, cx, cy, r, personality_type, ring_index, color, alpha, linewidth):
    steps = 800
    angles = np.linspace(0, 2 * np.pi, steps)
    seed = ring_index * 17

    if personality_type == "phlegmatic":
        x = cx + np.cos(angles) * r
        y = cy + np.sin(angles) * r

    elif personality_type == "melancholic":
        freq = 6
        amp = r * 0.045
        phase = (seed % 628) / 100
        rr = r + np.sin(angles * freq + phase) * amp
        x = cx + np.cos(angles) * rr
        y = cy + np.sin(angles) * rr

    elif personality_type == "choleric":
        freq = 18 + (ring_index % 6)
        amp = r * 0.045
        phase = (seed % 628) / 100
        rr = r + np.abs(np.sin(angles * freq + phase)) * amp
        x = cx + np.cos(angles) * rr
        y = cy + np.sin(angles) * rr

    elif personality_type == "sanguine":
        np.random.seed(seed)
        freq = 12 + np.random.randint(0, 4)
        amp = r * 0.04
        phase = np.random.rand()
        rr = r + np.sin(angles * freq + phase) * amp
        noise = np.random.uniform(-0.01, 0.01, len(angles))
        rr = rr * (1 + noise)
        x = cx + np.cos(angles) * rr
        y = cy + np.sin(angles) * rr

    ax.plot(x, y, color=color, alpha=alpha, linewidth=linewidth)


# --- Draw a child portrait ---
def draw_child_portrait(ax, cx, cy, child_age, color_hex, personality_type):
    core_r = 0.08
    # portrait radius scales gently with child's age
    max_r = 0.35 + (child_age / 100) * 0.55
    step = (max_r - core_r) / max(child_age, 1)

    for i in range(1, child_age + 1):
        r = core_r + i * step
        t = i / child_age
        # outermost ring gets the event color
        if i == child_age:
            color = hex_to_rgb(color_hex)
            alpha = 0.85
            lw = 1.5
        else:
            color = (0.24 + t * 0.39, 0.12 + t * 0.22, 0.02 + t * 0.10)
            alpha = 0.12 + t * 0.55
            lw = 0.5
        draw_ring(ax, cx, cy, r, personality_type, i, color, alpha, lw)

    ax.add_patch(plt.Circle((cx, cy), core_r * 0.6, color="#D3B392", zorder=10))
    return max_r


# --- Generate full artwork ---
def generate_art(age, personality_type, events):
    # collect all children from events
    all_children = []
    for ev in events:
        n = ev.get("children", 0)
        child_age = max(1, age - ev["age"])
        for _ in range(n):
            all_children.append({
                "age":   child_age,
                "color": ev["color"],
            })

    has_children = len(all_children) > 0

    # widen canvas if we have child portraits
    fig_w = 12 if has_children else 7
    fig, ax = plt.subplots(figsize=(fig_w, 7), facecolor="#faf8f3")
    ax.set_facecolor("#faf8f3")
    ax.set_aspect("equal")
    ax.axis("off")

    # parent portrait — shift left when children present
    cx, cy = (-0.8 if has_children else 0), 0
    core_r = 0.12
    max_r = 2.7
    step = (max_r - core_r) / max(age, 1)
    event_map = {ev["age"]: ev for ev in events}

    for i in range(1, age + 1):
        r = core_r + i * step
        t = i / age
        lw = 0.7

        if i in event_map:
            color = hex_to_rgb(event_map[i]["color"])
            alpha = 0.85
            lw = 1.5
        else:
            color = (0.24 + t * 0.39, 0.12 + t * 0.22, 0.02 + t * 0.10)
            alpha = 0.12 + t * 0.55

        draw_ring(ax, cx, cy, r, personality_type, i, color, alpha, lw)

    ax.add_patch(plt.Circle((cx, cy), core_r * 0.6, color="#D3B392", zorder=10))

    # --- Draw child portraits ---
    if has_children:
        n = len(all_children)
        cx_child = 2.4

        # spread children vertically, centred on 0
        total_span = min(5.5, n * 1.6)
        positions = np.linspace(-total_span / 2, total_span / 2, n) if n > 1 else [0.0]

        for i, child in enumerate(all_children):
            cy_child = positions[i]

            # dashed connector from parent core edge toward child
            ax.plot(
                [cx + 0.4, cx_child - 0.8],
                [cy, cy_child],
                color="#C0A882", linewidth=0.5,
                linestyle="--", alpha=0.4, zorder=0,
            )

            child_max_r = draw_child_portrait(
                ax, cx_child, cy_child,
                child["age"], child["color"], personality_type,
            )

            # small age label under each child portrait
            ax.text(
                cx_child, cy_child - child_max_r - 0.15,
                f"{child['age']}y",
                ha="center", va="top",
                fontsize=6, color="#8B7355", alpha=0.7,
            )

    # --- Legend ---
    if events:
        for ev in events:
            ax.plot([], [], color=hex_to_rgb(ev["color"]),
                    linewidth=2, label=f"Age {ev['age']}: {ev['label']}")
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.08),
                  frameon=False, fontsize=8, ncol=2)

    x_min = -4.5 if has_children else -3.2
    x_max = 4.8 if has_children else 3.2
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-3.2, 3.2)
    plt.tight_layout()
    return fig


# --- Live render ---
fig = generate_art(int(age), personality_type, st.session_state.events)
st.pyplot(fig)

# --- Download button ---
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
st.download_button(
    label="⬇️ Download portrait",
    data=buf,
    file_name=f"portrait_age{int(age)}_{personality_type}.png",
    mime="image/png",
)
