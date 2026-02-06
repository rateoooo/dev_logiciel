import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Configuration de la page (doit être la première commande Streamlit)
st.set_page_config(page_title="Dashboard Data Science Salaries", layout="wide", page_icon="💰")

# --- 1. Chargement des données ---
@st.cache_data
def load_data():
    # Gestion robuste du chemin de fichier
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "ds_salaries.csv")
    
    df = pd.read_csv(file_path)
    
    # Nettoyage / Renommage pour plus de clarté dans les graphiques
    df['experience_level'] = df['experience_level'].replace({
        'EN': 'Junior (EN)', 'MI': 'Intermédiaire (MI)', 'SE': 'Senior (SE)', 'EX': 'Expert (EX)'
    })
    df['employment_type'] = df['employment_type'].replace({
        'FT': 'Temps plein', 'PT': 'Temps partiel', 'CT': 'Contrat', 'FL': 'Freelance'
    })
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Le fichier 'ds_salaries.csv' est introuvable. Vérifiez son emplacement.")
    st.stop()

# --- 2. Sidebar (Filtres Globaux) ---
st.sidebar.header("🎚️ Filtres")
st.sidebar.markdown("Ces filtres s'appliquent à **toute** la page.")

# Filtre Année
years = sorted(df['work_year'].unique())
selected_years = st.sidebar.multiselect("Année", years, default=years)

# Filtre Niveau d'expérience
experiences = df['experience_level'].unique()
selected_experience = st.sidebar.multiselect("Expérience", experiences, default=experiences)

# Filtre Localisation (Pays)
locations = sorted(df['company_location'].unique())
selected_locations = st.sidebar.multiselect("Pays de l'entreprise", locations, default=locations)

# Application des filtres (Logique type SQL WHERE)
df_selection = df[
    (df['work_year'].isin(selected_years)) &
    (df['experience_level'].isin(selected_experience)) &
    (df['company_location'].isin(selected_locations))
]

# --- 3. Titre et KPIs ---
st.title("📊 Dashboard : Salaires en Data Science")
st.markdown("Analyse exploratoire des salaires selon l'expérience, le poste et la géographie.")

# Vérification si des données existent après filtrage
if df_selection.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# Affichage des KPIs en colonnes
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Nombre de profils", f"{len(df_selection)}")
with c2:
    med_salary = df_selection['salary_in_usd'].median()
    st.metric("Salaire Médian (USD)", f"{med_salary:,.0f} $")
with c3:
    avg_salary = df_selection['salary_in_usd'].mean()
    st.metric("Salaire Moyen (USD)", f"{avg_salary:,.0f} $")

st.markdown("---")

# --- 4. Analyses Univariées et Bivariées ---

# Organisation en onglets pour alléger la page
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendances & Distributions", "🌍 Géographie", "🔗 Corrélations & Détails", "📋 Données Brutes"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution des Salaires")
        fig_hist = px.histogram(df_selection, x="salary_in_usd", nbins=30, title="Répartition des salaires (USD)",
                                color_discrete_sequence=['#636EFA'])
        fig_hist.add_vline(x=med_salary, line_dash="dash", line_color="red", annotation_text="Médiane")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("Salaire par Niveau d'Expérience")
        fig_box = px.box(df_selection, x="experience_level", y="salary_in_usd", 
                         color="experience_level", 
                         title="Distribution par Expérience",
                         category_orders={"experience_level": ["Junior (EN)", "Intermédiaire (MI)", "Senior (SE)", "Expert (EX)"]})
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("🏆 Top 15 des métiers les mieux payés (Moyenne)")
    # Groupby (SQL: GROUP BY job_title)
    df_jobs = df_selection.groupby('job_title')['salary_in_usd'].mean().sort_values(ascending=False).head(15).reset_index()
    fig_bar = px.bar(df_jobs, x='salary_in_usd', y='job_title', orientation='h', 
                     color='salary_in_usd', title="Top 15 Job Titles",
                     color_continuous_scale='Viridis')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Ajout : Impact du Télétravail (Violin plot pour voir la densité)
    st.subheader("🏠 Impact du Télétravail sur le Salaire")
    df_selection['remote_label'] = df_selection['remote_ratio'].map({0: 'Présentiel', 50: 'Hybride', 100: 'Full Remote'})
    fig_remote = px.violin(df_selection, x="remote_label", y="salary_in_usd", box=True, points="all",
                           title="Salaire vs Télétravail", color="remote_label")
    st.plotly_chart(fig_remote, use_container_width=True)

with tab2:
    st.subheader("Carte mondiale des salaires moyens")
    # Agrégation par pays
    df_map = df_selection.groupby('company_location')['salary_in_usd'].mean().reset_index()
    
    fig_map = px.choropleth(df_map, locations="company_location", locationmode="ISO-3",
                            color="salary_in_usd", hover_name="company_location",
                            color_continuous_scale="Plasma",
                            title="Salaire Moyen par Pays (USD)")
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.info("Note : Les codes pays utilisent la norme ISO-3 (ex: US, FR, DE).")

with tab3:
    st.subheader("🔗 Matrice de Corrélation")
    st.markdown("Analyse des relations entre les variables numériques (ex: Année, Salaire, Télétravail).")
    
    # Sélection des colonnes numériques uniquement
    numeric_df = df_selection.select_dtypes(include=[np.number])
    # On retire les colonnes peu pertinentes pour la corrélation brute (ex: salaire en monnaie locale qui fausse tout)
    numeric_df = numeric_df.drop(columns=['salary'], errors='ignore')
    
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr()
        
        # Heatmap avec Plotly pour l'interactivité
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r",
                             title="Heatmap des Corrélations")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.write("Pas assez de données numériques pour la corrélation.")

    # Analyse croisée Taille Entreprise / Salaire
    st.subheader("🏢 Salaire par Taille d'Entreprise")
    df_size = df_selection.groupby('company_size')['salary_in_usd'].median().reset_index()
    # Ordre logique des tailles
    size_order = {'S': 1, 'M': 2, 'L': 3}
    df_size['order'] = df_size['company_size'].map(size_order)
    df_size = df_size.sort_values('order')
    
    fig_size = px.bar(df_size, x='company_size', y='salary_in_usd', 
                      title="Salaire Médian par Taille (S=Small, M=Medium, L=Large)",
                      text_auto='.2s')
    st.plotly_chart(fig_size, use_container_width=True)

with tab4:
    st.subheader("🔍 Exploration des données brutes")
    st.write(f"Affichage des {len(df_selection)} lignes filtrées.")
    st.dataframe(df_selection)
    
    # Bouton de téléchargement
    csv = df_selection.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données filtrées (CSV)",
        data=csv,
        file_name='salaries_filtered.csv',
        mime='text/csv',
    )