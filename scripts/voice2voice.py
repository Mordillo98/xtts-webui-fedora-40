import subprocess
import os
import json
import glob
from tqdm import tqdm
from pathlib import Path
import requests

def get_rvc_models(this_dir):
    rvc_models_base = this_dir / "voice2voice" / "rvc"
    # exclude the base_models folder from scanning
    exclude_dir = rvc_models_base / "base_models"

    models = []

    # Go through all folders inside rvc except base_models
    for model_dir in rvc_models_base.iterdir():
        if model_dir.is_dir() and model_dir != exclude_dir:
            pth_files = list(model_dir.glob('*.pth'))
            index_files = list(model_dir.glob('*.index'))
            model_name = model_dir.name

            # If there are .pth files, add model information to the list
            if pth_files:
                model_info = {'model_name': model_name}
                model_info['model_path'] = str(pth_files[0].absolute())
                if index_files:
                    model_info['index_path'] = str(index_files[0].absolute())
                models.append(model_info)

    return models

def find_rvc_model_by_name(this_dir,model_name):
    models = get_rvc_models(this_dir)
    for model in models:
        if model['model_name'] == model_name:
            # Check model_index key if it's exists 
            model_index = model.get('index_path', None)
            return model["model_path"] , model_index
    return None


def infer_rvc(pitch,index_rate,protect_voiceless,method,index_path,model_path,input_path,opt_path):
    f0method = method
    device = "cuda:0"
    is_half = True
    filter_radius = 3
    resample_sr = 0
    rms_mix_rate = 1
    protect = protect_voiceless
    crepe_hop_length = 128
    f0_minimum = 50
    f0_maximum = 1100
    autotune_enable = False

    index_path = str(index_path)
    model_path = str(model_path)
    try:
        cmd = [
            'venv/rvc_venv/scripts/python', '-m', 'rvc_python',
            '--input', input_path,
            '--model', index_path,
            '--pitch', str(pitch),
            '--method', f0method,
            '--output', opt_path,
            '--index', model_path,
            '--index_rate', str(index_rate),
            '--device', device,
            '--filter_radius', str(filter_radius),
            '--resample_sr', str(resample_sr),
            '--rms_mix_rate', str(rms_mix_rate),
            '--protect', str(protect).lower()
        ]

        subprocess.run(cmd)
    except Exception as e:
        print(f"Error: {e}")
        return False
    