
import arcade
from utils.GameOverView import GameOverView
from constants import *
from utils.GameView import BaseMapView

class CityMap(BaseMapView):
    """ Fourth map view """

    def __init__(self, game_view):
        super().__init__(game_view)
        # Variable pour stocker le nom du fichier d'arrière-plan
        self.background_file_name = None
        self.background = None
        self.flames = arcade.SpriteList()  # Use SpriteList instead of a regular list
        self.update_background()
        self.add_flames()  # Initialize flames in the map

    def update_background(self):
        """Update background image based on temporal state."""
        # Définir le nom du fichier d'arrière-plan en fonction de l'état temporel
        self.background_file_name = f"assets/images/backgrounds/city_map_{self.game_view.temporal_state}.png"
        self.background = arcade.Sprite(self.background_file_name)

        # Ajuster l'échelle de l'arrière-plan pour correspondre à la taille de la fenêtre
        image_width = self.background.width
        image_height = self.background.height

        # Mettre à l'échelle pour correspondre à la taille de la fenêtre
        self.background.scale = max(
            SCREEN_WIDTH / image_width, SCREEN_HEIGHT / image_height)

        # Positionner l'arrière-plan au centre de l'écran
        self.background.center_x = SCREEN_WIDTH // 2
        self.background.center_y = SCREEN_HEIGHT // 2

    def add_flames(self):
        """Add flame sprites to the city map in the past."""
        flame_positions = [(425, 350), (975, 550), (1200, 550),
                           (825, 115)]  # Example positions
        for pos in flame_positions:
            # Fixed path to flame sprite
            flame = arcade.Sprite("assets/images/flame.png", 0.2)
            flame.center_x, flame.center_y = pos
            self.flames.append(flame)  # This now adds to the SpriteList

    def on_draw(self):
        """ Draw the map. """
        self.background.draw()

        rectangle_height = 200  # Increased to fit all text
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT -
            150, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK + (200,)
        )

        # Draw the "At Killy's home" message centered inside the rectangle
        arcade.draw_text("City Mission ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                         arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

        # Draw each part of the story, ensuring long lines are wrapped within the screen width
        arcade.draw_text(
            "Reconnect with your friend by rejoining the weekly drawing class you both loved.",
            40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )

        arcade.draw_text(
            "You missed the chance before due to your car breaking down.",
            40, SCREEN_HEIGHT - 205,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )
        arcade.draw_text(
            "But now, with a second chance, take action to rebuild the friendship through shared hobbies.",
            40, SCREEN_HEIGHT - 235,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )

        # Dessiner des objets en fonction de l'état temporel
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Busy Streets", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Silent Ruins", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)
            # Draw flames in the past
            self.flames.draw()  # Efficiently draws all flames in the SpriteList

    def on_update(self, delta_time):
        """Met à jour l'arrière-plan si l'état temporel change."""

        # Comparer l'état temporel actuel avec celui du fichier chargé
        expected_background_file = f"assets/images/backgrounds/city_map_{self.game_view.temporal_state}.png"
        if self.background_file_name != expected_background_file:
            self.update_background()

        # Vérifier les collisions avec les flammes
        if self.game_view.temporal_state == PAST:  # Seulement dans le passé
            flames_hit_list = arcade.check_for_collision_with_list(
                self.game_view.player_sprite, self.flames)

            if flames_hit_list:
                # Si une collision est détectée, revenir à la première map
                game_over = GameOverView()
                self.game_view.window.show_view(
                    game_over)  # Use game_view.window

    def on_key_press(self, key, modifiers):
        """ Disable key press during the introduction """
        pass

    def on_key_release(self, key, modifiers):
        """ Disable key release during the introduction """
        pass

    def on_hide_view(self):
        """ Disable the manager when switching to another view """
        self.manager.disable()