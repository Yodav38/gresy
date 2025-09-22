import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("C:/Users/davra/gresy/Planning GRE_SY 2025 (v11).xlsx")

if uploaded_file:
xls = pd.ExcelFile(uploaded_file)
all_data = []

for sheet in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet, header=None)

    # Repérer où commence le tableau (Nom, Prénom, etc.)
    try:
        start_row = df.index[df.iloc[:, 9] == "Nom"][0]  # Colonne 9 ≈ "Nom"
    except IndexError:
        continue

    df_clean = pd.read_excel(xls, sheet_name=sheet, skiprows=start_row+1)

    if "Nom" in df_clean.columns and "Prénom" in df_clean.columns:
        # Reformatage long : un enregistrement par jour
        id_vars = ["Nom", "Prénom"]
        value_vars = [c for c in df_clean.columns if c not in id_vars]

        df_melt = df_clean.melt(id_vars=id_vars, value_vars=value_vars,
                                var_name="Date", value_name="Activité")
        df_melt["Mois"] = sheet
        all_data.append(df_melt)

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

    # Export possible
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Télécharger en CSV", data=csv, file_name="planning_filtré.csv", mime="text/csv")
