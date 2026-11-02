#!/usr/bin/env python3
"""Bake 2 s portrait / 2 s original GIF into a control-free animated WebP.
Offline authoring dependencies: Pillow, NumPy and OpenCV.
"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--cache', type=Path, required=True)
parser.add_argument('--background', type=Path, required=True)
parser.add_argument('--assets', type=Path, required=True)
parser.add_argument('--review', type=Path, required=True)
parser.add_argument('--stills', action='store_true')
args = parser.parse_args()
args.review.mkdir(parents=True, exist_ok=True)
SIZE, WIDTH, PADDING, FPS = 768, 928, 80, 50
GIF_LEFT_NUDGE = 24  # About 14 display pixels at the existing desktop size.
PHASE_FRAMES = 2 * FPS
PEACH = np.array([255, 212, 208])
metadata = json.loads((args.cache / 'metadata.json').read_text())
durations = metadata['durations_ms']
frame_ends = np.cumsum(durations)
photo = np.asarray(Image.open(args.assets / 'joshua-portfolio-hero.png').convert('RGB').resize((SIZE, SIZE), Image.Resampling.LANCZOS))
background = np.asarray(Image.open(args.background).convert('RGB'))

# Preserve the existing artwork, desktop photo size, and rounded bust silhouette.
yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
radius = np.hypot(xx - 384, yy - 384) / np.hypot(384, 384)
photo_edge = np.clip((.75 - radius) / .09, 0, 1)[:, :, None]
photo = np.rint(photo * photo_edge + PEACH * (1 - photo_edge)).astype(np.uint8)
ys, xs = np.where(np.all(photo[500:685] < 170, axis=2))
filled = np.zeros((185, SIZE), np.uint8)
cv2.fillConvexPoly(filled, cv2.convexHull(np.column_stack([xs, ys]).astype(np.int32)), 255)
bottom = np.where(filled > 0, np.arange(500, 685)[:, None], 500).max(axis=0).astype(np.float32)
bottom = cv2.GaussianBlur(bottom[None, :], (0, 0), 1.25)[0]

def pad(scene):
    canvas = np.empty((SIZE, WIDTH, 3), np.uint8)
    canvas[:] = PEACH
    canvas[:, PADDING:-PADDING] = scene
    return canvas

photo, background = pad(photo), pad(background)
yy, xx = np.mgrid[0:SIZE, 0:WIDTH].astype(np.float32)
# Source head spans y=20..352; align hairline/chin at about y=90..450.
# One fixed scale preserves original motion and leaves enough room to wave.
scale, source_center, origin_y = 1.08, 278., 68.
map_x = (xx - WIDTH / 2) / scale + source_center
map_y = (yy - origin_y) / scale
bottom = np.pad(bottom, (PADDING, PADDING), constant_values=500)[None, :]
hand_edge = 683 - 130 * np.power(np.abs((xx - WIDTH / 2) / (WIDTH / 2)), 2.3)
hand_weight = np.clip((xx - WIDTH / 2 - 100) / 90, 0, 1)
hand_weight = hand_weight * hand_weight * (3 - 2 * hand_weight)
allowed_bottom = bottom + np.maximum(hand_edge - bottom, 0) * hand_weight
crop = np.clip((allowed_bottom - yy) / 1.5 + .5, 0, 1)
cutouts = []
source_y, source_x = np.mgrid[0:metadata['height'], 0:metadata['width']]
left_edge = np.interp(np.arange(metadata['height']),
    [0, 440, 475, 510, 535, 560, 596, 608, 640],
    [0, 0, 118, 112, 94, 76, 49, 67, 52])[:, None]
first_hand_center = None
for index in range(metadata['frames']):
    original = np.asarray(Image.open(args.cache / f'{index:04d}.png').convert('RGBA')).copy()
    # Refine the source mask around the moving hand. Flood-connected dark room
    # pixels between the fingers are background, not part of the glove.
    rgb = original[:, :, :3]
    fingers = ((rgb[:, :, 0] > 190) & (rgb[:, :, 1] > 130) & (rgb[:, :, 2] > 80)
               & (source_x > 415) & (source_x < 625) & (source_y > 240) & (source_y < 390))
    hand_center = float(source_x[fingers].mean())
    hand_center_y = float(source_y[fingers].mean())
    palm = ((source_x - hand_center + 20) / 62) ** 2 + ((source_y - hand_center_y - 100) / 60) ** 2 < 1
    dark_room = ((rgb[:, :, 0] < 75) & (rgb[:, :, 1] < 43) & (rgb[:, :, 2] < 27)
                 & (rgb[:, :, 1] > rgb[:, :, 0] * .25)
                 & (source_x > 365) & (source_y > 215) & (source_y < 450) & ~palm)
    _, labels = cv2.connectedComponents(dark_room.astype(np.uint8))
    outside = np.unique(labels[dark_room & (original[:, :, 3] < 32)])
    outside = outside[outside != 0]
    original[:, :, 3][np.isin(labels, outside)] = 0
    # Follow the hand's horizontal motion when trimming the stationary chair
    # beyond the cuff; the portrait crop handles the lower edge afterwards.
    if first_hand_center is None:
        first_hand_center = hand_center
    shift = hand_center - first_hand_center
    right_edge = np.interp(np.arange(metadata['height']),
        [0, 400, 420, 430, 460, 500, 550, 600, 640],
        [640, 640, 524+.5*shift, 520+.45*shift, 521+.35*shift,
         529+.25*shift, 540+.15*shift, 557+.08*shift, 567])[:, None]
    exterior = np.clip((source_x - left_edge) / 1.5, 0, 1) * np.clip((right_edge - source_x) / 1.5, 0, 1)
    original[:, :, 3] = np.rint(original[:, :, 3] * exterior).astype(np.uint8)
    # Suppress isolated GIF dithering at the cut edge and keep the connected
    # character opaque; a subpixel blur restores smooth antialiasing.
    solid = (original[:, :, 3] > 127).astype(np.uint8) * 255
    kernel = np.ones((3, 3), np.uint8)
    solid = cv2.morphologyEx(solid, cv2.MORPH_OPEN, kernel)
    count, components, stats, _ = cv2.connectedComponentsWithStats(solid)
    if count > 1:
        solid = np.where(components == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    solid = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, kernel)
    original[:, :, 3] = cv2.GaussianBlur(solid, (3, 3), .45)
    placed = cv2.remap(original, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    placed[:, :, 3] = np.rint(placed[:, :, 3] * crop).astype(np.uint8)
    # Offset only the finished character; the photo, artwork, and scale stay fixed.
    shifted = np.zeros_like(placed)
    shifted[:, :-GIF_LEFT_NUDGE] = placed[:, GIF_LEFT_NUDGE:]
    cutouts.append(shifted)

def composite(cutout):
    alpha = cutout[:, :, 3:4].astype(np.float32) / 255
    return np.rint(cutout[:, :, :3] * alpha + background * (1 - alpha)).astype(np.uint8)

scenes = [composite(cutout) for cutout in cutouts]

def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

def loop_frame(index):
    if index < PHASE_FRAMES:
        return photo
    local = index - PHASE_FRAMES
    source_time = (local * 1000 / FPS) % frame_ends[-1]
    source_index = min(np.searchsorted(frame_ends, source_time, side='right'), len(scenes) - 1)
    # Crossfades sit inside the animation phase; the photo holds for 2 s.
    opacity = smoothstep(local / 10) * smoothstep((PHASE_FRAMES - 1 - local) / 10)
    return np.rint(photo * (1 - opacity) + scenes[source_index] * opacity).astype(np.uint8)

for time in [0, 2.1, 2.4, 2.8, 3.2, 3.6, 3.9]:
    Image.fromarray(loop_frame(round(time * FPS))).save(args.review / f'loop-{time}.png')
Image.fromarray(scenes[0]).save(args.review / 'aligned-gif.png')
Image.fromarray(cutouts[0]).save(args.review / 'transparent-gif.png')
Image.fromarray(scenes[9]).save(args.review / 'aligned-gif-9.png')
Image.fromarray(scenes[17]).save(args.review / 'aligned-gif-17.png')
if not args.stills:
    frames = [Image.fromarray(photo)]
    frames.extend(Image.fromarray(loop_frame(i)) for i in range(PHASE_FRAMES, PHASE_FRAMES * 2))
    output = args.assets / 'joshua-tenor-portrait-loop.webp'
    frames[0].save(output, format='WEBP', save_all=True, append_images=frames[1:],
                   duration=[2000] + [20] * PHASE_FRAMES, loop=0,
                   lossless=False, quality=92, method=4)
    transparent = args.assets / 'tenor-wave-transparent.webp'
    cutout_frames = [Image.fromarray(cutout) for cutout in cutouts]
    cutout_frames[0].save(transparent, format='WEBP', save_all=True, append_images=cutout_frames[1:],
                          duration=durations, loop=0, lossless=False, quality=95, method=4)
    print(json.dumps({'loop': str(output), 'duration_ms': 4000,
                      'photo_ms': 2000, 'gif_ms': 2000, 'transparent': str(transparent)}))
