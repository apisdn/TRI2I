#!/bin/bash
#SBATCH --time=72:00:00
#SBATCH --nodes=1
#SBATCH --account=notchpeak-gpu
#SBATCH --partition=notchpeak-gpu
#SBATCH -o testg-%j
#SBATCH --job-name=test_ab_day
#SBATCH --mem=0
#SBATCH --gres=gpu:1

DATADIR=/uufs/chpc.utah.edu/common/home/u1081622/dataset
OUTPUT=/uufs/chpc.utah.edu/common/home/u1081622/output.txt

module load miniconda3/latest

cd /uufs/chpc.utah.edu/common/home/u1081622/pytorch-CycleGAN-and-pix2pix

python test.py --dataroot $DATADIR --direction AtoB --model pix2pix --name ab_night --gpu_ids 0 --num_test 5325 > $OUTPUT
