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
    fox_death_rate: float = 0.01
    fox_reproduction_rate: float = 0.01
    movement_speed: float = 1.0
    rabbit_reproduction_rate: float = 19/26 # Normalized the 19/6 probability of a rabbit reproducing
    average_life: float = 0.6 # In average 0.6 rabbits only stay alive in the litter.
    interaction_distance: float = 5.0  # Increase interaction distance
    fox_eat_rabbit_prob: float = 0.02  # Rate at which rabbits are eaten by foxes
    dt: float= 0.1
    foxes:int = 5
    rabbits:int = 20

class Fox(Agent):
    config: LotkaVolterraConfig
    state: str = 'wandering'

    def update(self):
        self.change_position()
        if np.random.rand() < self.fox_pop_rate_of_change(self.config.rabbits,self.config.foxes,self.config.fox_reproduction_rate,self.config.fox_death_rate) * self.config.dt:
            self.kill()
            self.config.foxes -= 1
        self.hunt()
    
    def hunt(self):
        print(f"Fox at {self.pos} is hunting")  # Debugging statement
        rabbits = [agent for agent in self.in_proximity_accuracy() if isinstance(agent, Rabbit)]
        print(f"Rabbits in proximity: {len(rabbits)}")  # Debugging statement
        for rabbit in rabbits:
            if self.pos.distance_to(rabbit.pos) < self.config.interaction_distance:
                print(f"Fox at {self.pos} hunting rabbit at {rabbit.pos}")  # Debugging statement
                rabbit.kill()
                self.config.rabbits -= 1
                self.reproduce()
                self.config.foxes += 1
                break

    def fox_pop_rate_of_change(self,B,F,c,d):
        # Using the formula from the Lotka-Volterra
        return (c*B*F) - (d*F)

class Rabbit(Agent):
    config: LotkaVolterraConfig
    D:int = 1000 # We will make an assumption that every 1000 D is a month
    def update(self):
        self.D += 1
        self.change_position()
        # Every month there is a probability of the rabbit producing a letter. 
        # This probability is 19/26 after normalization
        if self.D % 1000 == 0:
            if np.random.rand() < self.config.rabbit_reproduction_rate:
                self.asexual_reproduction()
                self.config.rabbits += 1

    def asexual_reproduction(self):
        # The rabbit can give birth up to 12 per litters.
        for i in range(12):
            # There is a probability of 0.6 of every rabbit in the litter to make it.
            if np.random.rand() < self.config.average_life * self.rate_of_change_rabbit(self.config.rabbits, self.config.foxes, self.config.rabbit_reproduction_rate, self.config.fox_eat_rabbit_prob) * self.config.dt:
                self.reproduce()

    def rate_of_change_rabbit(self,B,F,a,b):
        # Using the formula from the Lotka-Volterra
        return (a*B) - (b*B*F)


simulation =  Simulation(
        LotkaVolterraConfig(
            image_rotation=True,
            movement_speed=1.0,
            radius=50,
            seed=1,
        ))

simulation.batch_spawn_agents(10, Fox, images=["images/red.png"])
simulation.batch_spawn_agents(20, Rabbit, images=["images/white.png"])
simulation.run()

