#!/usr/bin/env python3
"""Prepare reviewable storyboards and guard HyperFrames production with versioned approval."""
import argparse
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
import mimetypes
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

HYPERFRAMES = '0.8.37'


def fail(message):
    raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local_file(root, name):
    root = root.resolve()
    if not isinstance(name, str) or not name:
        fail('Use a nonempty project-relative file path.')
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        fail(f'Missing project asset or path outside project: {name}')
    return path


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f'{label} needs a nonempty value; resolve it before storyboarding.')
    return value


def load_project(root):
    data = json.loads(local_file(root, 'project.json').read_text())
    if data.get('schemaVersion') != 1:
        fail('Unsupported project.json schemaVersion; expected 1.')
    product, brand, video = (data.get(k, {}) for k in ('product', 'brand', 'video'))
    for name in ('name', 'summary', 'audience', 'promise', 'cta'):
        text(product.get(name), f'product.{name}')
    if not isinstance(product.get('fictional'), bool):
        fail('product.fictional must explicitly identify a real or fictional product.')
    text(data.get('direction'), 'direction')
    text(brand.get('basis'), 'brand.basis')
    text(brand.get('font'), 'brand.font')
    if not isinstance(brand.get('colors'), dict) or not brand['colors']:
        fail('Define the brand palette.')
    for color in brand['colors'].values():
        if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
            fail('Palette colors must use six-digit hex values.')
    for name in ('width', 'height', 'fps'):
        if type(video.get(name)) is not int or video[name] <= 0:
            fail(f'video.{name} must be a positive integer.')
    if video.get('audio') not in ('none', 'included'):
        fail('video.audio must be none or included; document rights for included audio.')
    scenes = data.get('scenes')
    if not isinstance(scenes, list) or not scenes:
        fail('The storyboard needs at least one scene.')
    files, ids = {}, set()
    for scene in scenes:
        name = text(scene.get('id'), 'scene.id')
        if name in ids:
            fail(f'Duplicate scene id: {name}')
        ids.add(name)
        if type(scene.get('duration')) not in (int, float) or not 0 < scene['duration'] <= 180:
            fail(f'Scene {name} needs a duration between 0 and 180 seconds.')
        for field in ('copy', 'motion'):
            text(scene.get(field), f'{name}.{field}')
        if not isinstance(scene.get('narration', ''), str):
            fail(f'{name}.narration must be text.')
        assets = scene.get('assets', [])
        if not isinstance(assets, list):
            fail(f'{name}.assets must be an array of relative paths.')
        for filename in [scene.get('frame'), *assets]:
            files[filename] = local_file(root, filename).read_bytes()
        frame = files[scene['frame']].decode('utf-8')
        visible = Composition(frame).visible_text()
        if ' '.join(scene['copy'].split()) not in ' '.join(visible.split()):
            fail(f'Exact scene copy is missing from frame: {name}')
    normalized = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    file_hashes = {k: sha(v) for k, v in sorted(files.items())}
    digest = sha(json.dumps({'project': normalized, 'files': file_hashes}, sort_keys=True).encode())
    return data, files, digest


def embedded_frame(root, scene, files):
    frame_path = local_file(root, scene['frame'])
    declared = {local_file(root, a): files[a] for a in scene.get('assets', [])}
    def resource(url):
        if url.startswith('data:') or url.startswith('#'):
            return url
        path = (frame_path.parent / url).resolve()
        if path not in declared:
            fail(f'Frame resource must be local and listed in scene.assets: {url}')
        mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        return f'data:{mime};base64,' + base64.b64encode(declared[path]).decode()
    source = files[scene['frame']].decode()
    class SvgResources(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag in ('image', 'use', 'feimage'):
                for key, value in attrs:
                    if key in ('href', 'xlink:href') and not (value or '').startswith('#'):
                        fail('SVG resource href must be an internal fragment; use a declared image src asset instead.')
    SvgResources().feed(source)
    if re.search(r'<\s*(script|link|iframe|object|embed)\b', source, re.I):
        fail('Storyboard frames must be static and self-contained; inline CSS and use declared local assets.')
    if re.search(r'@import|\bsrcset\s*=', source, re.I):
        fail('Inline stylesheet imports and srcset are unsupported; use declared local assets.')
    if re.search(r'''\bsrc\s*=\s*(?=[^\s'"])''', source, re.I):
        fail('Unquoted src attributes are unsupported; quote and declare every local asset.')
    source = re.sub(r'\bsrc\s*=\s*([\'"])(.*?)\1', lambda m: 'src="'+html.escape(resource(html.unescape(m[2])), quote=True)+'"', source, flags=re.I)
    source = re.sub(r'url\(\s*([\'"]?)(.*?)\1\s*\)', lambda m: 'url("'+resource(m[2])+'")', source, flags=re.I)
    return source


def storyboard_html(root, data, files, digest):
    esc = lambda value: html.escape(str(value), quote=True)
    p, v, b = data['product'], data['video'], data['brand']
    duration = sum(s['duration'] for s in data['scenes'])
    palette = ''.join(f'<span class="swatch"><i style="background:{esc(c)}"></i>{esc(k)} {esc(c)}</span>' for k,c in b['colors'].items())
    rows, start = [], 0
    for index, scene in enumerate(data['scenes'], 1):
        end = start + scene['duration']
        frame = esc(embedded_frame(root, scene, files))
        narration = scene.get('narration') or 'None. The story works with sound off.'
        rows.append(f'<article><div class="scene-heading"><h2>{index:02d} / {esc(scene["id"])}</h2><span>{start:g}–{end:g}s · {scene["duration"]:g}s</span></div><iframe title="Scene {index}: {esc(scene["copy"])}" sandbox="" srcdoc="{frame}" style="aspect-ratio:{v["width"]}/{v["height"]}"></iframe><div class="notes"><div><h3>On-screen copy</h3><p class="copy">{esc(scene["copy"])}</p><h3>Narration</h3><p>{esc(narration)}</p></div><div><h3>Intended motion</h3><p>{esc(scene["motion"])}</p><h3>Assets</h3><p>{esc(", ".join(scene.get("assets", [])) or "Original HTML product UI; no external assets.")}</p></div></div></article>')
        start = end
    fixture = 'Fictional demonstration product' if p['fictional'] else 'Product storyboard'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(p['name'])} · storyboard for approval</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#11141c;color:#e9edf6;font:16px/1.55 Arial,sans-serif}}main{{max-width:1200px;margin:auto;padding:48px 28px 80px}}header{{padding-bottom:34px;border-bottom:1px solid #354054}}h1{{font-size:52px;line-height:1.06;margin:14px 0}}h2{{font-size:20px}}h3{{font-size:12px;text-transform:uppercase;letter-spacing:.13em;color:#a6b7d4;margin:0 0 8px}}p{{margin:0 0 18px}}.eyebrow{{color:#80a9ff;font-weight:bold;font-size:13px;text-transform:uppercase;letter-spacing:.13em}}.lead{{font-size:22px;max-width:840px}}.meta,.brief,.notes{{display:grid;grid-template-columns:1fr 1fr;gap:28px}}.brief{{margin:30px 0}}.meta{{color:#bbc7dc;font-size:14px}}.palette{{display:flex;gap:18px;flex-wrap:wrap;margin:20px 0}}.swatch{{font-size:13px;display:flex;align-items:center;gap:8px}}.swatch i{{width:22px;height:22px;border:1px solid #738098;border-radius:50%}}article{{margin-top:42px}}.scene-heading{{display:flex;justify-content:space-between;align-items:center;color:#dce5f7}}.scene-heading span{{color:#a6b7d4;font-size:14px}}iframe{{display:block;width:100%;border:1px solid #39455c;border-radius:14px;background:white}}.notes{{padding:24px 4px;border-bottom:1px solid #354054}}.copy{{font-size:23px;color:white}}.approval{{margin-top:44px;padding:24px;background:#1d2940;border:1px solid #4678ce;border-radius:12px}}code{{overflow-wrap:anywhere;font-size:12px}}@media(max-width:650px){{main{{padding:28px 16px}}h1{{font-size:36px}}.brief,.notes,.meta{{grid-template-columns:1fr;gap:10px}}.copy{{font-size:20px}}}}
</style><main><header><span class="eyebrow">{fixture} · storyboard v1 · approval required</span><h1>{esc(p['name'])}</h1><p class="lead">{esc(p['summary'])}</p><div class="meta"><span>{v['width']} × {v['height']} · {v['fps']} fps · {duration:g}s</span><span>Audio: {esc(v['audio'])} · static designed frames</span></div></header><section class="brief"><div><h3>Audience</h3><p>{esc(p['audience'])}</p><h3>Promise</h3><p>{esc(p['promise'])}</p><h3>Closing action</h3><p>{esc(p['cta'])}</p></div><div><h3>Creative direction</h3><p>{esc(data['direction'])}</p><h3>Brand basis</h3><p>{esc(b['basis'])}</p><h3>Typography</h3><p>{esc(b['font'])}</p></div></section><div class="palette">{palette}</div>{''.join(rows)}<section class="approval"><h2>Approve this storyboard or request changes</h2><p>Review every designed frame, exact copy, scene timing and motion note. Full video production has not begun. Reply in the conversation with approval or scene-specific refinements. Silence is not approval.</p><p>Storyboard version: <code>{digest}</code></p></section></main></html>'''


def prepare(root):
    data, files, digest = load_project(root)
    result = storyboard_html(root, data, files, digest).encode()
    archive = root / 'storyboards' / f'{digest}.html'
    archive.parent.mkdir(exist_ok=True)
    if archive.exists() and archive.read_bytes() != result:
        fail('Stored storyboard differs for this version; preserve it and inspect the generator change.')
    archive.write_bytes(result)
    (root / 'storyboard.html').write_bytes(result)
    return {'version': digest, 'storyboard': str(root/'storyboard.html'), 'sha256': sha(result)}


def current_storyboard(root):
    data, files, digest = load_project(root)
    expected = storyboard_html(root, data, files, digest).encode()
    path = root/'storyboards'/f'{digest}.html'
    if not path.is_file() or path.read_bytes()!=expected or not (root/'storyboard.html').is_file() or (root/'storyboard.html').read_bytes()!=expected:
        fail('Storyboard is missing or stale. Run storyboard, show it, and obtain approval for this version.')
    return data, digest, sha(expected)


def record_approval(root, version, approver, decision):
    _, digest, storyboard_hash = current_storyboard(root)
    if digest != version:
        fail('Approval version does not match the currently reviewed storyboard.')
    text(approver, 'approver');text(decision, 'explicit approval statement')
    record = {'version':digest,'storyboardSha256':storyboard_hash,'approver':approver,'decision':decision,'at':datetime.now(timezone.utc).isoformat()}
    directory=root/'approvals';directory.mkdir(exist_ok=True)
    path=directory/f'{digest}.json'
    with path.open('x') as f:
        json.dump(record,f,indent=2)
    return record


def check_approval(root):
    data, digest, storyboard_hash=current_storyboard(root)
    path=root/'approvals'/f'{digest}.json'
    if not path.is_file():
        fail('User storyboard approval is required. Do not start full animation or rendering.')
    record=json.loads(path.read_text())
    if record.get('version')!=digest or record.get('storyboardSha256')!=storyboard_hash:
        fail('Approval does not match the current storyboard; obtain renewed approval.')
    text(record.get('approver'),'approval.approver');text(record.get('decision'),'approval.decision')
    return data, record


def run(command, root):
    try:
        result=subprocess.run(command,cwd=root,text=True,capture_output=True,check=True)
    except FileNotFoundError:
        fail(f'Missing command {command[0]}. Install the documented prerequisite and retry.')
    except subprocess.CalledProcessError as error:
        fail(f'{command[0]} failed. Inspect/fix the composition or asset, then retry the same approved version.\n{(error.stderr or error.stdout or "")[-2000:]}')
    return result.stdout


class Composition(HTMLParser):
    def __init__(self, source):
        super().__init__();self.nodes=[];self.words=[];self.ignored=0;self.feed(source)
    def handle_starttag(self, tag, attrs):
        if tag in ('style','script','title'): self.ignored+=1
        self.nodes.append(dict(attrs))
    def handle_endtag(self, tag):
        if tag in ('style','script','title'): self.ignored=max(0,self.ignored-1)
    def handle_data(self, data):
        if not self.ignored: self.words.append(data)
    def visible_text(self):
        return ' '.join(' '.join(self.words).split())


def verify_composition(root, data):
    parsed=Composition(local_file(root,'index.html').read_text())
    composition=next((n for n in parsed.nodes if 'data-composition-id' in n),{})
    duration=sum(s['duration'] for s in data['scenes'])
    for field,expected in [('data-width',data['video']['width']),('data-height',data['video']['height']),('data-duration',duration)]:
        try: matches=float(composition.get(field,'nan'))==expected
        except (TypeError,ValueError): matches=False
        if not matches: fail(f'Composition {field} does not match the approved storyboard.')
    children=[n for n in parsed.nodes if 'data-composition-src' in n]
    if [n.get('id') for n in children]!=[s['id'] for s in data['scenes']]:
        fail('Composition scene IDs/order do not match the approved storyboard.')
    start=0
    for child,scene in zip(children,data['scenes']):
        if float(child.get('data-start','nan'))!=start or float(child.get('data-duration','nan'))!=scene['duration']:
            fail(f'Scene timing differs from approval: {scene["id"]}')
        original=Composition(local_file(root,scene['frame']).read_text()).visible_text()
        subcomposition=Composition(local_file(root,child['data-composition-src']).read_text())
        inner=next((n for n in subcomposition.nodes if 'data-composition-id' in n),{})
        if child.get('data-composition-id')!=scene['id'] or inner.get('data-composition-id')!=scene['id']:
            fail(f'Scene mount and subcomposition IDs must match approval: {scene["id"]}')
        rendered=subcomposition.visible_text()
        if original!=rendered:
            fail(f'Scene text differs from the approved designed frame: {scene["id"]}')
        start+=scene['duration']


def render(root, output):
    root = root.resolve()
    data, approval=check_approval(root)
    verify_composition(root,data)
    destination=(root/output).resolve()
    if not destination.is_relative_to(root) or destination.exists():
        fail('Choose a new output path inside the project; existing videos are preserved.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    cli=['npx','--yes',f'hyperframes@{HYPERFRAMES}']
    run([*cli,'lint'],root)
    run([*cli,'check'],root)
    run([*cli,'render','--skill=product-launch-video','--quality','high','--fps',str(data['video']['fps']),'--output',str(destination)],root)
    metadata=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(destination)],root))
    video=next((s for s in metadata['streams'] if s.get('codec_type')=='video'),None)
    expected=data['video'];duration=sum(s['duration'] for s in data['scenes'])
    if not video: fail('Rendered file has no video stream.')
    numerator,denominator=map(int,video['avg_frame_rate'].split('/'))
    if video.get('codec_name')!='h264' or (video.get('width'),video.get('height'))!=(expected['width'],expected['height']) or abs(numerator/denominator-expected['fps'])>.01 or abs(float(metadata['format']['duration'])-duration)>.2:
        fail('Export specifications do not match the approved storyboard. Inspect ffprobe metadata and fix the render settings.')
    audio=any(s.get('codec_type')=='audio' for s in metadata['streams'])
    if audio!=(expected['audio']=='included'): fail('Export audio does not match the approved audio choice.')
    receipt={'output':str(destination),'approvalVersion':approval['version'],'sha256':sha(destination.read_bytes()),'ffprobe':metadata,'visualQA':'pending; inspect every scene and transition, and playback before delivery'}
    destination.with_suffix('.qa.json').write_text(json.dumps(receipt,indent=2))
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['storyboard','record-approval','check-approval','render'])
    parser.add_argument('project',type=Path)
    parser.add_argument('--version');parser.add_argument('--approver');parser.add_argument('--decision')
    parser.add_argument('--output',default='output/demo.mp4')
    args=parser.parse_args();root=args.project.resolve()
    try:
        if args.command=='storyboard': result=prepare(root)
        elif args.command=='record-approval': result=record_approval(root,args.version,args.approver,args.decision)
        elif args.command=='check-approval': result={'approved':True,'record':check_approval(root)[1]}
        else: result=render(root,args.output)
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError,ZeroDivisionError) as error:
        print(f'ERROR: {error}',file=sys.stderr);return 1
    return 0


if __name__=='__main__': sys.exit(main())
