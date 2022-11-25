# An Empirical Study On Contrastive Search And Contrastive Decoding For Open-ended Text Generation
**Authors**: Yixuan Su and Jialu Xu

This repository contains code other related resources of our work ["An Empirical Study On Contrastive Search And Contrastive Decoding For Open-ended Text Generation"](https://arxiv.org/abs/2211.10797).

**[Contact]** If you have any questions, feel free to contact me via (ys484 at cam.ac.uk).

****
If you find our paper and resources useful, please kindly leave a star and cite our papers. Thanks!

```bibtex
@article{su2022empirical,
  title={An Empirical Study On Contrastive Search And Contrastive Decoding For Open-ended Text Generation},
  author={Su, Yixuan and Xu, Jialu},
  journal={arXiv preprint arXiv:2211.10797},
  year={2022}
}

@article{su2022contrastiveiswhatyouneed,
  title={Contrastive Search Is What You Need For Neural Text Generation},
  author={Yixuan Su and Nigel Collier},
  journal={arXiv preprint arXiv:2210.14140},
  year={2022}
}

@inproceedings{su2022a,
  title={A Contrastive Framework for Neural Text Generation},
  author={Yixuan Su and Tian Lan and Yan Wang and Dani Yogatama and Lingpeng Kong and Nigel Collier},
  booktitle={Advances in Neural Information Processing Systems},
  editor={Alice H. Oh and Alekh Agarwal and Danielle Belgrave and Kyunghyun Cho},
  year={2022},
  url={https://openreview.net/forum?id=V88BafmH9Pj}
}
```

****

<span id='all_catelogue'/>

### Catalogue:
* <a href='#introduction'>1. Introduction</a>
* <a href='#environment_setup'>2. Environment Setup</a>
* <a href='#data'>3. Benchmark Data and Baseline Results</a>
* <a href='#inference'>4. Perform Inference with Contrastive Search</a>
* <a href='#automatic_evaluation'>5. Automatic Evaluation</a>
    * <a href='#baseline_evaluation'>5.1. Evaluate Baseline Results</a>
        * <a href='#baseline_diversity_and_mauve'>5.1.1. Diversity and MAUVE</a>
        * <a href='#baseline_coherence'>5.1.2. Coherence</a>
    * <a href='#contrastive_search_evaluation'>5.2. Evaluate Contrastive Search Results</a>
        * <a href='#contrastive_search_diversity_and_mauve'>5.2.1. Diversity and MAUVE</a>
        * <a href='#contrastive_search_coherence'>5.2.2. Coherence</a>
* <a href='#human_evaluation'>6. Human Evaluation Results</a>
* <a href='#case_study'>7. Replicating Qualitative Examples of Contrastive Search</a>
    * <a href='#load_language_model'>7.1. Load the Language Model</a>
    * <a href='#table_3'>7.2. Qualitative Example in Table 3</a>    
    * <a href='#table_4'>7.3. Qualitative Example in Table 4</a>    
    * <a href='#table_5'>7.4. Qualitative Example in Table 5</a>  
    
****

<span id='introduction'/>

#### 1. Introduction: <a href='#all_catelogue'>[Back to Top]</a>
In the study, we empirically compare the two recently proposed decoding methods, i.e. Contrastive Search (CS) and Contrastive Decoding (CD), for open-ended text generation. The automatic evaluation results suggest that, while CS performs worse than CD on the MAUVE metric, it substantially surpasses CD on the diversity and coherence metrics. More notably, extensive human evaluations across three different domains demonstrate that human annotators are universally more in favor of CS over CD with substantial margins. 

The contradicted results between MAUVE and human evaluations reveal that MAUVE does not accurately reflect human preferences. Therefore, we call upon the research community to develop better evaluation metrics for open-ended text generation.
****

<span id='environment_setup'/>

#### 2. Environment Setup: <a href='#all_catelogue'>[Back to Top]</a>
Before running the experiments, please setup the environment as
```yaml
pip install torch
pip install simctg --upgrade
pip install mauve-text
pip install "transformers>=4.24.0"
```

****

<span id='data'/>

#### 3. Benchmark Data and Baseline Results: <a href='#all_catelogue'>[Back to Top]</a>
To ensure a fair comparsion with [Li _et al._ (2022)](https://arxiv.org/abs/2210.15097), we use the benchmark data provided by the authors [[here]](https://github.com/XiangLi1999/ContrastiveDecoding/tree/main/text-generation/outputs_ignorePrefix_ccnews_256). The results of compared baselines are also provided by the authors [[here]](https://github.com/XiangLi1999/ContrastiveDecoding/tree/main/text-generation/outputs_ignorePrefix_ccnews_256).

**[Note]** All benchmark data and baseline results are provided by [Li _et al._ (2022)](https://arxiv.org/abs/2210.15097) at [the authors' released repository](https://github.com/XiangLi1999/ContrastiveDecoding/tree/main/text-generation/outputs_ignorePrefix_ccnews_256).



> **** The details of the data directory is listed below:

    .
    └── ./data_from_CD_repo/             
        └── ./benchmarks/ # The folder that contains benchmark data.
            ├── ./wikinews_contrastive_gpt2-xl_256.jsonl # News domain benchmark data.
            ├── ./wikitext_contrastive_gpt2-xl_256.jsonl # Wikipedia domain benchmark data.
            └── ./book_contrastive_gpt2-xl_256.jsonl # Story domain benchmark data.
        └── ./wikinews/ # The folder that contains baseline results for the News domain.
            ├── ./wikinews_greedy_gpt2-xl_256.jsonl # Greedy search result.
            ├── ./wikinews_k-50_gpt2-xl_256.jsonl # Top-k sampling result.
            ├── ./wikinews_p-0.95_gpt2-xl_256.jsonl # Nucleus sampling result.
            ├── ./wikinews_typical-0.95_gpt2-xl_256.jsonl # Typical sampling result.
            └── ./wikinews_gpt2-0.8-t0.5_gpt2-xl_256.jsonl # Contrastive decoding result.
        └── ./wikitext/ # The folder that contains baseline results for the Wikipedia domain.
            ├── ./wikitext_greedy_gpt2-xl_256.jsonl # Greedy search result.
            ├── ./wikitext_k-50_gpt2-xl_256.jsonl # Top-k sampling result.
            ├── ./wikitext_p-0.95_gpt2-xl_256.jsonl # Nucleus sampling result.
            ├── ./wikitext_typical-0.95_gpt2-xl_256.jsonl # Typical sampling result.
            └── ./wikitext_gpt2-0.8-t0.5_gpt2-xl_256.jsonl # Contrastive decoding result.
        └── ./book/ # The folder that contains baseline results for the Story domain.
            ├── ./book_greedy_gpt2-xl_256.jsonl # Greedy search result.
            ├── ./book_k-50_gpt2-xl_256.jsonl # Top-k sampling result.
            ├── ./book_p-0.95_gpt2-xl_256.jsonl # Nucleus sampling result.
            ├── ./book_typical-0.95_gpt2-xl_256.jsonl # Typical sampling result.
            └── ./book_gpt2-0.8-t0.5_gpt2-xl_256.jsonl # Contrastive decoding result.

****

<span id='inference'/>

#### 4. Perform Inference with Contrastive Search: <a href='#all_catelogue'>[Back to Top]</a>
To perform inference with contrastive search, please run the following commands:
```yaml
cd ./scripts/
chmod +x ./inference_{}.sh
./inference_{}.sh
```
where {} is in ['wikinews', 'wikitext', 'story'].

The arguments are as follows:
* `--model_name`: The name of the language model. In our experiments, we use `gpt2-xl`. 
* `--dataset_prefix`: The directory that contains the benchmark data. 
* `--dataset`: The domain of the benchmark data. 
* `--k`: The hyperparameter $k$ in contrastive search.
* `--alpha`: The hyperparameter $\alpha$ in contrastive search.
* `--save_path_prefix`: The directory that stores the inferenced result. 

> **** To ensure the reproducibility of our experiments, we provide the inferenced results of contrastive search as:

    .
    └── ./inference_results/gpt2-xl/             
        └── ./wikinews/ # Results of benchmark from the news domain.
            ├── ./wikinews_contrastive_k_5_alpha_0.6_result.json # The inferenced results of contrastive search.
            ├── ./wikinews_contrastive_k_5_alpha_0.6_result_diversity_mauve_gen_length_result.json # The evaluation results of diversity and MAUVE.
            └── ./wikinews_contrastive_k_5_alpha_0.6_result_opt-2.7b_coherence_result.json # The evaluation result of coherence.
        └── ./wikitext/ # Results of benchmark from the wikipedia domain.
            ├── ./wikitext_contrastive_k_5_alpha_0.6_result.json # The inferenced results of contrastive search.
            ├── ./wikitext_contrastive_k_5_alpha_0.6_result_diversity_mauve_gen_length_result.json # The evaluation results of diversity and MAUVE.
            └── ./wikitext_contrastive_k_5_alpha_0.6_result_opt-2.7b_coherence_result.json # The evaluation result of coherence.
        └── ./book/ # Results of benchmark from the story domain.
            ├── ./book_contrastive_k_6_alpha_0.6_result.json # The inferenced results of contrastive search.
            ├── ./book_contrastive_k_6_alpha_0.6_result_diversity_mauve_gen_length_result.json # The evaluation results of diversity and MAUVE.
            └── ./book_contrastive_k_6_alpha_0.6_result_opt-2.7b_coherence_result.json # The evaluation result of coherence.

        
****

<span id='automatic_evaluation'/>

#### 5. Automatic Evaluation: <a href='#all_catelogue'>[Back to Top]</a>
This section describes how to replicate the automatic evaluation results (i.e. the Figure below) for contrastive search as well as the baseline methods.

<img src="./automatic_evaluation_results.png" width="800" height="250">

<span id='baseline_evaluation'/>

##### 5.1. Evaluate Baseline Results:

<span id='baseline_diversity_and_mauve'/>

###### 5.1.1. Diversity and MAUVE:
To evaluate the diversity and MAUVE results of the baseline methods, please run the following commands:
```yaml
chmod +x ./measure_CD_result.sh
./measure_CD_result.sh
```

The argument is as follows:
* `--test_path`: The file path of the baseline result, e.g. `./data_from_CD_repo/wikinews/wikinews_greedy_gpt2-xl_256.jsonl`.

**[Note]** After the evaluation is completed, the evaluated results will saved in the same directory as the `--test_path`, e.g. `./data_from_CD_repo/wikinews/wikinews_greedy_gpt2-xl_256_diversity_mauve_gen_length_result.json`.


<span id='baseline_coherence'/>

###### 5.1.2. Diversity and MAUVE:
To evaluate the coherence of the baseline methods, please run the following commands:
```yaml
chmod +x ./measure_CD_coherence.sh
./measure_CD_coherence.sh
```

The arguments are as follows:
* `--opt_model_name`: The OPT model used to measure the coherence. In our experiments, we use `facebook/opt-2.7b`.
* `--test_path`: The file path of the baseline result, e.g. `./data_from_CD_repo/wikinews/wikinews_greedy_gpt2-xl_256.jsonl`.

**[Note]** After the evaluation is completed, the evaluated results will saved in the same directory as the `--test_path`, e.g. `./data_from_CD_repo/wikinews/wikinews_greedy_gpt2-xl_256_opt-2.7b_coherence_result.json`.


<span id='contrastive_search_evaluation'/>

##### 5.2. Evaluate Contrastive Search Results:

<span id='contrastive_search_diversity_and_mauve'/>

###### 5.2.1. Diversity and MAUVE:
To evaluate the diversity and MAUVE results of contrastive search, please run the following commands:
```yaml
cd ./scripts/
chmod +x ./measure_mauve.sh
./measure_mauve.sh
```

The argument is as follows:
* `--test_path`: The file path of the inferenced result.

**[Note]** After the evaluation is completed, the evaluated results will saved in the same directory as the `--test_path`.


<span id='contrastive_search_coherence'/>

###### 5.2.2. Coherence:
To evaluate the coherence of the baseline methods, please run the following commands:
```yaml
cd ./scripts/
chmod +x ./measure_coherence.sh
./measure_coherence.sh
```

The arguments are as follows:
* `--opt_model_name`: The OPT model used to measure the coherence. In our experiments, we use `facebook/opt-2.7b`.
* `--test_path`: The file path of the inferenced result.

**[Note]** After the evaluation is completed, the evaluated results will saved in the same directory as the `--test_path`.


****

<span id='human_evaluation'/>

#### 6. Human Evaluation Results: <a href='#all_catelogue'>[Back to Top]</a>
To ensure the reproducibility of our study, we also released the human annotations in our experiments of human evaluation.

<img src="./human_evaluation_results.png" width="650" height="360">

The annotation file is provided [[here]](./human_evaluation_annotations/human_evaluation_annotations.json). To conduct human evaluation, we randomly select a subset of the results generated by contrastive decoding and contrastive search using benchmarks from different domains. The complete results of contrastive decoding and contrastive search are provided as below:

|News Domain|Wikipedia Domain|Story Domain|
|:-------------:|:-------------:|:-------------:|
|[Results of Contrastive Decoding](./data_from_CD_repo/wikinews/wikinews_gpt2-0.8-t0.5_gpt2-xl_256.jsonl)|[Results of Contrastive Decoding](./data_from_CD_repo/wikitext/wikitext_gpt2-0.8-t0.5_gpt2-xl_256.jsonl)|[Results of Contrastive Decoding](./data_from_CD_repo/book/book_gpt2-0.8-t0.5_gpt2-xl_256.jsonl)|
|[Results of Contrastive Search](./inference_results/gpt2-xl/wikinews/wikinews_contrastive_k_5_alpha_0.6_result.json)|[Results of Contrastive Search](./inference_results/gpt2-xl/wikitext/wikitext_contrastive_k_5_alpha_0.6_result.json)|[Results of Contrastive Search](./inference_results/gpt2-xl/book/book_contrastive_k_6_alpha_0.6_result.json)|



To read the human evaluation results, you can simply run the following commands:
```yaml
cd ./human_evaluation_annotations/
python3 parse_human_annotation_results.py
```

The expected output is displayed as below.

```
========================================== Domain: Wikinews ==========================================
Contrastive Search is better at 68.5%; Two methods are comparable at 2.0%; Contrastive Decoding is better at 29.5%
------------------------------------------------------------------------------------------------------

========================================== Domain: Wikitext ==========================================
Contrastive Search is better at 65.0%; Two methods are comparable at 2.0%; Contrastive Decoding is better at 33.0%
------------------------------------------------------------------------------------------------------

========================================== Domain: Story ==========================================
Contrastive Search is better at 67.0%; Two methods are comparable at 1.0%; Contrastive Decoding is better at 32.0%
------------------------------------------------------------------------------------------------------
```

****

<span id='case_study'/>

#### 7. Replicating Qualitative Examples of Contrastive Search: <a href='#all_catelogue'>[Back to Top]</a>

In this section, we show how to reproduce the qualitative examples of contrastive search provided in the paper.

<span id='load_language_model'/>

##### 7.1. Load the Language Model:
First, we load the language model as 

```python
from transformers import GPT2Tokenizer, GPT2LMHeadModel

model_name = 'gpt2-xl'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
model.eval()
```

<span id='table_3'/>

##### 7.2. Qualitative Example in Table 3:

To reproduce the qualitative example in Table 3, we run the following code snippet.
```python
# prepare the prompt text
prefix_text = r'The first attacks carried out by United States Predator drones in Libya reportedly occurred today, as the Pentagon confirmed a strike carried out by the U.S. Air Force'
input_ids = tokenizer(prefix_text, return_tensors='pt').input_ids
_, prefix_len = input_ids.size()

# generate the result with contrastive search
output = model.generate(input_ids, penalty_alpha=0.6, top_k=5, max_length=prefix_len+256)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

<details>
<summary><b>Model Output: [click to expand]</b></summary>
  
```
Output:
----------------------------------------------------------------------------------------------------
The first attacks carried out by United States Predator drones in Libya reportedly occurred today,
as the Pentagon confirmed a strike carried out by the U.S. Air Force in Sirte.

According to Reuters, the drone was targeting militants who "appeared to be preparing to attack a
vehicle carrying Westerners, possibly American, on the outskirts of the city." It is unclear what
the target was, but Reuters reports that "the attack was the first time the United States has
acknowledged using drones in Libya since the overthrow of Muammar Gaddafi in 2011."

In an interview with The New York Times last week, Secretary of State John Kerry said, "We are
going to continue to take strikes wherever we can get them, but the fact of the matter is there
are no boots on the ground in Libya right now, which is a good thing for our national security
and it's a good thing for people's lives."

The Pentagon has been reluctant to provide details about the strikes, citing operational security
concerns. However, a Pentagon spokesman, Rear Adm. John Kirby, said in a statement that "U.S. 
forces conducted a strike against what they believed to be al-Qa'ida-associated terrorists in 
Sirte, Libya, on April 6, targeting a location used by terrorists to train for attacks against 
Westerners."

Kirby did not confirm the identity of the strike, but said it was...
----------------------------------------------------------------------------------------------------
```
</details>


<span id='table_4'/>

##### 7.3. Qualitative Example in Table 4:

To reproduce the qualitative example in Table 4, we run the following code snippet.
```python
# prepare the prompt text
prefix_text = r'The first North Korean crossing at the Paekchin ferry caught the Heavy Mortar Platoon unprepared in the act of setting up its weapons. It also caugh'
input_ids = tokenizer(prefix_text, return_tensors='pt').input_ids
_, prefix_len = input_ids.size()

# generate the result with contrastive search
output = model.generate(input_ids, penalty_alpha=0.6, top_k=5, max_length=prefix_len+256)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

<details>
<summary><b>Model Output: [click to expand]</b></summary>
  
```
Output:
----------------------------------------------------------------------------------------------------
The first North Korean crossing at the Paekchin ferry caught the Heavy Mortar Platoon unprepared
in the act of setting up its weapons. It also caugh to the fact that the North Koreans were able
to get a hold of an M1 Garand and a.30-06, two of the most commonly used weapons in the U.S. Army
and Marine Corps.

This is the first time in my career that I have been in a situation where a weapon of this calibre
was used in combat. It was a big shock to all of us and we had no idea what to do with the weapons
that we had in our hands.

The Heavy Mortar Platoon, under the command of Lt. Cmdr. John Bohn, took cover behind a sandbagged
bunker and waited for the attack to come. Bohn's men fired at the North Koreans as they approached
the bunkers, but their ammunition ran out before they could do much damage.

After several minutes of fire, the bunker was breached and the platoon made a hasty retreat to the
safety of the bunker. As soon as they were out of harm's way, a mortar round slammed into the
bunker and blew it to smithereens.

"That was one of the most intense moments of my life," Bohn said. "I remember looking at the smoke
billowing out of the hole and thinking...
----------------------------------------------------------------------------------------------------
```
</details>

<span id='table_5'/>

##### 7.4. Qualitative Example in Table 5:

To reproduce the qualitative example in Table 5, we run the following code snippet.
```python
# prepare the prompt text
prefix_text = r'Segun was completely lost. His system was on fire. How could he escape this mountain that had come to Mohamed even when Mohamed never gave it a thought to'
input_ids = tokenizer(prefix_text, return_tensors='pt').input_ids
_, prefix_len = input_ids.size()

# generate the result with contrastive search
output = model.generate(input_ids, penalty_alpha=0.6, top_k=6, max_length=prefix_len+256)
print("Output:\n" + 100 * '-')
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("" + 100 * '-')
```

<details>
<summary><b>Model Output: [click to expand]</b></summary>
  
```
Output:
----------------------------------------------------------------------------------------------------
Segun was completely lost. His system was on fire. How could he escape this mountain that had come
to Mohamed even when Mohamed never gave it a thought to do so?

Mohamed looked at the mountain in front of him and thought, "This is the most important thing in my
life right now. I need to climb this mountain as soon as possible so no one gets the chance to
catch me."

As a result, he started the climb at 5:30 in the morning without sleeping for three days and three
nights. It was a grueling and tepid climb with little to no food and very little water. The
temperature hovered around 30 degrees centigrade (86 degrees Fahrenheit), and there was nothing but
wind blowing all around him.

After climbing the 1,000 meters (3,280 feet) in less than an hour, Mohamed reached the top of the
mountain. He felt like he had accomplished something, but at the same time, he was in a daze. He
had no idea what to do with his newly acquired power of telekinesis.

Mohamed took a deep breath and said, "What the hell am I doing?"

The rest of the day was spent trying to figure out how to get back down to the base camp and what
was going to happen to him if he made it back alive.

At one point, a group of...
----------------------------------------------------------------------------------------------------
```
</details>

