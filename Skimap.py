import arcade
import math
from tense import Tense

# Constants specific to map1
TILE_SCALING = 1.5
CHARACTER_SCALING = 0.1
TILE_SIZE = 16
COLLECTING_DISTANCE = (TILE_SIZE * TILE_SCALING) * 2
CHASING_DISTANCE = TILE_SIZE * TILE_SCALING * 5
PLAYER_SPEED = 5
CHASING_SPEED = 2

class SkiMap:
  def __init__(self):
    self.tile_map = None
    self.scene = None
    self.physics_engine = None
    self.player_sprite = None
    self.monster_sprite = None
    self.nbFlag = 0
    self.collectFlag = 0
    self.tense = Tense.PRESENT

  def setup(self):
    map_name = "Map/SkiMap/test.json"
    self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
    self.scene = arcade.Scene.from_tilemap(self.tile_map)
    self.player_sprite = self.scene["you"].pop()
    # Setup physics engine
    self.update_walls_in_engine([self.scene["decoration"]])

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
    #self.near_sprites_in_list_aux(sprite_list, [self.player_sprite], action, COLLECTING_DISTANCE)
    return 

  def collect_flag(self, collectable):
    self.scene["redFlags"].remove(collectable)
    self.nbFlag += 1

  def display_invisibles(self, invisibles):
    if self.nbFlag > 3 and self.tense == Tense.PRESENT:
      self.scene["monsters"].visible = False
      

  def chase_player(self, sprite, speed):
    x_diff = self.player_sprite.center_x - sprite.center_x
    y_diff = self.player_sprite.center_y - sprite.center_y
    distance = math.sqrt(x_diff ** 2 + y_diff ** 2)
    if distance < 0.01:
      return  # Avoid division by zero
    sprite.center_x += (x_diff / distance) * speed
    sprite.center_y += (y_diff / distance) * speed

  def chase_by_monsters(self):
    if self.tense == Tense.PAST and self.chase_by_monsters < 4:
      self.scene["monsters"].visible = True
      for monster in self.scene["monsters"]:
        distance = math.sqrt((monster.center_x - self.player_sprite.center_x) ** 2 + 
                            (monster.center_y - self.player_sprite.center_y) ** 2)
        if distance < CHASING_DISTANCE:  # Check if the dog is near the player
          self.chase_player(monster, CHASING_SPEED)  # Make the dog chase the player

  

  def take_flag(self, dog_food_sprite):
    print("Take flag !")
    self.nbFlag += 1
    if(self.nbFlag >= 4):
      self.tense == Tense.PRESENT


  def on_draw(self):
    arcade.start_render()
    self.scene.draw()
    if self.nbFlag > 7:
      arcade.draw_text("Congrats ! you kept your promise.", TILE_SIZE*TILE_SCALING*53, TILE_SIZE*TILE_SCALING*35, arcade.color.BLACK, 15)

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
      self.near_sprites_in_list(self.scene["redFlags"], self.nbFlag)
      
    elif key == arcade.key.SPACE:
      self.switch_tense()

  def on_key_release(self, key, modifiers):
    if key == arcade.key.UP or key == arcade.key.DOWN:
      self.player_sprite.change_y = 0
    elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
      self.player_sprite.change_x = 0

  def on_update(self, delta_time):
    #self.collectFlag()
 
    self.physics_engine.update()
