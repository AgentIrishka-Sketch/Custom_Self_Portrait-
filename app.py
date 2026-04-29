import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Hair Age Art", layout="centered")
st.title("🌿 Hair Age Art")
st.write("Generate a unique portrait based on your age and hair type.")

age = st.slider("Age", min_value=1, max_value=100, value=35)
hair_type = st.selectbox("Hair type", ["straight", "medium", "curly"])

# --- Life events ---
st.subheader("✨ Major life events")
st.write("Add events that happened at a specific age — each will be highlighted on its ring.")

if "events" not in st.session_state:
    st.session_state.events = []

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    event_label = st.text_input("Event name", placeholder="e.g. Got married")
with col2:
    event_age = st.number_input("At age", min_value=1, max_value=age, value=min(20, age))
with col3:
    event_color = st.color_picker("Color", "#E63946")

if st.button("➕ Add event"):
    if event_label:
        st.session_state.events.append({
            "label": event_label,
            "age": int(event_age),
            "color": event_color
        })

# Show added events and allow removal
if st.session_state.events:
    st.write("**Your events:**")
    for idx, ev in enumerate(st.session_state.events):
        ecol1, ecol2 = st.columns([5, 1])
        with ecol1:
            st.markdown(
                f"<span style='color:{ev['color']}'>●</span> **Age {ev['age']}** — {ev['label']}",
                unsafe_allow_html=True
            )
        with ecol2:
            if st.button("✕", key=f"del_{idx}"):
                st.session_state.events.pop(idx)
                st.rerun()


def draw_ring(ax, cx, cy, r, hair_type, ring_index, color, alpha, linewidth):
    steps = 360
    angles = np.linspace(0, 2 * np.pi, steps)
    seed = ring_index * 17

    if hair_type == "straight":
        x = cx + np.cos(angles) * r
        y = cy + np.sin(angles) * r

    elif hair_type == "medium":
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


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


def generate_art(age, hair_type, events):
    fig, ax = plt.subplots(figsize=(7, 7), facecolor="#faf8f3")
    ax.set_facecolor("#faf8f3")
    ax.set_aspect("equal")
    ax.axis("off")

    cx, cy = 0, 0
    core_r = 0.12
    max_r = 2.7
    step = (max_r - core_r) / max(age, 1)

    # Build a lookup: ring index -> event
    event_map = {ev["age"]: ev for ev in events}

    for i in range(1, age + 1):
        r = core_r + i * step
        t = i / age

        if i in event_map:
            ev = event_map[i]
            color = hex_to_rgb(ev["color"])
            alpha = 0.95
            linewidth = 2.8
            # Draw a subtle glow behind it
            draw_ring(ax, cx, cy, r, hair_type, i, color, 0.18, 6.0)
        else:
            color = (
                0.24 + t * 0.39,
                0.12 + t * 0.22,
                0.02 + t * 0.10,
            )
            alpha = 0.12 + t * 0.55
            linewidth = 1.4 if i % 5 == 0 else 0.7

        draw_ring(ax, cx, cy, r, hair_type, i, color, alpha, linewidth)

    # Legend for events
    if events:
        for ev in events:
            ax.plot([], [], color=hex_to_rgb(ev["color"]),
                    linewidth=2.5, label=f"Age {ev['age']}: {ev['label']}")
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.08),
                  frameon=False, fontsize=8, ncol=2)

    core = plt.Circle((cx, cy), core_r, color="#8B5E3C", zorder=10)
    ax.add_patch(core)

    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    plt.tight_layout()
    return fig


fig = generate_art(age, hair_type, st.session_state.events)
st.pyplot(fig)

# Download button
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
st.download_button(
    label="⬇️ Download portrait",
    data=buf,
    file_name=f"portrait_age{age}_{hair_type}.png",
    mime="image/png"
)
