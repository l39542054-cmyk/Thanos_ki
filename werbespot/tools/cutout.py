"""Schuh freistellen (rembg / IS-Net) -> RGBA-PNG.  python3 cutout.py in.png out.png"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove, new_session

im = Image.open(sys.argv[1]).convert('RGB')
sess = new_session('isnet-general-use')
mask = remove(im, session=sess, only_mask=True, post_process_mask=True)
m = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 255
m = np.clip((m - 0.15) / 0.7, 0, 1)
from scipy.ndimage import binary_fill_holes
m = np.maximum(m, binary_fill_holes(m > 0.5).astype(np.float32))
rgba = np.dstack([np.asarray(im), (m * 255).astype(np.uint8)])
out = Image.fromarray(rgba, 'RGBA')
l, t, r, b = out.getbbox()
out.crop((max(0, l - 20), max(0, t - 20), min(out.width, r + 20), min(out.height, b + 20))).save(sys.argv[2])
print('ok', mask.size)
