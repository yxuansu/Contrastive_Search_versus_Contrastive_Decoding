import json
def parse_num(num_1, num_2):
    res = (num_1 / num_2) * 100
    return round(res, 1)

if __name__ == '__main__':
    result_dict = {
        'book':{
            'contrastive_search':0,
            'contrastive_decoding':0,
            'equal':0
        },
        'wikinews':{
            'contrastive_search':0,
            'contrastive_decoding':0,
            'equal':0
        },
        'wikitext':{
            'contrastive_search':0,
            'contrastive_decoding':0,
            'equal':0
        }
    }

    in_f = r'./human_evaluation_annotations.json'
    with open(in_f) as f:
        human_annotations = json.load(f)

    for item in human_annotations:
        domain = item['domain']
        annotations = item["human_annotation"]
        system_a_name, system_b_name = item['system_a_name'], item['system_b_name']
        for key in annotations:
            one_annotation = annotations[key]
            if one_annotation == "system a is more human-like.":
                result_dict[domain][system_a_name] += 1
            elif one_annotation == "system b is more human-like.":
                result_dict[domain][system_b_name] += 1
            elif one_annotation == "two systems are comparable.":
                result_dict[domain]['equal'] += 1
            else:
                raise Exception('Wrong Annotation!!!')

    for domain in ['wikinews', 'wikitext', 'book']:
        if domain == 'book':
            printed_domain = 'Story'
        elif domain == 'wikinews':
            printed_domain = 'Wikinews'
        else:
            printed_domain = 'Wikitext'

        contrastive_search_result = result_dict[domain]['contrastive_search']
        contrastive_decoding_result = result_dict[domain]['contrastive_decoding']
        equal_result = result_dict[domain]['equal']
        overall_num = contrastive_search_result + contrastive_decoding_result + equal_result
        contrastive_search_result = parse_num(contrastive_search_result, overall_num)
        contrastive_decoding_result = parse_num(contrastive_decoding_result, overall_num)
        equal_result = 100 - contrastive_search_result - contrastive_decoding_result
        
        print ('========================================== Domain: {} =========================================='.format(printed_domain))
        print ('Contrastive Search is better at {}%; Two methods are comparable at {}%; Contrastive Decoding is better at {}%'.format(
        contrastive_search_result, equal_result, contrastive_decoding_result))
        print ('------------------------------------------------------------------------------------------------------'+'\n')
        