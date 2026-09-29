# -*- coding: utf-8 -*-
"""
Applet Streamlit – Exemple 3 (Applications 8, A8.2)
Renforcement à l'effort tranchant d'un tablier continu au moyen du BFUP armé

Lancer localement :  streamlit run app.py
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import bfup_ex3 as core

st.set_page_config(page_title="BFUP armé – effort tranchant | Ex. 3", layout="wide")
D = core.ex3_inputs()

# ----------------------------------------------------------------------------
# Entrées
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Données d'entrée")
    st.caption("Valeurs par défaut : énoncé et corrigé du cours (p. 53-55).")

    st.subheader("Sollicitation et armatures existantes")
    V_d = st.number_input("V_d – effort tranchant [kN]", 0.0, 10000.0, D["V_d"], 10.0)
    a_section = st.number_input("Distance de la section à l'appui [mm]", 1000.0, 15000.0, D["a_section"], 100.0)
    V_Rsd = st.number_input("V_Rsd – étriers + précontrainte [kN]", 0.0, 10000.0, D["V_Rsd"], 10.0)

    st.subheader("Section composée BFUP-béton")
    d_sc = st.number_input("d_sc – armature du béton [mm]", 500.0, 5000.0, D["d_sc"], 10.0)
    d_sU = st.number_input("d_sU – armature du BFUP [mm]", 500.0, 5000.0, D["d_sU"], 10.0)
    d_U = st.number_input("d_U – couche de BFUP [mm]", 500.0, 5000.0, D["d_U"], 10.0)
    A_c = st.number_input("A_c – aire de béton [mm²]", 1e5, 5e6, D["A_c"], 1e4, format="%.0f")
    f_cd = st.number_input("f_cd – béton [MPa]", 5.0, 80.0, D["f_cd"], 1.0)
    A_sc = st.number_input("A_sc – armature du béton [mm²]", 0.0, 20000.0, D["A_sc"], 100.0)
    f_scd = st.number_input("f_scd [MPa]", 200.0, 600.0, D["f_scd"], 5.0)

    st.subheader("Couche de BFUP armé")
    h_U = st.number_input("h_U [mm]", 30.0, 300.0, D["h_U"], 5.0)
    phi_sU = st.number_input("Ø A_sU [mm]", 8.0, 40.0, D["phi_sU"], 2.0)
    s_sU = st.number_input("Espacement [mm]", 50.0, 300.0, D["s_sU"], 10.0)
    n_layers = st.number_input("Nombre de nappes", 1, 4, int(D["n_layers"]), 1)
    f_sUd = st.number_input("f_sUd – armature [MPa]", 200.0, 600.0, D["f_sUd"], 5.0)
    f_Utu = st.number_input("f_Utu – traction BFUP (rotule) [MPa]", 0.0, 15.0, D["f_Utu"], 0.5)
    f_Uc = st.number_input("f_Uc – compression BFUP [MPa]", 80.0, 250.0, D["f_Uc"], 5.0)
    k_Uc = st.slider("σ_c,max / f_Uc dans la rotule", 0.2, 1.0, D["k_Uc"], 0.05,
                     help="Hypothèse prudente du cours : 50 % de f_Uc lorsque ε_t atteint 2‰.")
    b_dowel = st.number_input("Largeur mobilisée par l'effet goujon b [mm]", 500.0, 10000.0, D["b_dowel"], 100.0)

    st.subheader("Mécanisme")
    alpha = st.slider("α – inclinaison de la fissure critique [°]", 20.0, 60.0, D["alpha"], 0.5)
    l_Z = st.number_input("l_Z – distance entre rotules [mm]", 300.0, 5000.0, D["l_Z"], 50.0)
    h_crack = st.number_input("Projection verticale de la fissure [mm]", 500.0, 5000.0, D["h_crack"], 10.0)
    b_w = st.number_input("b_w – épaisseur « moyenne » de l'âme [mm]", 100.0, 1000.0, D["b_w"], 10.0)
    k_sb = st.slider("x_eff / x (bloc de contraintes)", 0.6, 1.0, D["k_stress_block"], 0.05)

    with st.expander("Hypothèses du corrigé (avancé)"):
        f_Utd_deff = st.number_input("f_Utd dans d_eff et ω_m [MPa]", 0.0, 15.0, D["f_Utd_deff"], 0.5)
        f_sy = st.number_input("f_sy dans x_U [MPa]", 200.0, 700.0, D["f_sy"], 10.0)
        b_U_omega = st.number_input("Largeur de BFUP dans d_eff et ω_m [m]", 0.1, 10.0, D["b_U_omega"], 0.1)

p = dict(V_d=V_d, a_section=a_section, V_Rsd=V_Rsd, d_sc=d_sc, d_sU=d_sU, d_U=d_U, A_c=A_c, f_cd=f_cd,
         A_sc=A_sc, f_scd=f_scd, h_U=h_U, phi_sU=phi_sU, s_sU=s_sU, n_layers=n_layers, f_sUd=f_sUd,
         f_Utu=f_Utu, f_Uc=f_Uc, k_Uc=k_Uc, b_dowel=b_dowel, alpha=alpha, l_Z=l_Z, h_crack=h_crack,
         b_w=b_w, k_stress_block=k_sb, f_Utd_deff=f_Utd_deff, f_sy=f_sy, b_U_omega=b_U_omega)

r = core.ex3_compute(p)
p = r["p"]
if r["A_U"] <= 0:
    st.error("L'armature occupe plus que la section de la couche de BFUP : vérifier h_U, Ø et l'espacement.")
    st.stop()

# ----------------------------------------------------------------------------
# En-tête et indicateurs
# ----------------------------------------------------------------------------
st.title("Renforcement à l'effort tranchant d'un tablier continu – BFUP armé")
st.markdown("Mécanisme cinématique (borne supérieure, théorie de la plasticité) : écrasement de l'âme + effet goujon "
            "dans la couche de BFUP armé · *Cours « Structures existantes : chapitres choisis », "
            "Applications 8 / A8.2, p. 53-55*")

c1, c2, c3, c4 = st.columns(4)
c1.metric("V_Rcd – âme en béton", f"{r['V_Rcd']:.0f} kN", f"α = {p['alpha']:g}°", delta_color="off", delta_arrow="off")
c2.metric("V_RUd – effet goujon BFUP", f"{r['V_RUd']:.0f} kN", f"m_UR = {r['m_UR']:.0f} kNm/m",
          delta_color="off", delta_arrow="off")
c3.metric("V_Rd = V_Rcd + V_RUd + V_Rsd", f"{r['V_Rd']:.0f} kN",
          f"V_d/V_Rd = {p['V_d']/r['V_Rd']:.2f} – {'OK' if r['ok'] else 'NON'}",
          delta_color="normal" if r["ok"] else "inverse", delta_arrow="off")
if np.isfinite(r["alpha_min"]):
    ok_min = r["V_Rd_min"] >= p["V_d"]
    c4.metric("Minimum admissible (a0 ≤ a_section)", f"{r['V_Rd_min']:.0f} kN",
              f"α_min = {r['alpha_min']:.1f}° – {'OK' if ok_min else 'NON'}",
              delta_color="normal" if ok_min else "inverse", delta_arrow="off")
else:
    c4.metric("Minimum admissible", "—", "l_Z ≥ a_section", delta_color="off", delta_arrow="off")

if r["a0"] > p["a_section"] + 1:
    st.warning(f"Avec α = {p['alpha']:g}°, a0 = {r['a0']/1e3:.2f} m dépasse la distance de la section "
               f"({p['a_section']/1e3:.2f} m) : ce mécanisme n'est pas cinématiquement admissible pour cette section.")
if r["x_U"] >= p["h_U"] / 2:
    st.warning("x_U ≥ h_U/2 : la zone comprimée de la rotule atteint l'armature ; le modèle de rotule n'est plus valable.")


def fmt_table(df, fmts):
    out = df.copy().astype(object)
    for c, f in fmts.items():
        out[c] = [("" if (v is None or (isinstance(v, float) and np.isnan(v))) else f.format(round(v, 6) + 0.0))
                  for v in df[c]]
    return out


def show(fig, name):
    st.pyplot(fig, width="stretch")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    st.download_button("Télécharger la figure (PNG)", buf.getvalue(), file_name=name, mime="image/png", key=name)


GE = r"\geq" if r["ok"] else "<"

tab1, tab2, tab3, tab4, tab5 = st.tabs(["1) Mécanisme et V_Rd", "Âme en béton V_Rcd", "Effet goujon V_RUd",
                                        "Variation de α / étude paramétrique", "3) Discussion et notes"])

# ----------------------------------------------------------------------------
with tab1:
    fig, ax = plt.subplots(1, 2, figsize=(16, 5.2), gridspec_kw=dict(width_ratios=[2.6, 1], wspace=0.2))
    core.draw_mechanism(ax[0], r)
    core.draw_contributions(ax[1], r)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.05)
    show(fig, "ex3_mecanisme.png")
    st.latex(rf"V_{{Rd}} = V_{{Rcd}} + V_{{RUd}} + V_{{Rsd}} = {r['V_Rcd']:.0f} + {r['V_RUd']:.0f} + "
             rf"{p['V_Rsd']:.0f} = {r['V_Rd']:.0f}\ \mathrm{{kN}}\ {GE}\ V_d = {p['V_d']:.0f}\ \mathrm{{kN}}")
    (st.success if r["ok"] else st.error)(
        "Le renforcement apporte une résistance à l'effort tranchant suffisante." if r["ok"]
        else "Résistance à l'effort tranchant insuffisante.")

# ----------------------------------------------------------------------------
with tab2:
    left, right = st.columns([1, 1.2])
    with left:
        st.markdown("**Hauteur statique équivalente et taux mécanique d'armature**")
        rows = [[n, d, Af / 1e3, d * Af / 1e6] for n, d, Af in r["terms"]]
        rows.append(["Σ", np.nan, r["sumAf"] / 1e3, sum(t[1] * t[2] for t in r["terms"]) / 1e6])
        df = pd.DataFrame(rows, columns=["", "d_i [mm]", "A_i·f_i [kN]", "d_i·A_i·f_i [kNm]"])
        st.dataframe(fmt_table(df, {"d_i [mm]": "{:.0f}", "A_i·f_i [kN]": "{:.0f}", "d_i·A_i·f_i [kNm]": "{:.0f}"}),
                     hide_index=True, width="stretch")
        st.caption(f"A_sU = {r['A_sU']:.0f} mm²/m ; A_U = {r['A_U']:.0f} mm²/m ; "
                   f"BFUP pris sur {p['b_U_omega']:g} m avec f_Utd = {p['f_Utd_deff']:g} MPa (corrigé).")
    with right:
        st.latex(rf"d_{{eff}} = \frac{{\sum d_i A_i f_i}}{{\sum A_i f_i}} = {r['d_eff']:.0f}\ \mathrm{{mm}}")
        st.latex(rf"\omega_m = \frac{{\sum A_i f_i}}{{A_c f_{{cd}}}} = \frac{{{r['sumAf']/1e3:.0f}\ \mathrm{{kN}}}}"
                 rf"{{{p['A_c']:.0f}\cdot{p['f_cd']:g}}} = {r['omega']:.3f}")
        st.latex(rf"x = 0.9\,\omega_m\,d_{{eff}} = {r['x']:.0f}\ \mathrm{{mm}},\quad x_{{eff}} = "
                 rf"{p['k_stress_block']:g}\,x = {r['x_eff']:.0f}\ \mathrm{{mm}}")
        st.latex(rf"a_0 = \frac{{{p['h_crack']:.0f}}}{{\tan {p['alpha']:g}^\circ}} + l_Z = {r['a0']/1e3:.2f}\ \mathrm{{m}}")
        st.latex(rf"V_{{Rcd}} = b_w\,\frac{{x_{{eff}}}}{{\sin\alpha}}\,\frac{{f_{{cd}}}}{{2}}\,(1-\cos\alpha) = "
                 rf"{p['b_w']:.0f}\cdot\frac{{{r['x_eff']:.0f}}}{{\sin {p['alpha']:g}^\circ}}\cdot"
                 rf"{p['f_cd']/2:g}\cdot{1-np.cos(np.radians(p['alpha'])):.3f} = {r['V_Rcd']:.0f}\ \mathrm{{kN}}")
        st.caption(f"À 45° : a0 = {r['a0_45']/1e3:.2f} m et V_Rcd = {r['V_Rcd45']:.0f} kN (corrigé : 3.54 m ; 609 kN).")

# ----------------------------------------------------------------------------
with tab3:
    left, right = st.columns([1, 1.2])
    with left:
        fig, ax = plt.subplots(figsize=(6, 4.2))
        core.draw_hinge(ax, r)
        fig.tight_layout()
        show(fig, "ex3_rotule.png")
    with right:
        st.markdown("**Rotule plastique dans la couche de BFUP armé**")
        st.latex(rf"x_U = \frac{{\rho_{{sU}}\,h_U\,f_{{sy}}}}{{{p['k_Uc']:g}\,f_{{Uc}}}} = "
                 rf"\frac{{{r['rho']:.4f}\cdot{p['h_U']:.0f}\cdot{p['f_sy']:.0f}}}{{{p['k_Uc']*p['f_Uc']:.0f}}}"
                 rf" = {r['x_U']:.1f}\ \mathrm{{mm}}")
        st.latex(rf"m_{{UR}} = f_{{sd}}\,\rho_{{sU}}\,h_U\left(\tfrac{{h_U}}{{2}}-\tfrac{{x_U}}{{2}}\right) + "
                 rf"f_{{Utu}}\,(h_U-x_U)\left(\tfrac{{h_U}}{{2}}-x_U\right)")
        st.latex(rf"m_{{UR}} = {r['m_s']:.1f} + {r['m_U']:.1f} = {r['m_UR']:.1f}\ \mathrm{{kNm/m}}")
        st.latex(rf"V_{{RUd}} = \frac{{2\,m_{{UR}}}}{{l_Z}}\,b = \frac{{2\cdot{r['m_UR']:.1f}}}{{{p['l_Z']/1e3:g}}}"
                 rf"\cdot{p['b_dowel']/1e3:g} = {r['V_RUd']:.0f}\ \mathrm{{kN}}")
        st.caption(f"La part de l'armature ({r['m_s']/r['m_UR']*100:.0f} % de m_UR) domine ; "
                   "remonter la nappe ou augmenter son diamètre est le levier principal.")

# ----------------------------------------------------------------------------
with tab4:
    fig, ax = plt.subplots(figsize=(11, 4))
    core.draw_alpha(ax, r)
    fig.tight_layout()
    show(fig, "ex3_alpha.png")
    st.caption("Méthode cinématique : chaque α donne une borne supérieure ; la résistance est la plus faible valeur "
               "parmi les mécanismes admissibles (a0 ≤ distance de la section).")

    st.markdown("**Étude paramétrique**")
    PARAMS = {
        "h_U – épaisseur BFUP [mm]": ("h_U", 60.0, 250.0),
        "Ø A_sU [mm]": ("phi_sU", 10.0, 32.0),
        "Espacement A_sU [mm]": ("s_sU", 60.0, 250.0),
        "l_Z – distance entre rotules [mm]": ("l_Z", 600.0, 3000.0),
        "b_w – épaisseur de l'âme [mm]": ("b_w", 150.0, 600.0),
        "f_cd – béton [MPa]": ("f_cd", 10.0, 40.0),
        "V_Rsd – étriers + précontrainte [kN]": ("V_Rsd", 0.0, 2000.0),
    }
    a, b = st.columns([1, 2.2])
    with a:
        lab = st.selectbox("Paramètre", list(PARAMS))
        key, lo, hi = PARAMS[lab]
        rng = st.slider("Plage", lo, hi, (lo, hi))
        use_min = st.checkbox("Utiliser le minimum admissible sur α", value=False)
    vals = np.linspace(rng[0], rng[1], 41)
    rows = []
    for v in vals:
        q = dict(p)
        q[key] = v
        rr = core.ex3_compute(q)
        if rr["A_U"] <= 0:
            rows.append((v, np.nan, np.nan, np.nan))
            continue
        if use_min and np.isfinite(rr["alpha_min"]):
            vrc = core.VRc(rr["p"], rr["x_eff"], rr["alpha_min"])
            rows.append((v, vrc, rr["V_RUd"], vrc + rr["V_RUd"] + rr["p"]["V_Rsd"]))
        else:
            rows.append((v, rr["V_Rcd"], rr["V_RUd"], rr["V_Rd"]))
    o = np.array(rows, dtype=float)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(o[:, 0], o[:, 3], color="k", lw=2, label="V_Rd")
    ax.plot(o[:, 0], o[:, 1], color=core.C_COMP, label="V_Rcd")
    ax.plot(o[:, 0], o[:, 2], color=core.C_TENS, label="V_RUd")
    ax.axhline(p["V_d"], color="k", ls="--", lw=0.8, label="V_d")
    ax.axvline(p[key], color="0.6", ls=":", lw=0.9)
    ax.set_xlabel(lab)
    ax.set_ylabel("[kN]")
    ax.legend(frameon=False, fontsize=8, ncol=4)
    fig.tight_layout()
    with b:
        st.pyplot(fig, width="stretch")
    plt.close(fig)
    st.download_button("Télécharger les résultats (CSV)",
                       pd.DataFrame(o, columns=[key, "V_Rcd", "V_RUd", "V_Rd"]).to_csv(index=False),
                       file_name=f"ex3_parametrique_{key}.csv", mime="text/csv")

# ----------------------------------------------------------------------------
with tab5:
    st.markdown(f"""
**Discussion (point 3 du cours)**
- La méthode cinématique donne une borne supérieure : il faut varier α et retenir la plus faible valeur de V_Rd.
  Parmi les mécanismes dont la fissure reste entre l'appui et la section (a0 ≤ {p['a_section']/1e3:.1f} m),
  le minimum est obtenu pour α = {r['alpha_min']:.1f}° : V_Rd = {r['V_Rd_min']:.0f} kN.
- Leviers pour augmenter V_Rd : épaissir la couche de BFUP, utiliser des barres de plus grand diamètre placées
  plus haut dans la zone tendue (effet goujon), ou renforcer au BFUP la partie inférieure comprimée de la poutre
  (V_Rcd).

**Hypothèses du modèle**
- V_Rcd : écrasement de la partie comprimée de l'âme sur la hauteur x_eff le long de la fissure critique,
  contrainte f_cd/2 sur b_w « moyen » (moyenne âme 18 cm / talon 60 cm).
- V_RUd : deux rotules plastiques dans la couche de BFUP armé, distantes de l_Z, mobilisées sur la largeur b.
  Contrainte de compression limitée à {p['k_Uc']*100:.0f} % de f_Uc lorsque l'élongation atteint 2‰.
- V_Rsd : composante verticale des étriers et des deux câbles de précontrainte, donnée.
- A_sU, A_U et ρ_sU sont calculés à partir de Ø, de l'espacement et du nombre de nappes (corrigé : 6280 mm²,
  114 000 mm², 5.5 %).

**Écarts relevés dans le corrigé du cours**
- d_eff : la formule affiche 2040 mm pour l'armature du béton, mais le résultat (9 709 908) correspond à
  d_sc = 2360 mm. La valeur 2040 mm est reprise ici comme projection verticale de la fissure pour a0.
- V_Rcd : le corrigé utilise x = 490 mm, soit ≈ 0.85·x (x = 573 mm) ; interprété ici comme un bloc de
  contraintes (réglage « x_eff / x »).
- f_Utd = 7 MPa dans d_eff et ω_m, contre 6 MPa en A8.1 et dans la rotule ; f_sy = 500 MPa dans x_U mais
  f_sd = 435 MPa dans m_UR. Ces valeurs sont modifiables dans « Hypothèses du corrigé (avancé) ».
- Le BFUP est pris sur 1 m dans ω_m alors que l'effet goujon mobilise b = 2.5 m.
""")
