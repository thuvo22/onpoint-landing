#!/usr/bin/env python3
"""Build responsive WebP derivatives of existing project photos (requires Pillow).

Original files, crop/layout, captions, identity IDs and links to originals stay intact.
The manifest records original hashes and exact derivative dimensions for schema QA.
Run from any directory; no browser, network or publishing operations are performed.
"""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urljoin, urlsplit
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'tools/project-images.json'
BASE = 'https://onpointprostx.com/'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
RECIPE = 'webp-q85-method6-lanczos-v1'


def key(url, page):
    u = urlsplit(urljoin(BASE + page, url))
    return u.path.lstrip('/') if u.netloc == 'onpointprostx.com' else None


class Media(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.stack, self.items = [], []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in {'img','video','meta'}:
            line, col = self.getpos()
            self.items.append((self.offsets[line-1]+col, self.get_starttag_text(), tag, d, list(self.stack)))
        if tag not in VOID:
            self.stack.append((tag,d))

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def slot(page, attrs, parents):
    classes = [d.get('class','').split() for _,d in parents]
    flat = {c for cs in classes for c in cs}
    if page == 'blog/lvp-vs-hardwood.html':
        return '(max-width: 767px) calc(100vw - 32px), 704px'
    if 'project-proof' in flat:
        if 'proof-work' in flat:
            return '(max-width: 640px) calc(100vw - 34px), (max-width: 1151px) calc((100vw - 34px) / 2), 559px'
        if 'proof-pair' in flat:
            if 'proof-wide' in flat:
                return '(max-width: 1151px) calc((100vw - 40px) / 2), 556px'
            return '(max-width: 640px) calc((100vw - 40px) / 2), (max-width: 1151px) calc((100vw - 72px) / 4), 270px'
        if 'proof-wide' in flat:
            return '(max-width: 1151px) calc(100vw - 34px), 1118px'
        return '(max-width: 640px) calc(100vw - 34px), (max-width: 1151px) calc((100vw - 60px) / 2), 546px'
    if 'gallery-card' in flat:
        return '(max-width: 767px) calc(100vw - 32px), (max-width: 1023px) calc((100vw - 72px) / 2), (max-width: 1279px) calc((100vw - 112px) / 3), 384px'
    if 'absolute' in flat:
        return '100vw'
    # Conservative for mixed service/city/hero grids: avoids under-sized downloads.
    if any('md:grid-cols-2' in cs or 'lg:grid-cols-2' in cs for cs in classes):
        return '(max-width: 767px) calc(100vw - 32px), (max-width: 1279px) 50vw, 608px'
    return '(max-width: 767px) calc(100vw - 32px), (max-width: 1279px) calc(100vw - 64px), 1152px'


def set_attr(tag, name, value):
    replacement = name + '="' + html.escape(str(value), quote=True) + '"'
    pattern = r'\b' + re.escape(name) + r'\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27)'
    if re.search(pattern,tag):
        return re.sub(pattern,lambda _: replacement,tag,count=1)
    return tag[:-1] + ' ' + replacement + '>'


def main():
    prior = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    reverse = {v['path']: original for original,row in prior.items() for v in row['variants']}
    pages = sorted(p for p in ROOT.rglob('*.html') if not {'.git','node_modules'} & set(p.relative_to(ROOT).parts))
    originals = set()
    for p in pages:
        for _,_,tag,attrs,_ in Media(p.read_text()).items:
            if tag not in {'img','video'}:
                continue
            path = key(attrs.get('src' if tag == 'img' else 'poster',''),p.relative_to(ROOT).as_posix())
            path = reverse.get(path,path)
            if path and path.startswith(('images/jobs/','images/projects/')):
                originals.add(path)
    manifest = {}
    (ROOT/'images/optimized').mkdir(exist_ok=True)
    for original in sorted(originals):
        source = ROOT/original
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        version = hashlib.sha256((digest+RECIPE).encode()).hexdigest()[:12]
        with Image.open(source) as opened:
            im = ImageOps.exif_transpose(opened).convert('RGB')
            width,height = im.size
            widths = sorted({w for w in [480,800,1200] if w < width} | {min(width,1600)})
            variants=[]
            for w in widths:
                h=round(height*w/width)
                dest=f'images/optimized/{source.stem}-{version}-{w}w.webp'
                if not (ROOT/dest).exists():
                    image=im if w == width else im.resize((w,h),Image.Resampling.LANCZOS)
                    image.save(ROOT/dest,'WEBP',quality=85,method=6)
                # Do not replace an already efficient native-size WebP with a larger encode.
                if w == width and source.suffix.lower() == '.webp' and (ROOT/dest).stat().st_size > source.stat().st_size:
                    shutil.copyfile(source,ROOT/dest)
                variants.append({'path':dest,'width':w,'height':h,'bytes':(ROOT/dest).stat().st_size})
        manifest[original]={'sha256':digest,'recipe':RECIPE,'original_bytes':source.stat().st_size,'original_width':width,'original_height':height,'variants':variants}
    mapping={**manifest,**{old:manifest[src] for old,src in reverse.items() if src in manifest}}
    changed=[]
    for p in pages:
        rel=p.relative_to(ROOT).as_posix(); before=p.read_text(); text=before; edits=[]
        for offset,raw,tag,attrs,parents in Media(before).items:
            attr='src' if tag=='img' else 'poster' if tag=='video' else 'content'
            if tag=='meta' and attrs.get('property',attrs.get('name')) not in {'og:image','twitter:image'}:
                continue
            asset=mapping.get(key(attrs.get(attr,''),rel))
            if not asset:continue
            full=asset['variants'][-1]
            url=BASE+full['path'] if tag=='meta' else '/'+full['path']
            new=set_attr(raw,attr,url)
            if tag=='img':
                for k,v in {'srcset':', '.join('/'+x['path']+' '+str(x['width'])+'w' for x in asset['variants']), 'sizes':slot(rel,attrs,parents),'width':full['width'],'height':full['height']}.items():
                    new=set_attr(new,k,v)
            edits.append((offset,len(raw),new))
        for offset,length,new in reversed(edits):text=text[:offset]+new+text[offset+length:]
        def walk(node):
            if isinstance(node,list):
                for n in node:walk(n)
            elif isinstance(node,dict):
                types=node.get('@type',[])
                if isinstance(types,str):types=[types]
                if 'ImageObject' in types:
                    item=mapping.get(key(node.get('contentUrl',node.get('url','')),rel))
                    if item:
                        full=item['variants'][-1]
                        node['contentUrl']=BASE+full['path'];node['url']=BASE+full['path'];node['encodingFormat']='image/webp'
                        for dim in ['width','height']:
                            node[dim]={'@type':'QuantitativeValue','value':full[dim],'unitText':'pixel'}
                for k,v in list(node.items()):
                    if k in {'image','thumbnailUrl'} and isinstance(v,str) and key(v,rel) in mapping:
                        node[k]=BASE+mapping[key(v,rel)]['variants'][-1]['path']
                    else:walk(v)
        def structured(m):
            data=json.loads(m.group(2));old=json.dumps(data,sort_keys=True);walk(data)
            return m.group(0) if json.dumps(data,sort_keys=True)==old else m.group(1)+json.dumps(data,ensure_ascii=False,separators=(',',':'))+m.group(3)
        text=re.sub(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',structured,text,flags=re.S)
        if text!=before:p.write_text(text);changed.append(rel)
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'project_images':len(manifest),'derivatives':sum(len(v['variants']) for v in manifest.values()),'changed_pages':changed},indent=2))


if __name__=='__main__':main()
