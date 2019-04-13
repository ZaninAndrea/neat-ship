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
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(50))

    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-50')
    winner = p.run(eval_genomes, 1)

    simulation(winner, winner, config, True)

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)
    simulation(winner, winner, config, True)

    # # Display the winning genome.
    # print('\nBest genome:\n{!s}'.format(winner))

    # # Show output of the most fit genome against training data.
    # print('\nOutput:')
    # winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    # for xi, xo in zip(xor_inputs, xor_outputs):
    #     output = winner_net.activate(xi)
    #     print("input {!r}, expected output {!r}, got {!r}".format(
    #         xi, xo, output))

    # node_names = {- 1: 'A', -2: 'B', 0: 'A XOR B'}

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    # p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)
