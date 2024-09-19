import arcade
from Skimap import SkiMap  # Import the SkiMap class

# Constants for the main window
WINDOW_WIDTH = 68 * 16
WINDOW_HEIGHT = 40 * 16
WINDOW_TITLE = "Friendship & Time"

class MyGame(arcade.Window):
  def __init__(self, width, height, title):
    super().__init__(width, height, title)
    self.current_map = None  # This will hold the map instance

  def setup(self):
    self.current_map = SkiMap()  # Instantiate SkiMap
    self.current_map.setup()  # Setup the map

  def on_draw(self):
    self.clear()
    self.current_map.on_draw()  # Delegate drawing to the current map

  def on_key_press(self, key, modifiers):
    self.current_map.on_key_press(key, modifiers)  # Delegate key press to the map

  def on_key_release(self, key, modifiers):
    self.current_map.on_key_release(key, modifiers)  # Delegate key release to the map

  def on_update(self, delta_time):
    self.current_map.on_update(delta_time)  # Delegate update logic to the map


def main():
  window = MyGame(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
  window.setup()
  arcade.run()


if __name__ == "__main__":
  main()
