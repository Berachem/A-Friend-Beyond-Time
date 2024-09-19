class BaseMapView:
    """ Base class for all map views """

    def __init__(self, game_view):
        self.game_view = game_view  # Reference to the GameView
        self.player_sprite = game_view.player_sprite

    def on_draw(self):
        pass

    def on_update(self, delta_time):
        pass
