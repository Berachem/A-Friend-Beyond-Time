import arcade
from constants import *
from utils.BaseMapView import BaseMapView


class IntroductionMap(BaseMapView):
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

        # remove the button
        self.manager.disable()

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
