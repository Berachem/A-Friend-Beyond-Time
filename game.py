import arcade
import arcade.gui

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


class GameView(arcade.View):
    """
    Main game class with 4 views
    """

    def restart(self):
        """ Reset game state to start over """
        self.setup()  # Reinitialize the game state
        self.time_elapsed = 0
        self.items_collected = 0
        self.current_view = 0
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        # Assuming views need to be reset
        self.views[self.current_view].setup()

    def __init__(self):
        super().__init__()
        # Music variables
        self.background_music = None  # Music for the introduction
        self.present_music = None     # Music for the present
        self.past_music = None        # Music for the past
        self.current_music_player = None  # Current music player instance


        self.player_sprite = None
        self.temporal_state = PRESENT  # Current temporal state
        self.current_view = 0          # Keep track of the current view
        self.physics_engine = None

        # HUD elements
        self.time_elapsed = 0
        self.items_collected = 0

        # Load the torch image sprite
        self.torch_sprite = arcade.Sprite(
            ":resources:images/tiles/torch2.png", 0.30)

        # Set the position of the torch sprite where the "Time" text was
        self.torch_sprite.center_x = SCREEN_WIDTH - 100
        self.torch_sprite.center_y = SCREEN_HEIGHT - 30

        self.star_sprite = arcade.Sprite(
            ":resources:images/items/star.png", 0.5)
        self.star_sprite.center_x = SCREEN_WIDTH - 100
        self.star_sprite.center_y = SCREEN_HEIGHT - 60

        # Create the views (levels)
        self.views = [
            Introduction(self),
            MapForest(self),
            MapWinter(self),
            MapCITY(self)
        ]

    def change_view(self, new_view_index):
        """
        Change the current view to the specified map view index.
        This also resets the player's position.
        """
        self.current_view = new_view_index
        self.player_sprite.center_x = PLAYER_START_X  # Réinitialiser la position X
        self.player_sprite.center_y = PLAYER_START_Y  # Réinitialiser la position Y


    def change_music(self, new_music):
        """ Stop the current music and play new music """
        if self.current_music_player:
            arcade.stop_sound(self.current_music_player)
        self.current_music_player = arcade.play_sound(new_music, volume=0.5, looping=True)

    def setup(self):
        """ Set up the game here. """
        self.player_sprite = PlayerCharacter()
        # Set the player's position to the center of the screen for the introduction
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
         
        # Load and play background music for the introduction
        self.background_music = arcade.load_sound("assets/sounds/intro.mp3")
        self.current_music_player = arcade.play_sound(self.background_music, volume=0.5, looping=True)

        # Load music for present and past
        self.present_music = arcade.load_sound("assets/sounds/present.mp3")
        self.past_music = arcade.load_sound("assets/sounds/passe.mp3")

    def format_time(self, seconds):
        """ Format the elapsed time into hours, minutes, and seconds without showing zero units. """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        time_str = ""
        if hours > 0:
            time_str += f"{hours}h "
        if minutes > 0 or hours > 0:
            time_str += f"{minutes}m "
        time_str += f"{seconds}s"

        return time_str.strip()

    def on_draw(self):
        """ Draw the current view based on the current temporal state. """
        self.clear()

        # Draw the current view
        self.views[self.current_view].on_draw()

        # Draw the player
        self.player_sprite.draw()

        # Format the time in hours, minutes, and seconds
        formatted_time = self.format_time(self.time_elapsed)

        # Draw a black transparent background rectangle for time and collected items
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50, 200, 80, arcade.color.BLACK + (150,))

        # Draw the formatted time next to the torch image
        arcade.draw_text(f"{formatted_time}", SCREEN_WIDTH - 80, SCREEN_HEIGHT - 40,
                         arcade.color.WHITE, 20, bold=True)

        # Draw the torch sprite (replacing the "Time" text)
        self.torch_sprite.draw()

        # Draw the star sprite for collected items
        self.star_sprite.draw()

        # Draw the collected items number next to the star
        arcade.draw_text(f"{self.items_collected}", SCREEN_WIDTH - 75, SCREEN_HEIGHT - 70,
                         arcade.color.WHITE, 20, bold=True)

    def on_key_press(self, key, modifiers):
        """ Handle key press for moving the player and switching temporal state. """
        if key == arcade.key.SPACE:
            # Switch temporal state
            if self.temporal_state == PRESENT:
                self.temporal_state = PAST
                self.change_music(self.past_music)  # Play past music

            else:
                self.temporal_state = PRESENT
                self.change_music(self.present_music)  # Play present music

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


class Introduction(BaseMapView):
    """ First map view: House """

    def __init__(self, game_view):
        super().__init__(game_view)
        # Load the background image
        self.background = arcade.Sprite(
            "assets/images/backgrounds/house_map_present.png")

        # Adjust the scale of the background to fit the screen
        image_width = self.background.width
        image_height = self.background.height
        self.background.scale = max(
            SCREEN_WIDTH / image_width, SCREEN_HEIGHT / image_height)
        self.background.center_x = SCREEN_WIDTH // 2
        self.background.center_y = SCREEN_HEIGHT // 2

        # Create the UI Manager for the button
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Create the "Let's go" button
        self.lets_go_button = arcade.gui.UIFlatButton(
            text="Let's go !", width=200)

        # Center the button at the bottom of the screen
        self.v_box = arcade.gui.UIBoxLayout()
        self.v_box.add(self.lets_go_button.with_space_around(bottom=240))
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="bottom", child=self.v_box)
        )

        # Set up the button click event
        self.lets_go_button.on_click = self.on_lets_go_click

    def on_lets_go_click(self, event):
        """Switch to the next map when the button is clicked."""
         # Stop the introduction music
        if self.game_view.current_music_player:
            arcade.stop_sound(self.game_view.current_music_player)

        # Play the present music
        self.game_view.change_music(self.game_view.present_music)

        # reset player position to left edge
        self.game_view.player_sprite.center_x = PLAYER_BORDER_PADDING + 60
        self.game_view.player_sprite.center_y = SCREEN_HEIGHT // 2 - 120

        self.game_view.current_view = (
            self.game_view.current_view + 1) % len(self.game_view.views)

    def on_draw(self):
        """ Draw the map. """
        # Draw the background
        self.background.draw()

        # Draw a semi-transparent background box for the text
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 20, 160, arcade.color.BLACK + (200,))

        # Draw the map details
        arcade.draw_text("At home", 20, SCREEN_HEIGHT -
                         80, arcade.color.GREEN, 24)

        # Draw the introduction text
        arcade.draw_text(
            "Arrrrffff ! You and Kelly are fighting because you broke her favorite paint palette and got paint all over the floor....",
            20, SCREEN_HEIGHT - 150, arcade.color.WHITE, 18, width=SCREEN_WIDTH - 40
        )
        arcade.draw_text(
            "She's so mad that she's left the house and you're not sure where she's gone.",
            20, SCREEN_HEIGHT - 180, arcade.color.WHITE, 18, width=SCREEN_WIDTH - 40
        )
        arcade.draw_text(
            "You need to find her and apologize before she gets too far away.",
            20, SCREEN_HEIGHT - 210, arcade.color.WHITE, 18, width=SCREEN_WIDTH - 40
        )

        # Draw the button
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        """ Disable key press during the introduction """
        pass

    def on_key_release(self, key, modifiers):
        """ Disable key release during the introduction """
        pass

    def on_hide_view(self):
        """ Disable the manager when switching to another view """
        self.manager.disable()


class MapWinter(BaseMapView):
    """ Second map view """

    def __init__(self, game_view):
        super().__init__(game_view)
        self.broken_heart_collected = False
        self.normal_heart_collected = False
        self.broken_heart = None
        self.normal_heart = None

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

            if not self.broken_heart_collected:
                # Si le cœur brisé n'a pas été collecté, on le dessine
                if self.broken_heart is None:
                    self.broken_heart = arcade.Sprite(
                        # Augmenter la taille avec scale 0.20
                        "assets/images/items/coeurBrise.png", 0.30)
                    self.broken_heart.center_x = 400
                    self.broken_heart.center_y = 400
                self.broken_heart.draw()

        else:
            arcade.draw_text("Past: Frozen Wasteland", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 30)

            if not self.normal_heart_collected:
                # Si le cœur normal n'a pas été collecté, on le dessine
                if self.normal_heart is None:
                    self.normal_heart = arcade.Sprite(
                        "assets/images/items/coeur.png", 0.30)  # Augmenter la taille avec scale 0.20
                    self.normal_heart.center_x = 1150
                    self.normal_heart.center_y = 350
                self.normal_heart.draw()

    def on_update(self, delta_time):
        """ Handle updates such as collecting hearts and checking collisions. """
        # Vérifier la collecte du cœur brisé dans le présent
        if self.game_view.temporal_state == PRESENT and not self.broken_heart_collected:
            if self.broken_heart and self.game_view.player_sprite:
                if abs(self.game_view.player_sprite.center_x - self.broken_heart.center_x) < 50 and abs(self.game_view.player_sprite.center_y - self.broken_heart.center_y) < 50:
                    self.broken_heart_collected = True
                    # Supprimer le cœur brisé une fois collecté
                    self.broken_heart.remove_from_sprite_lists()
                    # Afficher la vue Game Over
                    game_over_view = GameOverView()
                    self.game_view.window.show_view(game_over_view)

        # Vérifier la collecte du cœur normal dans le passé
        if self.game_view.temporal_state == PAST and not self.normal_heart_collected:
            if self.normal_heart and self.game_view.player_sprite:
                if abs(self.game_view.player_sprite.center_x - self.normal_heart.center_x) < 50 and abs(self.game_view.player_sprite.center_y - self.normal_heart.center_y) < 50:
                    self.normal_heart_collected = True
                    # Supprimer le cœur normal une fois collecté
                    self.normal_heart.remove_from_sprite_lists()
                    # Incrémenter le compteur des objets collectés
                    self.game_view.items_collected += 1

                    # Redirection vers la carte City
                    # L'index 3 correspond à la MapCity
                    self.game_view.change_view(3)

        # Mettre à jour l'arrière-plan si la temporalité change
        expected_background_file = f"assets/images/backgrounds/winter_map_{
            self.game_view.temporal_state}.png"
        if self.background_file_name != expected_background_file:
            self.update_background()


class MapForest(BaseMapView):
    """ Third map view """

    def __init__(self, game_view):
        super().__init__(game_view)
        self.letter_collected = False
        self.letter = None
        self.show_dialog = False  # Flag to show the dialog window
        self.dialog_ui = None  # UIManager for the dialog
        # Variable pour stocker le nom du fichier d'arrière-plan
        self.background_file_name = None
        self.background = None
        self.update_background()

        # Setup the dialog UI manager
        self.setup_ui()

    def setup_ui(self):
        """ Setup the UI manager and the dialog box. """
        self.dialog_ui = arcade.gui.UIManager()
        self.dialog_ui.enable()

        # Create a box layout to organize the dialog and the button
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the dialog text
        self.dialog_text = arcade.gui.UILabel(
            text="Vous avez écrit une lettre pour Kelly !",
            text_color=arcade.color.BLACK,
            font_size=18,
            width=500,
            align="center",
        )

        self.v_box.add(self.dialog_text.with_space_around(bottom=20))

        # Create the "OK" button
        ok_button = arcade.gui.UIFlatButton(text="OK", width=200)
        self.v_box.add(ok_button)

        # Attach the button click event
        ok_button.on_click = self.on_ok_click

        # Add the UIBoxLayout with all widgets to the UIManager
        self.dialog_ui.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

    def on_draw(self):
        """ Draw the map and the dialog if applicable. """
        self.background.draw()

        arcade.draw_text("The Forest", 10, SCREEN_HEIGHT -
                         60, arcade.color.GREEN, 24)

        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Lush Forest", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
            if not self.letter_collected:
                if self.letter is None:
                    self.letter = arcade.Sprite(
                        "assets/images/items/letter.png", 0.10)
                    self.letter.center_x = 400
                    self.letter.center_y = 400
                self.letter.draw()

        else:
            arcade.draw_text("Past: Burnt Forest", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)
            spikes = arcade.Sprite(
                ":resources:images/enemies/saw.png", TILE_SCALING)
            spikes.center_x = SCREEN_WIDTH // 2
            spikes.center_y = SCREEN_HEIGHT // 2
            spikes.draw()

            female_adventurer = arcade.Sprite(
                ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", CHARACTER_SCALING)
            female_adventurer.center_x = SCREEN_WIDTH // 2 + 200
            female_adventurer.center_y = SCREEN_HEIGHT // 2
            female_adventurer.draw()

        # If the dialog is active, draw the dialog
        if self.show_dialog:
            # Draw the rectangle for the dialog background
            arcade.draw_rectangle_filled(
                # Beige with transparency
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 450, 200, (245,
                                                                  245, 220, 250)
            )

            # Draw the UI elements
            self.dialog_ui.draw()

    def on_ok_click(self, event):
        """ Handle click event for the OK button. """
        self.show_dialog = False  # Hide the dialog
        self.dialog_ui.disable()  # Disable the UI when dialog is closed

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

    def on_update(self, delta_time):
        """ Update the map and handle letter collection. """
        if self.game_view.temporal_state == PRESENT and not self.letter_collected:
            if self.letter and self.game_view.player_sprite:
                if abs(self.game_view.player_sprite.center_x - self.letter.center_x) < 50 and abs(self.game_view.player_sprite.center_y - self.letter.center_y) < 50:
                    self.letter_collected = True
                    self.letter.remove_from_sprite_lists()
                    self.game_view.items_collected += 1
                    self.show_dialog = True  # Show the dialog when the letter is collected
                    self.dialog_ui.enable()  # Enable the UI for the dialog

        # Update the background if the temporal state changes
        expected_background_file = f"assets/images/backgrounds/forest_map_{
            self.game_view.temporal_state}.png"
        if self.background_file_name != expected_background_file:
            self.update_background()

    def on_mouse_press(self, x, y, button, modifiers):
        """ Handle mouse clicks to close the dialog window. """
        if self.show_dialog:
            self.dialog_ui.on_mouse_press(x, y, button, modifiers)


class MapCITY(BaseMapView):
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

        arcade.draw_text("The City", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
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
        expected_background_file = f"assets/images/backgrounds/city_map_{
            self.game_view.temporal_state}.png"
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


class GameOverView(arcade.View):
    """ View to show when the game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

        # Initialize the UI manager and vertical box layout
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()

        # Add v_box to the manager
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box
            )
        )

        # Create and add buttons
        self.create_buttons()

    def create_buttons(self):
        """ Create the restart and quit buttons """
        # Restart Button
        restart_button = arcade.gui.UIFlatButton(text="Restart", width=200)
        restart_button.on_click = self.on_restart_button_click
        self.v_box.add(restart_button)

        # Quit Button
        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        quit_button.on_click = self.on_quit_button_click
        self.v_box.add(quit_button)

    def on_restart_button_click(self, event):
        """ Handle the restart button click """
        # Restart the game and go to the Introduction view
        game_view = GameView()  # Create a new instance of GameView
        game_view.setup()  # Set up the game state
        game_view.current_view = 0  # Ensure the introduction view is the first view
        self.window.show_view(game_view)  # Show the GameView with Introduction

    def on_quit_button_click(self, event):
        """ Handle the quit button click """
        # Quit the application
        arcade.exit()

    def on_draw(self):
        """ Draw this view """
        self.clear()

        # Draw the game over text
        arcade.draw_text(
            "Game Over",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 100,  # Shift the text upwards a bit
            arcade.color.WHITE,
            30,
            anchor_x="center",
        )

        # Draw the UI manager (this draws the buttons)
        self.manager.draw()

    def on_show_view(self):
        """ This is called when we switch to this view """
        # Make sure the mouse cursor is visible
        self.window.set_mouse_visible(True)


def main():
    """ Main function """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
