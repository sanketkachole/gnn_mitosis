## Setting up GaNDLF environment

`git clone https://github.com/sarthakpati/GaNDLF.git ./gandlf_mine`
SUCCESS!

`module load python/gpu/3.10.10`
SUCCESS!

`python -m venv ./venv`
SUCCESS!

`source ./venv/bin/activate`
SUCCESS!

`pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116`
SUCCESS!

`python -c "import torch as t;print(t.__version__);print(t.cuda.is_available())"`
1.13.1+cu116
False

`pip install -e .`
SUCCESS!

## Testing GPU availability

`srun -p gpu-debug -A r00362 --time 1:00:00 --cpus-per-task 12 --gpus 1 --pty bash`
srun: job 2067827 queued and waiting for resources
srun: job 2067827 has been allocated resources

`nvidia-smi`
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 515.43.04    Driver Version: 515.43.04    CUDA Version: 11.7     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA A100-SXM...  On   | 00000000:02:00.0 Off |                    0 |
| N/A   34C    P0    51W / 400W |      0MiB / 40960MiB |      0%      Default |
|                               |                      |             Disabled |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+

`module load python/gpu/3.10.10`
SUCCESS!

`source ~/projects/gandlf_mine/venv/bin/activate`
SUCCESS!

`python -c "import torch as t;print(t.__version__);print(t.cuda.is_available())"`
2.0.0+cu117
True

`~/projects/gandlf_mine/venv/bin/python -c "import torch as t;print(t.__version__);print(t.cuda.is_available())"`
1.13.1+cu116
True

## Submitting a job

`python submitter.py`
*****Folder: adam
sbatch -J adam_flexinet_dpn107_cosineannealing_0.0001 --mail-user=patis@iu.edu -e /geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/adam/flexinet_dpn107_cosineannealing_0.0001/adam_flexinet_dpn107_cosineannealing_0.0001.err -o /geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/adam/flexinet_dpn107_cosineannealing_0.0001/adam_flexinet_dpn107_cosineannealing_0.0001.out /geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/runner_iu.sh /N/u/patis/BigRed200/projects/gandlf_mine/venv/bin/python /N/u/patis/BigRed200/projects/gandlf_mine/gandlf_run /geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/train.csv,/geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/valid.csv /geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/adam/flexinet_dpn107_cosineannealing_0.0001.yaml /geode2/home/u070/patis/BigRed200/projects/gandlf_mine/exp_rano/adam/flexinet_dpn107_cosineannealing_0.0001 None
Submitted batch job 2071083

## Checking the status of a job

`squeue -u patis`
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
           2071083       gpu adam_fle    patis PD       0:00      1 (Priority)