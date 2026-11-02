#!/usr/bin/env python3
"""Remove the supplied GIF's room backdrop without regenerating its animation.

Offline authoring only: pip install 'rembg[cpu]' pillow numpy
"""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '4')
import numpy as np
import onnxruntime as ort
from PIL import Image
from rembg import new_session, remove

parser = argparse.ArgumentParser()
parser.add_argument('input', type=Path)
parser.add_argument('--cache', type=Path, required=True)
args = parser.parse_args()
args.cache.mkdir(parents=True, exist_ok=True)
options = ort.SessionOptions()
options.enable_cpu_mem_arena = False
options.enable_mem_pattern = False
options.inter_op_num_threads = 1
options.intra_op_num_threads = 2
session = new_session('birefnet-general-lite', sess_opts=options, providers=['CPUExecutionProvider'])
source = Image.open(args.input)
durations = []
for index in range(source.n_frames):
    source.seek(index)
    durations.append(source.info.get('duration', 40))
    target = args.cache / f'{index:04d}.png'
    if not target.exists():
        # Preserve the original GIF colors; use the model only for the alpha mask.
        cutout = np.asarray(source.convert('RGBA')).copy()
        mask = np.asarray(remove(source.convert('RGB'), session=session, only_mask=True))
        alpha = np.clip((mask.astype(np.float32) / 255 - .04) / .92, 0, 1)
        cutout[:, :, 3] = np.rint(alpha * 255).astype(np.uint8)
        Image.fromarray(cutout).save(target)
    print(f'Segmented GIF frame {index + 1}/{source.n_frames}', flush=True)
(args.cache / 'metadata.json').write_text(json.dumps({
    'frames': source.n_frames, 'durations_ms': durations,
    'source': 'https://tenor.com/view/anime-anime-wave-bye-wave-bye-gif-21919207',
    'width': source.width, 'height': source.height,
}, indent=2))
