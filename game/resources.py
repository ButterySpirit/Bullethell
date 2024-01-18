import pyglet
import os

# Construct the absolute path to the resources directory
resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')

# Set the resource path to the absolute path of the 'resources' directory
pyglet.resource.path = [resources_dir]

# Reindex the resources
pyglet.resource.reindex()

# Load the player and enemy frame-by-frame PNG images with the anchor point set
standing_player_frames = [
    pyglet.image.load(os.path.join(resources_dir, 'playerhell1v2.png')),
    pyglet.image.load(os.path.join(resources_dir, 'playerhell2v2.png'))
]

running_player_frames = [
    pyglet.image.load(os.path.join(resources_dir, 'running1.5.png')),
    pyglet.image.load(os.path.join(resources_dir, 'running2.png')),
    pyglet.image.load(os.path.join(resources_dir, 'running3.png')),
    pyglet.image.load(os.path.join(resources_dir, 'running4.png')),
    pyglet.image.load(os.path.join(resources_dir, 'running5.png'))
    
]

grumplord_frames = [
        pyglet.image.load(os.path.join(resources_dir, 'grumplord1.png')),
        pyglet.image.load(os.path.join(resources_dir, 'grumplord2.png')),

]


# Set the anchor point for the player frames (center of the sprite)
for frame in standing_player_frames:
    frame.anchor_x = frame.width // 2
    frame.anchor_y = frame.height // 2

for frame in running_player_frames:
    frame.anchor_x = frame.width // 2
    frame.anchor_y = frame.height // 2

enemy_frames = [
    pyglet.image.load(os.path.join(resources_dir, 'devil2v3.png')),
    pyglet.image.load(os.path.join(resources_dir, 'devil2v2.png'))
]

# Set the anchor point for the enemy frames (center of the sprite)
for frame in enemy_frames:
    frame.anchor_x = frame.width // 2
    frame.anchor_y = frame.height // 2

for frame in grumplord_frames:
    frame.anchor_x = frame.width // 2
    frame.anchor_y = frame.height // 2


enemy_bullet_image = pyglet.image.load(os.path.join(resources_dir, 'enemybullet.png'))

player_bullet_image = pyglet.image.load(os.path.join(resources_dir, 'heartbullet.png'))

player_bullet_image.anchor_x = player_bullet_image.width // 2
player_bullet_image.anchor_y = player_bullet_image.height // 2