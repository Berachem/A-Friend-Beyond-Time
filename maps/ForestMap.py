
import arcade
import math
from utils.BaseMapView import BaseMapView
from utils.tense import Tense
from constants import *
from utils.GameOverView import GameOverView


class ForestMap(BaseMapView):
    def __init__(self, game_view, game_player_sprite):
        super().__init__(game_view)
        self.game_view = game_view
        self.player_sprite = game_player_sprite
            # Positionner le joueur correctement dans la nouvelle carte
        self.player_sprite.center_x = 100  # Ou une autre position de départ logique dans ForestMap
        self.player_sprite.center_y = 100  # Position de départ
        self.player_sprite.visible = True
        print("here goes player", game_player_sprite)
        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.mail_sprite = None
        self.dog_food_sprites = arcade.SpriteList()
        self.wood = 0
        self.is_bridge_constructed = False
        self.feeded_dogs = 0
        self.tense = Tense.PRESENT
        self.setup()

    def setup(self):
        map_name = "assets/maps/forest/test-map.json"
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        mail_source = "assets/maps/raw/mail.png"
        self.mail_sprite = arcade.Sprite(mail_source, .3)
        self.mail_sprite.center_x = 75 * TILE_SIZE
        self.mail_sprite.center_y = 35 * TILE_SIZE
        self.scene.add_sprite("mail", self.mail_sprite)
        self.mail_sprite.visible = False

        dog_food = "assets/maps/raw/dog-food.png"
        actual_tile_size = TILE_SIZE * TILE_SCALING
        for i in range(5):
            dog_food_sprite = arcade.Sprite(dog_food , .1)
            dog_food_sprite.center_x = i * 3 * actual_tile_size + (actual_tile_size * 15)
            dog_food_sprite.center_y = actual_tile_size * 5
            self.dog_food_sprites.append(dog_food_sprite)
        self.scene.add_sprite_list(name="dog-food", sprite_list=self.dog_food_sprites)
        self.scene["dog-food"].visible = False

        # Setup physics engine
        self.update_walls_in_engine(
            [self.scene["angry-dogs"], self.scene["collectables"], self.scene["blocks"]])

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
        self.near_sprites_in_list_aux(
            sprite_list, [self.player_sprite], action, COLLECTING_DISTANCE)

    def check_player_dogs_collision(self):
        present_monsters = self.scene["angry-dogs"]
        present_collisions = arcade.check_for_collision_with_list(self.player_sprite, present_monsters)
        if self.tense == Tense.PRESENT and present_collisions :
            print("Game Over")
            game_over_view = GameOverView(self.game_view)  # Crée une instance de la vue "Game Over"
            self.game_view.window.show_view(
                            game_over_view) 
    def collect_wood(self, collectable):
        self.scene["collectables"].remove(collectable)
        self.wood += 1

    def display_invisibles(self, invisibles):
        if self.wood > 3 and self.tense == Tense.PAST:
            self.scene["invisibles"].visible = True
            self.scene["dog-food"].visible = True
            self.update_walls_in_engine(
                [self.scene["young-dogs"], self.scene["collectables"], self.scene["blocks"]])
            self.is_bridge_constructed = True

    def chase_player(self, sprite, speed):
        x_diff = self.player_sprite.center_x - sprite.center_x
        y_diff = self.player_sprite.center_y - sprite.center_y
        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)
        if distance < 0.01:
            return  # Avoid division by zero

        sprite.center_x += (x_diff / distance) * speed
        sprite.center_y += (y_diff / distance) * speed

    def chase_by_dogs(self):
        if self.tense == Tense.PRESENT and self.feeded_dogs < 4:
            self.scene["angry-dogs"].visible = True
            self.scene["friendly-dogs"].visible = False
            for dog in self.scene["angry-dogs"]:
                distance = math.sqrt((dog.center_x - self.player_sprite.center_x) ** 2 +
                                     (dog.center_y - self.player_sprite.center_y) ** 2)
                if distance < CHASING_DISTANCE:  # Check if the dog is near the player
                    # Make the dog chase the player
                    self.chase_player(dog, CHASING_SPEED)

    def chase_by_dog_food(self):
        for food in self.scene["dog-food"]:
            distance = math.sqrt((food.center_x - self.player_sprite.center_x) ** 2 +
                                 (food.center_y - self.player_sprite.center_y) ** 2)
            if distance < TILE_SIZE * TILE_SCALING * 2:
                self.chase_player(food, PLAYER_SPEED * 2)

    def feed_dog(self, dog_food_sprite):
        print("dogs are feeded")
        self.feeded_dogs += 1
        self.scene["dog-food"].remove(dog_food_sprite)
        if (self.feeded_dogs >= 4):
            self.mail_sprite.visible = True

    def switch_tense(self):
        if self.tense == Tense.PRESENT:
            if not self.is_bridge_constructed:
                self.scene["invisibles"].visible = False
                self.scene["bridge-blocks"].visible = True
                self.update_walls_in_engine(
                    [self.scene["young-dogs"], self.scene["collectables"], self.scene["blocks"], self.scene["bridge-blocks"]])
            else:
                self.scene["invisibles"].visible = True
                self.scene["bridge-blocks"].visible = False
                self.update_walls_in_engine(
                    [self.scene["young-dogs"], self.scene["collectables"], self.scene["blocks"]])

            self.scene["angry-dogs"].visible = False
            self.scene["friendly-dogs"].visible = False
            self.scene["young-dogs"].visible = True
            self.scene["dog-food"].visible = True if self.is_bridge_constructed else False

            self.tense = Tense.PAST

        else:
            self.scene["invisibles"].visible = True
            self.scene["bridge-blocks"].visible = False

            if self.feeded_dogs >= 4:
                self.scene["angry-dogs"].visible = False
                self.scene["friendly-dogs"].visible = True
                self.update_walls_in_engine(
                    [self.scene["friendly-dogs"], self.scene["collectables"], self.scene["blocks"]])
            else:
                self.scene["angry-dogs"].visible = True
                self.scene["friendly-dogs"].visible = False
                self.update_walls_in_engine(
                    [self.scene["angry-dogs"], self.scene["collectables"], self.scene["blocks"]])

            self.scene["young-dogs"].visible = False
            self.scene["dog-food"].visible = False

            self.tense = Tense.PRESENT

    def on_draw(self):
        # pass
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

        if self.mail_sprite.visible == True:
            arcade.draw_text("Congrats ! you kept your promise.", TILE_SIZE *
                             TILE_SCALING*53, TILE_SIZE*TILE_SCALING*35, arcade.color.BLACK, 15)

        # Check if the player will be out of bounds
        if self.player_sprite.center_y < SCREEN_HEIGHT-300:

            rectangle_height = 200  # Increased to fit all text
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT -
                150, SCREEN_WIDTH, rectangle_height, arcade.color.BLACK +
                (200,)
            )

            # Draw the "At Killy's home" message centered inside the rectangle
            arcade.draw_text("Forest Mission", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 125,  # Adjusted to be inside the rectangle
                             arcade.color.GREEN, 24, anchor_x="center", anchor_y="center")

            # Draw each part of the story, ensuring long lines are wrapped within the screen width
            arcade.draw_text(
                "Your past laziness and irresponsibility led to broken promises and lost trust.",
                40, SCREEN_HEIGHT - 175,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

            arcade.draw_text(
                "The dogs attacked, and your friend left because of your carelessness.",
                40, SCREEN_HEIGHT - 235,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
            )

            arcade.draw_text(
                "Now, it’s your chance to fix what you’ve done,take responsibility, rebuild trust, and save your friendship",
                40, SCREEN_HEIGHT - 205,  # Adjusted to fit inside the rectangle
                arcade.color.WHITE, 18, width=SCREEN_WIDTH - 80
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
            self.near_sprites_in_list(
                self.scene["invisibles"], self.display_invisibles)
            self.near_sprites_in_list(
                self.scene["collectables"], self.collect_wood)
            self.near_sprites_in_list_aux(
                self.scene["dog-food"], self.scene["young-dogs"], self.feed_dog, COLLECTING_DISTANCE*3)
        elif key == arcade.key.SPACE:
            self.switch_tense()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """ Update logic for chasing dogs and checking for game over condition. """
        # Mettre à jour la logique de poursuite des chiens
        self.chase_by_dogs()
        self.chase_by_dog_food()
        self.check_player_dogs_collision()

        # Mettre à jour le moteur de physique
        self.physics_engine.update()

        # Si mail_sprite est visible, passer à la carte suivante et incrémenter les items collectés
        if self.mail_sprite.visible:
            # Passez à la carte suivante
            self.game_view.items_collected += 1
            self.game_view.change_view(
                (self.game_view.current_view + 1) % len(self.game_view.views))
            
    def change_view(self, new_view):
        # Assurez-vous que vous passez correctement le sprite du joueur à la nouvelle vue
        new_view.setup()  # Initialiser la nouvelle vue
        self.window.show_view(new_view)