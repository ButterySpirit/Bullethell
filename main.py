import pyglet
from game.player import Player
from game.enemy import Enemy, Grumplord
import random
from game.windowmanager import window
import os
import pytmx.util_pyglet
import pytmx
from pyglet import graphics
from pyglet.gl import *
from pyglet.math import Mat4
import cProfile


# EACH MAP HAS TO BE 50 X 50 TILES

scale_factor = 2  # Adjust this value to control the zoom level

resource_dir = os.path.join(os.path.dirname(__file__), 'resources')

tmx_map = pytmx.util_pyglet.load_pyglet(os.path.join(resource_dir, 'level1.tmx'))

floor_items = []
walls_items = []
decoration_items = []
hitbox_items = []
spawn_items = []
enemy_spawn_items = []   

player = Player(x=window.width//2, y=window.height//2, window=window, walls_layer=hitbox_items)

camera_x = 0
camera_y = 0

projection_matrix = Mat4.orthogonal_projection(
    0, window.width, 0, window.height, -255, 255
)

floor_processed = False
walls_processed = False
decoration_processed = False
hitbox_processed = False
spawn_processed = False
enemy_spawn_processed = False

spawn_found = False

enemies = []
enemies_to_remove = []

# Create separate batches for each layer
floor_batch = pyglet.graphics.Batch()
walls_batch = pyglet.graphics.Batch()
decoration_batch = pyglet.graphics.Batch()
hitbox_batch = pyglet.graphics.Batch()
spawn_batch = pyglet.graphics.Batch()

@window.event
def spawn_enemy(dt):
    if not enemy_spawn_items:  # Ensure there are enemy spawn points
        print("No enemy spawn points found.")
        return

    # Choose a random enemy spawn tile
    spawn_tile = random.choice(enemy_spawn_items)

    # Determine which enemy type to spawn (50% chance for each)
    if random.random() < 0.5:
        enemy = Enemy(0, 0, player, window, walls_layer=hitbox_items)  # Temporarily spawn at (0, 0)
        enemy_type = "Enemy"
    else:
        enemy = Grumplord(0, 0, player, window, walls_layer=hitbox_items)  # Temporarily spawn at (0, 0)
        enemy_type = "Grumplord"

    # Use the sprite's dimensions for accurate positioning
    enemy_width = enemy.enemy_sprite.width
    enemy_height = enemy.enemy_sprite.height

    # Calculate enemy's spawn position to center it within the tile
    x = spawn_tile.x + (spawn_tile.width - enemy_width) / 2
    y = spawn_tile.y + (spawn_tile.height - enemy_height) / 2

    # Update the enemy's position
    enemy.x, enemy.y = x, y
    enemy.enemy_sprite.update(x=x, y=y)

    #print(f"Spawned {enemy_type} at ({x}, {y}) with size ({enemy_width}, {enemy_height})")

    enemies.append(enemy)
    pyglet.clock.schedule_interval(enemy.update, 1 / 60.0)  # Schedule enemy updates

# Define key handlers
key_states = {}

red_squares = []

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        # Calculate the world coordinates based on the camera's position
        world_x = player.player_sprite.x - window.width // 2 + x
        world_y = player.player_sprite.y - window.height // 2 + y

        # Use world_x and world_y for your game logic
        player.fire_bullet(world_x, world_y, camera_x, camera_y)

@window.event
def on_key_press(symbol, modifiers):
    key_states[symbol] = True

@window.event
def on_key_release(symbol, modifiers):
    key_states[symbol] = False

# Game update function
def update(dt):
    global player, sane_items
    
    # Update player's movement based on key states
    if key_states.get(pyglet.window.key.A):
        player.moving_left = True
    else:
        player.moving_left = False

    if key_states.get(pyglet.window.key.D):
        player.moving_right = True
    else:
        player.moving_right = False

    if key_states.get(pyglet.window.key.W):
        player.moving_up = True
    else:
        player.moving_up = False

    if key_states.get(pyglet.window.key.S):
        player.moving_down = True
    else:
        player.moving_down = False

    window.on_mouse_press = on_mouse_press

    # Update player and enemy positions
    player.update(dt)

    

    enemies_to_remove = []  # Create a list to store enemies to be removed

    for enemy in enemies:
        enemy.update(dt)
        player.detect_collision_with_enemy([enemy])
        player.detect_collision_with_bullet(enemy.new_objects)
        enemy.bullet_collides_with_player(player)

        if enemy.detect_collision_with_bullet(player.new_objects):
            enemies_to_remove.append(enemy)  # Mark enemy for removal

    # Remove enemies marked for removal after the loop
    for enemy in enemies_to_remove:
        enemies.remove(enemy)
    enemies_to_remove.clear()

def print_coordinates():
    # Print player coordinates
    print(f"Player Coordinates: ({int(player.player_sprite.x)}, {int(player.player_sprite.y)})")

    # Print tile coordinates in "PlayerSpawn" layer
    for tile in spawn_items:
        print(f"Tile in 'PlayerSpawn' Layer: ({int(tile.x)}, {int(tile.y)})")


def load_and_render_tiles():
    global floor_processed, walls_processed, decoration_processed

    if floor_processed and walls_processed and decoration_processed:
        return  # Stop processing once all layers are done

    scaled_tile_width = tmx_map.tilewidth * scale_factor
    scaled_tile_height = tmx_map.tileheight * scale_factor

    for layer in tmx_map.layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            print(f"Found layer: {layer.name}")
            tiles = list(layer.tiles())  # Convert the generator to a list
            for x, y, image in tiles:
                tile_x = x * scaled_tile_width  # Scale the x position
                tile_y = window.height - (y + 1) * scaled_tile_height  # Scale the y position
                
                if layer.name == "Floor":
                    batch = floor_batch
                    item_list = floor_items
                elif layer.name == "Walls":
                    batch = walls_batch
                    item_list = walls_items
                elif layer.name == "Decoration":
                    batch = decoration_batch
                    item_list = decoration_items
                elif layer.name == "PlayerSpawn":
                    batch = spawn_batch
                    item_list = spawn_items
                elif layer.name.strip() == "EnemySpawn":
                    item_list = enemy_spawn_items   
                
                elif layer.name == "Hitboxes":
                    item_list = hitbox_items

                

                else:
                    # Handle any other layers if needed
                    continue

                # Create a sprite for the tile with the scaled position and scale
                sprite = pyglet.sprite.Sprite(image, x=tile_x, y=tile_y, batch=batch)
                sprite.scale = scale_factor  # Scale the sprite

                # Add the sprite to the corresponding item list
                item_list.append(sprite)

                # Check if the current layer is the last layer to process
                if layer.name == "Floor" and len(floor_items) == len(tiles):
                    floor_processed = True
                elif layer.name == "Walls" and len(walls_items) == len(tiles):
                    walls_processed = True
                elif layer.name == "Decoration" and len(decoration_items) == len(tiles):
                    decoration_processed = True
                elif layer.name == "PlayerSpawn" and len(spawn_items) == len(tiles):
                    spawn_processed = True
                elif layer.name == "EnemySpawn" and len(enemy_spawn_items) == len(tiles):
                    for sprite in hitbox_items:
                        # Calculate half of the sprite's width and height
                        half_width = sprite.width / 2
                        half_height = sprite.height / 2

                        # Translate the sprite by half width to the right and half height upwards
                        sprite.x += half_width
                        sprite.y += half_height
                    enemy_spawn_processed = True
                elif layer.name == "Hitboxes" and len(hitbox_items) == len(tiles):
                    # Iterate through each sprite in the hitbox_items list
                    for sprite in hitbox_items:
                        # Calculate half of the sprite's width and height
                        half_width = sprite.width / 2
                        half_height = sprite.height / 2

                        # Translate the sprite by half width to the right and half height upwards
                        sprite.x += half_width
                        sprite.y += half_height
                    hitbox_processed = True

                # Translate the sprite position
                sprite.x += sprite.width / 2  # Half the sprite width to the right
                sprite.y += sprite.height / 2  # Half the sprite height upwards


                # Now you can print the layer information
                #print(f"Layer: {layer.name}, Tiles: {len(item_list)}")

def find_player_spawn():
    global player, spawn_found

    # Check if spawn has already been found, and exit if it has
    if spawn_found:
        return

    # Iterate through each tile in the "PlayerSpawn" layer
    for tile in spawn_items:
        # Calculate the center of the current tile
        tile_center_x = tile.x + tile.width / 2
        tile_center_y = tile.y + tile.height / 2

        # Set the player's position to the center of the current tile
        player.player_sprite.x = tile_center_x
        player.player_sprite.y = tile_center_y

        # Update the player's world coordinates
        player.world_x = tile_center_x
        player.world_y = tile_center_y

        # Set the spawn_found flag to True
        spawn_found = True

    # Ensure the coordinates remain overwritten even after the function ends
    player.x = player.player_sprite.x
    player.y = player.player_sprite.y



# Draw function
@window.event
def on_draw():
    window.clear()
    find_player_spawn()
    
    # Calculate the scaled dimensions of the map
    scaled_map_width = tmx_map.width * tmx_map.tilewidth * 2
    scaled_map_height = tmx_map.height * tmx_map.tileheight * 2
    # print_coordinates()
    # Ensure the camera doesn't go out of the scaled map boundaries
    camera_x = max(0, min(player.player_sprite.x - window.width // 2, scaled_map_width - window.width))
    camera_y = max(-scaled_map_height, min(player.player_sprite.y - window.height // 2, scaled_map_height - window.height))

    # Set the camera's projection matrix
    window.projection = projection_matrix

    # Set the camera's view matrix to simulate scrolling
    window.view = Mat4().translate((-camera_x, -camera_y, 0))

    load_and_render_tiles()
    floor_batch.draw()
    walls_batch.draw()
    decoration_batch.draw()
    #print(enemy_spawn_items)
    

    # Render the player sprite without applying camera translation
    player.player_sprite.draw()  # Render the player sprite

    for enemy in enemies:
        enemy.enemy_sprite.draw()  # Render enemy sprites
        for bullet in enemy.new_objects:
            bullet.update(1 / 60.0)  # Pass a fixed time delta of 1 / 60 seconds
            bullet.draw()  # Draw bullets
    for bullet in player.new_objects:
        bullet.update(1 / 60.0)  # Update player bullet position
        bullet.draw()  # Draw player bullets   


# Start the Pyglet event loop
pyglet.clock.schedule_interval(update, 1 / 60.0)  # Schedule game updates
pyglet.clock.schedule_interval(spawn_enemy, 2.0)  # Schedule enemy spawning

pyglet.app.run()


# def run_game():
#     pyglet.clock.schedule_interval(update, 1 / 60.0)  # Schedule game updates
#     pyglet.clock.schedule_interval(spawn_enemy, 2.0)  # Schedule enemy spawning

#     pyglet.app.run()


# if __name__ == "__main__":
#     # Wrap the Pyglet event loop with cProfile.run()
#     cProfile.run("run_game()", sort="cumulative")