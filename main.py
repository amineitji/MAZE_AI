import pygame
import random
import heapq
import math
import time
from enum import Enum
from typing import List, Tuple, Optional, Dict
import sys

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()

# Constantes
LARGEUR = 1400
HAUTEUR = 900
FPS = 60

# Couleurs - Palette AAA
NOIR_PROFOND = (8, 12, 20)
NOIR_ELEGANCE = (15, 15, 35)
BLANC_NEIGE = (245, 245, 250)
BLANC_PUR = (255, 255, 255)

# Couleurs néon pour effets AAA
NEON_CYAN = (0, 255, 255)
NEON_ROSE = (255, 20, 147)
NEON_VERT = (57, 255, 20)
NEON_ORANGE = (255, 140, 0)
NEON_VIOLET = (138, 43, 226)

# Couleurs d'interface élégantes
BLEU_ROYAL = (65, 105, 225)
ROUGE_CRIMSON = (220, 20, 60)
VERT_EMERAUDE = (46, 125, 50)
OR_IMPERIAL = (255, 215, 0)
ARGENT = (192, 192, 192)

# Couleurs avec transparence
OVERLAY_SOMBRE = (0, 0, 0, 180)
GLOW_EFFECT = (255, 255, 255, 50)

class EtatJeu(Enum):
    MENU_PRINCIPAL = 0
    SELECTION_DIFFICULTE = 1
    OPTIONS = 2
    JEU_ACTIF = 3
    PAUSE = 4
    VICTOIRE = 5
    CREDITS = 6

class DifficulteLabyrinthe(Enum):
    FACILE = (30, 20, "Facile", VERT_EMERAUDE)
    MOYEN = (50, 35, "Moyen", OR_IMPERIAL)
    DIFFICILE = (70, 50, "Difficile", NEON_ORANGE)
    EXTREME = (100, 70, "Extrême", ROUGE_CRIMSON)

class TypeCellule(Enum):
    VIDE = 0
    MUR = 1
    DEPART = 2
    ARRIVEE = 3
    LISTE_OUVERTE = 4
    LISTE_FERMEE = 5
    CHEMIN_FINAL = 6

class ParticuleAvancee:
    def __init__(self, x: float, y: float, couleur: Tuple[int, int, int], 
                 type_particule: str = "explosion", taille: float = 3.0):
        self.x = x
        self.y = y
        self.couleur = couleur
        self.type = type_particule
        self.taille_initiale = taille
        self.taille = taille
        self.age = 0
        self.duree_vie = random.randint(60, 120)
        
        # Propriétés selon le type
        if type_particule == "explosion":
            angle = random.uniform(0, 2 * math.pi)
            vitesse = random.uniform(2, 6)
            self.vx = math.cos(angle) * vitesse
            self.vy = math.sin(angle) * vitesse
            self.gravite = 0.1
        elif type_particule == "etincelle":
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-3, -1)
            self.gravite = 0.05
        elif type_particule == "glow":
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-0.5, 0.5)
            self.gravite = 0
            self.duree_vie = random.randint(30, 60)
        
        self.alpha = 255
    
    def mettre_a_jour(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravite
        self.age += 1
        
        # Diminution de la taille et de l'alpha
        progress = self.age / self.duree_vie
        self.taille = self.taille_initiale * (1 - progress)
        self.alpha = max(0, int(255 * (1 - progress)))
        
        return self.age < self.duree_vie and self.taille > 0

class EffetsVisuelsAAA:
    def __init__(self):
        self.particules = []
        self.animations_cellules = {}
        self.shake_camera = 0
        self.fade_alpha = 0
        self.temps_actuel = 0
        self.effets_sonores = {}
    
    def ajouter_explosion(self, x: int, y: int, couleur: Tuple[int, int, int], 
                         intensite: int = 15, taille_cellule: int = 20):
        centre_x = x * taille_cellule + taille_cellule // 2
        centre_y = y * taille_cellule + taille_cellule // 2
        
        # Particules d'explosion principales
        for _ in range(intensite):
            self.particules.append(ParticuleAvancee(centre_x, centre_y, couleur, "explosion", 
                                                  random.uniform(2, 5)))
        
        # Étincelles
        for _ in range(intensite // 2):
            self.particules.append(ParticuleAvancee(centre_x, centre_y, BLANC_PUR, "etincelle", 
                                                  random.uniform(1, 2)))
        
        # Effet de glow
        for _ in range(5):
            self.particules.append(ParticuleAvancee(centre_x, centre_y, couleur, "glow", 
                                                  random.uniform(8, 12)))
    
    def ajouter_trail_effet(self, positions: List[Tuple[int, int]], couleur: Tuple[int, int, int],
                           taille_cellule: int = 20):
        """Effet de traînée pour le chemin final"""
        for i, pos in enumerate(positions):
            delay = i * 5  # Délai pour effet de cascade
            self.animations_cellules[(pos[0], pos[1])] = (self.temps_actuel + delay, "trail", couleur)
    
    def shake_ecran(self, intensite: int = 10):
        """Effet de secousse d'écran"""
        self.shake_camera = intensite
    
    def fade_transition(self, alpha: int):
        """Effet de fondu"""
        self.fade_alpha = alpha
    
    def mettre_a_jour(self):
        self.temps_actuel += 1
        
        # Mise à jour des particules
        self.particules = [p for p in self.particules if p.mettre_a_jour()]
        
        # Réduction du shake
        if self.shake_camera > 0:
            self.shake_camera = max(0, self.shake_camera - 1)
        
        # Nettoyage des animations
        animations_a_supprimer = []
        for pos, (temps_debut, type_anim, _) in self.animations_cellules.items():
            if self.temps_actuel - temps_debut > 180:  # 3 secondes
                animations_a_supprimer.append(pos)
        
        for pos in animations_a_supprimer:
            del self.animations_cellules[pos]

class BoutonAAA:
    def __init__(self, x: int, y: int, largeur: int, hauteur: int, texte: str,
                 couleur_principale: Tuple[int, int, int] = BLEU_ROYAL,
                 couleur_hover: Tuple[int, int, int] = NEON_CYAN):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur_principale = couleur_principale
        self.couleur_hover = couleur_hover
        self.couleur_actuelle = couleur_principale
        self.hover = False
        self.animation_scale = 1.0
        self.glow_intensity = 0
        
        # Polices
        self.police = pygame.font.Font(None, 36)
        self.police_hover = pygame.font.Font(None, 38)
    
    def mettre_a_jour(self, pos_souris: Tuple[int, int]):
        etait_hover = self.hover
        self.hover = self.rect.collidepoint(pos_souris)
        
        # Animation de scale
        if self.hover:
            self.animation_scale = min(1.1, self.animation_scale + 0.05)
            self.glow_intensity = min(255, self.glow_intensity + 15)
            self.couleur_actuelle = self.couleur_hover
        else:
            self.animation_scale = max(1.0, self.animation_scale - 0.05)
            self.glow_intensity = max(0, self.glow_intensity - 15)
            self.couleur_actuelle = self.couleur_principale
        
        return self.hover and not etait_hover  # True si on commence à hover
    
    def dessiner(self, ecran: pygame.Surface, offset_shake: Tuple[int, int] = (0, 0)):
        # Position avec shake
        x = self.rect.x + offset_shake[0]
        y = self.rect.y + offset_shake[1]
        
        # Calcul de la taille avec animation
        largeur_animee = int(self.rect.width * self.animation_scale)
        hauteur_animee = int(self.rect.height * self.animation_scale)
        
        # Centrage du bouton animé
        rect_anime = pygame.Rect(
            x + (self.rect.width - largeur_animee) // 2,
            y + (self.rect.height - hauteur_animee) // 2,
            largeur_animee,
            hauteur_animee
        )
        
        # Effet glow
        if self.glow_intensity > 0:
            glow_surface = pygame.Surface((largeur_animee + 20, hauteur_animee + 20))
            glow_surface.set_alpha(self.glow_intensity // 3)
            glow_surface.fill(self.couleur_actuelle)
            ecran.blit(glow_surface, (rect_anime.x - 10, rect_anime.y - 10))
        
        # Dégradé du bouton
        for i in range(hauteur_animee):
            alpha = 1.0 - (i / hauteur_animee) * 0.3
            couleur_degradee = tuple(int(c * alpha) for c in self.couleur_actuelle)
            ligne_rect = pygame.Rect(rect_anime.x, rect_anime.y + i, largeur_animee, 1)
            pygame.draw.rect(ecran, couleur_degradee, ligne_rect)
        
        # Bordure brillante
        pygame.draw.rect(ecran, BLANC_PUR, rect_anime, 3)
        
        # Texte avec ombre
        police = self.police_hover if self.hover else self.police
        
        # Ombre du texte
        texte_ombre = police.render(self.texte, True, NOIR_PROFOND)
        rect_texte_ombre = texte_ombre.get_rect(center=(rect_anime.centerx + 2, rect_anime.centery + 2))
        ecran.blit(texte_ombre, rect_texte_ombre)
        
        # Texte principal
        texte_surface = police.render(self.texte, True, BLANC_PUR)
        rect_texte = texte_surface.get_rect(center=rect_anime.center)
        ecran.blit(texte_surface, rect_texte)
    
    def est_clique(self, pos_souris: Tuple[int, int], event_type: int) -> bool:
        return self.hover and event_type == pygame.MOUSEBUTTONDOWN

class MenuAAA:
    def __init__(self, largeur_ecran: int, hauteur_ecran: int):
        self.largeur_ecran = largeur_ecran
        self.hauteur_ecran = hauteur_ecran
        
        # Polices AAA
        self.police_titre = pygame.font.Font(None, 84)
        self.police_sous_titre = pygame.font.Font(None, 36)
        self.police_normale = pygame.font.Font(None, 28)
        
        # Particules de fond
        self.particules_fond = []
        self.temps_menu = 0
        
        # Initialiser particules de fond
        for _ in range(100):
            self.particules_fond.append({
                'x': random.randint(0, largeur_ecran),
                'y': random.randint(0, hauteur_ecran),
                'vitesse': random.uniform(0.1, 0.5),
                'taille': random.uniform(1, 3),
                'couleur': random.choice([NEON_CYAN, NEON_ROSE, NEON_VERT, ARGENT]),
                'alpha_base': random.randint(30, 100)
            })
        
        self.init_boutons()
    
    def init_boutons(self):
        centre_x = self.largeur_ecran // 2
        
        # Menu principal
        self.boutons_principal = [
            BoutonAAA(centre_x - 150, 350, 300, 60, "NOUVELLE PARTIE", VERT_EMERAUDE, NEON_VERT),
            BoutonAAA(centre_x - 150, 430, 300, 60, "OPTIONS", BLEU_ROYAL, NEON_CYAN),
            BoutonAAA(centre_x - 150, 510, 300, 60, "CRÉDITS", OR_IMPERIAL, NEON_ORANGE),
            BoutonAAA(centre_x - 150, 590, 300, 60, "QUITTER", ROUGE_CRIMSON, NEON_ROSE)
        ]
        
        # Sélection difficulté
        self.boutons_difficulte = []
        for i, difficulte in enumerate(DifficulteLabyrinthe):
            self.boutons_difficulte.append(
                BoutonAAA(centre_x - 150, 300 + i * 80, 300, 60, 
                         difficulte.value[2], difficulte.value[3], NEON_CYAN)
            )
        
        self.boutons_difficulte.append(
            BoutonAAA(centre_x - 100, 650, 200, 50, "RETOUR", ARGENT, BLANC_PUR)
        )
    
    def mettre_a_jour_particules_fond(self):
        self.temps_menu += 1
        
        for particule in self.particules_fond:
            particule['y'] -= particule['vitesse']
            if particule['y'] < -10:
                particule['y'] = self.hauteur_ecran + 10
                particule['x'] = random.randint(0, self.largeur_ecran)
            
            # Effet de pulsation
            particule['alpha'] = particule['alpha_base'] + int(30 * math.sin(self.temps_menu * 0.02 + particule['x'] * 0.01))
            particule['alpha'] = max(0, min(255, particule['alpha']))
    
    def dessiner_fond_anime(self, ecran: pygame.Surface):
        # Dégradé de fond
        for y in range(self.hauteur_ecran):
            ratio = y / self.hauteur_ecran
            r = int(NOIR_PROFOND[0] + (NOIR_ELEGANCE[0] - NOIR_PROFOND[0]) * ratio)
            g = int(NOIR_PROFOND[1] + (NOIR_ELEGANCE[1] - NOIR_PROFOND[1]) * ratio)
            b = int(NOIR_PROFOND[2] + (NOIR_ELEGANCE[2] - NOIR_PROFOND[2]) * ratio)
            pygame.draw.line(ecran, (r, g, b), (0, y), (self.largeur_ecran, y))
        
        # Particules de fond
        for particule in self.particules_fond:
            if particule.get('alpha', particule['alpha_base']) > 0:
                surface = pygame.Surface((particule['taille'] * 2, particule['taille'] * 2))
                surface.set_alpha(particule.get('alpha', particule['alpha_base']))
                pygame.draw.circle(surface, particule['couleur'], 
                                 (particule['taille'], particule['taille']), particule['taille'])
                ecran.blit(surface, (particule['x'], particule['y']))
    
    def dessiner_titre_principal(self, ecran: pygame.Surface):
        # Effet de glow pour le titre
        titre_text = "MAZE AI"
        
        # Titre avec effet néon
        for offset in [(4, 4), (2, 2), (0, 0)]:
            couleur = NOIR_PROFOND if offset != (0, 0) else NEON_CYAN
            surface_titre = self.police_titre.render(titre_text, True, couleur)
            rect_titre = surface_titre.get_rect(center=(self.largeur_ecran // 2 + offset[0], 150 + offset[1]))
            ecran.blit(surface_titre, rect_titre)
        
        # Sous-titre
        sous_titre = "Visualisation d'algorithme A* de nouvelle génération"
        surface_sous_titre = self.police_sous_titre.render(sous_titre, True, ARGENT)
        rect_sous_titre = surface_sous_titre.get_rect(center=(self.largeur_ecran // 2, 220))
        ecran.blit(surface_sous_titre, rect_sous_titre)

class Noeud:
    def __init__(self, position: Tuple[int, int], g: float = 0, h: float = 0, parent=None):
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __eq__(self, other):
        return self.position == other.position

class LabyrintheAAA:
    def __init__(self, largeur: int, hauteur: int, effets: EffetsVisuelsAAA):
        self.largeur = largeur
        self.hauteur = hauteur
        self.effets = effets
        self.grille = [[TypeCellule.MUR for _ in range(largeur)] for _ in range(hauteur)]
        self.depart = (1, 1)
        self.arrivee = (largeur - 2, hauteur - 2)
        self.generer_labyrinthe()
        
        # Calcul de la taille des cellules pour centrer le labyrinthe
        zone_jeu_largeur = LARGEUR - 400  # Laisser place pour l'interface
        zone_jeu_hauteur = HAUTEUR - 100
        
        self.taille_cellule = min(zone_jeu_largeur // largeur, zone_jeu_hauteur // hauteur)
        self.offset_x = 50
        self.offset_y = 50
        
    def generer_labyrinthe(self):
        # Génération avec animation
        for y in range(self.hauteur):
            for x in range(self.largeur):
                self.grille[y][x] = TypeCellule.MUR
        
        stack = []
        start_x, start_y = 1, 1
        self.grille[start_y][start_x] = TypeCellule.VIDE
        stack.append((start_x, start_y))
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            current_x, current_y = stack[-1]
            
            voisins = []
            for dx, dy in directions:
                new_x, new_y = current_x + dx, current_y + dy
                if (0 < new_x < self.largeur - 1 and 
                    0 < new_y < self.hauteur - 1 and 
                    self.grille[new_y][new_x] == TypeCellule.MUR):
                    voisins.append((new_x, new_y))
            
            if voisins:
                next_x, next_y = random.choice(voisins)
                wall_x = current_x + (next_x - current_x) // 2
                wall_y = current_y + (next_y - current_y) // 2
                
                self.grille[wall_y][wall_x] = TypeCellule.VIDE
                self.grille[next_y][next_x] = TypeCellule.VIDE
                stack.append((next_x, next_y))
            else:
                stack.pop()
        
        self.grille[self.depart[1]][self.depart[0]] = TypeCellule.DEPART
        self.grille[self.arrivee[1]][self.arrivee[0]] = TypeCellule.ARRIVEE
    
    def est_valide(self, x: int, y: int) -> bool:
        return (0 <= x < self.largeur and 
                0 <= y < self.hauteur and 
                self.grille[y][x] != TypeCellule.MUR)
    
    def obtenir_voisins(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = position
        voisins = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.est_valide(new_x, new_y):
                voisins.append((new_x, new_y))
        
        return voisins

class AgentIAAAA:
    def __init__(self, labyrinthe: LabyrintheAAA, effets: EffetsVisuelsAAA):
        self.labyrinthe = labyrinthe
        self.effets = effets
        self.chemin_final = []
        self.liste_ouverte_positions = set()
        self.liste_fermee_positions = set()
        self.algorithme_termine = False
        self.statistiques = {
            'noeuds_explores': 0,
            'noeuds_en_attente': 0,
            'longueur_chemin': 0,
            'temps_execution': 0,
            'efficacite': 0
        }
        self.temps_debut = 0
    
    def heuristique(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def reinitialiser(self):
        self.chemin_final.clear()
        self.liste_ouverte_positions.clear()
        self.liste_fermee_positions.clear()
        self.algorithme_termine = False
        self.temps_debut = time.time()
        
        # Réinitialiser les statistiques
        self.statistiques = {
            'noeuds_explores': 0,
            'noeuds_en_attente': 0,
            'longueur_chemin': 0,
            'temps_execution': 0,
            'efficacite': 0
        }
    
    def a_star_pas_a_pas(self):
        if hasattr(self, '_liste_ouverte'):
            if not self._liste_ouverte or self.algorithme_termine:
                return False
                
            noeud_actuel = heapq.heappop(self._liste_ouverte)
            
            if noeud_actuel.position in self._liste_fermee:
                return True
                
            self._liste_fermee.add(noeud_actuel.position)
            self.liste_fermee_positions.add(noeud_actuel.position)
            
            # Effet visuel spectaculaire pour l'exploration
            self.effets.ajouter_explosion(noeud_actuel.position[0], noeud_actuel.position[1], 
                                        NEON_CYAN, 8, self.labyrinthe.taille_cellule)
            
            if noeud_actuel.position == self.labyrinthe.arrivee:
                # Reconstruction du chemin avec effets
                chemin = []
                while noeud_actuel:
                    chemin.append(noeud_actuel.position)
                    noeud_actuel = noeud_actuel.parent
                self.chemin_final = chemin[::-1]
                
                # Effets spectaculaires pour la victoire
                self.effets.shake_ecran(20)
                self.effets.ajouter_trail_effet(self.chemin_final, NEON_VERT, self.labyrinthe.taille_cellule)
                
                # Explosions le long du chemin
                for pos in self.chemin_final:
                    self.effets.ajouter_explosion(pos[0], pos[1], NEON_VERT, 12, self.labyrinthe.taille_cellule)
                
                self.algorithme_termine = True
                self.statistiques['temps_execution'] = time.time() - self.temps_debut
                self.statistiques['longueur_chemin'] = len(self.chemin_final) - 1
                self.statistiques['efficacite'] = (len(self.chemin_final) / max(1, len(self.liste_fermee_positions))) * 100
                
                return False
            
            # Explorer les voisins avec effets visuels
            for voisin_pos in self.labyrinthe.obtenir_voisins(noeud_actuel.position):
                if voisin_pos in self._liste_fermee:
                    continue
                
                g_nouveau = noeud_actuel.g + 1
                h_nouveau = self.heuristique(voisin_pos, self.labyrinthe.arrivee)
                
                if (voisin_pos not in self._noeuds_ouverts or 
                    g_nouveau < self._noeuds_ouverts[voisin_pos].g):
                    
                    noeud_voisin = Noeud(voisin_pos, g_nouveau, h_nouveau, noeud_actuel)
                    heapq.heappush(self._liste_ouverte, noeud_voisin)
                    self._noeuds_ouverts[voisin_pos] = noeud_voisin
                    self.liste_ouverte_positions.add(voisin_pos)
                    
                    # Petit effet pour les nouvelles cellules
                    self.effets.ajouter_explosion(voisin_pos[0], voisin_pos[1], 
                                                BLEU_ROYAL, 4, self.labyrinthe.taille_cellule)
            
            # Mise à jour statistiques
            self.statistiques['noeuds_explores'] = len(self.liste_fermee_positions)
            self.statistiques['noeuds_en_attente'] = len(self._liste_ouverte)
            
            return True
        else:
            # Initialisation
            depart = self.labyrinthe.depart
            arrivee = self.labyrinthe.arrivee
            
            self._liste_ouverte = []
            heapq.heappush(self._liste_ouverte, Noeud(depart, 0, self.heuristique(depart, arrivee)))
            self._liste_fermee = set()
            self._noeuds_ouverts = {depart: Noeud(depart, 0, self.heuristique(depart, arrivee))}
            
            self.liste_ouverte_positions.add(depart)
            
            return True

class InterfaceJeuAAA:
    def __init__(self, largeur_panel: int):
        self.largeur_panel = largeur_panel
        
        # Polices élégantes
        self.police_titre = pygame.font.Font(None, 42)
        self.police_stats = pygame.font.Font(None, 28)
        self.police_mini = pygame.font.Font(None, 20)
        
        # Boutons avec style AAA
        base_x = LARGEUR - largeur_panel + 20
        self.boutons = {
            'auto': BoutonAAA(base_x, 120, 140, 45, "AUTO", VERT_EMERAUDE, NEON_VERT),
            'pas_a_pas': BoutonAAA(base_x + 150, 120, 140, 45, "ÉTAPE", BLEU_ROYAL, NEON_CYAN),
            'reset': BoutonAAA(base_x, 180, 290, 45, "RÉINITIALISER", OR_IMPERIAL, NEON_ORANGE),
            'nouveau': BoutonAAA(base_x, 240, 290, 45, "NOUVEAU LABYRINTHE", ROUGE_CRIMSON, NEON_ROSE),
            'menu': BoutonAAA(base_x, 300, 290, 45, "MENU PRINCIPAL", ARGENT, BLANC_PUR)
        }
    
    def dessiner_panel_principal(self, ecran: pygame.Surface, stats: Dict, offset_shake: Tuple[int, int]):
        # Panel avec effet de verre
        panel_rect = pygame.Rect(LARGEUR - self.largeur_panel, 0, self.largeur_panel, HAUTEUR)
        
        # Fond avec transparence
        panel_surface = pygame.Surface((self.largeur_panel, HAUTEUR))
        panel_surface.set_alpha(200)
        panel_surface.fill(NOIR_ELEGANCE)
        ecran.blit(panel_surface, (LARGEUR - self.largeur_panel + offset_shake[0], offset_shake[1]))
        
        # Bordure néon
        pygame.draw.line(ecran, NEON_CYAN, 
                        (LARGEUR - self.largeur_panel + offset_shake[0], offset_shake[1]), 
                        (LARGEUR - self.largeur_panel + offset_shake[0], HAUTEUR + offset_shake[1]), 3)
        
        # Titre avec effet glow
        titre = "ALGORITHME A*"
        for offset in [(2, 2), (1, 1), (0, 0)]:
            couleur = NOIR_PROFOND if offset != (0, 0) else NEON_CYAN
            surface_titre = self.police_titre.render(titre, True, couleur)
            ecran.blit(surface_titre, (LARGEUR - self.largeur_panel + 30 + offset[0] + offset_shake[0], 
                                     20 + offset[1] + offset_shake[1]))
        
        # Dessiner tous les boutons
        for bouton in self.boutons.values():
            bouton.dessiner(ecran, offset_shake)
    
    def dessiner_statistiques_avancees(self, ecran: pygame.Surface, stats: Dict, y_debut: int, offset_shake: Tuple[int, int]):
        # Titre section stats
        titre_stats = "PERFORMANCE TEMPS RÉEL"
        surface_titre = self.police_stats.render(titre_stats, True, NEON_ORANGE)
        ecran.blit(surface_titre, (LARGEUR - self.largeur_panel + 30 + offset_shake[0], 
                                 y_debut + offset_shake[1]))
        
        y = y_debut + 40
        
        # Statistiques avec barres de progression
        stats_affichage = [
            ("Nœuds explorés", stats['noeuds_explores'], 1000, NEON_CYAN),
            ("En attente", stats['noeuds_en_attente'], 500, BLEU_ROYAL),
            ("Longueur chemin", stats['longueur_chemin'], 200, NEON_VERT),
            ("Efficacité", f"{stats['efficacite']:.1f}%", 100, OR_IMPERIAL)
        ]
        
        for label, valeur, max_val, couleur_barre in stats_affichage:
            # Label
            surface_label = self.police_mini.render(f"{label}:", True, BLANC_NEIGE)
            ecran.blit(surface_label, (LARGEUR - self.largeur_panel + 30 + offset_shake[0], 
                                     y + offset_shake[1]))
            
            # Valeur
            valeur_str = str(valeur) if isinstance(valeur, int) else valeur
            surface_valeur = self.police_mini.render(valeur_str, True, couleur_barre)
            ecran.blit(surface_valeur, (LARGEUR - self.largeur_panel + 200 + offset_shake[0], 
                                      y + offset_shake[1]))
            
            # Barre de progression (pour les valeurs numériques)
            if isinstance(valeur, int) and max_val > 0:
                barre_largeur = 200
                barre_hauteur = 8
                progression = min(1.0, valeur / max_val)
                
                # Fond de la barre
                fond_rect = pygame.Rect(LARGEUR - self.largeur_panel + 30 + offset_shake[0], 
                                      y + 20 + offset_shake[1], barre_largeur, barre_hauteur)
                pygame.draw.rect(ecran, NOIR_PROFOND, fond_rect)
                
                # Barre de progression avec effet glow
                if progression > 0:
                    prog_rect = pygame.Rect(LARGEUR - self.largeur_panel + 30 + offset_shake[0], 
                                          y + 20 + offset_shake[1], 
                                          int(barre_largeur * progression), barre_hauteur)
                    pygame.draw.rect(ecran, couleur_barre, prog_rect)
                    
                    # Effet glow
                    glow_rect = pygame.Rect(prog_rect.x - 2, prog_rect.y - 2, 
                                          prog_rect.width + 4, prog_rect.height + 4)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
                    glow_surface.set_alpha(100)
                    glow_surface.fill(couleur_barre)
                    ecran.blit(glow_surface, (glow_rect.x, glow_rect.y))
            
            y += 50
    
    def dessiner_legende_detaillee(self, ecran: pygame.Surface, y_debut: int, offset_shake: Tuple[int, int]):
        titre_legende = "LÉGENDE VISUELLE"
        surface_titre = self.police_stats.render(titre_legende, True, NEON_ROSE)
        ecran.blit(surface_titre, (LARGEUR - self.largeur_panel + 30 + offset_shake[0], 
                                 y_debut + offset_shake[1]))
        
        y = y_debut + 40
        
        legendes = [
            ("🟢 Départ", NEON_VERT, "Point d'origine"),
            ("🔴 Arrivée", ROUGE_CRIMSON, "Objectif à atteindre"),
            ("🔵 Liste ouverte", BLEU_ROYAL, "Nœuds à explorer"),
            ("⚫ Liste fermée", ARGENT, "Nœuds explorés"),
            ("🟡 Chemin optimal", NEON_VERT, "Solution trouvée")
        ]
        
        for emoji, couleur, description in legendes:
            # Emoji/Symbole
            surface_emoji = self.police_mini.render(emoji, True, BLANC_PUR)
            ecran.blit(surface_emoji, (LARGEUR - self.largeur_panel + 30 + offset_shake[0], 
                                     y + offset_shake[1]))
            
            # Description
            surface_desc = self.police_mini.render(description, True, couleur)
            ecran.blit(surface_desc, (LARGEUR - self.largeur_panel + 60 + offset_shake[0], 
                                    y + offset_shake[1]))
            
            y += 25

class JeuAAA:
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("MAZE AI - Edition AAA")
        self.horloge = pygame.time.Clock()
        
        # États du jeu
        self.etat_actuel = EtatJeu.MENU_PRINCIPAL
        self.difficulte_selectionnee = None
        
        # Composants
        self.menu = MenuAAA(LARGEUR, HAUTEUR)
        self.effets = EffetsVisuelsAAA()
        self.labyrinthe = None
        self.agent = None
        self.interface_jeu = InterfaceJeuAAA(320)
        
        # Variables de jeu
        self.mode_automatique = False
        self.vitesse_animation = 8
        self.compteur_animation = 0
        self.temps_victoire = 0
        
        # Musique et sons (simulation)
        self.volume_musique = 0.7
        self.volume_effets = 0.8
    
    def initialiser_nouveau_jeu(self, difficulte: DifficulteLabyrinthe):
        """Initialise un nouveau jeu avec la difficulté choisie"""
        largeur, hauteur = difficulte.value[0], difficulte.value[1]
        
        # Réinitialiser les effets
        self.effets = EffetsVisuelsAAA()
        
        # Créer le nouveau labyrinthe
        self.labyrinthe = LabyrintheAAA(largeur, hauteur, self.effets)
        self.agent = AgentIAAAA(self.labyrinthe, self.effets)
        
        # Effet d'entrée spectaculaire
        self.effets.fade_transition(255)
        self.effets.shake_ecran(15)
        
        # Transition vers le jeu
        self.etat_actuel = EtatJeu.JEU_ACTIF
        
        print(f"Nouveau jeu créé - Difficulté: {difficulte.value[2]} ({largeur}x{hauteur})")
    
    def dessiner_cellule_ultra_detaillee(self, x: int, y: int, couleur_base: Tuple[int, int, int], 
                                        alpha: int = 255, effet_special: bool = False):
        """Dessine une cellule avec des effets visuels ultra-détaillés"""
        if not self.labyrinthe:
            return
            
        taille = self.labyrinthe.taille_cellule
        pos_x = x * taille + self.labyrinthe.offset_x
        pos_y = y * taille + self.labyrinthe.offset_y
        
        # Shake de la caméra
        shake_x = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        shake_y = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        
        pos_x += shake_x
        pos_y += shake_y
        
        rect = pygame.Rect(pos_x, pos_y, taille, taille)
        
        # Effet de pulsation pour les animations
        facteur_animation = 1.0
        if (x, y) in self.effets.animations_cellules:
            temps_debut, type_anim, couleur_anim = self.effets.animations_cellules[(x, y)]
            age = self.effets.temps_actuel - temps_debut
            
            if type_anim == "trail":
                facteur_animation = 1.0 + 0.5 * math.sin(age * 0.1)
                couleur_base = couleur_anim
            else:
                facteur_animation = 1.0 + 0.3 * math.sin(age * 0.2)
        
        # Effet de glow si activé
        if effet_special or facteur_animation > 1.0:
            glow_size = int(taille * facteur_animation * 1.2)
            glow_rect = pygame.Rect(pos_x - (glow_size - taille) // 2, 
                                  pos_y - (glow_size - taille) // 2, 
                                  glow_size, glow_size)
            
            glow_surface = pygame.Surface((glow_size, glow_size))
            glow_surface.set_alpha(50)
            glow_surface.fill(couleur_base)
            self.ecran.blit(glow_surface, glow_rect)
        
        # Cellule principale avec dégradé
        if alpha < 255:
            surface_cellule = pygame.Surface((taille, taille))
            surface_cellule.set_alpha(alpha)
            
            # Dégradé vertical
            for i in range(taille):
                ratio = i / taille
                couleur_degradee = tuple(int(c * (0.7 + 0.3 * ratio)) for c in couleur_base)
                pygame.draw.line(surface_cellule, couleur_degradee, (0, i), (taille, i))
            
            self.ecran.blit(surface_cellule, rect)
        else:
            # Dégradé direct
            for i in range(taille):
                ratio = i / taille
                couleur_degradee = tuple(int(c * (0.7 + 0.3 * ratio)) for c in couleur_base)
                pygame.draw.line(self.ecran, couleur_degradee, (rect.x, rect.y + i), (rect.x + taille, rect.y + i))
        
        # Bordure avec intensité variable
        intensite_bordure = int(3 * facteur_animation) if facteur_animation > 1.0 else 1
        couleur_bordure = BLANC_PUR if facteur_animation > 1.0 else (80, 80, 80)
        pygame.draw.rect(self.ecran, couleur_bordure, rect, intensite_bordure)
    
    def dessiner_labyrinthe_complet(self):
        """Dessine le labyrinthe avec tous les effets AAA"""
        if not self.labyrinthe:
            return
            
        for y in range(self.labyrinthe.hauteur):
            for x in range(self.labyrinthe.largeur):
                type_cellule = self.labyrinthe.grille[y][x]
                
                # Déterminer la couleur de base
                if type_cellule == TypeCellule.MUR:
                    self.dessiner_cellule_ultra_detaillee(x, y, NOIR_PROFOND)
                elif type_cellule == TypeCellule.DEPART:
                    self.dessiner_cellule_ultra_detaillee(x, y, NEON_VERT, effet_special=True)
                elif type_cellule == TypeCellule.ARRIVEE:
                    self.dessiner_cellule_ultra_detaillee(x, y, ROUGE_CRIMSON, effet_special=True)
                else:
                    self.dessiner_cellule_ultra_detaillee(x, y, BLANC_NEIGE)
                
                # Superposition des états A*
                if (x, y) in self.agent.liste_fermee_positions:
                    if (x, y) not in [self.labyrinthe.depart, self.labyrinthe.arrivee]:
                        self.dessiner_cellule_ultra_detaillee(x, y, ARGENT, 120)
                
                if (x, y) in self.agent.liste_ouverte_positions:
                    if (x, y) not in [self.labyrinthe.depart, self.labyrinthe.arrivee]:
                        self.dessiner_cellule_ultra_detaillee(x, y, BLEU_ROYAL, 150)
                
                # Chemin final avec effet trail
                if (x, y) in self.agent.chemin_final:
                    if (x, y) not in [self.labyrinthe.depart, self.labyrinthe.arrivee]:
                        self.dessiner_cellule_ultra_detaillee(x, y, NEON_VERT, 200, True)
    
    def dessiner_particules_avancees(self):
        """Dessine toutes les particules avec effets avancés"""
        for particule in self.effets.particules:
            if particule.taille > 0 and particule.alpha > 0:
                # Calcul de la position avec shake
                shake_x = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
                shake_y = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
                
                pos_x = particule.x + shake_x
                pos_y = particule.y + shake_y
                
                # Surface avec alpha pour la particule
                taille_surface = int(particule.taille * 3)
                surface = pygame.Surface((taille_surface, taille_surface))
                surface.set_alpha(particule.alpha)
                
                # Effet selon le type de particule
                if particule.type == "glow":
                    # Effet de glow avec dégradé radial
                    centre = taille_surface // 2
                    for rayon in range(int(particule.taille), 0, -1):
                        alpha_rayon = int(particule.alpha * (rayon / particule.taille))
                        #couleur_avec_alpha = (*particule.couleur, alpha_rayon)
                        pygame.draw.circle(surface, particule.couleur, (centre, centre), rayon)
                else:
                    # Particule normale avec halo
                    centre = taille_surface // 2
                    pygame.draw.circle(surface, particule.couleur, (centre, centre), int(particule.taille))
                
                self.ecran.blit(surface, (pos_x - taille_surface // 2, pos_y - taille_surface // 2))
    
    def gerer_evenements_menu(self, event):
        """Gère les événements dans les menus"""
        pos_souris = pygame.mouse.get_pos()
        
        if self.etat_actuel == EtatJeu.MENU_PRINCIPAL:
            # Mise à jour des boutons
            for i, bouton in enumerate(self.menu.boutons_principal):
                bouton.mettre_a_jour(pos_souris)
                
                if bouton.est_clique(pos_souris, event.type):
                    if i == 0:  # Nouvelle partie
                        self.etat_actuel = EtatJeu.SELECTION_DIFFICULTE
                    elif i == 1:  # Options
                        self.etat_actuel = EtatJeu.OPTIONS
                    elif i == 2:  # Crédits
                        self.etat_actuel = EtatJeu.CREDITS
                    elif i == 3:  # Quitter
                        return False
                    
                    # Effet sonore simulation
                    self.effets.shake_ecran(5)
        
        elif self.etat_actuel == EtatJeu.SELECTION_DIFFICULTE:
            # Boutons de difficulté
            for i, bouton in enumerate(self.menu.boutons_difficulte[:-1]):  # Exclure le bouton retour
                bouton.mettre_a_jour(pos_souris)
                
                if bouton.est_clique(pos_souris, event.type):
                    difficulte = list(DifficulteLabyrinthe)[i]
                    self.initialiser_nouveau_jeu(difficulte)
                    return True
            
            # Bouton retour
            bouton_retour = self.menu.boutons_difficulte[-1]
            bouton_retour.mettre_a_jour(pos_souris)
            if bouton_retour.est_clique(pos_souris, event.type):
                self.etat_actuel = EtatJeu.MENU_PRINCIPAL
        
        elif self.etat_actuel == EtatJeu.OPTIONS:
            # Retour au menu avec ECHAP
            pass
        
        elif self.etat_actuel == EtatJeu.CREDITS:
            # Retour au menu avec ECHAP
            pass
        
        return True
    
    def gerer_evenements_jeu(self, event):
        """Gère les événements pendant le jeu"""
        pos_souris = pygame.mouse.get_pos()
        
        # Calculer offset shake
        shake_x = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        shake_y = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        offset_shake = (shake_x, shake_y)
        
        # Mise à jour des boutons
        for nom, bouton in self.interface_jeu.boutons.items():
            bouton.mettre_a_jour(pos_souris)
            
            if bouton.est_clique(pos_souris, event.type):
                if nom == 'auto':
                    self.mode_automatique = True
                    self.agent.reinitialiser()
                    self.effets.shake_ecran(8)
                    
                elif nom == 'pas_a_pas':
                    if not hasattr(self.agent, '_liste_ouverte'):
                        self.agent.reinitialiser()
                    self.agent.a_star_pas_a_pas()
                    
                elif nom == 'reset':
                    self.agent.reinitialiser()
                    self.mode_automatique = False
                    self.effets.shake_ecran(5)
                    
                elif nom == 'nouveau':
                    if self.difficulte_selectionnee:
                        self.initialiser_nouveau_jeu(self.difficulte_selectionnee)
                    
                elif nom == 'menu':
                    self.etat_actuel = EtatJeu.MENU_PRINCIPAL
                    self.mode_automatique = False
        
        # Raccourcis clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.mode_automatique = True
                self.agent.reinitialiser()
            elif event.key == pygame.K_s:
                if not hasattr(self.agent, '_liste_ouverte'):
                    self.agent.reinitialiser()
                self.agent.a_star_pas_a_pas()
            elif event.key == pygame.K_r:
                self.agent.reinitialiser()
                self.mode_automatique = False
            elif event.key == pygame.K_ESCAPE:
                self.etat_actuel = EtatJeu.MENU_PRINCIPAL
        
        return True
    
    def dessiner_menu_principal(self):
        """Dessine le menu principal avec tous les effets"""
        # Fond animé
        self.menu.dessiner_fond_anime(self.ecran)
        
        # Mise à jour et dessin des particules de fond
        self.menu.mettre_a_jour_particules_fond()
        
        # Titre principal avec effets
        self.menu.dessiner_titre_principal(self.ecran)
        
        # Boutons avec animations
        pos_souris = pygame.mouse.get_pos()
        for bouton in self.menu.boutons_principal:
            bouton.mettre_a_jour(pos_souris)
            bouton.dessiner(self.ecran)
        
        # Version info
        version_text = "Version 2.0 - Édition AAA"
        surface_version = self.menu.police_normale.render(version_text, True, ARGENT)
        self.ecran.blit(surface_version, (20, HAUTEUR - 30))
    
    def dessiner_selection_difficulte(self):
        """Dessine le menu de sélection de difficulté"""
        self.menu.dessiner_fond_anime(self.ecran)
        self.menu.mettre_a_jour_particules_fond()
        
        # Titre
        titre = "SÉLECTION DE DIFFICULTÉ"
        surface_titre = self.menu.police_titre.render(titre, True, NEON_CYAN)
        rect_titre = surface_titre.get_rect(center=(LARGEUR // 2, 200))
        
        # Effet glow pour le titre
        for offset in [(3, 3), (2, 2), (1, 1), (0, 0)]:
            couleur = NOIR_PROFOND if offset != (0, 0) else NEON_CYAN
            surface_titre_glow = self.menu.police_titre.render(titre, True, couleur)
            rect_glow = surface_titre_glow.get_rect(center=(rect_titre.centerx + offset[0], rect_titre.centery + offset[1]))
            self.ecran.blit(surface_titre_glow, rect_glow)
        
        # Boutons de difficulté
        pos_souris = pygame.mouse.get_pos()
        for bouton in self.menu.boutons_difficulte:
            bouton.mettre_a_jour(pos_souris)
            bouton.dessiner(self.ecran)
    
    def dessiner_interface_jeu_complete(self):
        """Dessine l'interface de jeu complète"""
        if not self.agent:
            return
            
        # Calculer shake offset
        shake_x = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        shake_y = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        offset_shake = (shake_x, shake_y)
        
        # Panel principal
        self.interface_jeu.dessiner_panel_principal(self.ecran, self.agent.statistiques, offset_shake)
        
        # Statistiques avancées
        self.interface_jeu.dessiner_statistiques_avancees(self.ecran, self.agent.statistiques, 380, offset_shake)
        
        # Légende détaillée
        self.interface_jeu.dessiner_legende_detaillee(self.ecran, 600, offset_shake)
        
        # HUD temps réel en haut de l'écran
        if self.agent.algorithme_termine and self.agent.statistiques['temps_execution'] > 0:
            temps_texte = f"Résolu en {self.agent.statistiques['temps_execution']:.2f}s"
            surface_temps = self.interface_jeu.police_stats.render(temps_texte, True, NEON_VERT)
            self.ecran.blit(surface_temps, (50 + offset_shake[0], 20 + offset_shake[1]))
    
    def mettre_a_jour_jeu(self):
        """Met à jour la logique du jeu"""
        # Mise à jour des effets
        self.effets.mettre_a_jour()
        
        # Mode automatique
        if self.mode_automatique and self.agent and not self.agent.algorithme_termine:
            self.compteur_animation += 1
            if self.compteur_animation >= self.vitesse_animation:
                self.compteur_animation = 0
                if not self.agent.a_star_pas_a_pas():
                    self.mode_automatique = False
                    
                    # Transition vers écran de victoire
                    if self.agent.algorithme_termine:
                        self.temps_victoire = time.time()
                        self.etat_actuel = EtatJeu.VICTOIRE
    
    def dessiner_ecran_victoire(self):
        """Dessine l'écran de victoire spectaculaire"""
        # Fond sombre avec particules
        self.ecran.fill(NOIR_PROFOND)
        
        # Particules de célébration
        if time.time() - self.temps_victoire < 2:  # Effets pendant 2 secondes
            for _ in range(5):
                x = random.randint(0, LARGEUR)
                y = random.randint(0, HAUTEUR)
                couleur = random.choice([NEON_VERT, OR_IMPERIAL, NEON_CYAN, NEON_ROSE])
                self.effets.particules.append(ParticuleAvancee(x, y, couleur, "explosion", random.uniform(5, 10)))
        
        # Dessiner les particules
        self.dessiner_particules_avancees()
        
        # Titre de victoire
        titre = "LABYRINTHE RÉSOLU !"
        for offset in [(4, 4), (2, 2), (0, 0)]:
            couleur = NOIR_PROFOND if offset != (0, 0) else NEON_VERT
            surface_titre = self.menu.police_titre.render(titre, True, couleur)
            rect_titre = surface_titre.get_rect(center=(LARGEUR // 2 + offset[0], 200 + offset[1]))
            self.ecran.blit(surface_titre, rect_titre)
        
        # Statistiques finales
        stats_finales = [
            f"Temps d'exécution: {self.agent.statistiques['temps_execution']:.3f}s",
            f"Nœuds explorés: {self.agent.statistiques['noeuds_explores']}",
            f"Longueur du chemin: {self.agent.statistiques['longueur_chemin']}",
            f"Efficacité: {self.agent.statistiques['efficacite']:.1f}%"
        ]
        
        y_stats = 300
        for stat in stats_finales:
            surface_stat = self.menu.police_sous_titre.render(stat, True, BLANC_NEIGE)
            rect_stat = surface_stat.get_rect(center=(LARGEUR // 2, y_stats))
            self.ecran.blit(surface_stat, rect_stat)
            y_stats += 50
        
        # Instructions
        instruction = "Appuyez sur ESPACE pour continuer"
        surface_instruction = self.menu.police_normale.render(instruction, True, ARGENT)
        rect_instruction = surface_instruction.get_rect(center=(LARGEUR // 2, HAUTEUR - 100))
        self.ecran.blit(surface_instruction, rect_instruction)
    
    def gerer_evenements(self):
        """Gestionnaire principal des événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Raccourcis globaux
                if event.key == pygame.K_ESCAPE:
                    if self.etat_actuel in [EtatJeu.OPTIONS, EtatJeu.CREDITS, EtatJeu.VICTOIRE]:
                        self.etat_actuel = EtatJeu.MENU_PRINCIPAL
                elif event.key == pygame.K_SPACE:
                    if self.etat_actuel == EtatJeu.VICTOIRE:
                        self.etat_actuel = EtatJeu.MENU_PRINCIPAL
            
            # Gestion selon l'état
            if self.etat_actuel in [EtatJeu.MENU_PRINCIPAL, EtatJeu.SELECTION_DIFFICULTE, 
                                   EtatJeu.OPTIONS, EtatJeu.CREDITS]:
                if not self.gerer_evenements_menu(event):
                    return False
            
            elif self.etat_actuel == EtatJeu.JEU_ACTIF:
                if not self.gerer_evenements_jeu(event):
                    return False
        
        return True
    
    def executer(self):
        """Boucle principale du jeu AAA"""
        print("🎮 MAZE AI - Édition AAA Démarrée!")
        print("🎯 Utilisez la souris et le clavier pour naviguer")
        print("⚡ Préparez-vous pour une expérience visuelle époustouflante!")
        
        en_cours = True
        
        while en_cours:
            # Gestion des événements
            en_cours = self.gerer_evenements()
            
            # Mise à jour selon l'état
            if self.etat_actuel == EtatJeu.JEU_ACTIF:
                self.mettre_a_jour_jeu()
            
            # Rendu selon l'état
            if self.etat_actuel == EtatJeu.MENU_PRINCIPAL:
                self.dessiner_menu_principal()
                
            elif self.etat_actuel == EtatJeu.SELECTION_DIFFICULTE:
                self.dessiner_selection_difficulte()
                
            elif self.etat_actuel == EtatJeu.OPTIONS:
                self.dessiner_menu_options()
                
            elif self.etat_actuel == EtatJeu.CREDITS:
                self.dessiner_menu_credits()
                
            elif self.etat_actuel == EtatJeu.JEU_ACTIF:
                self.dessiner_jeu_complet()
                
            elif self.etat_actuel == EtatJeu.VICTOIRE:
                self.dessiner_ecran_victoire()
            
            # Effet de fade si nécessaire
            if self.effets.fade_alpha > 0:
                fade_surface = pygame.Surface((LARGEUR, HAUTEUR))
                fade_surface.set_alpha(self.effets.fade_alpha)
                fade_surface.fill(NOIR_PROFOND)
                self.ecran.blit(fade_surface, (0, 0))
                self.effets.fade_alpha = max(0, self.effets.fade_alpha - 5)
            
            pygame.display.flip()
            self.horloge.tick(FPS)
        
        print("👋 Merci d'avoir joué à MAZE AI!")
        pygame.quit()
        sys.exit()
    
    def dessiner_menu_options(self):
        """Dessine le menu des options"""
        self.menu.dessiner_fond_anime(self.ecran)
        self.menu.mettre_a_jour_particules_fond()
        
        # Titre
        titre = "OPTIONS"
        surface_titre = self.menu.police_titre.render(titre, True, NEON_ORANGE)
        rect_titre = surface_titre.get_rect(center=(LARGEUR // 2, 150))
        
        # Effet glow
        for offset in [(3, 3), (2, 2), (1, 1), (0, 0)]:
            couleur = NOIR_PROFOND if offset != (0, 0) else NEON_ORANGE
            surface_glow = self.menu.police_titre.render(titre, True, couleur)
            rect_glow = surface_glow.get_rect(center=(rect_titre.centerx + offset[0], rect_titre.centery + offset[1]))
            self.ecran.blit(surface_glow, rect_glow)
        
        # Options disponibles
        options = [
            "🔊 Volume Musique: {}%".format(int(self.volume_musique * 100)),
            "🎵 Volume Effets: {}%".format(int(self.volume_effets * 100)),
            "⚡ Vitesse Animation: {}".format(self.vitesse_animation),
            "🎨 Mode Plein Écran: Activé",
            "",
            "Appuyez sur ÉCHAP pour revenir"
        ]
        
        y_options = 250
        for option in options:
            if option:  # Ne pas afficher les lignes vides
                couleur = BLANC_NEIGE if not option.startswith("Appuyez") else ARGENT
                surface_option = self.menu.police_normale.render(option, True, couleur)
                rect_option = surface_option.get_rect(center=(LARGEUR // 2, y_options))
                self.ecran.blit(surface_option, rect_option)
            y_options += 50
    
    def dessiner_menu_credits(self):
        """Dessine le menu des crédits"""
        self.menu.dessiner_fond_anime(self.ecran)
        self.menu.mettre_a_jour_particules_fond()
        
        # Titre
        titre = "CRÉDITS"
        surface_titre = self.menu.police_titre.render(titre, True, NEON_ROSE)
        rect_titre = surface_titre.get_rect(center=(LARGEUR // 2, 120))
        
        # Effet glow
        for offset in [(3, 3), (2, 2), (1, 1), (0, 0)]:
            couleur = NOIR_PROFOND if offset != (0, 0) else NEON_ROSE
            surface_glow = self.menu.police_titre.render(titre, True, couleur)
            rect_glow = surface_glow.get_rect(center=(rect_titre.centerx + offset[0], rect_titre.centery + offset[1]))
            self.ecran.blit(surface_glow, rect_glow)
        
        # Crédits détaillés
        credits = [
            "🤖 DÉVELOPPEMENT",
            "Intelligence Artificielle: Algorithme A*",
            "Optimisation pathfinding avancée",
            "",
            "🎨 DESIGN VISUEL",
            "Effets de particules temps réel",
            "Système d'animation fluide",
            "Interface utilisateur moderne",
            "",
            "🎮 EXPÉRIENCE UTILISATEUR",
            "Contrôles intuitifs",
            "Visualisation étape par étape",
            "Statistiques de performance",
            "",
            "⚡ TECHNOLOGIES",
            "Python 3.9+ & Pygame",
            "Rendu 60 FPS optimisé",
            "Algorithmes de génération procédurale",
            "",
            "🏆 ÉDITION AAA",
            "Qualité studio professionnel",
            "Effets visuels spectaculaires",
            "",
            "Appuyez sur ÉCHAP pour revenir"
        ]
        
        y_credits = 180
        for credit in credits:
            if credit.startswith("🤖") or credit.startswith("🎨") or credit.startswith("🎮") or credit.startswith("⚡") or credit.startswith("🏆"):
                # Titres de section
                couleur = NEON_CYAN
                police = self.menu.police_sous_titre
            elif credit.startswith("Appuyez"):
                couleur = ARGENT
                police = self.menu.police_normale
            elif credit == "":
                y_credits += 20
                continue
            else:
                couleur = BLANC_NEIGE
                police = self.menu.police_normale
            
            surface_credit = police.render(credit, True, couleur)
            rect_credit = surface_credit.get_rect(center=(LARGEUR // 2, y_credits))
            self.ecran.blit(surface_credit, rect_credit)
            y_credits += 30
    
    def dessiner_jeu_complet(self):
        """Dessine l'écran de jeu complet avec tous les effets"""
        # Fond dégradé élégant
        for y in range(HAUTEUR):
            ratio = y / HAUTEUR
            r = int(NOIR_PROFOND[0] + (NOIR_ELEGANCE[0] - NOIR_PROFOND[0]) * ratio)
            g = int(NOIR_PROFOND[1] + (NOIR_ELEGANCE[1] - NOIR_PROFOND[1]) * ratio)
            b = int(NOIR_PROFOND[2] + (NOIR_ELEGANCE[2] - NOIR_PROFOND[2]) * ratio)
            pygame.draw.line(self.ecran, (r, g, b), (0, y), (LARGEUR, y))
        
        # Labyrinthe avec effets AAA
        self.dessiner_labyrinthe_complet()
        
        # Particules avancées
        self.dessiner_particules_avancees()
        
        # Interface de jeu
        self.dessiner_interface_jeu_complete()
        
        # HUD d'informations en temps réel
        self.dessiner_hud_temps_reel()
    
    def dessiner_hud_temps_reel(self):
        """Dessine le HUD avec informations temps réel"""
        if not self.agent:
            return
        
        # Calculer shake offset
        shake_x = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        shake_y = random.randint(-self.effets.shake_camera, self.effets.shake_camera) if self.effets.shake_camera > 0 else 0
        
        # Barre de progression globale (en haut de l'écran)
        if hasattr(self.agent, '_liste_ouverte') and not self.agent.algorithme_termine:
            # Estimer le progrès basé sur la distance heuristique moyenne
            progres_estime = min(100, (self.agent.statistiques['noeuds_explores'] / 
                                     max(1, self.labyrinthe.largeur * self.labyrinthe.hauteur * 0.1)) * 100)
            
            # Barre de progression
            barre_largeur = 400
            barre_hauteur = 12
            barre_x = (LARGEUR - barre_largeur) // 2 + shake_x
            barre_y = 20 + shake_y
            
            # Fond de la barre
            fond_rect = pygame.Rect(barre_x, barre_y, barre_largeur, barre_hauteur)
            pygame.draw.rect(self.ecran, NOIR_PROFOND, fond_rect)
            pygame.draw.rect(self.ecran, BLANC_PUR, fond_rect, 2)
            
            # Progression
            if progres_estime > 0:
                prog_rect = pygame.Rect(barre_x, barre_y, int(barre_largeur * progres_estime / 100), barre_hauteur)
                
                # Dégradé de couleur selon le progrès
                if progres_estime < 30:
                    couleur = ROUGE_CRIMSON
                elif progres_estime < 70:
                    couleur = NEON_ORANGE
                else:
                    couleur = NEON_VERT
                
                pygame.draw.rect(self.ecran, couleur, prog_rect)
                
                # Effet glow
                glow_rect = pygame.Rect(prog_rect.x - 2, prog_rect.y - 2, 
                                      prog_rect.width + 4, prog_rect.height + 4)
                glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
                glow_surface.set_alpha(80)
                glow_surface.fill(couleur)
                self.ecran.blit(glow_surface, glow_rect)
            
            # Texte de progression
            texte_progres = f"Exploration: {progres_estime:.1f}%"
            surface_progres = self.interface_jeu.police_stats.render(texte_progres, True, BLANC_PUR)
            rect_progres = surface_progres.get_rect(center=(barre_x + barre_largeur // 2, barre_y - 20))
            
            # Ombre du texte
            surface_ombre = self.interface_jeu.police_stats.render(texte_progres, True, NOIR_PROFOND)
            rect_ombre = surface_ombre.get_rect(center=(rect_progres.centerx + 1, rect_progres.centery + 1))
            self.ecran.blit(surface_ombre, rect_ombre)
            self.ecran.blit(surface_progres, rect_progres)
        
        # Indicateur de mode
        mode_texte = "🤖 MODE AUTO" if self.mode_automatique else "👆 MODE MANUEL"
        couleur_mode = NEON_VERT if self.mode_automatique else NEON_CYAN
        surface_mode = self.interface_jeu.police_stats.render(mode_texte, True, couleur_mode)
        self.ecran.blit(surface_mode, (20 + shake_x, HAUTEUR - 40 + shake_y))
        
        # FPS Counter (coin supérieur droit)
        fps_actuel = int(self.horloge.get_fps())
        couleur_fps = NEON_VERT if fps_actuel >= 50 else (NEON_ORANGE if fps_actuel >= 30 else ROUGE_CRIMSON)
        texte_fps = f"FPS: {fps_actuel}"
        surface_fps = self.interface_jeu.police_mini.render(texte_fps, True, couleur_fps)
        self.ecran.blit(surface_fps, (LARGEUR - 100 + shake_x, 5 + shake_y))

# Point d'entrée du jeu
if __name__ == "__main__":
    try:
        jeu = JeuAAA()
        jeu.executer()
    except Exception as e:
        import traceback
        print("❌ ERREUR CRITIQUE DÉTECTÉE ❌")
        print("=" * 60)
        print("TRACEBACK COMPLET:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        print(f"Type d'erreur: {type(e).__name__}")
        print(f"Message: {e}")
        print("=" * 60)
        
        pygame.quit()
        sys.exit(1)