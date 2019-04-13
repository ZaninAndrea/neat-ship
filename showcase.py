"""
2-input XOR example -- this is most likely the simplest possible example.
"""
import os
import neat
from simulation import simulation
import operator


def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-244')

    genomes = list(p.population.values())
    genomes = [genome for genome in genomes if genome.fitness is not None]
    genomes.sort(key=operator.attrgetter('fitness'))
    best = genomes[:2]
    simulation(best[0], best[1], config, True)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)
