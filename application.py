import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import streamlit.components.v1 as components

# --- Configuration de la page ---
st.set_page_config(page_title="Dashboard Data Science", layout="wide")

# --- CSS POUR L'IMPRESSION ---
st.markdown("""
<style>
@media print {
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { margin: 0 !important; padding: 0 !important; }
    .page-break { page-break-before: always; }
    header { display: none !important; }
    footer { display: none !important; }
    .no-print { display: none !important; }
}
</style>
""", unsafe_allow_html=True)

# --- 1. Chargement des données ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "data", "ds_salaries.csv")
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier introuvable à : {file_path}")
    
    # Nettoyage et traduction
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
    st.error(f"Erreur critique : {e}")
    st.stop()

# --- 2. Sidebar ---

# A. LOGO
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "images", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)

# B. MODE RAPPORT
st.sidebar.header("Export PDF")
report_mode = st.sidebar.toggle("Mode Rapport (Impression)", help="Activez pour tout afficher et imprimer.")

# C. PERSONNALISATION
st.sidebar.markdown("---")
st.sidebar.subheader("Style")
theme_choice = st.sidebar.selectbox("Thème graphique :", ["Standard", "Sombre (Dark)", "Vif (Plotly)", "Classique (Ggplot)"])

template_map = {"Standard": "seaborn", "Sombre (Dark)": "plotly_dark", "Vif (Plotly)": "plotly", "Classique (Ggplot)": "ggplot2"}
selected_template = template_map[theme_choice]

# D. FILTRES
st.sidebar.markdown("---")
st.sidebar.header("Filtres")
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

# --- 3. Fonctions Graphiques (Sans Emojis) ---

def show_trends(data, template):
    st.subheader("Évolution des Salaires (Moyenne par Année)")
    df_trend = data.groupby('work_year')['salary_in_usd'].mean().reset_index()
    fig_line = px.line(df_trend, x='work_year', y='salary_in_usd', markers=True,
                       title="Progression du Salaire Moyen (USD)", template=template)
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Répartition Globale")
        fig_hist = px.histogram(data, x="salary_in_usd", nbins=30, title="Histogramme des Salaires", template=template)
        fig_hist.add_vline(x=data['salary_in_usd'].median(), line_dash="dash", line_color="red", annotation_text="Médiane")
        st.plotly_chart(fig_hist, use_container_width=True)
    with c2:
        st.subheader("Par Expérience")
        fig_box = px.box(data, x="experience_level", y="salary_in_usd", color="experience_level", 
                         title="Comparaison par Niveau", template=template,
                         category_orders={"experience_level": ["Junior (EN)", "Intermédiaire (MI)", "Senior (SE)", "Expert (EX)"]})
        st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("---")
    
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top 15 Métiers")
        df_jobs = data.groupby('job_title')['salary_in_usd'].mean().sort_values(ascending=False).head(15).reset_index()
        fig_bar = px.bar(df_jobs, x='salary_in_usd', y='job_title', orientation='h', color='salary_in_usd', 
                         title="Métiers les mieux payés (Moyenne)", template=template)
        st.plotly_chart(fig_bar, use_container_width=True)
    with c4:
        st.subheader("Impact du Télétravail")
        data['remote_label'] = data['remote_ratio'].map({0: 'Présentiel', 50: 'Hybride', 100: 'Full Remote'})
        fig_remote = px.box(data, x="remote_label", y="salary_in_usd", title="Salaire vs Mode de travail", 
                            color="remote_label", template=template,
                            category_orders={"remote_label": ["Présentiel", "Hybride", "Full Remote"]})
        st.plotly_chart(fig_remote, use_container_width=True)

def show_map(data, template):
    st.subheader("Carte Mondiale des Salaires")
    df_map = data.groupby('iso_alpha')['salary_in_usd'].mean().reset_index()
    fig_map = px.choropleth(df_map, locations="iso_alpha", locationmode="ISO-3", color="salary_in_usd", 
                            hover_name="iso_alpha", color_continuous_scale="Plasma", 
                            title="Salaire Moyen par Pays (USD)", template=template)
    st.plotly_chart(fig_map, use_container_width=True)
    
    # PARTIE SUNBURST SUPPRIMÉE ICI COMME DEMANDÉ

def show_correlations(data, template):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Matrice de Corrélation")
        numeric_df = data.select_dtypes(include=[np.number]).drop(columns=['salary'], errors='ignore')
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r", template=template)
            st.plotly_chart(fig_corr, use_container_width=True)
    with c2:
        st.subheader("Répartition des Contrats")
        df_pie = data['employment_type'].value_counts().reset_index()
        df_pie.columns = ['Type', 'Count']
        fig_pie = px.pie(df_pie, values='Count', names='Type', hole=0.4, title="Types de contrats", template=template)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    
    st.subheader("Salaire par Taille d'Entreprise")
    df_size = data.groupby('company_size')['salary_in_usd'].median().reset_index()
    size_order = {'S': 1, 'M': 2, 'L': 3}
    df_size['order'] = df_size['company_size'].map(size_order)
    df_size = df_size.sort_values('order')
    fig_size = px.bar(df_size, x='company_size', y='salary_in_usd', title="Salaire Médian par Taille (S/M/L)", 
                      text_auto='.2s', template=template, color='salary_in_usd')
    st.plotly_chart(fig_size, use_container_width=True)

def show_data(data):
    st.subheader("Données Brutes")
    st.dataframe(data)

# --- 4. Corps de la page ---
st.title("Dashboard : Salaires Data Science")

if df_selection.empty:
    st.warning("Aucune donnée ne correspond aux filtres.")
    st.stop()

# KPIs
c1, c2, c3 = st.columns(3)
with c1: st.metric("Nombre de profils", f"{len(df_selection)}")
with c2: st.metric("Salaire Médian", f"{df_selection['salary_in_usd'].median():,.0f} $")
with c3: st.metric("Salaire Moyen", f"{df_selection['salary_in_usd'].mean():,.0f} $")
st.markdown("---")

# LOGIQUE PRINCIPALE : ONGLETS OU RAPPORT
if report_mode:
    # --- MODE RAPPORT (Impression PDF) ---
    st.info("Astuce : Si l'impression ne se lance pas, vérifiez que votre navigateur ne bloque pas les pop-ups.")

    if st.button("Lancer l'impression PDF"):
        js = """
        <script>
            function autoPrint() {
                window.parent.document.title = "Rapport_Data_Science";
                window.parent.print();
            }
            setTimeout(autoPrint, 500);
        </script>
        """
        components.html(js, height=0, width=0)

    st.markdown("---")

    st.header("1. Tendances & Évolution")
    show_trends(df_selection, selected_template)
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    st.header("2. Géographie")
    show_map(df_selection, selected_template)
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    st.header("3. Analyses Avancées")
    show_correlations(df_selection, selected_template)
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)
    
    st.header("4. Données")
    show_data(df_selection)

else:
    # --- MODE CLASSIQUE (Onglets) ---
    tab1, tab2, tab3, tab4 = st.tabs(["Tendances", "Géographie", "Analyses", "Données"])
    
    with tab1: show_trends(df_selection, selected_template)
    with tab2: show_map(df_selection, selected_template)
    with tab3: show_correlations(df_selection, selected_template)
    with tab4:
        show_data(df_selection)
        csv = df_selection.to_csv(index=False).encode('utf-8')
        st.download_button(label="Télécharger CSV", data=csv, file_name='salaries_filtered.csv', mime='text/csv')