import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Hair Age Art", layout="centered")
st.title("🌿 Hair Age Art")
st.write("Generate a unique portrait based on your age and hair type.")

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

# --- Top row: age slider + hair type ---
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



ev_col1, ev_col2, ev_col3 = st.columns([4, 2, 1])

with ev_col1:
    st.markdown("**Major life events**")
    event_label = st.text_input(
        " ", placeholder="e.g. Got married", label_visibility="collapsed"
    )

with ev_col2:
    st.markdown("**I was**", unsafe_allow_html=True)  # title inside the row, next to input
    event_age = st.number_input(
        "", min_value=1, max_value=100, value=20, label_visibility="collapsed"
    )

with ev_col3:
    # inject a tiny gap above the button to nudge it up visually
    st.markdown("**Title**", unsafe_allow_html=True)
    add_clicked = st.button("+ Add", key="add_event")
    
# --- Color picker: selectbox + colored preview ---
# --- Color picker: selectbox + colored preview ---
st.markdown("**Pick the color**")

color_col1, color_col2 = st.columns([3, 1])

with color_col1:
    selected_name = st.selectbox(
        "Color",
        options=list(PASTELS.keys()),
        index=0,
        label_visibility="collapsed",
    )

with color_col2:
    # Help Streamlit push the baseline to the selectbox level
    st.write("")

selected_hex = PASTELS[selected_name]

with color_col2:
    st.markdown(
        f"""
        <div style="
            display: inline-flex;
            justify-content: center;
            align-items: center;
            margin-top: -24px;
            height: 24px;
        ">
            <div style="
                width: 36px;
                height: 36px;
                border-radius: 50%;
                background: {selected_hex};
                border: 1px solid #ccc;
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
# --- Events state ---
if "events" not in st.session_state:
    st.session_state.events = []

if add_clicked and event_label:
    st.session_state.events.append({
        "label": event_label,
        "age": int(event_age),
        "color": selected_hex,
    })

# Show added events with remove button
for idx, ev in enumerate(st.session_state.events):
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(
            f"<span style='color:{ev['color']};font-size:18px;'>●</span> "
            f"<strong>Age {ev['age']}</strong> — {ev['label']}",
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


# --- Generate full artwork ---
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

    core = plt.Circle((cx, cy), core_r, color="#8B5E3C", zorder=10)
    ax.add_patch(core)

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


# --- Generate button ---
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
