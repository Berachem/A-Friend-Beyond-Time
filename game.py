import arcade

# --- Constants ---
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Lost in Time, Found in Friendship"

# Temporal Constants
PAST = "past"
PRESENT = "present"

TILE_SCALING = 0.5
CHARACTER_SCALING = TILE_SCALING * 2

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 15
RIGHT_FACING = 0
LEFT_FACING = 1

PLAYER_START_X = 100
PLAYER_START_Y = 100
PLAYER_BORDER_PADDING = 10  # Padding for detecting map change


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]


class PlayerCharacter(arcade.Sprite):
    """Player Sprite with animations for walking, jumping, and idle states"""

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

        # Charger les textures de saut
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")

        # Charger les textures de chute
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

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
        self.jumping = False

    def update_animation(self, delta_time: float = 1 / 60):
        """ Gérer l'animation en fonction du mouvement du personnage """

        # Si le joueur est en l'air, utiliser les textures de saut ou de chute
        if self.change_y > 0:
            self.texture = self.jump_texture_pair[self.facing_direction]
            return
        elif self.change_y < 0:
            self.texture = self.fall_texture_pair[self.facing_direction]
            return

        # Si le joueur est immobile (idle)
        if self.change_x == 0:
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

        # Limiter le joueur aux bords de l'écran verticalement
        if self.center_y < 0:
            self.center_y = 0
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = SCREEN_HEIGHT

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
        elif key == arcade.key.UP and not self.jumping:
            self.change_y = PLAYER_JUMP_SPEED
            self.jumping = True

    def on_key_release(self, key, modifiers):
        """ Gérer le relâchement des touches """
        if key == arcade.key.RIGHT or key == arcade.key.LEFT:
            self.change_x = 0
        elif key == arcade.key.UP:
            self.jumping = False


class GameView(arcade.View):
    """
    Main game class with 4 views
    """

    def __init__(self):
        super().__init__()
        self.player_sprite = None
        self.temporal_state = PRESENT  # Current temporal state
        self.current_view = 0          # Keep track of the current view
        self.physics_engine = None

        # HUD elements
        self.time_elapsed = 0
        self.items_collected = 0

        # Create the views (levels)
        self.views = [
            MapView1(self),
            MapForest(self),
            MapWinter(self),
            MapCITY(self)
        ]

    def setup(self):
        """ Set up the game here. """
        self.player_sprite = PlayerCharacter()

    def on_draw(self):
        """ Draw the current view based on the current temporal state. """
        self.clear()

        # Draw the current view
        self.views[self.current_view].on_draw()

        # Draw the player
        self.player_sprite.draw()

        # Draw HUD (top right)
        arcade.draw_text(f"Time: {self.time_elapsed:.1f}s", SCREEN_WIDTH -
                         150, SCREEN_HEIGHT - 40, arcade.color.WHITE, 20)
        arcade.draw_text(f"Collected: {self.items_collected}", SCREEN_WIDTH -
                         150, SCREEN_HEIGHT - 70, arcade.color.WHITE, 20)

        # Draw instruction to change time
        arcade.draw_text("Press Space to change of time...",
                         SCREEN_WIDTH // 2 - 100, 10, arcade.color.WHITE, 15)

    def on_key_press(self, key, modifiers):
        """ Handle key press for moving the player and switching temporal state. """
        if key == arcade.key.SPACE:
            # Switch temporal state
            if self.temporal_state == PRESENT:
                self.temporal_state = PAST
            else:
                self.temporal_state = PRESENT

        # Handle player movement
        if key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """ Handle key release for player movement. """
        if key in [arcade.key.RIGHT, arcade.key.LEFT]:
            self.player_sprite.change_x = 0
        elif key in [arcade.key.UP, arcade.key.DOWN]:
            self.player_sprite.change_y = 0

    def on_update(self, delta_time):
        """ Update the current view and check for map transitions. """
        self.player_sprite.update()
        self.time_elapsed += delta_time
        self.views[self.current_view].on_update(delta_time)

        # Check if the player has reached the right or left edge
        if self.player_sprite.center_x > SCREEN_WIDTH - PLAYER_BORDER_PADDING:
            # Player reached the right edge, go to the next map
            self.current_view = (self.current_view + 1) % len(self.views)
            self.player_sprite.center_x = PLAYER_BORDER_PADDING  # Reset player to left edge
        elif self.player_sprite.center_x < PLAYER_BORDER_PADDING:
            # Prevent transition from map 1 to map 4 by going left
            if self.current_view == 0:
                self.player_sprite.center_x = PLAYER_BORDER_PADDING  # Keep player on map 1
            else:
                self.current_view = (self.current_view - 1) % len(self.views)
                self.player_sprite.center_x = SCREEN_WIDTH - \
                    PLAYER_BORDER_PADDING  # Reset player to right edge


class BaseMapView:
    """ Base class for all map views """

    def __init__(self, game_view):
        self.game_view = game_view  # Reference to the GameView
        self.player_sprite = game_view.player_sprite

    def on_draw(self):
        pass

    def on_update(self, delta_time):
        pass


class MapView1(BaseMapView):
    """ First map view: House """

    def __init__(self, game_view):
        super().__init__(game_view)
        # Load the background image
        self.background = arcade.Sprite(
            "assets/images/backgrounds/house_map_present.png")

        # Adjust the scale of the background to fit the screen
        image_width = self.background.width
        image_height = self.background.height

        # Scale to match the window size
        self.background.scale = max(
            SCREEN_WIDTH / image_width, SCREEN_HEIGHT / image_height)

        # Set the background position to the center of the screen
        self.background.center_x = SCREEN_WIDTH // 2
        self.background.center_y = SCREEN_HEIGHT // 2

    def on_draw(self):
        """ Draw the map. """

        # Draw the background
        self.background.draw()

        # Draw the map details
        arcade.draw_text("The Kitchen", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)

        # Draw objects based on temporal state
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Cozy Kitchen ", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)

            oven = arcade.Sprite(
                ":resources:images/tiles/brickTextureWhite.png", TILE_SCALING)
            oven.center_x = 200
            oven.center_y = 150
            oven.draw()

        else:
            arcade.draw_text("Past: Abandoned Kitchen ", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)

            # Add kitchen props

            fridge = arcade.Sprite(
                ":resources:images/tiles/lockYellow.png", TILE_SCALING)
            fridge.center_x = 300
            fridge.center_y = 150

            fridge.draw()


class MapWinter(BaseMapView):
    """ Second map view """

    def __init__(self, game_view):
        super().__init__(game_view)
        self.letter_collected = False
        self.letter = None

        # Variable pour stocker le nom du fichier d'arrière-plan
        self.background_file_name = None
        self.background = None
        self.update_background()

    def update_background(self):
        """Update background image based on temporal state."""
        # Définir le nom du fichier d'arrière-plan en fonction de l'état temporel
        self.background_file_name = f"assets/images/backgrounds/winter_map_{
            self.game_view.temporal_state}.png"
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

    def on_draw(self):
        """ Draw the map. """

        # Dessiner l'arrière-plan
        self.background.draw()

        arcade.draw_text("The Winter Land", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)

        # Dessiner des objets en fonction de l'état temporel

        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Snowy Landscape", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)

            if not self.letter_collected:
                # Si la lettre n'a pas été collectée, on la dessine
                if self.letter is None:
                    self.letter = arcade.Sprite(
                        "assets/images/items/letter.png", 0.10)
                    self.letter.center_x = 400
                    self.letter.center_y = 400
                self.letter.draw()

        else:
            arcade.draw_text("Past: Frozen Wasteland", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)

            # Ajouter des objets dans le passé, par exemple des pics
            spikes = arcade.Sprite(
                ":resources:images/enemies/saw.png", TILE_SCALING)
            spikes.center_x = SCREEN_WIDTH // 2
            spikes.center_y = SCREEN_HEIGHT // 2
            spikes.draw()

            # Ajouter un personnage féminin à côté des pics
            female_adventurer = arcade.Sprite(
                ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", CHARACTER_SCALING)
            female_adventurer.center_x = SCREEN_WIDTH // 2 + 200
            female_adventurer.center_y = SCREEN_HEIGHT // 2
            female_adventurer.draw()

    def on_update(self, delta_time):
        """ Handle updates such as collecting letters and checking collisions. """
        # Vérifier la collecte de la lettre dans le présent
        if self.game_view.temporal_state == PRESENT and not self.letter_collected:
            if self.letter and self.game_view.player_sprite:
                if abs(self.game_view.player_sprite.center_x - self.letter.center_x) < 50 and abs(self.game_view.player_sprite.center_y - self.letter.center_y) < 50:
                    self.letter_collected = True
                    # Supprimer la lettre une fois collectée
                    self.letter.remove_from_sprite_lists()
                    self.game_view.items_collected += 1

        # Vérifier les collisions avec les spikes dans le passé
        if self.game_view.temporal_state == PAST and self.game_view.player_sprite:
            if abs(self.game_view.player_sprite.center_x - SCREEN_WIDTH // 2) < 50 and abs(self.game_view.player_sprite.center_y - SCREEN_HEIGHT // 2) < 50:
                # Redémarrer le jeu en cas de collision avec les spikes
                self.game_view.setup()

        # Mettre à jour l'arrière-plan si la temporalité change
        expected_background_file = f"assets/images/backgrounds/winter_map_{
            self.game_view.temporal_state}.png"
        if self.background_file_name != expected_background_file:
            self.update_background()


class MapForest(BaseMapView):
    """ Third map view """

    def __init__(self, game_view):
        super().__init__(game_view)
        # Variable pour stocker le nom du fichier d'arrière-plan
        self.background_file_name = None
        self.background = None
        self.update_background()

    def update_background(self):
        """Update background image based on temporal state."""
        # Définir le nom du fichier d'arrière-plan en fonction de l'état temporel
        self.background_file_name = f"assets/images/backgrounds/forest_map_{
            self.game_view.temporal_state}.png"
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

    def on_draw(self):
        """ Draw the map. """

        self.background.draw()

        arcade.draw_text("The Forest", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)

        # Dessiner des objets en fonction de l'état temporel

        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Lush Forest", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Burnt Forest", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)

    def on_update(self, delta_time):
        """Met à jour l'arrière-plan si l'état temporel change."""
        # Comparer l'état temporel actuel avec celui du fichier chargé
        expected_background_file = f"assets/images/backgrounds/forest_map_{
            self.game_view.temporal_state}.png"
        if self.background_file_name != expected_background_file:
            self.update_background()


class MapCITY(BaseMapView):
    """ Fourth map view """

    def __init__(self, game_view):
        super().__init__(game_view)
        # Variable pour stocker le nom du fichier d'arrière-plan
        self.background_file_name = None
        self.background = None
        self.update_background()

    def update_background(self):
        """Update background image based on temporal state."""
        # Définir le nom du fichier d'arrière-plan en fonction de l'état temporel
        self.background_file_name = f"assets/images/backgrounds/city_map_{
            self.game_view.temporal_state}.png"
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

    def on_draw(self):
        """ Draw the map. """
        self.background.draw()

        arcade.draw_text("The City", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
        # Dessiner des objets en fonction de l'état temporel
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Busy Streets", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Silent Ruins", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)

    def on_update(self, delta_time):
        """Met à jour l'arrière-plan si l'état temporel change."""
        # Comparer l'état temporel actuel avec celui du fichier chargé
        expected_background_file = f"assets/images/backgrounds/city_map_{
            self.game_view.temporal_state}.png"
        if self.background_file_name != expected_background_file:
            self.update_background()


def main():
    """ Main function """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
