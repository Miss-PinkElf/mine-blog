#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import base64, json, os, time, urllib.error, urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)

REPO = None
for p in Path(__file__).resolve().parents:
    envp = p / '.codex' / 'skills' / 'gpt-image-generate' / '.env'
    if envp.is_file():
        for raw in envp.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            k, v = k.strip(), v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)
        REPO = p
        break
if REPO is None:
    raise SystemExit('no skill env')

BASE = os.environ['OPENAI_BASE_URL'].rstrip('/')
KEY = os.environ['OPENAI_API_KEY']
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-image-2')
CHAR = REPO / 'zzz-prompt-debug/origin/OC/generated/rin-01-global-design.png'
STYLE = REPO / 'zzz-prompt-debug/origin/OC/ref-style/style-05.jpg'

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)

def post(path, body, timeout=180):
    data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    url = f'{BASE}{path}'
    log(f'POST {url} body={len(data):,} timeout={timeout}')
    req = urllib.request.Request(url, data=data, method='POST', headers={
        'Authorization': f'Bearer {KEY}',
        'Content-Type': 'application/json',
        'User-Agent': 'oc-probe/1.1',
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(getattr(resp, 'status', 200) or 200), resp.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return int(e.code), (e.read() if e.fp else b''), time.time() - t0
    except Exception as e:
        return 0, str(e).encode(), time.time() - t0

def jpeg_bytes(path, max_edge=1024, quality=85):
    try:
        from PIL import Image
        import io
        im = Image.open(path).convert('RGB')
        w, h = im.size
        edge = max(w, h)
        if edge > max_edge:
            s = max_edge / edge
            im = im.resize((int(w * s), int(h * s)), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format='JPEG', quality=quality, optimize=True)
        b = buf.getvalue()
        log(f'  prep {path.name}: {path.stat().st_size:,}->{len(b):,} {im.size}')
        return b, 'image/jpeg'
    except Exception as e:
        b = path.read_bytes()
        log(f'  prep skip {e}: {len(b):,}')
        mime = 'image/jpeg' if path.suffix.lower() in {'.jpg', '.jpeg'} else 'image/png'
        return b, mime

def data_url(mime, raw):
    return f'data:{mime};base64,{base64.b64encode(raw).decode("ascii")}'

def head(raw, n=400):
    return raw.decode('utf-8', errors='replace')[:n].replace('\n', ' ')

def main():
    log(f'base={BASE} model={MODEL} key=***{KEY[-4:]}')
    style_b, style_m = jpeg_bytes(STYLE, max_edge=768)
    char_b, char_m = jpeg_bytes(CHAR, max_edge=1024)
    cases = [
        ('A-chat-text', '/chat/completions', {
            'model': MODEL, 'stream': False,
            'messages': [{'role':'user','content':'Generate a tiny red circle on pure white background. Flat simple icon. No text.'}]
        }, 180),
        ('E-responses-text', '/responses', {
            'model': MODEL,
            'input': [{'role':'user','content':[{'type':'input_text','text':'Generate a tiny blue square on white. Flat icon. No text.'}]}]
        }, 180),
        ('B-chat-single-char', '/chat/completions', {
            'model': MODEL, 'stream': False,
            'messages': [{'role':'user','content':[
                {'type':'text','text':'Using this character design sheet, generate ONE full-body image of the same character standing casually. Preserve hair, eyes, outfit. No text.'},
                {'type':'image_url','image_url':{'url': data_url(char_m, char_b)}},
            ]}]
        }, 240),
        ('C-chat-dual', '/chat/completions', {
            'model': MODEL, 'stream': False,
            'messages': [{'role':'user','content':[
                {'type':'text','text':'Image1=style ref. Image2=character sheet. Generate the character from Image2 in the art style of Image1, rainy neon street, full body, no text.'},
                {'type':'image_url','image_url':{'url': data_url(style_m, style_b)}},
                {'type':'image_url','image_url':{'url': data_url(char_m, char_b)}},
            ]}]
        }, 300),
        ('D-responses-dual', '/responses', {
            'model': MODEL,
            'input': [{'role':'user','content':[
                {'type':'input_text','text':'Image1=style ref. Image2=character sheet. Generate the character from Image2 in the art style of Image1, rainy neon street, full body, no text.'},
                {'type':'input_image','image_url': data_url(style_m, style_b)},
                {'type':'input_image','image_url': data_url(char_m, char_b)},
            ]}]
        }, 300),
    ]
    summary = []
    for name, path, body, timeout in cases:
        log(f'=== {name} ===')
        code, raw, elapsed = post(path, body, timeout)
        outp = OUT / f'probe-{name}.json'
        outp.write_bytes(raw[:2000000])
        maybe = code == 200 and (b'b64' in raw or b'data:image' in raw or b'http' in raw or b'image' in raw.lower())
        row = {'name': name, 'path': path, 'http': code, 'elapsed': round(elapsed,2), 'bytes': len(raw), 'file': str(outp), 'head': head(raw), 'maybe_image': bool(maybe)}
        summary.append(row)
        log(f'  -> http={code} elapsed={elapsed:.1f}s bytes={len(raw):,} maybe_image={maybe}')
        log(f'  head: {row[\"head\"]}')
    sp = OUT / f'probe-summary-{datetime.now().strftime(\"%Y%m%d-%H%M%S\")}.json'
    sp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    log(f'summary written {sp}')
    print('\\nSUMMARY')
    for r in summary:
        print(f\"{r['name']}: http={r['http']} {r['elapsed']}s bytes={r['bytes']} maybe_image={r['maybe_image']}\")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
