import config
import data
from Testbench.util import print_error, my_print
import RNN.config
import RNN.train
import numpy
from RNN.train import initialize_train
__author__ = 'patrickchen'


def run(param):
    pass


def get_acc(param):
    if len(data.training_input) < config.training_segment:
        print_error("training segment > data number")
        return False
    d = 0.0

    # Run all seq between [training_segment, training_input_len)
    for i in range(config.training_segment, data.training_input_len + 1, RNN.config.batch_num):
        c = data.training_input_sequential_selection(RNN.config.batch_num, i)
        d += RNN.train.cost(c[0], c[1])
    my_print("Cost", d)
