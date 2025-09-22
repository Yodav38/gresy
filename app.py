import streamlit as st
import pandas as pd

# Upload du fichier
uploaded_file = st.file_uploader("Planning GRE_SY 2025 (v11)", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    all_data = []

# Charger la liste des feuilles
xls = pd.ExcelFile(uploaded_file, engine="openpyxl")

for sheet in xls.sheet_names:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=sheet, header=None, engine="openpyxl")

        # Repérer où commence le tableau (colonne ≈ "Nom")
        try:
            start_row = df.index[df.iloc[:, 9] == "Nom"][0]
        except IndexError:
            continue

        df_clean = pd.read_excel(uploaded_file, sheet_name=sheet, skiprows=start_row+1, engine="openpyxl")

        if "Nom" in df_clean.columns and "Prénom" in df_clean.columns:
            id_vars = ["Nom", "Prénom"]
            value_vars = [c for c in df_clean.columns if c not in id_vars]

            df_melt = df_clean.melt(id_vars=id_vars, value_vars=value_vars,
                                    var_name="Date", value_name="Activité")
            df_melt["Mois"] = sheet
            all_data.append(df_melt)

    except Exception as e:
        st.warning(f"⚠️ Impossible de lire l’onglet {sheet} : {e}")
        continue

if all_data:
    planning = pd.concat(all_data, ignore_index=True)

    # ---------------------------
    # Filtres
    # ---------------------------
    st.sidebar.header("Filtres")
    personnes = planning["Nom"].dropna().unique()
    mois = planning["Mois"].unique()

    selected_personne = st.sidebar.selectbox("Personne", ["Toutes"] + list(personnes))
    selected_mois = st.sidebar.selectbox("Mois", ["Tous"] + list(mois))

    filtered = planning.copy()
    if selected_personne != "Toutes":
        filtered = filtered[filtered["Nom"] == selected_personne]
    if selected_mois != "Tous":
        filtered = filtered[filtered["Mois"] == selected_mois]

    # ---------------------------
    # Affichage style calendrier
    # ---------------------------
    st.write("### Vue calendrier")

    if not filtered.empty:
        # Pivot pour recréer une grille
        try:
            cal = filtered.pivot_table(
                index=["Nom", "Prénom"], 
                columns="Date", 
                values="Activité", 
                aggfunc=lambda x: " / ".join(str(v) for v in x if pd.notna(v))
            ).fillna("")

            # Trier les colonnes par ordre chronologique si ce sont des nombres
            try:
                cal = cal[sorted(cal.columns, key=lambda x: int(str(x)) if str(x).isdigit() else str(x))]
            except:
                pass

            st.dataframe(cal)
        except Exception as e:
            st.error(f"Impossible d’afficher la vue calendrier : {e}")

    # ---------------------------
    # Export CSV
    # ---------------------------
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger en CSV", data=csv, file_name="planning_filtré.csv", mime="text/csv")
else:
    st.error("Aucune donnée exploitable trouvée dans le fichier.")

