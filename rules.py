import os
from PIL import Image, ExifTags
import cv2
import numpy as np
import ssdeep

# tiny helpers 
def _open_image_fix_orientation(path):
    img = Image.open(path)
    try:
        exif = img._getexif() or {}
        ori_tag = next((k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None)
        if ori_tag and exif.get(ori_tag) == 3:  img = img.rotate(180, expand=True)
        if ori_tag and exif.get(ori_tag) == 6:  img = img.rotate(270, expand=True)
        if ori_tag and exif.get(ori_tag) == 8:  img = img.rotate(90,  expand=True)
    except Exception:
        pass
    return img

def _gray_cv2(path, cap=900):
    g = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if g is None:  # fallback via PIL
        g = np.array(_open_image_fix_orientation(path).convert("L"))
    h, w = g.shape[:2]
    m = max(h, w)
    if m > cap:
        scale = cap / float(m)
        g = cv2.resize(g, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    return g

# Rule 1: Metadata (max 30)
def rule_metadata(a, b):
    try:
        ia = _open_image_fix_orientation(a)
        ib = _open_image_fix_orientation(b)
        w1, h1 = ia.size
        w2, h2 = ib.size

        # dimension closeness: higher if both width and height are close
        def closeness(x, y):
            if max(x, y) == 0: return 0.0
            return 1.0 - abs(x - y) / float(max(x, y))

        c = (closeness(w1, w2) + closeness(h1, h2)) / 2.0
        dim_pts = int(round(20 * c))

        # file size ratio: rough signal, small weight
        s1, s2 = os.path.getsize(a), os.path.getsize(b)
        ratio = min(s1, s2) / float(max(s1, s2)) if max(s1, s2) else 0.0
        if   ratio >= 0.90: size_pts = 10
        elif ratio >= 0.75: size_pts = 7
        elif ratio >= 0.60: size_pts = 4
        else:               size_pts = 0

        pts = min(30, dim_pts + size_pts)
        note = f"Rule1 Metadata: dims {w1}x{h1} vs {w2}x{h2} (≈{c:.2f}) + size_ratio={ratio:.2f} -> {pts}/30"
        return pts, note
    except Exception as e:
        return 0, f"Rule1 Metadata: ERROR {e} -> 0/30"

# Rule 2: ssdeep (max 10) 
def rule_ssdeep(a, b):
    try:
        h1 = ssdeep.hash_from_file(a)
        h2 = ssdeep.hash_from_file(b)
        sim = ssdeep.compare(h1, h2)  # 0..100
        if   sim >= 80: pts = 10
        elif sim >= 50: pts = 6
        elif sim >= 25: pts = 3
        else:           pts = 0
        return pts, f"Rule2 ssdeep: sim={sim} -> {pts}/10"
    except Exception as e:
        return 0, f"Rule2 ssdeep: ERROR {e} -> 0/10"

# Rule 3: Template match (max 60) 
def _best_corr(tpl, img):
    if tpl.shape[0] > img.shape[0] or tpl.shape[1] > img.shape[1]:
        return 0.0
    res = cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
    return float(cv2.minMaxLoc(res)[1])

def rule_template(a, b):
    try:
        ga = _gray_cv2(a)
        gb = _gray_cv2(b)

        # pick the smaller one as template
        if ga.size <= gb.size:
            tpl0, img = ga, gb
        else:
            tpl0, img = gb, ga

        # scales to try (small set keeps it fast)
        scales = (1.0, 0.9, 0.8)
        best = 0.0

        # raw templates
        for s in scales:
            th = int(tpl0.shape[0] * s); tw = int(tpl0.shape[1] * s)
            if th < 20 or tw < 20:  
                continue
            tpl = cv2.resize(tpl0, (tw, th), interpolation=cv2.INTER_AREA)
            best = max(best, _best_corr(tpl, img))

        # edge-based (brightness-robust)
        e_tpl0 = cv2.Canny(tpl0, 50, 150)
        e_img  = cv2.Canny(img,  50, 150)
        for s in scales:
            th = int(e_tpl0.shape[0] * s); tw = int(e_tpl0.shape[1] * s)
            if th < 20 or tw < 20:
                continue
            e_tpl = cv2.resize(e_tpl0, (tw, th), interpolation=cv2.INTER_AREA)
            best = max(best, _best_corr(e_tpl, e_img))

        # simple piecewise mapping to 0..60
        if   best >= 0.85: pts = 60
        elif best >= 0.80: pts = 54
        elif best >= 0.75: pts = 48
        elif best >= 0.70: pts = 42
        elif best >= 0.65: pts = 36
        elif best >= 0.60: pts = 30
        elif best >= 0.55: pts = 20
        elif best >= 0.50: pts = 10
        else:              pts = 0

        return pts, f"Rule3 Template: best_corr={best:.2f} -> {pts}/60"
    except Exception as e:
        return 0, f"Rule3 Template: ERROR {e} -> 0/60"