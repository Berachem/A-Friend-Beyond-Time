import arcade
import math
from tense import Tense
import random

# Constants specific to map1
TILE_SCALING = 2
CHARACTER_SCALING = 0.1
TILE_SIZE = 16
COLLECTING_DISTANCE = (TILE_SIZE * TILE_SCALING) * 2
CHASING_DISTANCE = TILE_SIZE * TILE_SCALING * 5
PLAYER_SPEED = 5
CHASING_SPEED = 2
HORIZONTAL_TILES = 45
VERTICAL_TILES = 25

class MapWinter:
  def __init__(self, game_view, game_player_sprite):
    self.game_view = game_view
    self.player_sprite = game_player_sprite
    self.tile_map = None
    self.scene = None
    self.physics_engine = None
    self.monster_sprite = None
    self.collected_flags = 0
    self.tense = Tense.PRESENT    
    self.setup()

  def setup(self):
    map_name = "assets/maps/ski/ski.json"
    self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
    self.scene = arcade.Scene.from_tilemap(self.tile_map)

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

  def check_player_monster_collision(self):
    past_monsters = self.scene["past-monsters"]
    present_monsters = self.scene["present-monsters"]
    past_collisions = arcade.check_for_collision_with_list(self.player_sprite, past_monsters)
    present_collisions = arcade.check_for_collision_with_list(self.player_sprite, present_monsters)
    if self.tense == Tense.PRESENT and present_collisions or self.tense == Tense.PAST and past_collisions :
      print("Game Over")

  def move_monsters(self, n, m):
    monsters = self.scene["past-monsters"]
    walls = self.scene["decoration"]
    map_width = TILE_SCALING * HORIZONTAL_TILES * 16
    map_height = TILE_SCALING * VERTICAL_TILES * 16
    
    for monster in monsters:
      # If the monster doesn't have an initial position, store it
      if not hasattr(monster, 'initial_x'):
        monster.initial_x = monster.center_x
        monster.initial_y = monster.center_y

      # If the monster doesn't have a direction, choose one
      if not hasattr(monster, 'direction'):
        monster.direction = random.choice(['up', 'down', 'left', 'right'])
      
      old_x = monster.center_x
      old_y = monster.center_y

      # Move monster in the current direction
      if monster.direction == 'up':
        monster.center_y += n
      elif monster.direction == 'down':
        monster.center_y -= n
      elif monster.direction == 'left':
        monster.center_x -= n
      elif monster.direction == 'right':
        monster.center_x += n

      # Check for collisions with walls, boundaries, or if it's out of the allowed radius
      distance_from_start = math.sqrt((monster.center_x - monster.initial_x) ** 2 +
                                      (monster.center_y - monster.initial_y) ** 2)

      if (monster.center_x < 0 or monster.center_x > map_width or
          monster.center_y < 0 or monster.center_y > map_height or
          arcade.check_for_collision_with_list(monster, walls) or
          distance_from_start > m):
        # Revert movement if there is a collision, out of bounds, or exceeds radius
        monster.center_x = old_x
        monster.center_y = old_y
        # Pick a new random direction
        monster.direction = random.choice(['up', 'down', 'left', 'right'])

  def check_flag_collisions(self):
    flags = self.scene["flags"]
    for flag in flags:
      if arcade.check_for_collision(self.player_sprite, flag):
        self.collected_flags += 1
        flags.remove(flag)  # Remove the flag on collision with player

  def display_invisibles(self, invisibles):
    if self.nbFlag > 3 and self.tense == Tense.PRESENT:
      self.scene["past-monsters"].visible = False

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
      self.scene["past-monsters"].visible = True
      for monster in self.scene["past-monsters"]:
        distance = math.sqrt((monster.center_x - self.player_sprite.center_x) ** 2 + 
                            (monster.center_y - self.player_sprite.center_y) ** 2)
        if distance < CHASING_DISTANCE:  # Check if the dog is near the player
          self.chase_player(monster, CHASING_SPEED)  # Make the dog chase the player

  def take_flag(self, dog_food_sprite):
    print("Take flag !")
    self.nbFlag += 1
    if(self.nbFlag >= 4):
      self.tense == Tense.PRESENT

  def switch_tense(self):
    print(self.tense)
    if self.tense == Tense.PRESENT:
      self.scene["past-monsters"].visible = True
      self.scene["present-monsters"].visible = False
      self.tense = Tense.PAST
    else:
      if self.collected_flags > 3:
        self.scene["past-monsters"].visible = False
        self.scene["present-monsters"].visible = False
        print("You won !")
      else:
        self.scene["past-monsters"].visible = False
        self.scene["present-monsters"].visible = True
      
      self.tense = Tense.PRESENT
      

  def on_draw(self):
    self.scene.draw()

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
    self.move_monsters(3, TILE_SCALING * 16 * 10)
    self.check_player_monster_collision()
    self.check_flag_collisions()
    self.physics_engine.update()