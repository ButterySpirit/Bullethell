import pyglet
from game.physicalobject import PhysicalObject
from game.resources import enemy_bullet_image, player_bullet_image

class EnemyBullet(PhysicalObject):
    def __init__(self, world_x, world_y, velocity_x, velocity_y, camera_x=0, camera_y=0, walls_layer=None):
        super().__init__(image=enemy_bullet_image, x=0, y=0, walls_layer=walls_layer)
        self.world_x = world_x
        self.world_y = world_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.camera_x = camera_x
        self.camera_y = camera_y

    def update(self, dt):
        # Update world coordinates based on velocity
        self.world_x += self.velocity_x * dt
        self.world_y += self.velocity_y * dt

        # Calculate screen coordinates based on world coordinates and camera position
        self.x = self.world_x - self.camera_x  # Calculate screen X coordinate
        self.y = self.world_y - self.camera_y  # Calculate screen Y coordinate

        # Check for collisions with walls
        if self.detect_collision_with_walls(self.walls_layer):
            self.dead = True  # Mark the bullet for deletion if it collides with walls


class PlayerBullet(PhysicalObject):
    def __init__(self, world_x, world_y, velocity_x, velocity_y, camera_x, camera_y, walls_layer):
        # Set world coordinates
        super().__init__(image=player_bullet_image, x=0, y=0, walls_layer=walls_layer)
        self.world_x = world_x
        self.world_y = world_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.camera_x = camera_x
        self.camera_y = camera_y

    def update(self, dt):
        # Update world coordinates based on velocity
        self.world_x += self.velocity_x * dt
        self.world_y += self.velocity_y * dt

        # Check for collisions with walls
        if self.detect_collision_with_walls(self.walls_layer):
            # Remove the bullet if it collides with walls
            #print("Bullet collided with walls")
            #Sprint (self.world_x, self.world_y)
            self.dead = True
            
                
        # Calculate screen coordinates based on world coordinates and camera position
        self.x = self.world_x 
        self.y = self.world_y 


        


