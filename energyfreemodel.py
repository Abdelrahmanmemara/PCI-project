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
    fox_death_rate: float = 0.01  # Lowered to increase fox survival
    fox_reproduction_rate: float = 0.05
    movement_speed: float = 1.0
    rabbit_reproduction_rate: float = 0.7
    average_life: float = 0.8
    interaction_distance: float = 20.0
    fox_eat_rabbit_prob: float = 0.02
    dt: float = 0.1
    initial_foxes: int = 10
    initial_rabbits: int = 50

class Fox(Agent):
    config: LotkaVolterraConfig
    state: str = 'wandering'

    def update(self):
        self.change_position()
        if np.random.rand() < self.config.fox_death_rate * self.config.dt:
            self.kill()
            self.config.initial_foxes -= 1
            return
        self.hunt()

    def hunt(self):
        rabbits = [agent for agent in simulation._agents if isinstance(agent, Rabbit)]
        for rabbit in rabbits:
            if self.pos.distance_to(rabbit.pos) < self.config.interaction_distance:
                if np.random.rand() < self.config.fox_eat_rabbit_prob:
                    rabbit.kill()
                    self.config.initial_rabbits -= 1
                    self.reproduce()
                    self.config.initial_foxes += 1
                    break

class Rabbit(Agent):
    config: LotkaVolterraConfig
    D: int = 0

    def update(self):
        self.D += 1
        self.change_position()
        if self.D % 1000 == 0:
            if np.random.rand() < self.config.rabbit_reproduction_rate:
                self.asexual_reproduction()
                self.config.initial_rabbits += 1

    def asexual_reproduction(self):
        for i in range(6):  # Reduced litter size to prevent rapid overpopulation
            if np.random.rand() < self.config.average_life:
                self.reproduce()

# Initialize simulation
simulation = Simulation(
    LotkaVolterraConfig(
        image_rotation=True,
        movement_speed=1.0,
        radius=50,
        seed=1,
    )
)

# Spawn agents
simulation.batch_spawn_agents(10, Fox, images=["images/red.png"])
simulation.batch_spawn_agents(50, Rabbit, images=["images/white.png"])

# Run simulation
simulation.run()
