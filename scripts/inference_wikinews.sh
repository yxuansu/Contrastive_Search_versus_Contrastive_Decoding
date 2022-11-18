CUDA_VISIBLE_DEVICES=0 python ../inference.py\
    --model_name gpt2-xl\
    --dataset_prefix ../data_from_CD_repo/benchmarks/\
    --dataset wikinews\
    --k 5\
    --alpha 0.6\
    --save_path_prefix ../inference_results/