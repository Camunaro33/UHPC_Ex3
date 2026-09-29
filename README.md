# BFUP armé – effort tranchant : applet de l'exemple 3 (A8.2)

Applet Streamlit qui reproduit l'application 8 / A8.2 (p. 53-55) du cours « Structures existantes : chapitres choisis » : résistance ultime à l'effort tranchant d'un tablier continu renforcé par une couche de BFUP armé, par la méthode cinématique (borne supérieure de la théorie de la plasticité).

V_Rd = V_Rcd + V_RUd + V_Rsd, avec :

- **V_Rcd** – écrasement de la partie comprimée de l'âme en béton le long de la fissure critique (hauteur statique équivalente d_eff, taux mécanique ω_m, hauteur comprimée x) ;
- **V_RUd** – effet goujon : deux rotules plastiques dans la couche de BFUP armé, distantes de l_Z ;
- **V_Rsd** – étriers et composante verticale de la précontrainte (donnée).

Onglets :

- **1) Mécanisme et V_Rd** : schéma du mécanisme (fissure, rotules, a0), contributions et vérification V_Rd ≥ V_d.
- **Âme en béton V_Rcd** : tableau d_eff, ω_m, x, a0 et V_Rcd.
- **Effet goujon V_RUd** : section de la rotule, x_U, m_UR et V_RUd.
- **Variation de α / étude paramétrique** : V_Rd(α) avec la zone des mécanismes non admissibles (a0 > distance de la section) et le minimum admissible ; influence de h_U, de l'armature, de l_Z, de b_w, de f_cd ou de V_Rsd, avec export CSV.
- **3) Discussion et notes** : leviers d'amélioration, hypothèses, écarts relevés dans le corrigé.

Toutes les entrées sont modifiables dans la barre latérale ; les hypothèses propres au corrigé sont regroupées dans « Hypothèses du corrigé (avancé) ».

## Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Pousser ce dossier dans un dépôt GitHub.
2. Sur [share.streamlit.io](https://share.streamlit.io) : **Create app**, puis indiquer l'URL du fichier, au format
   `https://github.com/<utilisateur>/<depot>/blob/main/app.py`.
3. **Deploy**. L'applet est redéployée à chaque `git push`.

## Structure

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit |
| `bfup_ex3.py` | Calculs et fonctions de tracé ; utilisable seul dans Spyder (`python bfup_ex3.py`) |
| `test_app.py` | Tests : valeurs du corrigé et exécution de l'applet (`pytest`) |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème |

## Écarts relevés dans le corrigé du cours

- d_eff : la formule affiche 2040 mm pour l'armature du béton, mais le résultat (9 709 908) correspond à d_sc = 2360 mm ; 2040 mm est repris comme projection verticale de la fissure pour a0.
- V_Rcd utilise x = 490 mm ≈ 0.85·x (x = 573 mm), interprété comme un bloc de contraintes.
- f_Utd = 7 MPa dans d_eff et ω_m, contre 6 MPa en A8.1 et dans la rotule ; f_sy = 500 MPa dans x_U mais f_sd = 435 MPa dans m_UR.
- Le BFUP est pris sur 1 m dans ω_m alors que l'effet goujon mobilise 2.5 m.
- Le corrigé retient α = 35° ; le minimum parmi les mécanismes admissibles est à α = 34.2° (V_Rd = 1869 kN), ce qui ne change pas la conclusion.

Unités internes : N, mm, MPa ; résultats en kN et kNm/m.
