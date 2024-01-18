import pyglet
from . import util

class PhysicalObject(pyglet.sprite.Sprite):
    def __init__(self, image=None, walls_layer=None, *args, **kwargs):
        super().__init__(image, *args, **kwargs)
        self.reacts_to_bullets = True
        self.is_bullet = False
        self.velocity_x, self.velocity_y = 0.0, 0.0
        self.dead = False
        self.new_objects = []
        self.collision_occurred = False
        self.collision_cooldown = 0.0
        self.collision_cooldown_duration = 0.5  # Adjust as needed (in seconds)
        self.walls_layer = walls_layer  # Store the "Walls" layer
        
    def updates(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
        else:
            self.collision_occurred = False

    def collides_with(self, other_object):
        if self.image is None or other_object.image is None:
            return False  # One of the objects doesn't have an image

        # Get the dimensions of the sprites directly
        self_width = self.width
        other_width = other_object.width
        self_height = self.height
        other_height = other_object.height

        # Calculate the bounding boxes of the sprites
        left1 = self.x - self_width / 2
        bottom1 = self.y - self_height / 2
        right1 = left1 + self_width
        top1 = bottom1 + self_height

        left2 = other_object.x - other_width / 2
        bottom2 = other_object.y - other_height / 2
        right2 = left2 + other_width
        top2 = bottom2 + other_height

        # Check if the bounding boxes overlap
        if (right1 >= left2 and left1 <= right2 and
            top1 >= bottom2 and bottom1 <= top2):
            return True

        return False

    def handle_collision_with(self, other_object):
        if not self.collision_occurred:
            if other_object.__class__ == self.__class__:
                self.dead = False
            else:
                self.dead = True
                self.collision_occurred = True
                self.collision_cooldown = self.collision_cooldown_duration
        else:
            self.dead = True

    def detect_collision_with_walls(self, walls_layer):
        """
        Detect collisions with objects on the "Walls" layer of the TMX map.

        Args:
            walls_layer (pytmx.TiledObjectGroup): The "Walls" layer from the TMX map.

        Returns:
            bool: True if a collision with walls is detected, False otherwise.
        """
        for obj in walls_layer:
            if self.collides_with(obj):
                return True
        return False
        