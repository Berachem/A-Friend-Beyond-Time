import arcade
import math
from utils.GameOverView import GameOverView
from utils.BaseMapView import BaseMapView
from utils.tense import Tense
import random
from constants import *

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

class WinterMap(BaseMapView):
  def __init__(self, game_view, game_player_sprite):
    self.game_view = game_view
    self.player_sprite = game_player_sprite
    self.tile_map = None
    self.scene = None
    self.physics_engine = None
    self.monster_sprite = None
    self.collected_flags_past = 0
    self.collected_flags_present = 0
    self.tense = Tense.PRESENT    
    self.setup()

  def setup(self):
    map_name = "assets/maps/ski/ski.json"
    self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
    self.scene = arcade.Scene.from_tilemap(self.tile_map)
    #print("WinterMap ",self.scene["decoration"])

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
      #print("Game Over")
      game_over_view = GameOverView(self.game_view)  # Crée une instance de la vue "Game Over"
      self.game_view.window.show_view(
                      game_over_view)  # Affiche la vue "Game Over"

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
    flags_present = self.scene["flags-present"]
    if self.tense == Tense.PAST:
      for flag in flags:
          if arcade.check_for_collision(self.player_sprite, flag):
            self.collected_flags_past += 1
            flags.remove(flag)
    else:
      for flag in flags_present:
          if arcade.check_for_collision(self.player_sprite, flag):
            self.collected_flags_present += 1
            flags_present.remove(flag)

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

  def switch_tense(self):
    #print(self.tense)
    if self.tense == Tense.PRESENT:
      self.scene["past-monsters"].visible = True
      self.scene["present-monsters"].visible = False
      self.tense = Tense.PAST
    else:
      if self.collected_flags_past > 3:
        self.scene["past-monsters"].visible = False
        self.scene["present-monsters"].visible = False
        self.scene["flags-present"].visible = True
      else:
        self.scene["past-monsters"].visible = False
        self.scene["present-monsters"].visible = True
        self.scene["flags-present"].visible = False
      
      self.tense = Tense.PRESENT
      

  def on_draw(self):
    self.scene.draw()
    # Si on est dans le passé, dessiner un rectangle gris transparent
    if self.tense == Tense.PAST:
            # Rectangle gris transparent sur tout l'écran
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,  # Position au centre de l'écran
                SCREEN_WIDTH, SCREEN_HEIGHT,  # Taille du rectangle pour couvrir tout l'écran
                # Couleur grise avec une transparence (alpha = 150 sur 255)
                (*arcade.color.GRAY, 150)
            )

            # Effet vignette : Rectangle noir transparent en bas
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, 0,  # Position au bas de l'écran
                SCREEN_WIDTH, 50,  # Largeur complète, hauteur réduite pour l'effet
                arcade.color.BLACK
            )

            # Effet vignette : Rectangle noir transparent à gauche
            arcade.draw_rectangle_filled(
                0, SCREEN_HEIGHT // 2,  # Position à gauche de l'écran
                50, SCREEN_HEIGHT,  # Largeur réduite, hauteur complète
                arcade.color.BLACK
            )

            # Effet vignette : Rectangle noir transparent à droite
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH, SCREEN_HEIGHT // 2,  # Position à droite de l'écran
                50, SCREEN_HEIGHT,  # Largeur réduite, hauteur complète
                arcade.color.BLACK
            )

        # Check if the player will be out of bounds
    if self.player_sprite.center_y < SCREEN_HEIGHT-300:

            rectangle_height = 200  # Increased to fit all text
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT -
                150, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK +
                (200,)
            )

            # Draw the "At Killy's home" message centered inside the rectangle
            arcade.draw_text("Ski Mission", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                             arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

            # Draw each part of the story, ensuring long lines are wrapped within the screen width
            arcade.draw_text(
                " You were afraid of the monsters and hesitated to collect the red flags with your friend.Your reluctance and tendency to give up led ",
                40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

            arcade.draw_text(
                " your friend to leave, feeling let down by your weakness.Though the fear of those monsters still lingers, you’re now determined ",
                40, SCREEN_HEIGHT - 205,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

            arcade.draw_text(
                " To make things right,go back to the past,Confront your fears,collect the red flag and return to the present to collect them to win",
                40, SCREEN_HEIGHT - 235,  # Adjusted to fit inside the rectangle
                arcade.color.YELLOW, 18, width=SCREEN_WIDTH - 80
            )

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
    #if self.collected_flags_past > 3:
    #  self.game_view.items_collected += 1
    #  self.game_view.change_view(
    #              (self.game_view.current_view + 1) % len(self.game_view.views))

    if self.collected_flags_present > 3 and self.tense == Tense.PRESENT:
      self.game_view.items_collected += 1
      self.game_view.change_view(
                  (self.game_view.current_view + 1) % len(self.game_view.views))

    self.move_monsters(3, TILE_SCALING * 16 * 10)
    self.check_player_monster_collision()
    self.check_flag_collisions()
    self.physics_engine.update()
    
