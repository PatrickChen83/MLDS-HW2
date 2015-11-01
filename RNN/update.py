from itertools import izip
from theano import tensor as T
import config
import param
__author__ = 'patrickchen'

update = None


def initialize_update():
    global update
    update = [(p, p - config.learning_rate * g) for p, g in izip(param.parameters, T.sum(param.grad, axis=0))]
