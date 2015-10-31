__author__ = 'patrickchen'

input_dim = 0
output_dim = 0
hidden_layer_dimension_list = []
batch_num = 1
layer_num = 1

train_input_file = "train.ark"
train_answer_file = "answer_map.txt"
test_input_file = "test.ark"
test_output_file = "test_ans.csv"

random_mu = 0
random_sigma = 0.1


class DumpConfig:
    def __init__(self):
        self.input_dim = 0
        self.output_dim = 0
        self.hidden_layer_neuron_num_list = []
        self.batch_num = 1
        self.layer_num = 1