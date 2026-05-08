import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

# -------------------------------------------------------------------
# Page setup
# -------------------------------------------------------------------

st.set_page_config(
    page_title="RINGS — Year by Year",
    layout="centered"
)

st.title("RINGS — Year by Year")

st.write(
    "Hi there! My name is Irina. "
    "Here's a fun project you can try — "
    "a personal artwork generated from your life story."
)

# -------------------------------------------------------------------
# Colors
# -------------------------------------------------------------------

PASTELS = {
    "Rose": "#F4A7B9",
    "Peach": "#F7C6A3",
    "Lemon": "#FAE29A",
    "Sage": "#B8E4A8",
    "Sky": "#A8D8EA",
    "Lavender": "#C3B1E1",
    "Pink": "#F2B5D4",
    "Mint": "#A8E6CF",
    "Apricot": "#FFD3B6",
    "Dusty Rose": "#D4A5A5",
    "Seafoam": "#B5D5C5",
    "Sand": "#E8C5A0",
    "Lilac": "#C5B4E3",
    "Powder Blue": "#A0C4D8",
    "Blush": "#F0C9C0",
    "Ice Blue": "#D6EAF8",
    "Pale Green": "#D5F5E3",
    "Cream": "#FDEBD0",
    "Ballet": "#F9EBEA",
    "Wisteria": "#E8DAEF",
}

PERSONALITY_COLORS = {
    "phlegmatic": "#B8D6BE",
    "melancholic": "#A7C4EB",
    "sanguine": "#FAE0AA",
    "choleric": "#F4A896",
}

# -------------------------------------------------------------------
# Animation configs
# -------------------------------------------------------------------

ANIM_CONFIG = {
    "phlegmatic": {
        "steps": 12,
        "sleep": 0.06,
        "easing": "ease_out",
    },
    "melancholic": {
        "steps": 16,
        "sleep": 0.05,
        "easing": "ease_in",
    },
    "sanguine": {
        "steps": 8,
        "sleep": 0.03,
        "easing": "bounce",
    },
    "choleric": {
        "steps": 6,
        "sleep": 0.02,
        "easing": "linear",
    },
}

# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

defaults = {
    "events": [],
    "depth": 0.0,
    "is_3d": False,
    "animating": False,
}

for k, v in defaults.items():

    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------------------------
# Inputs
# -------------------------------------------------------------------

st.markdown("### Your age")

age = st.slider(
    "",
    1,
    100,
    20,
    label_visibility="collapsed"
)

st.markdown("### Personality type")

personality_type = st.radio(
    "",
    ["Phlegmatic", "Melancholic", "Sanguine", "Choleric"],
    horizontal=True,
    label_visibility="collapsed"
).lower()

st.markdown("---")

col1, col2 = st.columns([4, 2])

with col1:

    event_label = st.text_input(
        "",
        placeholder="e.g. Got married, moved abroad...",
        label_visibility="collapsed"
    )

with col2:

    event_age = st.number_input(
        "",
        min_value=1,
        max_value=100,
        value=20,
        label_visibility="collapsed"
    )

c1, c2, c3 = st.columns([4, 1, 1])

with c1:

    selected_name = st.selectbox(
        "",
        list(PASTELS.keys()),
        label_visibility="collapsed"
    )

selected_hex = PASTELS[selected_name]

with c2:

    st.markdown(
        f"""
        <div style="
            width:32px;
            height:32px;
            border-radius:50%;
            background:{selected_hex};
            border:1px solid #ccc;
            margin-top:8px;">
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    add_clicked = st.button("+ Add")

# -------------------------------------------------------------------
# Event add
# -------------------------------------------------------------------

if add_clicked and event_label:

    st.session_state.events.append({
        "label": event_label,
        "age": int(event_age),
        "color": selected_hex,
    })

# -------------------------------------------------------------------
# Show events
# -------------------------------------------------------------------

for idx, ev in enumerate(st.session_state.events):

    cc1, cc2 = st.columns([6, 1])

    with cc1:

        st.markdown(
            f"<span style='color:{ev['color']};font-size:18px;'>●</span> "
            f"<strong>Age {ev['age']}</strong> — {ev['label']}",
            unsafe_allow_html=True
        )

    with cc2:

        if st.button("×", key=f"del_{idx}"):

            st.session_state.events.pop(idx)

            st.rerun()

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16) / 255
        for i in (0, 2, 4)
    )

def get_ring_color(pt, t):

    base = hex_to_rgb(
        PERSONALITY_COLORS.get(pt, "#D3B392")
    )

    return tuple(
        min(1.0, c * (0.45 + t * 0.65))
        for c in base
    )

def ease(t, mode):

    if mode == "ease_out":
        return 1 - (1 - t) ** 2

    elif mode == "ease_in":
        return t ** 2

    elif mode == "bounce":

        if t < 0.7:
            return (t / 0.7) ** 2 * 1.12

        return 1.12 - (1.12 - 1.0) * ((t - 0.7) / 0.3)

    return t

# -------------------------------------------------------------------
# Ring renderer
# -------------------------------------------------------------------

def draw_ring(
    ax,
    cx,
    cy,
    r,
    personality_type,
    ring_index,
    color,
    alpha,
    linewidth,
    depth=1.0,
):

    steps = 240

    angles = np.linspace(
        0,
        2 * np.pi,
        steps
    )

    seed = ring_index * 17

    # ---------------------------------------------------------------
    # Organic deformation
    # ---------------------------------------------------------------

    if personality_type == "phlegmatic":

        freq = 5
        amp = r * 0.035

        rr = r + np.sin(
            angles * freq + seed * 0.01
        ) * amp

    elif personality_type == "melancholic":

        freq = 28
        amp = r * 0.006

        rr = r + np.sin(
            angles * freq + seed * 0.01
        ) * amp

    elif personality_type == "sanguine":

        freq = 10
        amp = r * 0.05

        rr = r + np.sin(
            angles * freq + seed * 0.01
        ) * amp

    elif personality_type == "choleric":

        np.random.seed(seed)

        freq = 12 + np.random.randint(0, 4)

        amp = r * 0.045

        rr = r + np.sin(
            angles * freq
        ) * amp

        noise = np.random.uniform(
            -0.01,
            0.01,
            len(angles)
        )

        rr *= (1 + noise * depth)

    else:

        rr = np.full_like(angles, r)

    # ---------------------------------------------------------------
    # Perspective
    # ---------------------------------------------------------------

    y_scale = 0.82

    x = np.cos(angles) * rr

    y = np.sin(angles) * rr * y_scale

    # ---------------------------------------------------------------
    # Extrusion depth
    # ---------------------------------------------------------------

    if depth > 0.01:

        layers = int(10 * depth)

        extrusion = 0.018 * depth

        for z in range(layers):

            t = z / max(layers, 1)

            dark = 0.55 - (t * 0.18)

            layer_color = (
                color[0] * dark,
                color[1] * dark,
                color[2] * dark,
            )

            ox = extrusion * z
            oy = -extrusion * z

            ax.plot(
                cx + x + ox,
                cy + y + oy,
                color=layer_color,
                linewidth=linewidth + 1.4,
                alpha=alpha * 0.9,
                solid_capstyle="round",
            )

    # ---------------------------------------------------------------
    # Top ring
    # ---------------------------------------------------------------

    top_color = (
        min(1.0, color[0] + 0.08),
        min(1.0, color[1] + 0.08),
        min(1.0, color[2] + 0.08),
    )

    ax.plot(
        cx + x,
        cy + y,
        color=top_color,
        linewidth=linewidth,
        alpha=alpha,
        solid_capstyle="round",
    )

# -------------------------------------------------------------------
# Generate artwork
# -------------------------------------------------------------------

def generate_art(
    age,
    personality_type,
    events,
    depth=1.0
):

    fig, ax = plt.subplots(
        figsize=(7, 7),
        facecolor="white"
    )

    ax.set_facecolor("white")

    ax.axis("off")

    ax.set_aspect("equal")

    core_r = 0.12

    max_r = 2.7

    step = (max_r - core_r) / max(age, 1)

    event_map = {
        ev["age"]: ev
        for ev in events
    }

    for i in range(1, age + 1):

        r = core_r + i * step

        t = i / age

        if i in event_map:

            color = hex_to_rgb(
                event_map[i]["color"]
            )

            alpha = 0.95

            lw = 1.6

        else:

            color = get_ring_color(
                personality_type,
                t
            )

            alpha = 0.15 + t * 0.5

            lw = 0.8

        draw_ring(
            ax=ax,
            cx=0,
            cy=0,
            r=r,
            personality_type=personality_type,
            ring_index=i,
            color=color,
            alpha=alpha,
            linewidth=lw,
            depth=depth,
        )

    # Core

    ax.add_patch(

        plt.Circle(
            (0, 0),
            core_r * 0.65,
            color=PERSONALITY_COLORS[
                personality_type
            ],
            zorder=10,
        )
    )

    # Legend

    if events:

        for ev in events:

            ax.plot(
                [],
                [],
                color=hex_to_rgb(ev["color"]),
                linewidth=3,
                label=f"Age {ev['age']}: {ev['label']}"
            )

        ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.08),
            frameon=False,
            fontsize=8,
            ncol=2
        )

    ax.set_xlim(-4, 4)

    ax.set_ylim(-3.5, 3.5)

    plt.tight_layout()

    return fig

# -------------------------------------------------------------------
# Deep dive button
# -------------------------------------------------------------------

cfg = ANIM_CONFIG[personality_type]

button_text = (
    "🌿 Return to surface"
    if st.session_state.is_3d
    else "🔮 Deep Dive"
)

clicked = st.button(
    button_text,
    use_container_width=True,
    disabled=st.session_state.animating
)

if clicked and not st.session_state.animating:

    st.session_state.animating = True

    st.session_state.is_3d = (
        not st.session_state.is_3d
    )

# -------------------------------------------------------------------
# Render
# -------------------------------------------------------------------

placeholder = st.empty()

if st.session_state.animating:

    steps = cfg["steps"]

    sleep = cfg["sleep"]

    easing_mode = cfg["easing"]

    target_3d = st.session_state.is_3d

    for frame in range(steps + 1):

        t = frame / steps

        eased = ease(t, easing_mode)

        depth = (
            eased
            if target_3d
            else 1.0 - eased
        )

        fig = generate_art(
            age,
            personality_type,
            st.session_state.events,
            depth
        )

        placeholder.pyplot(fig)

        plt.close(fig)

        if frame < steps:

            time.sleep(sleep)

    st.session_state.depth = (
        1.0 if target_3d else 0.0
    )

    st.session_state.animating = False

    st.rerun()

else:

    fig = generate_art(
        age,
        personality_type,
        st.session_state.events,
        st.session_state.depth
    )

    placeholder.pyplot(fig)

# -------------------------------------------------------------------
# Download
# -------------------------------------------------------------------

buf = BytesIO()

fig.savefig(
    buf,
    format="png",
    dpi=140,
    bbox_inches="tight"
)

buf.seek(0)

mode = (
    "3d"
    if st.session_state.is_3d
    else "2d"
)

st.download_button(
    label="⬇️ Download portrait",
    data=buf,
    file_name=f"portrait_{mode}.png",
    mime="image/png"
)
