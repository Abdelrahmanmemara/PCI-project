from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import numpy as np
import scipy.stats
from PIL import Image, ImageEnhance

# Function to resize and enhance the image
def resize_and_enhance_image(image_path, size, sharpness_factor):
    image = Image.open(image_path)
    resized_image = image.resize(size, Image.LANCZOS)
    enhancer = ImageEnhance.Sharpness(resized_image)
    enhanced_image = enhancer.enhance(sharpness_factor)
    enhanced_image_path = image_path.replace(".png", "_resized_enhanced.png")
    enhanced_image.save(enhanced_image_path)
    return enhanced_image_path

# Resize and enhance the images
the_outer_shape = resize_and_enhance_image("images/bubble-full.png", (300, 300), 2.0)

@deserialize
@dataclass
class LotkaVolterraConfig(Config):
    fox_death_rate: float = 0.001
    fox_reproduction_rate: float = 0.1
    movement_speed: float = 1.0
    rabbit_reproduction_rate: float = 0.001
    interaction_distance: float = 5.0  # Increase interaction distance

class Fox(Agent):
    config: LotkaVolterraConfig
    state: str = 'wandering'

    def update(self):
        if self.state == 'wandering':
            self.change_position()
            if np.random.rand() < self.config.fox_death_rate:
                self.kill()
            self.hunt()

    def change_position(self):
        if np.random.rand() < 0.2:  # Increase probability of changing direction
            self.move = Vector2(np.random.uniform(-1, 1), np.random.uniform(-1, 1)).normalize()
        self.pos += self.move * self.config.movement_speed
        self.there_is_no_escape()
    
    def hunt(self):
        print(f"Fox at {self.pos} is hunting")  # Debugging statement
        rabbits = [agent for agent in self.in_proximity_accuracy() if isinstance(agent, Rabbit)]
        print(f"Rabbits in proximity: {len(rabbits)}")  # Debugging statement
        for rabbit in rabbits:
            if self.pos.distance_to(rabbit.pos) < self.config.interaction_distance:
                print(f"Fox at {self.pos} hunting rabbit at {rabbit.pos}")  # Debugging statement
                rabbit.kill()
                self.reproduce()
                break

   
    def there_is_no_escape(self):
        if self.pos.x < 235:
            self.pos.x = 235
        if self.pos.x > 515:
            self.pos.x = 515
        if self.pos.y < 235:
            self.pos.y = 235
        if self.pos.y > 515:
            self.pos.y = 515

class Rabbit(Agent):
    config: LotkaVolterraConfig
    state: str = 'wandering'

    def update(self):
        if self.state == 'wandering':
            self.change_position()
            if np.random.rand() < self.config.rabbit_reproduction_rate:
                self.reproduce()

    def change_position(self):
        if np.random.rand() < 0.2:  # Increase probability of changing direction
            self.move = Vector2(np.random.uniform(-1, 1), np.random.uniform(-1, 1)).normalize()
        self.pos += self.move * self.config.movement_speed
        self.there_is_no_escape()
    
    def there_is_no_escape(self):
        if self.pos.x < 235:
            self.pos.x = 235
        if self.pos.x > 515:
            self.pos.x = 515
        if self.pos.y < 235:
            self.pos.y = 235
        if self.pos.y > 515:
            self.pos.y = 515


(
    Simulation(
        LotkaVolterraConfig(
            image_rotation=True,
            movement_speed=1.0,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(5, Fox, images=["images/red.png"])
    .batch_spawn_agents(20, Rabbit, images=["images/white.png"])
    .spawn_obstacle(the_outer_shape, 375, 375)
    .run()
)
