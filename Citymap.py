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

class CityMap:
  def __init__(self):
    self.tile_map = None
    self.scene = None
    self.physics_engine = None
    self.player_sprite = None
    self.tense = Tense.PRESENT
    self.tool = False
    self.is_car_fixed = False
    self.car_present = False

  def setup(self):
    map_name = "Map/CityMap/City.json"
    self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
    self.scene = arcade.Scene.from_tilemap(self.tile_map)
    image_source = "Map/Assets/player.png"
    self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
    self.player_sprite.center_x = 20 * TILE_SIZE
    self.player_sprite.center_y = 20 * TILE_SIZE
    self.scene.add_sprite("player", self.player_sprite)
    # Setup physics engine
    self.update_walls_in_engine([self.scene["decoration"], self.scene["immeuble"], self.scene["present_car"], self.scene["past_car"], self.scene["road"], self.scene["wall"]])

  def update_walls_in_engine(self, walls):
    self.physics_engine = arcade.PhysicsEngineSimple(
      self.player_sprite, walls=walls
    )

 
  def on_draw(self):
    arcade.start_render()
    self.scene.draw()
    

  def on_key_press(self, key, modifiers):
    if not self.is_car_fixed:
      self.move_player([self.player_sprite], key)
      if key == arcade.key.ENTER and self.tense == Tense.PAST:
        self.near_sprites_in_list(self.scene["tool"], self.collect)
        if self.tool == True :
          self.near_sprites_in_list(self.scene["problem"], self.repar_car)
      elif key == arcade.key.SPACE:
        self.switch_tense()
    else:
      if self.tense == Tense.PAST:
        print("past trying to move car", key)
        self.move_sprites(self.scene["past_car"], key)
      elif self.tense == Tense.PRESENT:
        self.move_sprites(self.scene["present_car"], key)

  def move_player(self, sprites, key):
    for sprite in sprites:
        if key == arcade.key.UP:
            sprite.change_y = PLAYER_SPEED
        elif key == arcade.key.DOWN:
            sprite.change_y = -PLAYER_SPEED
        elif key == arcade.key.LEFT:
            sprite.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            sprite.change_x = PLAYER_SPEED
    
  def move_sprites(self, sprites, key):
    for sprite in sprites:
      if arcade.check_for_collision_with_list(sprite, self.scene["road"]) or arcade.check_for_collision_with_list(sprite, self.scene["terrain"]):
        if key == arcade.key.UP:
            sprite.center_y += PLAYER_SPEED * 5
        elif key == arcade.key.DOWN:
            sprite.center_y -= PLAYER_SPEED * 5
        elif key == arcade.key.LEFT:
            sprite.center_x -= PLAYER_SPEED * 5
        elif key == arcade.key.RIGHT:
            sprite.center_x += PLAYER_SPEED * 5

  def collect(self, collectable):
    self.scene["tool"].remove(collectable)
    self.tool = True

  
  def repar_car(self, collectable):
    self.scene["problem"].remove(collectable)
    self.player_sprite.visible = False
    self.is_car_fixed = True

  def switch_tense(self):
    self.scene["problem"].visible = not self.is_car_fixed
    if self.tense == Tense.PRESENT:
      self.scene["tool"].visible = True
      self.scene["past_car"].visible = True
      self.scene["present_car"].visible = False
      self.tense = Tense.PAST
    else:
      self.scene["tool"].visible = False
      self.scene["past_car"].visible = False
      self.scene["present_car"].visible = True
      self.tense = Tense.PRESENT

  def near_sprites_in_list_aux(self, sprite_list_1, sprite_list_2, action, radius):
    for sprite1 in sprite_list_1:
        for sprite2 in sprite_list_2:
          distance = math.sqrt((sprite1.center_x - sprite2.center_x) ** 2 + 
                              (sprite1.center_y - sprite2.center_y) ** 2)
          if distance < radius:
            action(sprite1)
            break

  def near_sprites_in_list(self, sprite_list, action):
    self.near_sprites_in_list_aux(sprite_list, [self.player_sprite], action, COLLECTING_DISTANCE)

  def on_key_release(self, key, modifiers):
    if key == arcade.key.UP or key == arcade.key.DOWN:
      self.player_sprite.change_y = 0
    elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
      self.player_sprite.change_x = 0

  def on_update(self, delta_time):
    # Update physics engine (for player and walls interaction)
    self.physics_engine.update()
    
    # Move the car if it has been repaired
    # if self.is_car_fixed :
        # car_sprite = self.scene.get_sprite_list("past_car")  # Assuming the car is in a sprite list
    #     for car in car_sprite:
    #         car.center_x += PLAYER_SPEED  # Move the car to the right or adjust based on your need
    #         if car.center_x > 810 :
    #           self.is_car_fixed = False
    #           self.car_present = True

