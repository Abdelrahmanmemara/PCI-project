from enum import Enum, auto
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import numpy as np
import scipy.stats

@deserialize
@dataclass
class LotkaVolterraConfig(Config):
    fox_death_rate: float = 0.001
    fox_reproduction_rate: float = 0.1
    movement_speed: float = 1.0
    rabbit_reproduction_rate: float = 19/26 # Normalized the 19/6 probability of a rabbit reproducing
    average_life: float = 0.6 # In average 0.6 rabbits only stay alive in the litter.
    interaction_distance: float = 5.0  # Increase interaction distance

class Fox(Agent):
    config: LotkaVolterraConfig
    state: str = 'wandering'

    def update(self):
        self.change_position()
        if np.random.rand() < self.config.fox_death_rate:
            self.kill()
        self.hunt()
    
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


class Rabbit(Agent):
    config: LotkaVolterraConfig
    D:int = 0 # We will make an assumption that every 1000 D is a month
    def update(self):
        self.D += 1
        self.change_position()
        # Every month there is a probability of the rabbit producing a letter. 
        # This probability is 19/26 after normalization
        if self.D % 1000 == 0:
            if np.random.rand() < self.config.rabbit_reproduction_rate:
                self.asexual_reproduction()

    def asexual_reproduction(self):
        # The rabbit can give birth up to 12 per litters.
        for i in range(12):
            if np.random.rand() < self.config.average_life:
                self.reproduce()




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
    .run()
)
