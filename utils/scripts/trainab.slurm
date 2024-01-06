#!/bin/bash
#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --account=notchpeak-gpu
#SBATCH --partition=notchpeak-gpu
#SBATCH -o ba1-%j
#SBATCH --job-name=ab_night
#SBATCH --mem=0
#SBATCH --gres=gpu:4

DATADIR=/uufs/chpc.utah.edu/common/home/u1081622/dataset
OUTPUT=/uufs/chpc.utah.edu/common/home/u1081622/output.txt

module load cuda/11.2 cudnn/8.1.1
module load miniconda3/latest

cd /uufs/chpc.utah.edu/common/home/u1081622/pytorch-CycleGAN-and-pix2pix

python train.py --dataroot $DATADIR --name ab_night --model pix2pix --direction AtoB --dataset_mode aligned --display_id -1 --netG unet_256 --netD n_layers --n_layers_D 3 --gpu_ids 0,1,2,3 --use_wandb --wandb_project_name "pix2pix tir2rgb" > $OUTPUT
