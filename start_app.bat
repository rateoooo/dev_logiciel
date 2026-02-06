@echo off
:: Cette commande permet de se placer automatiquement dans le dossier où se trouve ce fichier .bat
:: Donc ici : C:\IUT_2026\dev_logiciel\projet_notebook
cd /d "%~dp0"

echo ==================================================
echo      Lancement du Dashboard depuis projet_notebook
echo ==================================================
echo.

:: Lancement de Streamlit
python -m streamlit run application.py

:: Si ça plante, on garde la fenetre ouverte pour lire l'erreur
if %errorlevel% neq 0 (
    echo.
    echo UNE ERREUR S'EST PRODUITE !
    pause
)