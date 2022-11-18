import json
import torch
import mauve 
import argparse
import numpy as np

def decode(tokens, tokenizer):
    token_id_list = tokenizer.convert_tokens_to_ids(tokens)
    text = tokenizer.decode(token_id_list)
    return text

def parse_one_mauve_text(text, tokenizer, prefix_len):
    '''
        Truncating the text to maximum token of 128 accoridng to the author's implementation:
        https://github.com/XiangLi1999/ContrastiveDecoding/blob/98cad19349fb08ee95b0f25a661179866f8e2c84/text-generation/eval_script.py#L228
    '''
    tokens = tokenizer.tokenize(text)[prefix_len:][:128]
    return decode(tokens, tokenizer), len(tokens)

def parse_mauve_triplet(prefix_text, prediction_text, gold_text, tokenizer):
    prefix_tokens = tokenizer.tokenize(prefix_text)
    prefix_len = len(prefix_tokens)
    predicted_continuation, predicted_len = parse_one_mauve_text(prediction_text, tokenizer, prefix_len)
    reference_continuation, reference_len = parse_one_mauve_text(gold_text, tokenizer, prefix_len)

    '''
        Only evaluate instances with exact 128 tokens length based on the author's implementation:
        https://github.com/XiangLi1999/ContrastiveDecoding/blob/98cad19349fb08ee95b0f25a661179866f8e2c84/text-generation/eval_script.py#L235
    '''
    if min(predicted_len, reference_len) == 128:
        flag = True
    else:
        flag = False
    return predicted_continuation, reference_continuation, flag

def parse_mauve_all_data(prefix_text_list, prediction_text_list, gold_text_list, tokenizer):
    assert len(prefix_text_list) == len(prediction_text_list)
    assert len(prefix_text_list) == len(gold_text_list)

    predicted_continuation_list, reference_continuation_list = [], []
    for index in range(len(prefix_text_list)):
        prefix_text, prediction_text, gold_text = prefix_text_list[index],\
        prediction_text_list[index], gold_text_list[index]

        one_prediction, one_reference, one_flag = \
        parse_mauve_triplet(prefix_text, prediction_text, gold_text, tokenizer)
        if one_flag:
            predicted_continuation_list.append(one_prediction)
            reference_continuation_list.append(one_reference)
    return predicted_continuation_list, reference_continuation_list

def parse_one_diversity_gen_len_text(text, tokenizer, prefix_len):
    tokens = tokenizer.tokenize(text)[prefix_len:]
    return decode(tokens, tokenizer)

def parse_diversity_gen_len_data(prefix_text_list, prediction_text_list, gold_text_list, tokenizer):
    assert len(prefix_text_list) == len(prediction_text_list)
    assert len(prefix_text_list) == len(gold_text_list)

    prediction_list, reference_list = [], []
    for index in range(len(prefix_text_list)):
        prefix_text, prediction_text, gold_text = prefix_text_list[index],\
        prediction_text_list[index], gold_text_list[index]

        prefix_tokens = tokenizer.tokenize(prefix_text)
        prefix_len = len(prefix_tokens)
        # extract the generated continuation
        one_prediction = parse_one_diversity_gen_len_text(prediction_text, tokenizer, prefix_len)
        # extract the reference continuation
        one_reference = parse_one_diversity_gen_len_text(gold_text, tokenizer, prefix_len)
        prediction_list.append(one_prediction)
        reference_list.append(one_reference)
    return prediction_list, reference_list

        
def load_result(in_f):
    with open(in_f, 'r') as json_file:
        json_list = list(json_file)

    result_list = []
    for json_str in json_list:
        result_list.append(json.loads(json_str))

    prefix_text_list, prediction_text_list, gold_text_list = [], [], []
    for item in result_list:
        prefix_text_list.append(item[0]['prompt'])
        prediction_text_list.append(item[0]['gen_text'])
        gold_text_list.append(item[0]['gold_ref'])
    return prefix_text_list, prediction_text_list, gold_text_list

def compute_one_gen_len(text_list):
    all_len = 0.
    for text in text_list:
        all_len += len(text.strip().split())
    return all_len / len(text_list)

def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_path", type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_config()
    evaluation_save_path = args.test_path[:-6] + '_diversity_mauve_gen_length_result.json'

    from transformers import GPT2Tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    prefix_text_list, prediction_text_list, gold_text_list = load_result(args.test_path)

    print ('Measuring MAUVE...')
    mauve_predicted_continuation_list, mauve_reference_continuation_list = \
    parse_mauve_all_data(prefix_text_list, prediction_text_list, gold_text_list, tokenizer)
    out =  mauve.compute_mauve(p_text=mauve_reference_continuation_list, 
        q_text=mauve_predicted_continuation_list, device_id=0, verbose=False,
        featurize_model_name='gpt2')
    mauve_score = out.mauve
    mauve_score = round(mauve_score*100, 2)
    print ('MAUVE score is {}'.format(mauve_score))

    print ('Measuring diversity and generation length...')
    from simctg.evaluation import measure_repetition_and_diversity
    prediction_list, reference_list = parse_diversity_gen_len_data(prefix_text_list, 
        prediction_text_list, gold_text_list, tokenizer)

    _, _, _, reference_diversity = measure_repetition_and_diversity(reference_list)
    reference_diversity = round(reference_diversity*100, 2)
    _, _, _, prediction_diversity = measure_repetition_and_diversity(prediction_list)
    prediction_diversity = round(prediction_diversity*100, 2)

    print ('Measuring generation length...')
    prediction_gen_length = compute_one_gen_len(prediction_list)
    prediction_gen_length = round(prediction_gen_length, 2)

    result_dict = {
        'reference_div': reference_diversity,
        'prediction_dive': prediction_diversity,
        'prediction_gen_len': prediction_gen_length,
        'mauve_score': mauve_score
    }

    print (result_dict)
    import json
    with open(evaluation_save_path, 'w') as outfile:
        json.dump([result_dict], outfile, indent=4)


