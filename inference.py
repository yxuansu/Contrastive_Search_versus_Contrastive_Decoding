# coding=utf-8
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.multiprocessing as mp
import argparse, os
import random
import numpy as np
import time
import logging
import progressbar

import logging
logging.getLogger('transformers.generation_utils').disabled = True

import json
def parse_text(item, tokenizer, mode):
    if mode == 'wikitext':
        prefix_text, full_text = item[0]['prompt'].strip(r'<|endoftext|> '), \
        item[0]['gold_ref'].strip(r'<|endoftext|> ')
    else:
        prefix_text, full_text = item[0]['prompt'], item[0]['gold_ref']
    prefix_token_list = tokenizer.tokenize(prefix_text)
    prefix_token_id_list = tokenizer.convert_tokens_to_ids(prefix_token_list)
    prefix_len = len(prefix_token_id_list)

    full_token_list = tokenizer.tokenize(full_text)
    full_token_id_list = tokenizer.convert_tokens_to_ids(full_token_list)
    reference_text = tokenizer.decode(full_token_id_list[prefix_len:])
    return prefix_text, prefix_token_id_list, reference_text

def load_data(in_f, tokenizer, mode):
    with open(in_f, 'r') as json_file:
        json_list = list(json_file)

    result_list = []
    for json_str in json_list:
        result_list.append(json.loads(json_str))
    
    prefix_text_list, prefix_token_id_list, reference_text_list = [], [], []
    for item in result_list:
        one_prefix_text, one_prefix_token_id, one_reference_text = parse_text(item, tokenizer, mode)
        prefix_text_list.append(one_prefix_text)
        prefix_token_id_list.append(one_prefix_token_id)
        reference_text_list.append(one_reference_text)
    return prefix_text_list, prefix_token_id_list, reference_text_list

def parse_config():
    parser = argparse.ArgumentParser()
    # model and data configuration
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--dataset_prefix", type=str)
    parser.add_argument("--dataset", type=str)
    parser.add_argument("--k", type=int)
    parser.add_argument("--alpha", type=float)
    parser.add_argument("--save_path_prefix", type=str)
    return parser.parse_args()

if __name__ == '__main__':
    if torch.cuda.is_available():
        print ('Cuda is available.')
    cuda_available = torch.cuda.is_available()
    args = parse_config()
    device = torch.device('cuda')

    assert args.dataset in ['book', 'wikinews', 'wikitext']
    full_data_path = r'{}/{}_contrastive_gpt2-xl_256.jsonl'.format(args.dataset_prefix, args.dataset)
    print ('Full data path is {}'.format(full_data_path))

    save_path_prefix = args.save_path_prefix + '{}/{}/'.format(args.model_name, args.dataset)
    import os
    if os.path.exists(save_path_prefix):
        pass
    else: # recursively construct directory
        os.makedirs(save_path_prefix, exist_ok=True)
    save_name = '{}_contrastive_k_{}_alpha_{}_result.json'.format(args.dataset, args.k, args.alpha)
    save_path = save_path_prefix + save_name
    print ('Result saving path is {}'.format(save_path))

    print ('Loading model...')
    # load the LMs
    from transformers import GPT2Tokenizer, GPT2LMHeadModel
    model_name = args.model_name
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    eos_token_id = tokenizer.eos_token_id
    model = GPT2LMHeadModel.from_pretrained(model_name)
    if cuda_available:
        model = model.to(device)
    model.eval()
    print ('Model loaded.')

    prefix_text_list, prefix_token_id_list, reference_text_list = \
    load_data(full_data_path, tokenizer, mode=args.dataset)

    print ('Performing inference...')
    data_num = len(prefix_text_list)
    print (data_num)
    p = progressbar.ProgressBar(data_num)
    p.start()
    result_list = []
    with torch.no_grad():
        for index in range(data_num):
            p.update(index)

            one_prefix_text = prefix_text_list[index]
            one_reference_text = reference_text_list[index]
            input_ids = tokenizer(one_prefix_text, return_tensors='pt').input_ids
            if cuda_available:
                input_ids = input_ids.cuda(device)
            _, prefix_len = input_ids.size()

            output = model.generate(input_ids, 
                                    penalty_alpha=args.alpha, 
                                    top_k=args.k, 
                                    max_length=prefix_len+256)

            one_generation_text = tokenizer.decode(output[0][prefix_len:], skip_special_tokens=True)
            one_res_dict = {
                    'prefix_text': one_prefix_text,
                    'reference_text': one_reference_text,
                    'generated_result':{
                            '0':one_generation_text
                    }
            }
            result_list.append(one_res_dict)
    p.finish()
    print ('Inference completed!')

    import json
    with open(save_path, 'w') as outfile:
        json.dump(result_list, outfile, indent=4)
