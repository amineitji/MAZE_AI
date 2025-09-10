# MAZE AI - Edition AAA 🎮

## Vue d'ensemble

**MAZE AI** est un visualiseur d'algorithme A* de nouvelle génération avec des effets visuels AAA spectaculaires. Ce projet combine l'apprentissage des algorithmes de pathfinding avec une expérience visuelle immersive digne d'un jeu vidéo professionnel.

## ✨ Fonctionnalités

### 🎯 Algorithme & Intelligence
- **Algorithme A*** avec visualisation temps réel
- **Génération procédurale** de labyrinthes
- **Mode automatique** et **mode pas à pas**
- **Statistiques détaillées** de performance
- **4 niveaux de difficulté** (Facile, Moyen, Difficile, Extrême)

### 🎨 Effets Visuels AAA
- **Système de particules avancé** (explosions, étincelles, glow)
- **Animations fluides** 60 FPS
- **Effets de secousse d'écran** pour les moments intenses
- **Transitions et fondus** élégants
- **Interface néon futuriste** avec effets de glow
- **Particules de fond animées**

### 🎮 Expérience Utilisateur
- **Menu principal** avec animations
- **Sélection de difficulté** interactive
- **Interface temps réel** avec statistiques live
- **Raccourcis clavier** pour les power users
- **Écran de victoire** spectaculaire
- **Système audio** (simulation intégrée)

## 🚀 Installation

### Prérequis
```bash
Python 3.9+
pygame 2.0+
```

### Installation rapide
```bash
# Cloner le repository
git clone https://github.com/votre-username/maze-ai-aaa.git
cd maze-ai-aaa

# Installer les dépendances
pip install pygame

# Lancer le jeu
python main.py
```

### Installation avec environnement virtuel (recommandé)
```bash
# Créer l'environnement virtuel
python -m venv maze_ai_env

# Activer l'environnement
# Sur Windows:
maze_ai_env\Scripts\activate
# Sur macOS/Linux:
source maze_ai_env/bin/activate

# Installer les dépendances
pip install pygame

# Lancer le jeu
python main.py
```

## 🎮 Guide d'utilisation

### Contrôles

#### Menu
- **Souris** : Navigation dans les menus
- **Clic gauche** : Sélection des options
- **ÉCHAP** : Retour au menu précédent

#### Jeu
- **ESPACE** : Lancer la résolution automatique
- **S** : Exécuter une étape de l'algorithme
- **R** : Réinitialiser le labyrinthe
- **ÉCHAP** : Retour au menu principal

#### Boutons Interface
- **AUTO** : Mode résolution automatique
- **ÉTAPE** : Mode pas à pas
- **RÉINITIALISER** : Reset de l'état actuel
- **NOUVEAU LABYRINTHE** : Génération d'un nouveau labyrinthe
- **MENU PRINCIPAL** : Retour à l'accueil

### Niveaux de Difficulté

| Difficulté | Taille | Complexité | Temps moyen |
|------------|---------|------------|-------------|
| **Facile** | 30x20 | ⭐ | 2-5 secondes |
| **Moyen** | 50x35 | ⭐⭐ | 5-15 secondes |
| **Difficile** | 70x50 | ⭐⭐⭐ | 15-45 secondes |
| **Extrême** | 100x70 | ⭐⭐⭐⭐ | 45+ secondes |

## 🔧 Architecture Technique

### Structure du Code

```
maze_ai_aaa.py
├── Classes Principales
│   ├── JeuAAA           # Gestionnaire principal
│   ├── LabyrintheAAA    # Génération et gestion du labyrinthe
│   ├── AgentIAAAA      # Implémentation A* avec effets
│   └── InterfaceJeuAAA  # Interface utilisateur avancée
├── Systèmes d'Effets
│   ├── EffetsVisuelsAAA # Gestionnaire d'effets visuels
│   ├── ParticuleAvancee # Système de particules
│   └── BoutonAAA        # Boutons avec animations
├── Menus & Navigation
│   └── MenuAAA          # Système de menus complet
└── Enums & Types
    ├── EtatJeu          # États du jeu
    ├── DifficulteLabyrinthe
    └── TypeCellule
```

### Algorithme A*

L'implémentation utilise :
- **Heuristique Manhattan** pour l'estimation de distance
- **Liste ouverte** avec heapq pour l'optimisation
- **Visualisation temps réel** des nœuds explorés
- **Reconstruction du chemin** avec effets visuels
- **Statistiques détaillées** de performance

### Système de Particules

```python
Types de particules :
- explosion : Particules radiaires avec gravité
- etincelle : Petites particules lumineuses
- glow      : Effets de halo et de brillance
```

## 🎨 Palette de Couleurs

### Couleurs Principales
```python
NOIR_PROFOND = (8, 12, 20)      # Fond principal
NOIR_ELEGANCE = (15, 15, 35)    # Fond dégradé
BLANC_NEIGE = (245, 245, 250)   # Texte principal
```

### Couleurs Néon
```python
NEON_CYAN = (0, 255, 255)       # Éléments interactifs
NEON_ROSE = (255, 20, 147)      # Accents et effets
NEON_VERT = (57, 255, 20)       # Succès et validation
NEON_ORANGE = (255, 140, 0)     # Alertes et progression
```

## 📊 Statistiques & Performance

Le jeu affiche en temps réel :
- **Nœuds explorés** : Nombre de cellules analysées
- **Nœuds en attente** : Taille de la liste ouverte
- **Longueur du chemin** : Distance de la solution
- **Temps d'exécution** : Performance de l'algorithme
- **Efficacité** : Ratio chemin optimal / nœuds explorés

## 🔧 Configuration

### Performance
```python
FPS = 60                    # Images par seconde
VITESSE_ANIMATION = 8       # Délai entre les étapes auto
TAILLE_PARTICULES = 3.0     # Taille des effets visuels
```

### Affichage
```python
LARGEUR = 1400             # Largeur de la fenêtre
HAUTEUR = 900              # Hauteur de la fenêtre
PANEL_INTERFACE = 320      # Largeur du panel de droite
```

## 🚀 Fonctionnalités Avancées

### Génération de Labyrinthe
- **Algorithme de backtracking récursif**
- **Garantie de solution unique**
- **Optimisation pour la visualisation**

### Effets Visuels
- **Shake de caméra** pour les moments intenses
- **Transitions fluides** entre les états
- **Glow et halos** dynamiques
- **Particules contextuelles** selon les actions

### Interface Adaptative
- **Boutons avec animations hover**
- **Barres de progression temps réel**
- **Légende interactive détaillée**
- **HUD avec informations contextuelles**


## 📧 Contact

Créé par Amine ITJI

---

