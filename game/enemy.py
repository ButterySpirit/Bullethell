import pyglet
from game.resources import enemy_frames, grumplord_frames
from game.physicalobject import PhysicalObject
from game.bullets import EnemyBullet
from game.windowmanager import window
import random
import math

class Enemy(PhysicalObject):
    def __init__(self, x, y, player, window, walls_layer):
        super().__init__(image=enemy_frames[0], x=x, y=y, walls_layer=walls_layer)
        self.speed = 100.0  # Adjust the speed as needed
        self.player = player  # Reference to the player object
        self.window = window
        self.velocity_x = 0.0  # Initialize velocity in the x direction
        self.velocity_y = 0.0  # Initialize velocity in the y direction
        self.random_movement_timer = 0.0  # Random initial timer
        self.random_movement_duration = random.uniform(1.0, 2.0)  # Random movement duration
        self.target_player_timer = random.uniform(1.0, 3.0)  # Random initial timer for targeting
        self.target_duration = random.uniform(1.0, 3.0)  # Random duration for targeting
        self.targeting = False  # Flag to indicate if the enemy is targeting the player
        self.pause_timer = 0.0  # Timer for pause duration
        self.pause_duration = 2.0  # Initial pause duration (2 seconds)
        self.new_objects = []

        # Create an animation from the enemy frames
        self.enemy_animation = pyglet.image.Animation.from_image_sequence(enemy_frames, duration=0.2, loop=True)
        self.enemy_sprite = pyglet.sprite.Sprite(self.enemy_animation)

    def apply_random_movement(self):
        # Apply random perturbation to the velocity vector
        random_angle = random.uniform(0, 2 * 3.14159)
        perturbation_x = self.speed * math.cos(random_angle)
        perturbation_y = self.speed * math.sin(random_angle)

        # Update the enemy's velocity with random perturbation
        self.velocity_x = perturbation_x
        self.velocity_y = perturbation_y

    def fire_wrapper(self, dt):
        self.fire()

    def fire(self):
        # Calculate direction towards the player
        direction_x = self.player.x - self.x
        direction_y = self.player.y - self.y

        # Normalize the direction vector
        magnitude = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if magnitude != 0:
            direction_x /= magnitude
            direction_y /= magnitude

        # Set the bullet speed
        bullet_speed = 200.0  # Adjust bullet speed as needed

        # Calculate the velocity for the bullets in the direction of the player
        bullet_velocity_x = direction_x * bullet_speed
        bullet_velocity_y = direction_y * bullet_speed

        # Define the number of bullets to fire in each cycle
        num_bullets_to_fire = 3  # Adjust as needed

        # Calculate the time delay between each bullet
        bullet_delay = 0.1  # Adjust the delay as needed (in seconds)

        # Calculate the starting position for the bullets relative to the enemy
        bullet_start_x = self.x
        bullet_start_y = self.y

        # Schedule the firing of bullets with a delay between them
        for i in range(num_bullets_to_fire):
            def fire_bullet(dt):
                nonlocal bullet_start_x, bullet_start_y
                bullet_x = bullet_start_x + i * bullet_velocity_x * bullet_delay
                bullet_y = bullet_start_y + i * bullet_velocity_y * bullet_delay
                bullet = EnemyBullet(bullet_x, bullet_y, bullet_velocity_x, bullet_velocity_y,walls_layer=self.walls_layer)
                self.new_objects.append(bullet)

            # Schedule each bullet with a delay
            pyglet.clock.schedule_once(fire_bullet, i * bullet_delay)

    def bullet_collides_with_player(self, player):
        bullets_to_remove = []  # Create a list to store bullets to be removed

        for bullet in self.new_objects:
            if player.collides_with(bullet):
                bullets_to_remove.append(bullet)  # Add the bullet to the removal list

        # Remove the collided bullets from the enemy's bullets list
        for bullet in bullets_to_remove:
            self.new_objects.remove(bullet)

        # Clear the bullets_to_remove list after removal
        bullets_to_remove.clear()

    def detect_collision_with_bullet(self, bullets):
        for bullet in bullets:
            if self.collides_with(bullet):
                print("enemy hit")
                return True
        return False

    def update(self, dt):
        if self.pause_timer > 0:
            self.pause_timer -= dt
            if self.pause_timer <= 0:
                # Resume movement and schedule the first bullet firing
                self.random_movement_timer = random.uniform(1.0, 2.0)
                self.apply_random_movement()
                pyglet.clock.schedule_once(self.fire_wrapper, 0.0)  # Start firing bullets immediately
            return  # Don't update if in pause state
        self.new_objects = [bullet for bullet in self.new_objects if not bullet.dead]
        # Save the previous position
        prev_x = self.x
        prev_y = self.y

        # Update the enemy's position based on velocity
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Check collision in the X direction
        if self.detect_collision_with_walls(self.walls_layer):
            self.x = prev_x
            self.velocity_x = 0
            self.random_movement_timer = random.uniform(1.0, 2.0)  # Reset random movement timer

        # Check collision in the Y direction
        if self.detect_collision_with_walls(self.walls_layer):
            self.y = prev_y
            self.velocity_y = 0
            self.random_movement_timer = random.uniform(1.0, 2.0)  # Reset random movement timer

        # Rest of the update method

        if not self.targeting:
            self.random_movement_timer -= dt
            if self.random_movement_timer <= 0:
                self.random_movement_timer = random.uniform(1.0, 2.0)  # Random duration for random movement
                self.apply_random_movement()
                self.pause_timer = self.pause_duration  # Start pause timer
        else:
            # Calculate direction towards the player
            direction_x = self.player.x - self.x
            direction_y = self.player.y - self.y

            # Normalize the direction vector
            magnitude = (direction_x ** 2 + direction_y ** 2) ** 0.5
            if magnitude != 0:
                direction_x /= magnitude
                direction_y /= magnitude

            # Update the enemy's velocity towards the player
            self.velocity_x = direction_x * self.speed
            self.velocity_y = direction_y * self.speed

            # Decrement the target player timer
            self.target_player_timer -= dt

            # If the target player timer reaches 0, switch back to random movement
            if self.target_player_timer <= 0:
                self.targeting = False
                self.random_movement_timer = random.uniform(1.0, 2.0)  # Random duration for random movement

        # Rest of the update method...

        # Update the enemy animation's position
        self.enemy_sprite.x = self.x
        self.enemy_sprite.y = self.y

        self.bullet_collides_with_player(self.player)

class Grumplord(Enemy):
    def __init__(self, x, y, player, window, walls_layer):
        super().__init__(x, y, player, window, walls_layer=walls_layer)

        # Customize attributes specific to the Grumplord
        self.speed = 150.0  # Adjust the speed
        self.target_duration = 2.0  # Adjust targeting duration
        self.can_fire_shotgun = True  # Flag to control shotgun firing

        # Load Grumplord frames as an animation
        self.enemy_animation = pyglet.image.Animation.from_image_sequence(
            grumplord_frames, duration=0.2, loop=True
        )

        # Create a sprite for the Grumplord animation
        self.enemy_sprite = pyglet.sprite.Sprite(self.enemy_animation)

        

        # Set the initial position of the sprite
        self.enemy_sprite.x = self.x
        self.enemy_sprite.y = self.y

    def fire(self):
        if self.can_fire_shotgun:
            # Calculate direction towards the player
            direction_x = self.player.x - self.x
            direction_y = self.player.y - self.y

            # Normalize the direction vector
            magnitude = (direction_x ** 2 + direction_y ** 2) ** 0.5
            if magnitude != 0:
                direction_x /= magnitude
                direction_y /= magnitude

            # Define the number of bullets in the shotgun blast
            num_bullets = 5  # Adjust as needed

            # Calculate the angular spacing between bullets
            angular_spacing = 20  # Adjust as needed (in degrees)

            # Calculate the initial angle to start firing bullets
            initial_angle = -angular_spacing * (num_bullets // 2)

            # Set the bullet speed
            bullet_speed = 200.0  # Adjust bullet speed as needed

            # Calculate the direction angle from Grumplord to player
            direction_angle = math.atan2(direction_y, direction_x)

            # Create bullets in different directions
            for i in range(num_bullets):
                # Calculate the angle for this bullet relative to the direction angle
                bullet_angle = direction_angle + math.radians(initial_angle + i * angular_spacing)

                # Calculate the velocity for the bullet in this direction
                bullet_velocity_x = bullet_speed * math.cos(bullet_angle)
                bullet_velocity_y = bullet_speed * math.sin(bullet_angle)

                # Create an instance of the enemy bullet and add it to the list of new objects
                bullet = EnemyBullet(self.x, self.y, bullet_velocity_x, bullet_velocity_y,walls_layer=self.walls_layer)
                self.new_objects.append(bullet)

            # Prevent firing another shotgun blast until cooldown completes
            self.can_fire_shotgun = False

            # Schedule the firing cooldown
            fire_cooldown = 2.0  # Adjust the cooldown duration as needed
            pyglet.clock.schedule_once(self.reset_fire_cooldown, fire_cooldown)

    def reset_fire_cooldown(self, dt):
        self.can_fire_shotgun = True

