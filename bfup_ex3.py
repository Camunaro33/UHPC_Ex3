# -*- coding: utf-8 -*-
"""
bfup_ex3.py – noyau de calcul et de tracé de l'exemple 3 (Applications 8, A8.2)
Renforcement à l'effort tranchant d'un tablier continu au moyen du BFUP armé.
Mécanisme cinématique (borne supérieure) : (1) écrasement de l'âme en béton comprimée,
(2) effet goujon par formation de deux rotules plastiques dans la couche de BFUP armé.

Cours « Structures existantes : chapitres choisis », p. 53-55.
Unités internes : N, mm, MPa ; résultats en kN, kNm/m.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

C_CONC, C_UHPC, C_STEEL, C_COMP, C_TENS, C_NA = "0.85", "0.55", "k", "#b2182b", "#2166ac", "#d6604d"
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})


def ex3_inputs():
    return dict(
        # hauteurs statiques de la section composée BFUP-béton
        d_sc=2360.0, d_sU=2460.0, d_U=2460.0,
        # béton existant
        A_c=760000.0, f_cd=20.0, A_sc=1000.0, f_scd=435.0,
        # couche de BFUP armé (même couche que A8.1)
        h_U=120.0, phi_sU=20.0, s_sU=100.0, n_layers=2,
        f_sUd=435.0, f_sy=500.0,          # f_sy : utilisé par le corrigé pour x_U
        f_Utd_deff=7.0,                   # f_Utd utilisé par le corrigé dans d_eff et ω_m
        f_Utu=6.0, f_Uc=150.0, k_Uc=0.5,  # rotule : σ_c max = k_Uc · f_Uc (hypothèse prudente)
        b_U_omega=1.0,                    # largeur de BFUP [m] prise dans d_eff et ω_m (corrigé : 1 m)
        b_dowel=2500.0,                   # largeur de BFUP mobilisée par l'effet goujon [mm]
        # mécanisme
        alpha=35.0, l_Z=1500.0, h_crack=2040.0, b_w=300.0, k_stress_block=0.85,
        # sollicitations
        V_Rsd=1030.0, V_d=1550.0, a_section=4500.0,
    )


def bar_area(phi, s):
    return np.pi * phi**2 / 4.0 * 1000.0 / s


def VRc(p, x_eff, alpha_deg):
    """Contribution de l'âme comprimée [kN] : b_w · x_eff/sinα · f_cd/2 · (1 − cosα)."""
    a = np.radians(alpha_deg)
    return p["b_w"] * x_eff / np.sin(a) * p["f_cd"] / 2 * (1 - np.cos(a)) / 1e3


def a0_of(p, alpha_deg):
    return p["h_crack"] / np.tan(np.radians(alpha_deg)) + p["l_Z"]


def ex3_compute(p=None):
    p = ex3_inputs() if p is None else {**ex3_inputs(), **p}
    A_sU = p["n_layers"] * bar_area(p["phi_sU"], p["s_sU"])      # mm²/m
    A_U = 1000.0 * p["h_U"] - A_sU                                # mm²/m
    rho = A_sU / A_U
    bU = p["b_U_omega"]
    terms = [("BFUP", p["d_U"], bU * A_U * p["f_Utd_deff"]),
             ("A_sU", p["d_sU"], bU * A_sU * p["f_sUd"]),
             ("A_sc", p["d_sc"], p["A_sc"] * p["f_scd"])]
    sumAf = sum(t[2] for t in terms)
    d_eff = sum(t[1] * t[2] for t in terms) / sumAf
    omega = sumAf / (p["A_c"] * p["f_cd"])
    x = 0.9 * omega * d_eff
    x_eff = p["k_stress_block"] * x
    a0 = a0_of(p, p["alpha"])
    V_Rcd = VRc(p, x_eff, p["alpha"])
    # rotule plastique dans la couche de BFUP armé
    hU = p["h_U"]
    x_U = rho * hU * p["f_sy"] / (p["k_Uc"] * p["f_Uc"])
    m_s = p["f_sUd"] * rho * hU * (hU / 2 - x_U / 2) / 1e3        # kNm/m
    m_U = p["f_Utu"] * (hU - x_U) * (hU / 2 - x_U) / 1e3          # kNm/m
    m_UR = m_s + m_U
    V_RUd = 2 * m_UR / (p["l_Z"] / 1e3) * p["b_dowel"] / 1e3      # kN
    V_Rd = V_Rcd + V_RUd + p["V_Rsd"]
    # borne supérieure : α minimal admissible (a0 ≤ distance de la section)
    free = p["a_section"] - p["l_Z"]
    alpha_min = np.degrees(np.arctan(p["h_crack"] / free)) if free > 0 else np.nan
    V_Rd_min = (VRc(p, x_eff, alpha_min) + V_RUd + p["V_Rsd"]) if free > 0 else np.nan
    alphas = np.linspace(15, 70, 111)
    return dict(p=p, A_sU=A_sU, A_U=A_U, rho=rho, terms=terms, sumAf=sumAf, d_eff=d_eff, omega=omega,
                x=x, x_eff=x_eff, a0=a0, V_Rcd=V_Rcd, V_Rcd45=VRc(p, x_eff, 45.0), a0_45=a0_of(p, 45.0),
                x_U=x_U, m_s=m_s, m_U=m_U, m_UR=m_UR, V_RUd=V_RUd, V_Rd=V_Rd, ok=V_Rd >= p["V_d"],
                alpha_min=alpha_min, V_Rd_min=V_Rd_min, alphas=alphas,
                VRd_alpha=np.array([VRc(p, x_eff, a) for a in alphas]) + V_RUd + p["V_Rsd"],
                a0_alpha=a0_of(p, alphas))


# ----------------------------------------------------------------------------
# Tracés
# ----------------------------------------------------------------------------
def draw_mechanism(ax, r):
    p = r["p"]
    H = 2.5
    L = max(7.0, (r["a0"] + p["l_Z"]) / 1e3 + 1.5)
    ax.add_patch(Rectangle((0, 0), L, H, fc=C_CONC, ec="k", lw=0.8))
    ax.add_patch(Rectangle((0, H), L, max(0.08, p["h_U"] / 800), fc=C_UHPC, ec="k", lw=0.8))
    tU = max(0.08, p["h_U"] / 800)
    xc = min(r["x_eff"] / 1e3, H * 0.6)
    x0 = 0.3
    a = np.radians(p["alpha"])
    dx = p["h_crack"] / 1e3 / np.tan(a)
    ax.plot([x0, x0 + dx], [xc, min(H, xc + p["h_crack"] / 1e3)], color=C_COMP, lw=2)
    ax.add_patch(Rectangle((0, 0), x0 + 0.6, xc, fc=C_COMP, alpha=0.3, ec="none"))
    for xh in (x0 + dx, x0 + dx + p["l_Z"] / 1e3):
        ax.plot(xh, H + tU / 2, "o", ms=9, mfc="w", mec=C_TENS, mew=2)
    ax.text(x0 + dx + p["l_Z"] / 2e3, H + tU + 0.12, f"l_Z = {p['l_Z']/1e3:.2f} m\n(2 rotules BFUP)",
            ha="center", color=C_TENS, fontsize=8)
    ax.annotate("", (x0, -0.35), (x0 + r["a0"] / 1e3, -0.35), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(x0 + r["a0"] / 2e3, -0.3, f"a0 = {r['a0']/1e3:.2f} m", ha="center", va="bottom")
    ax.text(x0 + 0.4, xc + 0.12, f"α = {p['alpha']:.1f}°", color=C_COMP)
    ax.text(0.05, xc / 2, f"x_eff = {r['x_eff']:.0f} mm", fontsize=8, va="center")
    ax.add_patch(Polygon([(0.15, -0.25), (0.45, -0.25), (0.3, 0)], fc="0.3"))
    xs = x0 + p["a_section"] / 1e3
    ax.annotate("", (xs, H + tU), (xs, H + 0.95), arrowprops=dict(arrowstyle="-|>", lw=2))
    ax.text(xs + 0.1, H + 0.6, f"V_d = {p['V_d']:.0f} kN\n(section à {p['a_section']/1e3:.1f} m)", fontsize=8)
    ax.set_xlim(-0.3, L + 0.2)
    ax.set_ylim(-0.6, H + 1.15)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Mécanisme : (1) écrasement de l'âme, (2) deux rotules dans le BFUP armé")


def draw_hinge(ax, r):
    p = r["p"]
    hU, xU = p["h_U"], r["x_U"]
    sc = -p["k_Uc"] * p["f_Uc"]
    ax.fill_betweenx([0, xU], 0, sc, color=C_COMP, alpha=0.4)
    ax.fill_betweenx([xU, hU], 0, p["f_Utu"] * 5, color=C_TENS, alpha=0.4)
    ax.text(sc / 2, xU / 2, f"{p['k_Uc']:g}·f_Uc\n= {-sc:.0f} MPa", ha="center", va="center", fontsize=8)
    ax.text(p["f_Utu"] * 5, (xU + hU) / 2, f" f_Utu = {p['f_Utu']:g} MPa\n (échelle ×5)", va="center", fontsize=8)
    ax.plot(0, hU / 2, "o", color=C_STEEL, ms=8)
    ax.text(3, hU / 2 + 3, f"ρ_sU = {r['rho']*100:.1f} %, f_sd = {p['f_sUd']:.0f}", fontsize=8)
    ax.axhline(xU, color=C_NA, ls="--")
    ax.text(sc * 1.3, xU + 2, f"x_U = {xU:.0f} mm", color=C_NA, fontsize=8)
    ax.axhline(hU, color="k", lw=0.6)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlim(sc * 1.75, 95)
    ax.set_ylim(-5, hU + 10)
    ax.set_xlabel("σ [MPa]")
    ax.set_ylabel("hauteur dans la couche [mm]")
    ax.set_title(f"Rotule plastique : m_UR = {r['m_UR']:.0f} kNm/m")


def draw_contributions(ax, r):
    p = r["p"]
    parts = [("V_Rsd (étriers + précontrainte)", p["V_Rsd"], "0.6"), ("V_Rcd (âme béton)", r["V_Rcd"], C_COMP),
             ("V_RUd (goujon BFUP)", r["V_RUd"], C_TENS)]
    bot = 0
    for lab, v, c in parts:
        ax.bar(0, v, bottom=bot, color=c, width=0.5, label=f"{lab} : {v:.0f}")
        if v > 0.05 * max(p["V_d"], 1):
            ax.text(0, bot + v / 2, f"{v:.0f}", ha="center", va="center", color="w", weight="bold")
        bot += v
    ax.axhline(p["V_d"], color="k", ls="--")
    ax.text(0.3, p["V_d"], f"V_d = {p['V_d']:.0f}", va="bottom")
    ax.text(0, bot, f"V_Rd = {bot:.0f}", ha="center", va="bottom", weight="bold")
    ax.set_xlim(-0.6, 0.9)
    ax.set_ylim(0, max(bot, p["V_d"]) * 1.12)
    ax.set_xticks([])
    ax.set_ylabel("[kN]")
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    ax.set_title("Contributions à V_Rd")


def draw_alpha(ax, r):
    p = r["p"]
    ax.plot(r["alphas"], r["VRd_alpha"], color=C_TENS, label="V_Rd(α)")
    ax.axhline(p["V_d"], color="k", ls="--", lw=0.8, label="V_d")
    ax.axvline(p["alpha"], color="0.5", ls=":")
    if np.isfinite(r["alpha_min"]):
        ax.axvspan(r["alphas"][0], r["alpha_min"], color="0.9", zorder=0)
        ax.plot(r["alpha_min"], r["V_Rd_min"], "o", color=C_TENS)
        ax.text(r["alpha_min"], r["V_Rd_min"], f"  α_min = {r['alpha_min']:.1f}° → {r['V_Rd_min']:.0f} kN",
                fontsize=8, va="top")
    ax.set_xlabel("α [°]")
    ax.set_ylabel("V_Rd [kN]")
    ax2 = ax.twinx()
    ax2.plot(r["alphas"], r["a0_alpha"] / 1e3, color=C_COMP, ls="-.", label="a0(α)")
    ax2.axhline(p["a_section"] / 1e3, color=C_COMP, lw=0.6, ls=":")
    ax2.text(r["alphas"][-1], p["a_section"] / 1e3, "a_section ", color=C_COMP, fontsize=7.5, ha="right", va="bottom")
    ax2.set_ylabel("a0 [m]", color=C_COMP)
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7.5, frameon=False, loc="lower right")
    ax.set_title("Borne supérieure : variation de α (zone grise : a0 > a_section)")


if __name__ == "__main__":
    r = ex3_compute()
    print(f"d_eff = {r['d_eff']:.0f} mm ; ω = {r['omega']:.3f} ; x = {r['x']:.0f} ; V_Rcd = {r['V_Rcd']:.0f} ; "
          f"m_UR = {r['m_UR']:.1f} ; V_RUd = {r['V_RUd']:.0f} ; V_Rd = {r['V_Rd']:.0f} kN ; "
          f"α_min = {r['alpha_min']:.1f}° → {r['V_Rd_min']:.0f} kN")
    fig, ax = plt.subplots(2, 2, figsize=(15, 9))
    draw_mechanism(ax[0, 0], r); draw_hinge(ax[0, 1], r); draw_contributions(ax[1, 0], r); draw_alpha(ax[1, 1], r)
    plt.show()
