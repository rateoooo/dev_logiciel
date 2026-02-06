import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Data Science", layout="wide")

# --- 1. Chargement et Préparation des données ---
@st.cache_data
def load_data():
    # Récupère le dossier où se trouve ce script (projet_notebook)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construit le chemin vers le dossier 'data'
    file_path = os.path.join(current_dir, "data", "ds_salaries.csv")
    
    # Chargement CSV
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # On relance l'erreur pour qu'elle soit attrapée plus bas avec un message clair
        raise FileNotFoundError(f"Fichier introuvable à : {file_path}")
    
    # Nettoyage
    df['experience_level'] = df['experience_level'].replace({
        'EN': 'Junior (EN)', 'MI': 'Intermédiaire (MI)', 'SE': 'Senior (SE)', 'EX': 'Expert (EX)'
    })
    df['employment_type'] = df['employment_type'].replace({
        'FT': 'Temps plein', 'PT': 'Temps partiel', 'CT': 'Contrat', 'FL': 'Freelance'
    })
    
    # Mapping ISO pour la carte
    iso_map = {
        'ES': 'ESP', 'US': 'USA', 'CA': 'CAN', 'DE': 'DEU', 'GB': 'GBR', 'NG': 'NGA', 
        'IN': 'IND', 'HK': 'HKG', 'NL': 'NLD', 'CH': 'CHE', 'CF': 'CAF', 'FR': 'FRA', 
        'FI': 'FIN', 'UA': 'UKR', 'IE': 'IRL', 'IL': 'ISR', 'GH': 'GHA', 'CO': 'COL', 
        'SG': 'SGP', 'AU': 'AUS', 'SE': 'SWE', 'SI': 'SVN', 'MX': 'MEX', 'BR': 'BRA', 
        'PT': 'PRT', 'RU': 'RUS', 'TH': 'THA', 'HR': 'HRV', 'VN': 'VNM', 'EE': 'EST', 
        'AM': 'ARM', 'BA': 'BIH', 'KE': 'KEN', 'GR': 'GRC', 'MK': 'MKD', 'LV': 'LVA', 
        'RO': 'ROU', 'PK': 'PAK', 'IT': 'ITA', 'MA': 'MAR', 'PL': 'POL', 'AL': 'ALB', 
        'AR': 'ARG', 'LT': 'LTU', 'AS': 'ASM', 'CR': 'CRI', 'IR': 'IRN', 'BS': 'BHS', 
        'HU': 'HUN', 'AT': 'AUT', 'SK': 'SVK', 'CZ': 'CZE', 'TR': 'TUR', 'PR': 'PRI', 
        'DK': 'DNK', 'BO': 'BOL', 'PH': 'PHL', 'BE': 'BEL', 'ID': 'IDN', 'EG': 'EGY', 
        'AE': 'ARE', 'LU': 'LUX', 'MY': 'MYS', 'HN': 'HND', 'JP': 'JPN', 'DZ': 'DZA', 
        'IQ': 'IRQ', 'CN': 'CHN', 'NZ': 'NZL', 'CL': 'CHL', 'MD': 'MDA', 'MT': 'MLT'
    }
    df['iso_alpha'] = df['company_location'].map(iso_map)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    st.stop()

# --- 2. Sidebar (Logo, Thème & Filtres) ---

# A. LOGO (Toujours dans le dossier 'images')
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "images", "logo.png")

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)

# B. SÉLECTEUR DE THÈME GRAPHIQUE
st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Personnalisation")
theme_choice = st.sidebar.selectbox(
    "Style des graphiques :",
    ["Standard", "Sombre (Dark)", "Vif (Plotly)", "Classique (Ggplot)"]
)

template_map = {
    "Standard": "seaborn",
    "Sombre (Dark)": "plotly_dark",
    "Vif (Plotly)": "plotly",
    "Classique (Ggplot)": "ggplot2"
}
selected_template = template_map[theme_choice]

# C. FILTRES
st.sidebar.markdown("---")
st.sidebar.header("🎚️ Filtres Données")

years = sorted(df['work_year'].unique())
selected_years = st.sidebar.multiselect("Année", years, default=years)

experiences = df['experience_level'].unique()
selected_experience = st.sidebar.multiselect("Expérience", experiences, default=experiences)

locations = sorted(df['company_location'].unique())
selected_locations = st.sidebar.multiselect("Pays (Code)", locations, default=locations)

# Application des filtres
df_selection = df[
    (df['work_year'].isin(selected_years)) &
    (df['experience_level'].isin(selected_experience)) &
    (df['company_location'].isin(selected_locations))
]

# --- 3. Corps de la page ---
st.title("📊 Dashboard : Salaires Data Science")

if df_selection.empty:
    st.warning("Aucune donnée ne correspond aux filtres.")
    st.stop()

# KPIs
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Nombre de profils", f"{len(df_selection)}")
with c2:
    st.metric("Salaire Médian", f"{df_selection['salary_in_usd'].median():,.0f} $")
with c3:
    st.metric("Salaire Moyen", f"{df_selection['salary_in_usd'].mean():,.0f} $")

st.markdown("---")

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["📈 Tendances", "🌍 Carte", "🔗 Corrélations", "📋 Données"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribution des Salaires")
        fig_hist = px.histogram(df_selection, x="salary_in_usd", nbins=30, 
                                title="Répartition des salaires (USD)",
                                template=selected_template)
        fig_hist.add_vline(x=df_selection['salary_in_usd'].median(), line_dash="dash", line_color="red")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("Salaire par Niveau d'Expérience")
        fig_box = px.box(df_selection, x="experience_level", y="salary_in_usd", 
                         color="experience_level", 
                         title="Distribution par Expérience",
                         template=selected_template,
                         category_orders={"experience_level": ["Junior (EN)", "Intermédiaire (MI)", "Senior (SE)", "Expert (EX)"]})
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("🏆 Top 15 Métiers")
    df_jobs = df_selection.groupby('job_title')['salary_in_usd'].mean().sort_values(ascending=False).head(15).reset_index()
    fig_bar = px.bar(df_jobs, x='salary_in_usd', y='job_title', orientation='h', 
                     color='salary_in_usd', title="Top 15 Job Titles (Salaire Moyen)",
                     template=selected_template)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🏠 Impact du Télétravail (Box Plot)")
    df_selection['remote_label'] = df_selection['remote_ratio'].map({0: 'Présentiel', 50: 'Hybride', 100: 'Full Remote'})
    fig_remote = px.box(df_selection, x="remote_label", y="salary_in_usd", 
                        title="Salaire vs Télétravail", color="remote_label",
                        template=selected_template,
                        category_orders={"remote_label": ["Présentiel", "Hybride", "Full Remote"]})
    st.plotly_chart(fig_remote, use_container_width=True)

with tab2:
    st.subheader("Carte mondiale des salaires")
    df_map = df_selection.groupby('iso_alpha')['salary_in_usd'].mean().reset_index()
    
    fig_map = px.choropleth(df_map, locations="iso_alpha", locationmode="ISO-3",
                            color="salary_in_usd", hover_name="iso_alpha",
                            color_continuous_scale="Plasma",
                            title="Salaire Moyen par Pays (USD)",
                            template=selected_template)
    st.plotly_chart(fig_map, use_container_width=True)

with tab3:
    st.subheader("🔗 Matrice de Corrélation")
    numeric_df = df_selection.select_dtypes(include=[np.number]).drop(columns=['salary'], errors='ignore')
    
    if not numeric_df.empty:
        corr_matrix = numeric_df.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                             color_continuous_scale="RdBu_r",
                             title="Heatmap des Corrélations",
                             template=selected_template)
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.write("Pas assez de données numériques.")

    st.subheader("🏢 Salaire par Taille d'Entreprise")
    df_size = df_selection.groupby('company_size')['salary_in_usd'].median().reset_index()
    size_order = {'S': 1, 'M': 2, 'L': 3}
    df_size['order'] = df_size['company_size'].map(size_order)
    df_size = df_size.sort_values('order')
    
    fig_size = px.bar(df_size, x='company_size', y='salary_in_usd', 
                      title="Salaire Médian par Taille",
                      text_auto='.2s',
                      template=selected_template)
    st.plotly_chart(fig_size, use_container_width=True)

with tab4:
    st.subheader("🔍 Données Brutes")
    st.dataframe(df_selection)
    csv = df_selection.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Télécharger CSV", data=csv, file_name='salaries_filtered.csv', mime='text/csv')