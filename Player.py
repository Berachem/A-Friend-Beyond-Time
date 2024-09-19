



import arcade
import math

from constants import *

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class PlayerCharacter(arcade.Sprite):
    """Player Sprite with animations for walking and idle states, no jumping"""

    def __init__(self):
        # Initialiser avec une image statique (idle)
        super().__init__()

        # Par défaut, le personnage fait face à droite
        self.facing_direction = RIGHT_FACING

        # Utilisé pour les séquences d'images
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Chemin principal pour les fichiers d'animation
        main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"

        # Charger les textures idle (statique)
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # Charger les textures de marche
        self.walk_textures = []
        for i in range(8):  # 8 frames pour la marche
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Définir la texture initiale
        self.texture = self.idle_texture_pair[0]

        # Points de la hitbox basés sur la texture initiale
        self.set_hit_box(self.texture.hit_box_points)

        # Initialiser la vélocité du joueur
        self.change_x = 0
        self.change_y = 0

    def update_animation(self, delta_time: float = 1 / 60):
        """ Gérer l'animation en fonction du mouvement du personnage """

        # Si le joueur est immobile (idle)
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Si le joueur marche, changer les textures de marche
        self.cur_texture += 1
        if self.cur_texture >= 8 * 5:  # 8 frames avec une vitesse de changement
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture //
                                          5][self.facing_direction]

    def update(self):
        """ Update player position """
        self.center_x += self.change_x
        self.center_y += self.change_y

        # # Limiter le joueur aux bords de l'écran verticalement
        # if self.center_y < 0:
        #     self.center_y = 0
        # if self.center_y > SCREEN_HEIGHT:
        #     self.center_y = SCREEN_HEIGHT

        # Limiter le joueur aux bords de l'écran horizontalement
        if self.left < 0:
            self.left = 0
        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH

        # Limiter le joueur aux bords de l'écran verticalement
        if self.bottom < 0:
            self.bottom = 0
        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT
        # Mettre à jour l'animation du joueur
        self.update_animation()

    def on_key_press(self, key, modifiers):
        """ Gérer les touches de déplacement """
        if key == arcade.key.RIGHT:
            self.change_x = PLAYER_MOVEMENT_SPEED
            self.facing_direction = RIGHT_FACING
        elif key == arcade.key.LEFT:
            self.change_x = -PLAYER_MOVEMENT_SPEED
            self.facing_direction = LEFT_FACING
        elif key == arcade.key.UP:
            self.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.change_y = -PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """ Gérer le relâchement des touches """
        if key == arcade.key.RIGHT or key == arcade.key.LEFT:
            self.change_x = 0
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.change_y = 0