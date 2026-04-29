import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

# --- Top row: hair type ---
hair_type = st.selectbox("Hair type", ["straight", "medium", "curly"])

# --- Section row: Major life events + Your age ---
st.markdown("---")
col_events, col_age = st.columns(2)

with col_age:
    st.markdown("**Your age**")
    age = st.number_input("", min_value=1, max_value=100, value=35, label_visibility="collapsed")

with col_events:
    st.markdown("**Major life events**")
    event_label = st.text_input("Event name", placeholder="e.g. Got married")

    st.markdown("**Color**")
    color_cols = st.columns(10)
    if "selected_color" not in st.session_state:
        st.session_state.selected_color = PASTELS[0]

    for i, color in enumerate(PASTELS):
        with color_cols[i % 10]:
            if st.button(
                " ",
                key=f"color_{i}",
                help=color,
                type="secondary",
            ):
                st.session_state.selected_color = color

    st.markdown(
        f"<div style='width:24px;height:24px;border-radius:50%;background:{st.session_state.selected_color};"
        f"border:2px solid #888;margin-bottom:8px;'></div>",
        unsafe_allow_html=True,
    )

    if "events" not in st.session_state:
        st.session_state.events = []

    if st.button("➕ Add event"):
        if event_label:
            st.session_state.events.append({
                "label": event_label,
                "age": int(age),
                "color": st.session_state.selected_color,
            })

    if st.session_state.events:
        st.write("**Your events:**")
        for idx, ev in enumerate(st.session_state.events):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f"<span style='color:{ev['color']}'>●</span> <strong>Age {ev['age']}</strong> — {ev['label']}",
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("✕", key=f"del_{idx}"):
                    st.session_state.events.pop(idx)
                    st.rerun()


# --- Drawing functions ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))


def draw_ring(ax, cx, cy, r, hair_type, ring_index, color, alpha, linewidth):
    steps = 800
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
            ev = event_map[i]
            color = hex_to_rgb(ev["color"])
            alpha = 0.85
        else:
            color = (
                0.24 + t * 0.39,
                0.12 + t * 0.22,
                0.02 + t * 0.10,
            )
            alpha = 0.12 + t * 0.55

        draw_ring(ax, cx, cy, r, hair_type, i, color, alpha, lw)

    # Core dot
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


fig = generate_art(int(age), hair_type, st.session_state.events)
st.pyplot(fig)

# Download button
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
st.download_button(
    label="⬇️ Download portrait",
    data=buf,
    file_name=f"portrait_age{int(age)}_{hair_type}.png",
    mime="image/png",
)
