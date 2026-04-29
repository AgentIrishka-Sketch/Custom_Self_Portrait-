import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Hair Age Art", layout="centered")
st.title("🌿 Hair Age Art")
st.write("Generate a unique portrait based on your age and hair type.")

PASTELS = [
    "#F4A7B9", "#F7C6A3", "#FAE29A", "#B8E4A8", "#A8D8EA",
    "#C3B1E1", "#F2B5D4", "#A8E6CF", "#FFD3B6", "#D4A5A5",
    "#B5D5C5", "#E8C5A0", "#C5B4E3", "#A0C4D8", "#F0C9C0",
    "#D6EAF8", "#D5F5E3", "#FDEBD0", "#F9EBEA", "#E8DAEF",
]

# --- Top row: age slider on left, hair type on right ---
col_age, col_hair = st.columns(2)

with col_age:
    st.markdown("**Your age**")
    age = st.slider("", min_value=1, max_value=100, value=35, label_visibility="collapsed")

with col_hair:
    st.markdown("**Hair type**")
    hair_type = st.radio("", ["Straight", "Wavy", "Curly"],
                         horizontal=True, label_visibility="collapsed")
    hair_type = hair_type.lower()

st.markdown("---")

# --- Life events section ---
st.markdown("**Major life events**")

# Event name + age + add button in one row
ev_col1, ev_col2, ev_col3 = st.columns([4, 2, 1])
with ev_col1:
    event_label = st.text_input("", placeholder="e.g. Got married", label_visibility="collapsed")
with ev_col2:
    event_age = st.number_input("", min_value=1, max_value=100, value=20,
                                placeholder="Age", label_visibility="collapsed")
with ev_col3:
    add_clicked = st.button("+ Add")

# --- Pastel color swatches ---
st.markdown("**Color**")

if "selected_color" not in st.session_state:
    st.session_state.selected_color = PASTELS[0]

# Draw all swatches as clickable colored buttons using HTML + st.button trick
swatch_cols = st.columns(len(PASTELS))
for i, color in enumerate(PASTELS):
    with swatch_cols[i]:
        border = "3px solid #333" if st.session_state.selected_color == color else "3px solid transparent"
        st.markdown(
            f"<div style='width:22px;height:22px;border-radius:50%;background:{color};"
            f"border:{border};cursor:pointer;margin:auto;'></div>",
            unsafe_allow_html=True,
        )
        if st.button(" ", key=f"sw_{i}", help=color):
            st.session_state.selected_color = color
            st.rerun()

# --- Events list in session state ---
if "events" not in st.session_state:
    st.session_state.events = []

if add_clicked and event_label:
    st.session_state.events.append({
        "label": event_label,
        "age": int(event_age),
        "color": st.session_state.selected_color,
    })

# Show added events
for idx, ev in enumerate(st.session_state.events):
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(
            f"<span style='color:{ev['color']};font-size:16px;'>●</span> "
            f"<strong>Age {ev['age']}</strong> — {ev['label']}",
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("×", key=f"del_{idx}"):
            st.session_state.events.pop(idx)
            st.rerun()

st.markdown("---")


# --- Helper: hex to RGB 0-1 float tuple ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


# --- Draw a single ring ---
def draw_ring(ax, cx, cy, r, hair_type, ring_index, color, alpha, linewidth):
    steps = 800
    angles = np.linspace(0, 2 * np.pi, steps)
    seed = ring_index * 17

    if hair_type == "straight":
        x = cx + np.cos(angles) * r
        y = cy + np.sin(angles) * r

    elif hair_type == "wavy":
        freq = 6
        amp = r * 0.045
        phase = (seed % 628) / 100
        rr = r + np.sin(angles * freq + phase) * amp
        x = cx + np.cos(angles) * rr
        y = cy + np.sin(angles) * rr

    elif hair_type == "curly":
        freq = 18 + (ring_index % 6)
        amp = r * 0.045
        phase = (seed % 628) / 100
        rr = r + np.abs(np.sin(angles * freq + phase)) * amp
        x = cx + np.cos(angles) * rr
        y = cy + np.sin(angles) * rr

    ax.plot(x, y, color=color, alpha=alpha, linewidth=linewidth)


# --- Generate the full artwork ---
def generate_art(age, hair_type, events):
    fig, ax = plt.subplots(figsize=(7, 7), facecolor="#faf8f3")
    ax.set_facecolor("#faf8f3")
    ax.set_aspect("equal")
    ax.axis("off")

    cx, cy = 0, 0
    core_r = 0.12
    max_r = 2.7
    step = (max_r - core_r) / max(age, 1)

    event_map = {ev["age"]: ev for ev in events}

    for i in range(1, age + 1):
        r = core_r + i * step
        t = i / age
        lw = 1.4 if i % 5 == 0 else 0.7

        if i in event_map:
            color = hex_to_rgb(event_map[i]["color"])
            alpha = 0.85
        else:
            color = (0.24 + t * 0.39, 0.12 + t * 0.22, 0.02 + t * 0.10)
            alpha = 0.12 + t * 0.55

        draw_ring(ax, cx, cy, r, hair_type, i, color, alpha, lw)

    # Central dot
    core = plt.Circle((cx, cy), core_r, color="#8B5E3C", zorder=10)
    ax.add_patch(core)

    # Legend
    if events:
        for ev in events:
            ax.plot([], [], color=hex_to_rgb(ev["color"]),
                    linewidth=2, label=f"Age {ev['age']}: {ev['label']}")
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.08),
                  frameon=False, fontsize=8, ncol=2)

    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    plt.tight_layout()
    return fig


# --- Generate button + output ---
if st.button("Generate portrait"):
    fig = generate_art(int(age), hair_type, st.session_state.events)
    st.pyplot(fig)

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        label="⬇️ Download portrait",
        data=buf,
        file_name=f"portrait_age{int(age)}_{hair_type}.png",
        mime="image/png",
    )
