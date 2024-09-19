import arcade
import math
from utils.tense import Tense
from constants import *

# Constants specific to map1
TILE_SCALING = 2
CHARACTER_SCALING = 0.1
TILE_SIZE = 16
COLLECTING_DISTANCE = (TILE_SIZE * TILE_SCALING) * 2
CHASING_DISTANCE = TILE_SIZE * TILE_SCALING * 5
PLAYER_SPEED = 5
CHASING_SPEED = 2

class CityMap:
  def __init__(self, game_view, game_player_sprite):
    self.game_view = game_view
    self.player_sprite = game_player_sprite
    
    
    self.tile_map = None
    self.scene = None
    self.physics_engine = None
    self.tense = Tense.PRESENT
    self.tool = False
    self.is_car_fixed = False
    self.car_present = False
    self.setup()

  def setup(self):
    map_name = "assets/maps/city/City.json"
    self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
    self.scene = arcade.Scene.from_tilemap(self.tile_map)
    
    # Setup physics engine
    self.update_walls_in_engine([self.scene["decoration"], self.scene["immeuble"], self.scene["present_car"], self.scene["past_car"], self.scene["road"], self.scene["wall"]])

  def update_walls_in_engine(self, walls):
    self.physics_engine = arcade.PhysicsEngineSimple(
      self.player_sprite, walls=walls
    )

 
  def on_draw(self):
    arcade.start_render()
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

        rectangle_height = 150  # Increased to fit all text
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT -
            180, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK + (200,)
        )

        # Draw the "At Killy's home" message centered inside the rectangle
        arcade.draw_text("City Mission ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                         arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

        # Draw each part of the story, ensuring long lines are wrapped within the screen width
        arcade.draw_text(
            "Reconnect with your friend by rejoining the weekly drawing class you both loved.",
            40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )

        arcade.draw_text(
            "You missed the chance before due to your car breaking down.",
            40, SCREEN_HEIGHT - 205,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )
        arcade.draw_text(
            "But now, with a second chance, take action to rebuild the friendship through shared hobbies.",
            40, SCREEN_HEIGHT - 235,  # Adjusted to fit inside the rectangle
            arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
        )
    

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

