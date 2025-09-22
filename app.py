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
        # Lire l'onglet brut (même si cellules fusionnées)
        df = pd.read_excel(uploaded_file, sheet_name=sheet, header=None, engine="openpyxl")

        # Repérer où commence le tableau (colonne ≈ "Nom")
        try:
            start_row = df.index[df.iloc[:, 9] == "Nom"][0]
        except IndexError:
            continue

        # Relire proprement à partir du tableau
        df_clean = pd.read_excel(uploaded_file, sheet_name=sheet, skiprows=start_row+1, engine="openpyxl")

        if "Nom" in df_clean.columns and "Prénom" in df_clean.columns:
            # Reformatage long : un enregistrement par jour
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
    # 2. Interface de filtrage
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
    # 3. Affichage
    # ---------------------------
    st.write("### Planning filtré")
    st.dataframe(filtered)

    # Export CSV
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger en CSV", data=csv, file_name="planning_filtré.csv", mime="text/csv")
else:
    st.error("Aucune donnée exploitable trouvée dans le fichier.")
