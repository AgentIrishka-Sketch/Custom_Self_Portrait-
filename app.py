import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Hair Age Art", layout="centered")

st.title("🌿 Hair Age Art")
st.write("Generate a unique portrait based on your age and hair type.")

age = st.slider("Age", min_value=1, max_value=100, value=35)
hair_type = st.selectbox("Hair type", ["straight", "medium", "curly"])

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
        freq = 10 + (ring_index % 6)
        amp = r * 0.06 + 2
        phase = (seed % 628) / 100
        rr = r + np.sin(angles * freq + phase) * amp
        x = cx + np.cos(angles) * rr
        y = cy + np.sin(angles) * rr

    ax.plot(x, y, color=color, alpha=alpha, linewidth=linewidth)


def generate_art(age, hair_type):
    fig, ax = plt.subplots(figsize=(7, 7), facecolor="#faf8f3")
    ax.set_facecolor("#faf8f3")
    ax.set_aspect("equal")
    ax.axis("off")

    cx, cy = 0, 0
    core_r = 0.12
    max_r = 2.7
    step = (max_r - core_r) / max(age, 1)

    for i in range(1, age + 1):
        r = core_r + i * step
        t = i / age
        color = (
            0.24 + t * 0.39,
            0.12 + t * 0.22,
            0.02 + t * 0.10,
        )
        alpha = 0.12 + t * 0.55
        linewidth = 1.4 if i % 5 == 0 else 0.7
        draw_ring(ax, cx, cy, r, hair_type, i, color, alpha, linewidth)

    core = plt.Circle((cx, cy), core_r, color="#8B5E3C", zorder=10)
    ax.add_patch(core)

    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    plt.tight_layout()
    return fig


fig = generate_art(age, hair_type)
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
