#!/bin/bash
#SBATCH --job-name=CFM-ExploreBench
#SBATCH --partition=kimq,gpua30q,gpul40q
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=CFM-ExploreBench-%j.out
#SBATCH --error=CFM-ExploreBench-%j.err

source ~/miniconda3/bin/activate
conda activate mujoco-env

# One BLAS/OpenMP thread per process. Each SubprocVecEnv worker runs torch,
# which otherwise spawns threads for every core on the node and the 8 workers
# thrash the 8-CPU allocation.
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

cd ~/explore-bench-cfm/explore-bench/cfm-example

echo "Running on $(hostname)"
echo "current directory: $(pwd)"
python --version

nvidia-smi

#DATA COLLECTION

#data collection from teacher 
python collect_data.py --method milp_cpp --every 1 --episodes 10 --out data_cpp.npz
python collect_data.py --method mtsp --replan 10 --episodes 10 --out data_mtsp.npz

#TRAINING 
#training flow-matching with two different teachers
python train_cfm.py --data data_cpp.npz --out cfm_cpp.pt
python train_cfm.py --data data_mtsp.npz --out cfm_mtsp.pt

#EVALUATIONS 

#evaluations for cfm with milp_cpp teacher
python run_eval.py --method cfm --ckpt cfm_cpp.pt --seed 41
python run_eval.py --method cfm --ckpt cfm_cpp.pt --seed 42
python run_eval.py --method cfm --ckpt cfm_cpp.pt --seed 43

#evaluations for cfm with mtsp teacher
python run_eval.py --method cfm --ckpt cfm_mtsp.pt --seed 41
python run_eval.py --method cfm --ckpt cfm_mtsp.pt --seed 42
python run_eval.py --method cfm --ckpt cfm_mtsp.pt --seed 43

#evaluations for mtsp
python run_eval.py --method mtsp --seed 41
python run_eval.py --method mtsp --seed 42
python run_eval.py --method mtsp --seed 43

#evaluations for mtsp
python run_eval.py --method milp_cpp --seed 41
python run_eval.py --method milp_cpp --seed 42
python run_eval.py --method milp_cpp --seed 43

#evaluations for cost
python run_eval.py --method cost --seed 41
python run_eval.py --method cost --seed 42
python run_eval.py --method cost --seed 43

#evaluations for mmpf
python run_eval.py --method mmpf --seed 41
python run_eval.py --method mmpf --seed 42
python run_eval.py --method mmpf --seed 43


WEBHOOK_URL=$(cat ~/.discord_webhook)

curl -sS \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"Job ${SLURM_JOB_ID} finished successfully\"}" \
