import sys
import os
import operator
from operator import itemgetter
import torch
from torch import nn
import random
import argparse
import numpy as np
import torch.nn.functional as F

import json
def decode(tokens, tokenizer):
    token_id_list = tokenizer.convert_tokens_to_ids(tokens)
    text = tokenizer.decode(token_id_list)
    return text

def parse_one_text(text, tokenizer, prefix_len):
    tokens = tokenizer.tokenize(text)[prefix_len:]
    return decode(tokens, tokenizer)

def parse_data(prefix_text_list, prediction_text_list, tokenizer):
    assert len(prefix_text_list) == len(prediction_text_list)
    prediction_list = []
    for index in range(len(prefix_text_list)):
        prefix_text, prediction_text = prefix_text_list[index],\
        prediction_text_list[index]

        prefix_tokens = tokenizer.tokenize(prefix_text)
        prefix_len = len(prefix_tokens)
        # extract the generated continuation
        one_prediction = parse_one_text(prediction_text, tokenizer, prefix_len)
        prediction_list.append(one_prediction)
    return prediction_list

def load_result(in_f):
    from transformers import GPT2Tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    with open(in_f, 'r') as json_file:
        json_list = list(json_file)

    result_list = []
    for json_str in json_list:
        result_list.append(json.loads(json_str))

    prefix_text_list, prediction_text_list, gold_text_list = [], [], []
    for item in result_list:
        prefix_text_list.append(item[0]['prompt'])
        prediction_text_list.append(item[0]['gen_text'])

    prediction_list = parse_data(prefix_text_list, prediction_text_list, tokenizer)
    return [prefix_text_list], [prediction_list]

class CoherenceEvaluator(nn.Module):
    def __init__(self, model_name):
        super(CoherenceEvaluator, self).__init__()
        from transformers import GPT2Tokenizer, OPTForCausalLM
        print ('Loading model...')
        self.model = OPTForCausalLM.from_pretrained(model_name)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        print ('Model loaded.')
        self.vocab_size = self.model.config.vocab_size
        print ('The vocabulary size of the language model is {}'.format(self.vocab_size))
        self.embed_dim = self.model.config.hidden_size
        self.bos_token_id = self.tokenizer.bos_token_id

    @torch.no_grad()
    def forward(self, input_ids):
        # input_ids : bsz x seqlen
        bsz, seqlen = input_ids.size()
        outputs = self.model(input_ids=input_ids, output_hidden_states=True)
        logits = outputs.logits
        assert logits.size() == torch.Size([bsz, seqlen, self.vocab_size])
        probability = F.softmax(logits, dim=-1) # bsz x seqlen x vocab_size
        last_hidden_states = outputs.hidden_states[-1]
        assert last_hidden_states.size() == torch.Size([bsz, seqlen, self.embed_dim])
        return last_hidden_states, probability

    def extract_probabilities(self, probabilities, labels):
        '''
            probabilities: 1 x seqlen x vocab_size
            labels: 1 x seqlen
        '''
        _, seqlen, vocab_size = probabilities.size()
        assert labels.size()[1] == seqlen
        p_list = torch.unbind(probabilities, dim=1)
        l_list = torch.unbind(labels, dim=1)
        assert len(p_list) == len(l_list)
        result_list = []
        for idx in range(seqlen):
            one_prob = p_list[idx][:,l_list[idx]].view(-1).detach().cpu().numpy()[0]
            result_list.append(one_prob)
        return result_list

    def compute_coherence(self, context_id, prediction_id):
        '''
            context_id: 1 x context_len
            prediction_id: 1 x prediction_len
        '''
        _, context_len = context_id.size()
        _, prediction_len = prediction_id.size()
        concat = torch.cat([context_id, prediction_id], dim = 1) # 1 x (context_len + prediction)
        hidden_states, probabilities = self.forward(concat)
        _, _, vocab_size = probabilities.size()
        # hidden_states: 1 x (context_len + prediction) x embed_dim
        # probabilities: 1 x (context_len + prediction) x vocab_size

        # extract probabilities
        label_probabilities = probabilities[:,:-1,:][:,-prediction_len:,:]
        # label_probabilities: 1 x prediction x vocab_size
        assert label_probabilities.size()[1] == prediction_len
        assert label_probabilities.size()[2] == vocab_size

        prediction_probability_list = self.extract_probabilities(label_probabilities, prediction_id)
        assert len(prediction_probability_list) == prediction_len
        prediction_logp_list = []
        for p in prediction_probability_list:
            prediction_logp_list.append(np.log(p))

        return np.mean(prediction_logp_list)

    def evaluate_coherence(self, prefix_text, prediction_text, cuda_available, device):
        context_tokens = self.tokenizer.tokenize(prefix_text)
        context_token_ids = [self.bos_token_id] + self.tokenizer.convert_tokens_to_ids(context_tokens)
        context_token_ids = torch.LongTensor(context_token_ids).view(1,-1)

        prediction_tokens = self.tokenizer.tokenize(prediction_text)
        prediction_token_ids = self.tokenizer.convert_tokens_to_ids(prediction_tokens)
        prediction_token_ids = torch.LongTensor(prediction_token_ids).view(1,-1)

        if cuda_available:
            context_token_ids = context_token_ids.cuda(device)
            prediction_token_ids = prediction_token_ids.cuda(device)

        coherence = self.compute_coherence(context_token_ids, prediction_token_ids)
        return coherence

import progressbar
def evaluate_batch_coherence(model, prefix_text_list, prediction_text_list, cuda_available, device):
    assert len(prefix_text_list) == len(prediction_text_list)

    data_num = len(prefix_text_list)
    p = progressbar.ProgressBar(data_num)
    result_list = []
    with torch.no_grad():
        p.start()
        for index in range(data_num):
            p.update(index)
            one_prefix_text = prefix_text_list[index]
            one_prediction_text = prediction_text_list[index]
            if len(one_prediction_text.strip().split()) == 0:
                continue
            one_coherence_score = model.evaluate_coherence(one_prefix_text, one_prediction_text, cuda_available, device)
            result_list.append(one_coherence_score)
        p.finish()
    return np.mean(result_list)

def parse_config():
    parser = argparse.ArgumentParser()
    # model and data configuration
    parser.add_argument("--opt_model_name", type=str)
    parser.add_argument("--test_path", type=str)
    return parser.parse_args()

if __name__ == '__main__':
    if torch.cuda.is_available():
        print ('Cuda is available.')
    cuda_available = torch.cuda.is_available()
    args = parse_config()
    device = torch.device('cuda')

    opt_model_name = args.opt_model_name.split('/')[1]
    evaluation_save_path = args.test_path[:-6] + '_{}_coherence_result.json'.format(opt_model_name)
    print ('Result save path is {}'.format(evaluation_save_path))

    model = CoherenceEvaluator(args.opt_model_name)
    model.eval()
    if cuda_available:
        model = model.to(device)
    model.eval()

    all_prefix_text_list, all_prediction_list = load_result(args.test_path)
    number_of_predictions_per_instance = len(all_prefix_text_list)
    coherence_score_list = []
    for idx in range(number_of_predictions_per_instance):
        one_coherence_score = evaluate_batch_coherence(model, all_prefix_text_list[idx], 
            all_prediction_list[idx], cuda_available=cuda_available, device=device)
        coherence_score_list.append(one_coherence_score)

    coherence_mean, coherence_std = np.mean(coherence_score_list), np.std(coherence_score_list)
    result_dict = {
        "coherence_score_list": [str(num) for num in coherence_score_list],
        "coherence_mean": str(coherence_mean),
        "coherence_std": str(coherence_std)
    }

    print ('Result save path is {}'.format(evaluation_save_path))
    print (result_dict)
    with open(evaluation_save_path, 'w') as outfile:
        json.dump([result_dict], outfile, indent=4)

