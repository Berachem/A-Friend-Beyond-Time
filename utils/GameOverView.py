import arcade
from constants import *


class GameOverView(arcade.View):
    """ View to show when the game is over """

    def __init__(self):
        """ This is run once when we switch to this view """
        super().__init__()
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

        # Load background image
        # Update to the correct path for your background
        self.background_image = arcade.load_texture(
            "assets/images/backgrounds/game_over.jpg")

        # Initialize the UI manager and vertical box layout
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout(
            space_between=20)  # Add space between buttons

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

        # Load the game over image
        self.game_over_image = arcade.load_texture(
            "assets/images/items/coeurBrise.png")  # Change the path to your image file

        # Load and prepare background music
        self.game_over_music = arcade.load_sound(
            "assets/sounds/game_over_sound.mp3")
        self.current_music_player = None

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
        from utils.GameView import GameView
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

        # Draw the background image
        arcade.draw_lrwh_rectangle_textured(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_image
        )

        # Draw the game over text
        arcade.draw_text(
            "Game Over",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 100,  # Shift the text upwards a bit
            arcade.color.BLACK,
            30,
            anchor_x="center",
        )

        arcade.draw_texture_rectangle(
            SCREEN_WIDTH / 2 + 150,  # Adjust the x position to the right of the text
            SCREEN_HEIGHT / 2 + 100,  # Align the image vertically with the text
            100,  # Width of the image
            100,  # Height of the image
            self.game_over_image
        )
        # Draw the UI manager (this draws the buttons)
        self.manager.draw()

    def on_show_view(self):
        """ This is called when we switch to this view """
        # Make sure the mouse cursor is visible
        self.window.set_mouse_visible(True)

        # Play the game over music in the background
        if self.current_music_player:
            arcade.stop_sound(self.current_music_player)
        self.current_music_player = arcade.play_sound(
            self.game_over_music, volume=0.5, looping=True)

    def on_hide_view(self):
        """ This is called when we leave the view """
        # Stop the music when leaving the view
        if self.current_music_player:
            arcade.stop_sound(self.current_music_player)
