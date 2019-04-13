"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
import visualize
from simulation import simulation
import progressbar
from random import sample


def pairs(l):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), 2):
        yield l[i:i + 2]


ROUNDS = 10


def eval_genomes(genomes, config):
    for _, genome in genomes:
        genome.fitness = 0

    for _ in range(ROUNDS):
        for pair in pairs(sample(genomes, len(genomes))):
            if len(pair) == 2:
                [(_, genome1), (_, genome2)] = pair
                simulation(genome1, genome2, config)
            else:
                [(_, genome)] = pair
                simulation(genome, genome, config)
                genome.fitness = genome.fitness / 2


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    local_dir = os.path.dirname(__file__)
    checkpoint_path = os.path.join(local_dir, 'checkpoint')

    if os.path.isfile(checkpoint_path):
        p = neat.Checkpointer.restore_checkpoint(checkpoint_path)
    else:
        p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))

    winner = p.run(eval_genomes, 5000)
    simulation(winner, winner, config, True)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)
