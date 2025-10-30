#!/bin/bash

#SBATCH -p gpu
#SBATCH --mail-type=ALL
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --time=48:00:00

#Load any modules that your program needs
module load python/gpu/3.10.10

echo $SLURM_JOB_NODELIST
echo $SLURM_JOB_NUM_NODES
echo $SLURM_TASKS_PER_NODE
echo $SLURM_GPUS

nvidia-smi -L

### print out some useful execute node information
numcpu=`grep -c processor /proc/cpuinfo`
echo "Number of CPUs: $numcpu"
mem_ask=`grep MemTotal /proc/meminfo`
echo $mem_ask

### Are the GPUs there? This tells you what type of GPUs are present
echo "GPUs located:"
lspci | grep NVIDIA
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

echo "1: $1"
echo "2: $2"
echo "3: $3"
echo "4: $4"
# echo "5: $5" ## old_way: https://github.com/mlcommons/GaNDLF/pull/845

# command_to_run="$1 $2 --inputdata $3 --config $4 --modeldir $5 --train True --device cuda --reset True" ## old_way
command_to_run="$1 --inputdata $2 --config $3 --modeldir $4 --train True --device cuda --reset True"

echo "command_to_run: $command_to_run"

$command_to_run

# $1 ../tackle_scratch_space.py -g $2 -d $3 -c $4 -o $5 -f $6


# $1 \  # python interpreter
# $2 \  # gandlf_run
# --inputdata $3 \  # data.csv
# --config $4 \  # yaml config
# --modeldir $5 \  # output_dir
# --train True --device cuda \  # train on cuda
# --reset True # this removes previously saved checkpoints and data
