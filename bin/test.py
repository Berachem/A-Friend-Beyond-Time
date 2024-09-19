import arcade
import random

# Constants
SCREEN_WIDTH = 16*45
SCREEN_HEIGHT = 16*25
SCREEN_TITLE = "Map Example with Moving Character"

# Tilemap
TILE_SCALING = 1
PLAYER_SCALING = 1
MOVEMENT_SPEED = 5

# Map and Player
TILEMAP_PATH = "forest.tmx"  # Assurez-vous que votre fichier TMX est bien exporté.
PLAYER_IMAGE = "D:/ESIEE2024/2024GameGAM/Game_Jam/assets/images/Ski/Tiles/tile_0070.png"  # Image du joueur

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Sprite lists
        self.wall_list = None
        self.player_sprite = None
        
        # Physics
        self.physics_engine = None
        
    def setup(self):
        """Configurez la carte et le joueur ici."""
        # Charger la carte
        self.tile_map = arcade.load_tilemap(TILEMAP_PATH, scaling=TILE_SCALING)
        
        # Configurer les couches
        self.wall_list = self.tile_map.sprite_lists["terrain"]
        
        # Créer le joueur
        self.player_sprite = arcade.Sprite(PLAYER_IMAGE, PLAYER_SCALING)
        
        # Position initiale aléatoire du joueur
        self.player_sprite.center_x = random.randint(0, SCREEN_WIDTH)
        self.player_sprite.center_y = random.randint(0, SCREEN_HEIGHT)
        
        # Configurer le moteur de physique
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)
        
        # Fond de l'écran
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
    
    def on_draw(self):
        """Rendu de l'écran."""
        self.clear()
        self.wall_list.draw()
        self.player_sprite.draw()
    
    def on_update(self, delta_time):
        """Mise à jour à chaque frame."""
        self.physics_engine.update()
        
    def on_key_press(self, key, modifiers):
        """Gérer le déplacement du joueur avec les touches de direction."""
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        """Arrêter le joueur quand les touches sont relâchées."""
        if key in [arcade.key.UP, arcade.key.DOWN]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.LEFT, arcade.key.RIGHT]:
            self.player_sprite.change_x = 0


def main():
    game = MyGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
