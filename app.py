import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="RINGS — Year by Year", layout="centered")
st.title("RINGS — Year by Year")
st.write(" Hi there! My name is Irina. Here's a fun project you can try — and a chance to see a tangible outcome of my art shaped by your own data. Feel free to download your final personalised infographic. This is just the beginning — I'll be adding new features soon! We can also print your artwork on beautiful textured paper and send it directly to you. Enjoy!")
st.write("The concept: Each line represents a year of your life, inspired by the quiet rings inside a tree. This is your foundation. The rest reveals itself.")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
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

PERSONALITY_COLORS = {
    "phlegmatic": "#B8D6BE",
    "melancholic": "#A7C4EB",
    "choleric":    "#F4A896",
    "sanguine":    "#FAE0AA",
}

# Per-personality animation config
# steps  — number of rerender frames (more = smoother)
# sleep  — seconds between frames
# easing — "linear" | "ease_in" | "ease_out" | "bounce"
# label  — status message shown during animation
ANIM_CONFIG = {
    "phlegmatic": {"steps": 14, "sleep": 0.09, "easing": "ease_out", "label": "Breathing deeper…"},
    "melancholic": {"steps": 20, "sleep": 0.07, "easing": "ease_in",  "label": "Carving inward…"},
    "sanguine":   {"steps":  8, "sleep": 0.04, "easing": "bounce",   "label": "Coming alive!"},
    "choleric":   {"steps":  6, "sleep": 0.03, "easing": "linear",   "label": "Igniting…"},
}

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
for key, default in [
    ("events", []),
    ("depth", 0.0),
    ("is_3d", False),
    ("animating", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------------
# UI — inputs
# ---------------------------------------------------------------------------
col_age, = st.columns(1)
with col_age:
    st.markdown("**Your age**")
    age = st.slider("", min_value=1, max_value=100, value=20, label_visibility="collapsed")

col_personality, = st.columns(1)
with col_personality:
    st.markdown("**What is your personality type?**")
    personality_type = st.radio(
        "",
        ["Phlegmatic", "Melancholic", "Sanguine", "Choleric"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    personality_type = personality_type.lower()

st.markdown("---")

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

color_col1, color_col2, ev_col3 = st.columns([4, 1, 1])
with color_col1:
    st.markdown("**Pick the color of each major event**")
    selected_name = st.selectbox(
        "Color", options=list(PASTELS.keys()), index=0, label_visibility="collapsed",
    )
selected_hex = PASTELS[selected_name]

with color_col2:
    st.markdown("&nbsp;", unsafe_allow_html=True)
    st.markdown(
        f'<div style="margin-top:6px;"><div style="width:32px;height:32px;border-radius:50%;'
        f'background:{selected_hex};border:1px solid #ccc;"></div></div>',
        unsafe_allow_html=True,
    )
with ev_col3:
    st.markdown("&nbsp;", unsafe_allow_html=True)
    add_clicked = st.button("+ Add", key="add_event")


def detect_children(label):
    label_lower = label.lower()
    if "quadruplets" in label_lower: return 4
    if "triplets"    in label_lower: return 3
    if "twins"       in label_lower: return 2
    if any(k in label_lower for k in ["baby","child","deliver kid","born","daughter","son","kid"]): return 1
    return 0


if add_clicked and event_label:
    st.session_state.events.append({
        "label": event_label, "age": int(event_age),
        "color": selected_hex, "children": detect_children(event_label),
    })

for idx, ev in enumerate(st.session_state.events):
    c1, c2 = st.columns([6, 1])
    with c1:
        child_tag = ""
        if ev.get("children", 0) > 0:
            names = {1:"👶 child",2:"👶👶 twins",3:"👶👶👶 triplets",4:"👶👶👶👶 quadruplets"}
            child_tag = f" · <em>{names.get(ev['children'],'')}</em>"
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

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))

def get_ring_color(pt, t):
    if pt in PERSONALITY_COLORS:
        base = hex_to_rgb(PERSONALITY_COLORS[pt])
        return tuple(base[i] * (0.5 + 0.5 * t) for i in range(3))
    return (0.24 + t*0.39, 0.12 + t*0.22, 0.02 + t*0.10)

def _adjust_color(color, factor):
    return tuple(min(1.0, max(0.0, c * factor)) for c in color)

def _add_brightness(color, amount):
    return tuple(min(1.0, max(0.0, c + amount)) for c in color)

def _ease(t, mode):
    """Map linear 0→1 to eased 0→1."""
    if   mode == "ease_out": return 1 - (1 - t) ** 2
    elif mode == "ease_in":  return t ** 2
    elif mode == "bounce":
        # overshoot slightly then settle — feels energetic (sanguine)
        if t < 0.7:
            return (t / 0.7) ** 2 * 1.15
        else:
            return 1.15 - (1.15 - 1.0) * ((t - 0.7) / 0.3)
    else:  # linear (choleric — raw, no softening)
        return t


def draw_ring(ax, cx, cy, r, personality_type, ring_index, color, alpha, linewidth, depth=1.0):
    """
    depth=0.0  →  flat 2D (shadow/highlight invisible)
    depth=1.0  →  full 3D highlight+shadow effect
    """
    steps  = 800
    angles = np.linspace(0, 2 * np.pi, steps)
    seed   = ring_index * 17

    raw_offset    = max(r * 0.012, 0.018)
    shadow_offset = raw_offset * depth           # scales away when depth=0
    sx, sy        =  shadow_offset, -shadow_offset
    hx, hy        = -shadow_offset,  shadow_offset

    shadow_color    = _adjust_color(color, 0.45)
    highlight_color = _add_brightness(color, 0.30)

    def _plot_pass(cx_, cy_, col, alp, lw):
        if personality_type == "phlegmatic":
            freq = 6; amp = r * 0.045; phase = (seed % 628) / 100
            rr = r + np.sin(angles * freq + phase) * amp
            ax.plot(cx_ + np.cos(angles)*rr, cy_ + np.sin(angles)*rr,
                    color=col, alpha=alp, linewidth=lw)

        elif personality_type == "melancholic":
            for angle in np.linspace(0, 2*np.pi, 72, endpoint=False):
                x0 = cx_ + np.cos(angle)*(r - 0.02); x1 = cx_ + np.cos(angle)*(r + 0.02)
                y0 = cy_ + np.sin(angle)*(r - 0.02); y1 = cy_ + np.sin(angle)*(r + 0.02)
                ax.plot([x0, x1], [y0, y1], color=col, alpha=alp, linewidth=lw)

        elif personality_type == "sanguine":
            freq = 12; amp = r * 0.045; phase = (seed % 628) / 100
            rr = r + np.sin(angles * freq + phase) * amp
            ax.plot(cx_ + np.cos(angles)*rr, cy_ + np.sin(angles)*rr,
                    color=col, alpha=alp, linewidth=lw)

        elif personality_type == "choleric":
            np.random.seed(seed)
            freq = 12 + np.random.randint(0, 4); amp = r * 0.04; phase = np.random.rand()
            rr = r + np.sin(angles * freq + phase) * amp
            noise = np.random.uniform(-0.01, 0.01, len(angles)) * depth  # noise also scales
            rr = rr * (1 + noise)
            ax.plot(cx_ + np.cos(angles)*rr, cy_ + np.sin(angles)*rr,
                    color=col, alpha=alp, linewidth=lw)

        else:
            ax.plot(cx_ + np.cos(angles)*r, cy_ + np.sin(angles)*r,
                    color=col, alpha=alp, linewidth=lw)

    # Shadow pass — invisible at depth=0
    if depth > 0.005:
        _plot_pass(cx+sx, cy+sy, shadow_color,    alpha * 0.35 * depth, linewidth * 1.8)
    # Main ring — always drawn
    _plot_pass(cx, cy, color, alpha, linewidth)
    # Highlight pass — invisible at depth=0
    if depth > 0.005:
        _plot_pass(cx+hx, cy+hy, highlight_color, alpha * 0.45 * depth, linewidth * 0.55)


def draw_child_portrait(ax, cx, cy, child_age, color_hex, personality_type, depth=1.0):
    core_r = 0.08
    max_r  = 0.35 + (child_age / 100) * 0.55
    step   = (max_r - core_r) / max(child_age, 1)
    for i in range(1, child_age + 1):
        r = core_r + i * step; t = i / child_age
        if i == child_age:
            color = hex_to_rgb(color_hex); alpha = 0.85; lw = 1.5
        else:
            color = get_ring_color(personality_type, t); alpha = 0.12 + t*0.55; lw = 0.5
        draw_ring(ax, cx, cy, r, personality_type, i, color, alpha, lw, depth=depth)
    ax.add_patch(plt.Circle((cx, cy), core_r*0.6,
                             color=PERSONALITY_COLORS.get(personality_type, "#D3B392"), zorder=10))
    return max_r


def generate_art(age, personality_type, events, depth=1.0):
    all_children = []
    for ev in events:
        n = ev.get("children", 0)
        child_age = max(1, age - ev["age"])
        for _ in range(n):
            all_children.append({"age": child_age, "color": ev["color"], "event_age": ev["age"]})

    has_children = len(all_children) > 0
    fig_w = 12 if has_children else 7
    fig, ax = plt.subplots(figsize=(fig_w, 7), facecolor="#ffffff")
    ax.set_facecolor("#ffffff"); ax.set_aspect("equal"); ax.axis("off")

    cx, cy = (-0.8 if has_children else 0), 0
    core_r = 0.12; max_r = 2.7
    step = (max_r - core_r) / max(age, 1)
    event_map = {ev["age"]: ev for ev in events}

    for i in range(1, age + 1):
        r = core_r + i * step; t = i / age; lw = 0.7
        if i in event_map:
            color = hex_to_rgb(event_map[i]["color"]); alpha = 0.85; lw = 1.5
        else:
            color = get_ring_color(personality_type, t); alpha = 0.12 + t*0.55
        draw_ring(ax, cx, cy, r, personality_type, i, color, alpha, lw, depth=depth)

    ax.add_patch(plt.Circle((cx, cy), core_r*0.6,
                             color=PERSONALITY_COLORS.get(personality_type, "#D3B392"), zorder=10))

    if has_children:
        cx_child   = 2.4
        total_span = min(5.5, len(all_children) * 1.6)
        positions  = np.linspace(-total_span/2, total_span/2, len(all_children)) if len(all_children) > 1 else [0.0]
        for i, child in enumerate(all_children):
            cy_child    = positions[i]
            child_max_r = draw_child_portrait(ax, cx_child, cy_child,
                                              child["age"], child["color"],
                                              personality_type, depth=depth)
            r_birth = core_r + child["event_age"] * step
            dx = cx_child - cx; dy = cy_child - cy
            angle   = np.arctan2(dy, dx)
            x_start = cx + r_birth * np.cos(angle)
            y_start = cy + r_birth * np.sin(angle)
            x_end   = cx_child - child_max_r * np.cos(angle)
            y_end   = cy_child - child_max_r * np.sin(angle)
            ax.plot([x_start, x_end], [y_start, y_end],
                    color="#C0A882", linewidth=0.5, linestyle="--", alpha=0.4, zorder=0)
            ax.text(cx_child, cy_child - child_max_r - 0.15, f"{child['age']}y",
                    ha="center", va="top", fontsize=6, color="#8B7355", alpha=0.7)

    if events:
        for ev in events:
            ax.plot([], [], color=hex_to_rgb(ev["color"]),
                    linewidth=2, label=f"Age {ev['age']}: {ev['label']}")
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.08),
                  frameon=False, fontsize=8, ncol=2)

    x_min = -4.5 if has_children else -3.2
    x_max =  4.8 if has_children else  3.2
    ax.set_xlim(x_min, x_max); ax.set_ylim(-3.2, 3.2)
    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Deep Dive button
# ---------------------------------------------------------------------------
cfg = ANIM_CONFIG[personality_type]

if st.session_state.is_3d:
    btn_label = "🌿 Return to surface"
else:
    btn_label = "🔮 Deep Dive"

col_btn, col_status = st.columns([2, 5])
with col_btn:
    deep_dive_clicked = st.button(btn_label, use_container_width=True,
                                  disabled=st.session_state.animating)
with col_status:
    if st.session_state.animating:
        direction = "→ 3D" if not st.session_state.is_3d else "→ 2D"
        st.caption(f"{cfg['label']} {direction}")
    elif st.session_state.is_3d:
        st.caption("✦ Deep view active")

if deep_dive_clicked and not st.session_state.animating:
    st.session_state.animating = True
    st.session_state.is_3d = not st.session_state.is_3d  # flip target

st.markdown("---")

# ---------------------------------------------------------------------------
# Render — animated or static
# ---------------------------------------------------------------------------
chart_placeholder = st.empty()

if st.session_state.animating:
    steps  = cfg["steps"]
    sleep  = cfg["sleep"]
    easing = cfg["easing"]
    going_3d = st.session_state.is_3d  # already flipped above

    for frame in range(steps + 1):
        t_linear = frame / steps
        t_eased  = _ease(t_linear, easing)
        depth    = t_eased if going_3d else 1.0 - t_eased
        depth    = max(0.0, min(1.0, depth))   # clamp (bounce can overshoot)

        fig = generate_art(int(age), personality_type, st.session_state.events, depth=depth)
        chart_placeholder.pyplot(fig)
        plt.close(fig)
        if frame < steps:
            time.sleep(sleep)

    # Snap to exact final value
    st.session_state.depth     = 1.0 if going_3d else 0.0
    st.session_state.animating = False
    st.rerun()

else:
    fig = generate_art(int(age), personality_type, st.session_state.events,
                       depth=st.session_state.depth)
    chart_placeholder.pyplot(fig)

# ---------------------------------------------------------------------------
# Download — labelled with current mode
# ---------------------------------------------------------------------------
buf = BytesIO()
fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
buf.seek(0)
mode_tag = "3d" if st.session_state.is_3d else "2d"
st.download_button(
    label="⬇️ Download portrait",
    data=buf,
    file_name=f"portrait_age{int(age)}_{personality_type}_{mode_tag}.png",
    mime="image/png",
)
