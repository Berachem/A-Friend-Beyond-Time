import arcade
import arcade.gui
from enum import Enum
import math
# Constants specific to the forest map
TILE_SCALING = 1.1
TILE_SIZE = 16
COLLECTING_DISTANCE = (TILE_SIZE * TILE_SCALING) * 4
CHASING_DISTANCE = TILE_SIZE * TILE_SCALING * 5
PLAYER_SPEED = 5
CHASING_SPEED = 5

# --- Constants ---
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Lost in Time, Found in Friendship"


# Temporal Constants
PAST = "past"
PRESENT = "present"

# TILE_SCALING = 0.5
CHARACTER_SCALING = TILE_SCALING * .7

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
        self.setup()

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
            MapForest(self, self.player_sprite),
            MapWinter(self),
            MapCITY(self),
            Arrivee(self)

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
        self.current_music_player = arcade.play_sound(
            new_music, volume=0.5, looping=True)

    def setup(self):
        """ Set up the game here. """
        self.player_sprite = PlayerCharacter()
        # Set the player's position to the center of the screen for the introduction
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        # Load and play background music for the introduction
        self.background_music = arcade.load_sound("assets/sounds/intro.mp3")
        self.current_music_player = arcade.play_sound(
            self.background_music, volume=0.5, looping=True)

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
        arcade.draw_text(f"{formatted_time}", SCREEN_WIDTH - 88, SCREEN_HEIGHT - 40,
                         arcade.color.WHITE, 20, bold=True)

        # Draw the torch sprite (replacing the "Time" text)
        self.torch_sprite.draw()

        # Draw the star sprite for collected items
        self.star_sprite.draw()

        # Draw the collected items number next to the star
        arcade.draw_text(f"{self.items_collected}", SCREEN_WIDTH - 80, SCREEN_HEIGHT - 70,
                         arcade.color.WHITE, 20, bold=True)

        # Draw a text for the commands at the bottom right with improved style
        arcade.draw_text("Press ", SCREEN_WIDTH - 240,
                         62, arcade.color.WHITE, 12, bold=True)
        arcade.draw_text("Enter", SCREEN_WIDTH - 190, 62,
                         arcade.color.YELLOW, 14, bold=True)
        arcade.draw_text(" to get item!", SCREEN_WIDTH -
                         135, 62, arcade.color.WHITE, 12, bold=True)

        arcade.draw_text("Press ", SCREEN_WIDTH - 250,
                         40, arcade.color.WHITE, 12, bold=True)
        arcade.draw_text("SPACE", SCREEN_WIDTH - 200, 40,
                         arcade.color.YELLOW, 14, bold=True)
        arcade.draw_text(" to switch time", SCREEN_WIDTH -
                         135, 40, arcade.color.WHITE, 12, bold=True)

        arcade.draw_text("Use ", SCREEN_WIDTH - 250,
                         20, arcade.color.WHITE, 12, bold=True)
        arcade.draw_text("arrow keys", SCREEN_WIDTH - 210, 20,
                         arcade.color.YELLOW, 14, bold=True)
        arcade.draw_text(" to move", SCREEN_WIDTH - 110,
                         20, arcade.color.WHITE, 12, bold=True)

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

        self.views[self.current_view].on_key_press(key, modifiers)

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
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 20, 200, arcade.color.BLACK + (200,))

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
        arcade.draw_text(
            "Change the time to find her...",
            SCREEN_WIDTH - 400, SCREEN_HEIGHT - 240, arcade.color.WHITE, 18, width=SCREEN_WIDTH - 40, bold=True
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

        # arcade.draw_text("The Winter Land", 10,
        #                  SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
        rectangle_height = 200  # Increased to fit all text
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT -
            150, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK + (200,)
        )

        # Draw the "At Killy's home" message centered inside the rectangle
        arcade.draw_text("Ski Mission", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                         arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

        # Draw each part of the story, ensuring long lines are wrapped within the screen width
        arcade.draw_text(
            "Overcome your fear of monsters and redeem yourself by collecting the red flags with your friends.",
            40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )

        arcade.draw_text(
            "Your past hesitation caused a rift, but now, determined to make things right,",
            40, SCREEN_HEIGHT - 235,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )

        arcade.draw_text(
            "you must confront your fears and restore the bond by succeeding together.",
            40, SCREEN_HEIGHT - 205,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )
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
    def __init__(self, game_view, game_player_sprite):
        super().__init__(game_view)
        self.game_view = game_view
        self.player_sprite = game_player_sprite
        print("here goes player", game_player_sprite)
        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.mail_sprite = None
        self.wood = 0
        self.is_bridge_constructed = False
        self.feeded_dogs = 0
        self.tense = Tense.PRESENT
        self.setup()

    def setup(self):
        map_name = "assets/maps/forest/test-map.json"
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        mail_source = "assets/maps/raw/mail.png"
        self.mail_sprite = arcade.Sprite(mail_source, .3)
        self.mail_sprite.center_x = 75 * TILE_SIZE
        self.mail_sprite.center_y = 35 * TILE_SIZE
        self.scene.add_sprite("mail", self.mail_sprite)
        self.mail_sprite.visible = False

        # Setup physics engine
        self.update_walls_in_engine(
            [self.scene["angry-dogs"], self.scene["collectables"], self.scene["blocks"]])

    def update_walls_in_engine(self, walls):
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, walls=walls
        )

    def near_sprites_in_list_aux(self, sprite_list_1, sprite_list_2, action, radius):
        for sprite1 in sprite_list_1:
            for sprite2 in sprite_list_2:
                distance = math.sqrt((sprite1.center_x - sprite2.center_x) ** 2 +
                                     (sprite1.center_y - sprite2.center_y) ** 2)
                if distance < radius:
                    action(sprite1)
                    break

    def near_sprites_in_list(self, sprite_list, action):
        self.near_sprites_in_list_aux(
            sprite_list, [self.player_sprite], action, COLLECTING_DISTANCE)

    def collect_wood(self, collectable):
        self.scene["collectables"].remove(collectable)
        self.wood += 1

    def display_invisibles(self, invisibles):
        if self.wood > 3 and self.tense == Tense.PAST:
            self.scene["invisibles"].visible = True
            self.scene["dog-food"].visible = True
            self.update_walls_in_engine(
                [self.scene["young-dogs"], self.scene["collectables"], self.scene["blocks"]])
            self.is_bridge_constructed = True

    def chase_player(self, sprite, speed):
        x_diff = self.player_sprite.center_x - sprite.center_x
        y_diff = self.player_sprite.center_y - sprite.center_y
        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)
        if distance < 0.01:
            return  # Avoid division by zero

        sprite.center_x += (x_diff / distance) * speed
        sprite.center_y += (y_diff / distance) * speed

    def chase_by_dogs(self):
        if self.tense == Tense.PRESENT and self.feeded_dogs < 4:
            self.scene["angry-dogs"].visible = True
            self.scene["friendly-dogs"].visible = False
            for dog in self.scene["angry-dogs"]:
                distance = math.sqrt((dog.center_x - self.player_sprite.center_x) ** 2 +
                                     (dog.center_y - self.player_sprite.center_y) ** 2)
                if distance < CHASING_DISTANCE:  # Check if the dog is near the player
                    # Make the dog chase the player
                    self.chase_player(dog, CHASING_SPEED)

    def chase_by_dog_food(self):
        for food in self.scene["dog-food"]:
            distance = math.sqrt((food.center_x - self.player_sprite.center_x) ** 2 +
                                 (food.center_y - self.player_sprite.center_y) ** 2)
            if distance < TILE_SIZE * TILE_SCALING * 2:
                self.chase_player(food, PLAYER_SPEED * 2)

    def feed_dog(self, dog_food_sprite):
        print("dogs are feeded")
        self.feeded_dogs += 1
        self.scene["dog-food"].remove(dog_food_sprite)
        if (self.feeded_dogs >= 4):
            self.mail_sprite.visible = True

    def switch_tense(self):
        if self.tense == Tense.PRESENT:
            if not self.is_bridge_constructed:
                self.scene["invisibles"].visible = False
                self.scene["bridge-blocks"].visible = True
                self.update_walls_in_engine(
                    [self.scene["young-dogs"], self.scene["collectables"], self.scene["blocks"], self.scene["bridge-blocks"]])
            else:
                self.scene["invisibles"].visible = True
                self.scene["bridge-blocks"].visible = False
                self.update_walls_in_engine(
                    [self.scene["young-dogs"], self.scene["collectables"], self.scene["blocks"]])

            self.scene["angry-dogs"].visible = False
            self.scene["friendly-dogs"].visible = False
            self.scene["young-dogs"].visible = True
            self.scene["dog-food"].visible = True if self.is_bridge_constructed else False

            self.tense = Tense.PAST

        else:
            self.scene["invisibles"].visible = True
            self.scene["bridge-blocks"].visible = False

            if self.feeded_dogs >= 4:
                self.scene["angry-dogs"].visible = False
                self.scene["friendly-dogs"].visible = True
                self.update_walls_in_engine(
                    [self.scene["friendly-dogs"], self.scene["collectables"], self.scene["blocks"]])
            else:
                self.scene["angry-dogs"].visible = True
                self.scene["friendly-dogs"].visible = False
                self.update_walls_in_engine(
                    [self.scene["angry-dogs"], self.scene["collectables"], self.scene["blocks"]])

            self.scene["young-dogs"].visible = False
            self.scene["dog-food"].visible = False

            self.tense = Tense.PRESENT

    def on_draw(self):
        # pass
        arcade.start_render()
        self.scene.draw()

       # Si on est dans le passé, dessiner un rectangle gris transparent
        if self.tense == Tense.PAST:
            # Rectangle gris transparent sur tout l'écran
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,  # Position au centre de l'écran
                SCREEN_WIDTH, SCREEN_HEIGHT,  # Taille du rectangle pour couvrir tout l'écran
                # Couleur grise avec une transparence (alpha = 150 sur 255)
                (*arcade.color.GRAY, 150)
            )

            # Effet vignette : Rectangle noir transparent en bas
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, 0,  # Position au bas de l'écran
                SCREEN_WIDTH, 50,  # Largeur complète, hauteur réduite pour l'effet
                arcade.color.BLACK
            )

            # Effet vignette : Rectangle noir transparent à gauche
            arcade.draw_rectangle_filled(
                0, SCREEN_HEIGHT // 2,  # Position à gauche de l'écran
                50, SCREEN_HEIGHT,  # Largeur réduite, hauteur complète
                arcade.color.BLACK
            )

            # Effet vignette : Rectangle noir transparent à droite
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH, SCREEN_HEIGHT // 2,  # Position à droite de l'écran
                50, SCREEN_HEIGHT,  # Largeur réduite, hauteur complète
                arcade.color.BLACK
            )

        if self.mail_sprite.visible == True:
            arcade.draw_text("Congrats ! you kept your promise.", TILE_SIZE *
                             TILE_SCALING*53, TILE_SIZE*TILE_SCALING*35, arcade.color.BLACK, 15)

        # Check if the player will be out of bounds
        if self.player_sprite.center_y < SCREEN_HEIGHT-300:

            rectangle_height = 200  # Increased to fit all text
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT -
                150, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK +
                (200,)
            )

            # Draw the "At Killy's home" message centered inside the rectangle
            arcade.draw_text("Forest Mission", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                             arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

            # Draw each part of the story, ensuring long lines are wrapped within the screen width
            arcade.draw_text(
                "Your past laziness and irresponsibility led to broken promises and lost trust.",
                40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

            arcade.draw_text(
                "The dogs attacked, and your friend left because of your carelessness.",
                40, SCREEN_HEIGHT - 235,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

            arcade.draw_text(
                "Now, it’s your chance to fix what you’ve done,take responsibility, rebuild trust, and save your friendship",
                40, SCREEN_HEIGHT - 205,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_SPEED
        elif key == arcade.key.ENTER:
            self.near_sprites_in_list(
                self.scene["invisibles"], self.display_invisibles)
            self.near_sprites_in_list(
                self.scene["collectables"], self.collect_wood)
            self.near_sprites_in_list_aux(
                self.scene["dog-food"], self.scene["young-dogs"], self.feed_dog, COLLECTING_DISTANCE*3)
        elif key == arcade.key.SPACE:
            self.switch_tense()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Update logic for chasing dogs and checking for game over condition. """
        # Mettre à jour la logique de poursuite des chiens
        self.chase_by_dogs()
        self.chase_by_dog_food()

        # Mettre à jour le moteur de physique
        self.physics_engine.update()

        # Si mail_sprite est visible, passer à la carte suivante et incrémenter les items collectés
        if self.mail_sprite.visible:
            # Passez à la carte suivante
            self.game_view.items_collected += 1
            self.game_view.change_view(
                (self.game_view.current_view + 1) % len(self.game_view.views))
        # Vérifier la collision entre le joueur et les chiens (chiens en colère)
        # S'applique uniquement dans le présent avant de nourrir les chiens
        if self.tense == Tense.PRESENT and self.feeded_dogs < 4:
            angry_dogs = self.scene["angry-dogs"]
            for dog in angry_dogs:
                # Si un chien entre en collision avec le joueur, déclencher le game over
                if arcade.check_for_collision(self.player_sprite, dog):
                    game_over_view = GameOverView()  # Crée une instance de la vue "Game Over"
                    self.game_view.window.show_view(
                        game_over_view)  # Affiche la vue "Game Over"
                    break


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


class Arrivee(BaseMapView):
    """ Arrival view: displays 'You Win' message and a restart button """

    def __init__(self, game_view):
        super().__init__(game_view)

        # Load the background image
        self.background = arcade.Sprite(
            "assets/images/backgrounds/kelly_house.png")

        # Adjust the scale of the background to fit the screen
        image_width = self.background.width
        image_height = self.background.height
        self.background.scale = max(
            SCREEN_WIDTH / image_width, SCREEN_HEIGHT / image_height)
        self.background.center_x = SCREEN_WIDTH // 2
        self.background.center_y = SCREEN_HEIGHT // 2

        # Initialize the UI manager and vertical box layout for the button
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

        # Create and add the restart button
        self.create_button()

    def create_button(self):
        """ Create the restart and quit buttons """
        # Create a horizontal box layout
        h_box = arcade.gui.UIBoxLayout(horizontal=True)

        # Restart Button
        restart_button = arcade.gui.UIFlatButton(text="Restart", width=200)
        restart_button.on_click = self.on_restart_button_click
        # Add space to the right of the Restart button
        h_box.add(restart_button.with_space_around(right=200, bottom=20))

        # Quit Button
        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        quit_button.on_click = self.on_quit_button_click
        # Add Quit button next to Restart button
        h_box.add(quit_button.with_space_around(right=200))

        # Add the horizontal box to the vertical box layout (centered)
        self.v_box.add(h_box.with_space_around(top=800, bottom=400))

    def on_restart_button_click(self, event):
        """ Handle the restart button click """
        # Restart the game and go to the Introduction view
        game_view = GameView()  # Create a new instance of GameView
        game_view.setup()  # Set up the game state
        game_view.current_view = 0  # Ensure the introduction view is the first view
        # Show the GameView with Introduction
        self.game_view.window.show_view(game_view)

    def on_quit_button_click(self, event):
        """ Handle the quit button click """
        # Quit the application
        arcade.exit()

    def on_draw(self):
        """ Draw the arrival scene with the 'You Win' message and restart button """
        # Draw the background
        self.background.draw()

        # Adjust the rectangle to be taller to fit all the text
        rectangle_height = 150  # Increased to fit all text
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT -
            150, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK + (200,)
        )

        # Draw the "At Killy's home" message centered inside the rectangle
        arcade.draw_text("At Killy's home", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                         arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

        # Draw each part of the story, ensuring long lines are wrapped within the screen width
        arcade.draw_text(
            "Congratulations! You’ve completed the three missions that have tested your resolve, responsibility, and kindness.",
            40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )

        # Draw the UI manager (this draws the restart button)
        self.manager.draw()

    def on_show_view(self):
        """ This is called when we switch to this view """
        # Make sure the mouse cursor is visible
        self.window.set_mouse_visible(True)

    def on_hide_view(self):
        """ Disable the manager when switching to another view """
        self.manager.disable()


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


class Tense(Enum):
    PRESENT = 1
    PAST = 2


def main():
    """ Main function """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
