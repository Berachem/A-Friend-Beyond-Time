
import arcade
from Player import PlayerCharacter
from constants import *
from maps.CityMap import CityMap
from maps.EndingMap import EndingMap
from maps.ForestMap import ForestMap
from maps.IntroductionMap import IntroductionMap
from maps.WinterMap import WinterMap


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
            IntroductionMap(self),
            CityMap(self, self.player_sprite),
            ForestMap(self, self.player_sprite),
            WinterMap(self, self.player_sprite),

            EndingMap(self)

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
        arcade.draw_text(" to interact", SCREEN_WIDTH -
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

        self.views[self.current_view].on_key_release(key, modifiers)

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
