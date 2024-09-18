import arcade

# --- Constants ---
SCREEN_WIDTH = 1040
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

PLAYER_START_X = 100
PLAYER_START_Y = 100
PLAYER_BORDER_PADDING = 10  # Padding for detecting map change


class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):
        super().__init__(filename=":resources:images/animated_characters/male_person/malePerson_idle.png",
                         scale=CHARACTER_SCALING)
        self.center_x = PLAYER_START_X
        self.center_y = PLAYER_START_Y
        self.change_x = 0
        self.change_y = 0

    def update(self):
        """ Update player position """
        # Update position based on movement speed
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Limit player to screen bounds vertically
        if self.center_y < 0:
            self.center_y = 0
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = SCREEN_HEIGHT


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

        # Create the views (levels)
        self.views = [
            MapView1(self),
            MapView2(self),
            MapView3(self),
            MapView4(self)
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

        # Overlay for temporal state
        # arcade.draw_text(f"🕰️ Temporal State: {self.temporal_state}",
        #                10, SCREEN_HEIGHT - 40,
        #                arcade.color.WHITE, 20)

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

    def on_draw(self):
        """ Draw the map. """
        arcade.draw_text("🏡 Map 1: The Kitchen", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
        # Draw objects based on temporal state
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Cozy Kitchen 🍳", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Abandoned Kitchen 🥄", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)

        # Add kitchen props
        oven = arcade.Sprite(
            ":resources:images/tiles/brickTextureWhite.png", TILE_SCALING)
        fridge = arcade.Sprite(
            ":resources:images/tiles/lockYellow.png", TILE_SCALING)
        oven.center_x = 200
        oven.center_y = 150
        fridge.center_x = 300
        fridge.center_y = 150

        oven.draw()
        fridge.draw()


class MapView2(BaseMapView):
    """ Second map view """

    def on_draw(self):
        """ Draw the map. """
        arcade.draw_text("🌲 Map 2: The Forest", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
        # Draw objects based on temporal state
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Lush Trees 🌳", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Burnt Forest 🌲🔥", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)


class MapView3(BaseMapView):
    """ Third map view """

    def on_draw(self):
        """ Draw the map. """
        arcade.draw_text("🌊 Map 3: The Lake", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
        # Draw objects based on temporal state
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Peaceful Lake 🦆", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Drained Lake 🏞️", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)


class MapView4(BaseMapView):
    """ Fourth map view """

    def on_draw(self):
        """ Draw the map. """
        arcade.draw_text("🏙️ Map 4: The City", 10,
                         SCREEN_HEIGHT - 60, arcade.color.GREEN, 24)
        # Draw objects based on temporal state
        if self.game_view.temporal_state == PRESENT:
            arcade.draw_text("Present: Busy Streets 🚗", 10,
                             SCREEN_HEIGHT - 100, arcade.color.WHITE, 20)
        else:
            arcade.draw_text("Past: Silent Ruins 🏚️", 10,
                             SCREEN_HEIGHT - 100, arcade.color.GRAY, 20)


def main():
    """ Main function """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
