```python
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="RINGS — Year by Year", layout="centered")

st.title("RINGS — Year by Year")

st.write(
    " Hi there! My name is Irina. Here's a fun project you can try — "
    "and a chance to see a tangible outcome of my art shaped by your own data."
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
    "choleric": "#F4A896",
    "sanguine": "#FAE0AA",
}

ANIM_CONFIG = {
    "phlegmatic": {
        "steps": 14,
        "sleep": 0.09,
        "easing": "ease_out",
        "label": "Breathing deeper…",
    },
    "melancholic": {
        "steps": 20,
        "sleep": 0.07,
        "easing": "ease_in",
        "label": "Carving inward…",
    },
    "sanguine": {
        "steps": 8,
        "sleep": 0.04,
        "easing": "bounce",
        "label": "Coming alive!",
    },
    "choleric": {
        "steps": 6,
        "sleep": 0.03,
        "easing": "linear",
        "label": "Igniting…",
    },
}

# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

for key, default in [
    ("events", []),
    ("depth", 0.0),
    ("is_3d", False),
    ("animating", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------------------------------------------------------
# UI
# -------------------------------------------------------------------

st.markdown("### Your age")

age = st.slider(
    "",
    min_value=1,
    max_value=100,
    value=20,
    label_visibility="collapsed",
)

st.markdown("### Personality type")

personality_type = st.radio(
    "",
    ["Phlegmatic", "Melancholic", "Sanguine", "Choleric"],
    horizontal=True,
    label_visibility="collapsed",
).lower()

st.markdown("---")

col1, col2 = st.columns([4, 2])

with col1:
    event_label = st.text_input(
        "",
        placeholder="e.g. Got married, had a baby...",
        label_visibility="collapsed",
    )

with col2:
    event_age = st.number_input(
        "",
        min_value=1,
        max_value=100,
        value=20,
        label_visibility="collapsed",
    )

c1, c2, c3 = st.columns([4, 1, 1])

with c1:
    selected_name = st.selectbox(
        "Color",
        list(PASTELS.keys()),
        label_visibility="collapsed",
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
        unsafe_allow_html=True,
    )

with c3:
    add_clicked = st.button("+ Add")

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def detect_children(label):

    label = label.lower()

    if "quadruplets" in label:
        return 4

    if "triplets" in label:
        return 3

    if "twins" in label:
        return 2

    if any(
        k in label
        for k in ["baby", "child", "daughter", "son", "born"]
    ):
        return 1

    return 0


if add_clicked and event_label:

    st.session_state.events.append({
        "label": event_label,
        "age": int(event_age),
        "color": selected_hex,
        "children": detect_children(event_label),
    })

for idx, ev in enumerate(st.session_state.events):

    cc1, cc2 = st.columns([6, 1])

    with cc1:

        st.markdown(
            f"<span style='color:{ev['color']};font-size:18px;'>●</span> "
            f"<strong>Age {ev['age']}</strong> — {ev['label']}",
            unsafe_allow_html=True,
        )

    with cc2:

        if st.button("×", key=f"del_{idx}"):

            st.session_state.events.pop(idx)
            st.rerun()

# -------------------------------------------------------------------
# Drawing
# -------------------------------------------------------------------

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16) / 255
        for i in (0, 2, 4)
    )


def get_ring_color(pt, t):

    if pt in PERSONALITY_COLORS:

        base = hex_to_rgb(PERSONALITY_COLORS[pt])

        return tuple(base[i] * (0.5 + 0.5 * t) for i in range(3))

    return (0.24 + t*0.39, 0.12 + t*0.22, 0.02 + t*0.10)


def ease(t, mode):

    if mode == "ease_out":
        return 1 - (1 - t) ** 2

    elif mode == "ease_in":
        return t ** 2

    elif mode == "bounce":

        if t < 0.7:
            return (t / 0.7) ** 2 * 1.15

        return 1.15 - (1.15 - 1.0) * ((t - 0.7) / 0.3)

    return t


# -------------------------------------------------------------------
# NEW 3D RING ENGINE
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

    steps = 900

    angles = np.linspace(0, 2*np.pi, steps)

    seed = ring_index * 17

    y_scale = 0.82 + (0.12 * (1.0 - depth))

    light_angle = -np.pi / 4

    # ---------------------------------------------------------
    # personality deformation
    # ---------------------------------------------------------

    if personality_type == "phlegmatic":

        freq = 6
        amp = r * 0.045
        phase = (seed % 628) / 100

        rr = r + np.sin(angles * freq + phase) * amp

    elif personality_type == "melancholic":

        freq = 32
        amp = r * 0.008
        phase = (seed % 628) / 100

        rr = r + np.sin(angles * freq + phase) * amp

    elif personality_type == "sanguine":

        freq = 12
        amp = r * 0.05
        phase = (seed % 628) / 100

        rr = r + np.sin(angles * freq + phase) * amp

    elif personality_type == "choleric":

        np.random.seed(seed)

        freq = 14 + np.random.randint(0, 5)

        amp = r * 0.045

        phase = np.random.rand()

        rr = r + np.sin(angles * freq + phase) * amp

        noise = np.random.uniform(-0.012, 0.012, len(angles))

        rr *= (1 + noise * depth)

    else:

        rr = np.full_like(angles, r)

    # ---------------------------------------------------------
    # geometry
    # ---------------------------------------------------------

    x_base = np.cos(angles) * rr

    y_base = np.sin(angles) * rr * y_scale

    # ---------------------------------------------------------
    # directional lighting
    # ---------------------------------------------------------

    light = 0.60 + 0.40 * np.cos(angles - light_angle)

    # ---------------------------------------------------------
    # extrusion layers
    # ---------------------------------------------------------

    if depth > 0.01:

        layers = int(20 * depth)

        extrusion = 0.018 * depth

        for z in range(layers):

            t = z / max(layers, 1)

            ox = extrusion * z

            oy = -extrusion * z

            darkness = 0.55 - (t * 0.20)

            layer_colors = [

                (
                    min(1.0, max(0.0, color[0] * darkness * l)),
                    min(1.0, max(0.0, color[1] * darkness * l)),
                    min(1.0, max(0.0, color[2] * darkness * l)),
                )

                for l in light
            ]

            layer_lw = linewidth + (1.8 * (1 - t))

            for i in range(len(angles) - 1):

                ax.plot(
                    [cx + ox + x_base[i], cx + ox + x_base[i + 1]],
                    [cy + oy + y_base[i], cy + oy + y_base[i + 1]],
                    color=layer_colors[i],
                    alpha=alpha * 0.95,
                    linewidth=layer_lw,
                    solid_capstyle="round",
                )

    # ---------------------------------------------------------
    # top surface
    # ---------------------------------------------------------

    top_colors = [

        (
            min(1.0, color[0] * l + 0.08),
            min(1.0, color[1] * l + 0.08),
            min(1.0, color[2] * l + 0.08),
        )

        for l in light
    ]

    for i in range(len(angles) - 1):

        ax.plot(
            [cx + x_base[i], cx + x_base[i + 1]],
            [cy + y_base[i], cy + y_base[i + 1]],
            color=top_colors[i],
            alpha=alpha,
            linewidth=linewidth,
            solid_capstyle="round",
        )


# -------------------------------------------------------------------
# Main artwork
# -------------------------------------------------------------------

def generate_art(age, personality_type, events, depth=1.0):

    fig, ax = plt.subplots(
        figsize=(7, 7),
        facecolor="#ffffff"
    )

    ax.set_facecolor("#ffffff")

    ax.set_aspect(0.82)

    ax.axis("off")

    cx, cy = 0, 0

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

            alpha = 0.9

            lw = 1.6

        else:

            color = get_ring_color(personality_type, t)

            alpha = 0.12 + t * 0.55

        draw_ring(
            ax,
            cx,
            cy,
            r,
            personality_type,
            i,
            color,
            alpha,
            lw,
            depth=depth,
        )

    ax.add_patch(
        plt.Circle(
            (cx, cy),
            core_r * 0.6,
            color=PERSONALITY_COLORS.get(
                personality_type,
                "#D3B392"
            ),
            zorder=10,
        )
    )

    ax.set_xlim(-4, 4)

    ax.set_ylim(-3.5, 3.5)

    plt.tight_layout()

    return fig


# -------------------------------------------------------------------
# Deep dive button
# -------------------------------------------------------------------

cfg = ANIM_CONFIG[personality_type]

btn_label = (
    "🌿 Return to surface"
    if st.session_state.is_3d
    else "🔮 Deep Dive"
)

col_btn, col_status = st.columns([2, 5])

with col_btn:

    deep_dive_clicked = st.button(
        btn_label,
        use_container_width=True,
        disabled=st.session_state.animating,
    )

with col_status:

    if st.session_state.animating:

        direction = (
            "→ 3D"
            if not st.session_state.is_3d
            else "→ 2D"
        )

        st.caption(f"{cfg['label']} {direction}")

    elif st.session_state.is_3d:

        st.caption("✦ Deep view active")


if deep_dive_clicked and not st.session_state.animating:

    st.session_state.animating = True

    st.session_state.is_3d = not st.session_state.is_3d

st.markdown("---")

# -------------------------------------------------------------------
# Render
# -------------------------------------------------------------------

chart_placeholder = st.empty()

if st.session_state.animating:

    steps = cfg["steps"]

    sleep = cfg["sleep"]

    easing_mode = cfg["easing"]

    going_3d = st.session_state.is_3d

    for frame in range(steps + 1):

        t_linear = frame / steps

        t_eased = ease(t_linear, easing_mode)

        depth = (
            t_eased
            if going_3d
            else 1.0 - t_eased
        )

        depth = max(0.0, min(1.0, depth))

        fig = generate_art(
            int(age),
            personality_type,
            st.session_state.events,
            depth=depth,
        )

        chart_placeholder.pyplot(fig)

        plt.close(fig)

        if frame < steps:

            time.sleep(sleep)

    st.session_state.depth = (
        1.0 if going_3d else 0.0
    )

    st.session_state.animating = False

    st.rerun()

else:

    fig = generate_art(
        int(age),
        personality_type,
        st.session_state.events,
        depth=st.session_state.depth,
    )

    chart_placeholder.pyplot(fig)

# -------------------------------------------------------------------
# Download
# -------------------------------------------------------------------

buf = BytesIO()

fig.savefig(
    buf,
    format="png",
    dpi=200,
    bbox_inches="tight",
)

buf.seek(0)

mode_tag = (
    "3d"
    if st.session_state.is_3d
    else "2d"
)

st.download_button(
    label="⬇️ Download portrait",
    data=buf,
    file_name=f"portrait_{mode_tag}.png",
    mime="image/png",
)
```
