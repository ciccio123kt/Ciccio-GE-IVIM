"""Genera l'icona dell'app (icon.png / icon.ico) - curva bi-esponenziale stilizzata."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

here = os.path.dirname(os.path.abspath(__file__))
fig = plt.figure(figsize=(2.56, 2.56), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
ax.add_patch(plt.Circle((0.5, 0.5), 0.48, color="#4B2E83"))
b = np.linspace(0, 800, 200)
s = 0.2 * np.exp(-b * 0.06) + 0.8 * np.exp(-b * 1.1e-3)
ax.plot(0.18 + 0.64 * b / 800, 0.30 + 0.45 * s, color="white", lw=6, solid_capstyle="round")
ax.text(0.5, 0.17, "IVIM", color="white", ha="center", va="center", fontsize=30, weight="bold")
png = os.path.join(here, "icon.png")
fig.savefig(png, transparent=True)
Image.open(png).save(os.path.join(here, "icon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icona creata")
