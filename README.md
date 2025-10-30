# GaNDLF Experiments Template - KEEP ALL DOWNSTREAM REPOS _PRIVATE_ !!!

This repo contains a mechanism to run multiple [GaNDLF](https://github.com/CBICA/GaNDLF) experiments on the SLURM scheduler for IU clusters (Big Red, Quartz).

Please contribute back to this repo to increase everyone's efficacy. 

## Pre-requisites

- This repo will allow you to submit **multiple** GPU jobs on the cluster, which gives you great power; and you know [what comes with that](https://memegenerator.net/img/instances/10306177/with-great-power-comes-great-responsibility-albus-dumbledore.jpg). If [CIB's](https://uits.iu.edu/about/facilities/cib/index.html) wrath falls upon you, you are on your own.
- Read up on how to submit batch jobs for GPU in [SLURM](https://kb.iu.edu/d/avjk#batch).
- Be intimately familiar with the data you are going to use.
- Be familiar with [GaNDLF's usage](https://cbica.github.io/GaNDLF/usage), and try to do a single epoch training on [the toy dataset](https://cbica.github.io/GaNDLF/usage#examples).
- You have [installed GaNDLF](https://cbica.github.io/GaNDLF/setup) on your home directory or comp_space.
- You have run a single epoch of the GaNDLF training loop (training and validation) using your own data _somewhere_ (either via an [interactive node](https://kb.iu.edu/d/avjk#interactive) or own machine - doesn't matter), so that you know how to [customize the configuration](https://cbica.github.io/GaNDLF/usage#customize-the-training).

## Configurations

All configuration options can be changed depending on the experiment at hand. 

- In the file [`config_generator.py`](./config_generator.py), there are examples using which the various hyper-parameters can be altered to create different configurations. 
- Maximum flexibility is given to the user to decide the base experiment folder (i.e., which hyper-parameter to choose to create folders from) and configuration file structure. 
- It is suggested that the user alters few hyper-parameters while keeping the rest consistent. This allows meaningful comparisons between different experiments.
- This repo allows the creation of such an extensive experimental design.
- Requirements:  
  - A baseline config has been identified.
  - The configurations should be generated under a single folder structure. An example of such a structure exploring 2 different architectures for learning rates of `[0.1,0.01]` with optimizers of `[adam,sgd]` is shown:
```
experiment_template_folder
│
| README.md
|
| config.yaml
|
└───unet
│   │
│   | lr_0.1_adam.yaml
│   | lr_0.01_adam.yaml
│   | lr_0.1_sgd.yaml
│   | lr_0.01_sgd.yaml
│   
└───transunet
│   │
│   | lr_0.1_adam.yaml
│   | lr_0.01_adam.yaml
│   | lr_0.1_sgd.yaml
│   | lr_0.01_sgd.yaml
│   
│ ...   
│   
└───unetr
│   │ ...
```


## Usage

### Creating Configurations

- Once the experimental design has been established, the configurations can be generated using the [`config_generator.py`](./config_generator.py) script. 
- The user can edit this file to create the desired configurations. 
```bash
python config_generator.py
```

### Submitting Jobs to the IU Cluster (Big Red, Quartz)

```bash
python submitter.py -h
usage: GANDLF_Experiment_Submitter [-h] [-i] [-g] [-d] [-f] [-r] [-a] [-e]

Submit GaNDLF experiments on IU Cluster (Big Red, Quartz).

Contact: patis@iu.edu

This program is NOT FDA/CE approved and NOT intended for clinical use.
Copyright (c) 2023 Indiana University. All rights reserved.

optional arguments:
  -h, --help            show this help message and exit
  -i , --interpreter    Full path of python interpreter to be called.
  -g , --gandlfrun      Full path of 'gandlf_run' script to be called.
  -d , --datafile       Full path to 'data.csv'. This can be comma-separated for specific train/val/test files.
  -f , --foldertocopy   Full path to the data folder to copy into the location in '/N/scratch/$username'.
  -r , --runnerscript   'runner.sh' script to be called.
  -a , --account        IU account name.
  -e , --email          Email address to be used for notifications.
```

### Getting overall statistics

The following command will collect the training and validation logs from all experiments and provide the best loss values along with specified metrics for each experiment:

```bash
python config_generator.py -c False
```

This will generate a file `best_info.csv` in the current directory. This file can be used to generate a table of best results for each experiment.

## Important Notes

- All parameters have _some_ defaults, and should be changed based on the experiment at hand.
- Use this repo as template to create a new **PRIVATE** repo.
- Update common config properties as needed.
- Edit the `data.csv` file to fill in updated data list (channel list should not matter as long as it is consistent). Ensure you have read access to the data. This can be changed to separate `train.csv` and `val.csv` files if needed, which can be passed as comma-separated.
- Run `python ./submitter.py` with correct options (**OR** change the defaults - whatever is easier) to submit the experiments.
