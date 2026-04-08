# 🧠 Job Scraping (CLI)

Un script Python en ligne de commande permettant de **scraper des offres d'emploi depuis LinkedIn**, avec support de **requêtes booléennes avancées** et de **filtres temporels**.

---

## 🚀 Fonctionnalités

- 🔍 Recherche par **intitulé de poste** et **localisation multiple**
- 🧠 Support des **requêtes booléennes** (`AND`, `OR`, `NOT`, parenthèses, guillemets)
- 📅 Filtrage par date :
  - dernières 24h
  - dernière semaine
  - dernier mois
- 🧹 Suppression des doublons
- 🎯 Filtrage intelligent des résultats
- 💻 Affichage clair en terminal (avec mise en forme)

---

## 📦 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Veys0ne/Job-scraping.git
cd Job-scraping
```

### 2. Créer un environnement virtuel

Sur Linux/Mac :
```bash
python3 -m venv venv
source venv/bin/activate  
```

Sur Windows :
```bash
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ⚙️ Utilisation

```bash
python3 scraping.py -t "<QUERY>" -l "<LOCATIONS>" [OPTIONS]
```

### Arguments obligatoires

| Argument | Description |
|--------|------------|
| `-t`, `--title` | Requête de recherche (supporte booléens) |
| `-l`, `--location` | Liste de localisations séparées par des virgules |

### Options

| Option | Description |
|--------|------------|
| `-d`, `--day` | Offres des dernières 24h |
| `-w`, `--week` | Offres de la dernière semaine |
| `-m`, `--month` | Offres du dernier mois |

---

## 🧠 Requêtes avancées

Le script supporte les opérateurs :

- `AND`
- `OR`
- `NOT`
- `(...)`
- `"phrase exacte"`

### Exemple de requête

```bash
python3 scraping.py \
-t '("stage" OR "stagiaire" OR "intern") AND ("IT" OR "informatique" OR "info")' \
-l "île-de-France, strasbourg, france" \
-d
```

👉 Cette commande va :
- chercher des stages en informatique
- dans plusieurs régions
- publiés dans les dernières 24h

---

## 📊 Fonctionnement

1. Génère une URL LinkedIn avec les paramètres
2. Scrape les résultats HTML avec BeautifulSoup
3. Extrait :
   - titre
   - entreprise
   - localisation
   - lien
   - date
4. Filtre les résultats avec ta requête booléenne
5. Supprime les doublons
6. Affiche les résultats

---
