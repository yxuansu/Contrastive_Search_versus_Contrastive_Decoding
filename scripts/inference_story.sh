CUDA_VISIBLE_DEVICES=1 python ../inference.py\
    --model_name gpt2-xl\
    --dataset_prefix ../data_from_CD_repo/benchmarks/\
    --dataset book\
    --k 6\
    --alpha 0.6\
    --save_path_prefix ../inference_results/