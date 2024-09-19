


import arcade
from constants import *
from utils.BaseMapView import BaseMapView

class EndingMap(BaseMapView):
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