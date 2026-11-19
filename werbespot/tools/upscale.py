"""Real-ESRGAN (realesr-general-x4v3, SRVGGNetCompact) – reine numpy-Inferenz, ohne torch.
python3 upscale.py weights.pth in.png out.png"""
import pickle, sys, zipfile
import numpy as np
from PIL import Image


def load_pth(path):
    zf = zipfile.ZipFile(path)
    root = zf.namelist()[0].split('/')[0]
    dtypes = {'FloatStorage': np.float32, 'HalfStorage': np.float16, 'LongStorage': np.int64}

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if name in dtypes:
                return name
            if name == '_rebuild_tensor_v2':
                def rb(storage, off, size, stride, *a):
                    arr = storage
                    if not size:
                        return arr[off]
                    st = [s * arr.itemsize for s in stride]
                    return np.lib.stride_tricks.as_strided(arr[off:], size, st).copy()
                return rb
            if name == 'OrderedDict':
                import collections
                return collections.OrderedDict
            return super().find_class(mod, name)

        def persistent_load(self, pid):
            _, stype, key, _, numel = pid
            raw = zf.read(f'{root}/data/{key}')
            return np.frombuffer(raw, dtype=dtypes[stype]).astype(np.float32)

    return U(zf.open(f'{root}/data.pkl')).load()


def conv3(x, w, b):
    C, Hh, Ww = x.shape
    xp = np.pad(x, ((0, 0), (1, 1), (1, 1)))
    cols = np.lib.stride_tricks.sliding_window_view(xp, (3, 3), axis=(1, 2))  # C,H,W,3,3
    cols = cols.transpose(1, 2, 0, 3, 4).reshape(Hh * Ww, C * 9)
    out = cols @ w.reshape(w.shape[0], -1).T + b
    return out.T.reshape(w.shape[0], Hh, Ww)


def prelu(x, a):
    return np.where(x > 0, x, x * a[:, None, None])


def run(sd, img):
    x = img.transpose(2, 0, 1).astype(np.float32)
    h = x
    i = 0
    while f'body.{i}.weight' in sd:
        w = sd[f'body.{i}.weight']
        if w.ndim == 4:
            h = conv3(h, w, sd[f'body.{i}.bias'])
        else:
            h = prelu(h, w)
        i += 1
    r = 4
    C, Hh, Ww = h.shape
    h = h.reshape(C // (r * r), r, r, Hh, Ww).transpose(0, 3, 1, 4, 2).reshape(C // (r * r), Hh * r, Ww * r)
    h += np.repeat(np.repeat(x, r, 1), r, 2)
    return np.clip(h.transpose(1, 2, 0), 0, 1)


if __name__ == '__main__':
    sd = load_pth(sys.argv[1])
    sd = sd.get('params', sd.get('params_ema', sd))
    im = Image.open(sys.argv[2]).convert('RGB')
    out = run(sd, np.asarray(im) / 255.0)
    Image.fromarray((out * 255 + 0.5).astype(np.uint8)).save(sys.argv[3])
    print('ok', out.shape)
