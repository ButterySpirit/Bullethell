import pyglet
from game.resources import standing_player_frames, running_player_frames
from game.physicalobject import PhysicalObject
from game.bullets import PlayerBullet

class Player(PhysicalObject):
    def __init__(self, x, y, window, walls_layer):
        super().__init__(image=standing_player_frames[0], walls_layer=walls_layer, x=x, y=y)
        self.speed = 250.0  # Adjust the speed as needed
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        self.window = window
        self.world_x = x  # Initialize world X coordinate
        self.world_y = y  # Initialize world Y coordinate

        # Create an animation from the running player frames
        self.running_animation = pyglet.image.Animation.from_image_sequence(running_player_frames, duration=0.1, loop=True)

        # Create a sprite for the running animation
        self.running_sprite = pyglet.sprite.Sprite(self.running_animation)

        # Create a sprite for the standing player frames animation
        self.standing_animation = pyglet.image.Animation.from_image_sequence(standing_player_frames, duration=0.2, loop=True)

        # Create a sprite for the standing animation
        self.standing_sprite = pyglet.sprite.Sprite(self.standing_animation)

        # Set the initial sprite to standing
        self.player_sprite = self.standing_sprite

    def detect_collision_with_enemy(self, enemies):
        for enemy in enemies:
            if self.collides_with(enemy):
                print("Collision detected with enemy")

    def detect_collision_with_bullet(self, bullets):
        for bullet in bullets:
            if self.collides_with(bullet):
                print("Player hit")

    def fire_bullet(self, target_x, target_y, camera_x, camera_y):
        # Calculate direction towards the mouse click point in screen coordinates
        direction_x = target_x - (self.x - camera_x)
        direction_y = target_y - (self.y - camera_y)

        # Normalize the direction vector
        magnitude = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if magnitude != 0:
            direction_x /= magnitude
            direction_y /= magnitude

        # Set the bullet speed
        bullet_speed = 300.0  # Adjust bullet speed as needed

        # Calculate the velocity for the bullet in the direction of the mouse click
        bullet_velocity_x = direction_x * bullet_speed
        bullet_velocity_y = direction_y * bullet_speed

        # Calculate the starting position for the bullet in world coordinates
        bullet_start_x = self.world_x
        bullet_start_y = self.world_y
        # print(f"Calculated Bullet Starting Position: ({bullet_start_x}, {bullet_start_y})")
        # print(f"Player Starting Position: ({self.world_x}, {self.world_y})")
        # print(f"Camera Position: ({camera_x}, {camera_y})")
        # Create a new bullet instance and add it to the list of bullets
        bullet = PlayerBullet(bullet_start_x, bullet_start_y, bullet_velocity_x, bullet_velocity_y, camera_x, camera_y,self.walls_layer)
        self.new_objects.append(bullet)

    def update(self, dt):
        # Calculate the movement amount based on the speed and time elapsed
        dx = 0
        dy = 0
        if self.moving_left:
            dx -= self.speed * dt
            # Flip the sprite horizontally when moving left
            self.player_sprite.scale_x = -1
        if self.moving_right:
            dx += self.speed * dt
            # Reset the sprite's scale when moving right
            self.player_sprite.scale_x = 1
        if self.moving_up:
            dy += self.speed * dt
        if self.moving_down:
            dy -= self.speed * dt

        # Store the current position for potential rollback
        prev_x = self.x
        prev_y = self.y

        # Update the player's position
        self.world_x += dx
        self.world_y += dy
        self.x += dx
        self.y += dy

        if self.detect_collision_with_walls(self.walls_layer) and (self.moving_left or self.moving_right):
            print("y collision")
            print(f"Player Coordinates: ({(self.player_sprite.x)}, {(self.player_sprite.y)})")
            self.x = prev_x
            self.world_x = self.x
        if self.detect_collision_with_walls(self.walls_layer) and (self.moving_up or self.moving_down):
            print("x collision")
            self.y = prev_y
            self.world_y = self.y  
            print(f"Player Coordinates: ({(self.player_sprite.x)}, {(self.player_sprite.y)})")
                   # Check for collisions with the "Walls" layer
        

    

        # if self.detect_collision_with_walls(self.walls_layer):
        #     self.x = prev_x
        #     self.world_x = self.x
        #     self.y = prev_y
        #     self.world_y = self.y 

        # Determine which sprite to use based on movement flags
        if any([self.moving_left, self.moving_right, self.moving_up, self.moving_down]):
            self.player_sprite = self.running_sprite
        else:
            self.player_sprite = self.standing_sprite

        # Update the player sprite's position
        self.player_sprite.x = self.x
        self.player_sprite.y = self.y    
        self.new_objects = [bullet for bullet in self.new_objects if not bullet.dead]