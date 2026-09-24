"""Validate and package only reviewed public files; standard-library dependencies only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
PUBLIC_URL='https://jokerman89.github.io/lintel/'
GENERATED={'downloads/lintel-techshots-offline.zip','site/file-hashes.json'}
class Links(HTMLParser):
    def __init__(self):super().__init__();self.refs=[];self.ids=set();self.citations=[];self.current_href=None;self.current_label=""
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':self.current_href=a.get('href');self.current_label=''
        if 'id' in a:self.ids.add(a['id'])
        for name in ('href','src','poster'):
            if a.get(name):self.refs.append(a[name])

    def handle_data(self,data):
        if self.current_href is not None:self.current_label+=data
    def handle_endtag(self,tag):
        if tag=='a' and self.current_href is not None:
            self.citations.append((self.current_href,self.current_label));self.current_href=None

def main():
    files=json.loads((ROOT/'site-files.json').read_text(encoding='utf-8'))
    errors=[];parsed={};texts={}
    if len(files)!=len(set(files)):errors.append('Duplicate allowlist entry')
    banned={'.git','.build','.claude','.codex-finalizer','node_modules','__pycache__'}
    for name in files:
        p=ROOT/name
        if Path(name).is_absolute() or '..' in Path(name).parts or banned.intersection(Path(name).parts):
            errors.append('Forbidden publication path: '+name);continue
        if not p.is_file() or p.is_symlink():errors.append('Missing file or symlink: '+name);continue
        if p.suffix in {'.html','.js','.css','.md','.json','.svg'}:
            text=p.read_text(encoding='utf-8-sig');texts[name]=text
            for label,pattern in [('workstation path',r'(?i)(?:[A-Z]:[/\\](?:Users|Workspace)[/\\]|file:///)'),('credential signature',r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')]:
                if re.search(pattern,text):errors.append(label+': '+name)
            if p.suffix=='.html':parser=Links();parser.feed(text);parsed[name]=parser
    slide_text=texts.get('show/content.js','');slides=json.loads(slide_text[slide_text.index('['):slide_text.rindex(']')+1])
    if len({s['id'] for s in slides})!=len(slides):errors.append('Duplicate slide ID')
    if sum(s['minutes'] for s in slides if not s.get('optional'))!=50:errors.append('Core must remain 50 minutes')
    if sum(s['minutes'] for s in slides if s.get('track')=='technical')!=18:errors.append('Technical module must remain 18 minutes')
    if sum(s['minutes'] for s in slides if s.get('track')=='products')!=6:errors.append('Product module must remain 6 minutes')
    if len([s for s in slides if s.get('track')=='products'])!=5:errors.append('Product module must have five slides')
    parsed['show/index.html'].ids.update(s['id'] for s in slides)
    count=0
    def link(source,ref):
        nonlocal count
        u=urlsplit(ref)
        if u.scheme or u.netloc or ref.startswith('data:'):return
        count+=1
        target=(ROOT/Path(source).parent/unquote(u.path)).resolve() if u.path else ROOT/source
        try:name=target.relative_to(ROOT).as_posix()
        except ValueError:errors.append('Link leaves site: '+source+' -> '+ref);return
        if target.is_dir():name=name.rstrip('/')+'/index.html'
        if name not in files and name not in GENERATED:errors.append('Missing public target: '+source+' -> '+ref)
        elif u.fragment and name in parsed and unquote(u.fragment) not in parsed[name].ids:errors.append('Missing anchor: '+source+' -> '+ref)
    for name,parser in parsed.items():
        for ref in parser.refs:link(name,ref)
    for name,text in texts.items():
        if name.endswith('.css'):
            for ref in re.findall(r'url\([\'\"]?([^\)\'\"]+)',text):link(name,ref)
    ranges_checked=0
    for source,parser in parsed.items():
        for ref,label in parser.citations:
            u=urlsplit(ref)
            if u.scheme or 'reference-source/' not in u.path:continue
            target=(ROOT/Path(source).parent/unquote(u.path)).resolve()
            try:name=target.relative_to(ROOT).as_posix()
            except ValueError:continue
            if name not in parsed:continue
            for start,end in re.findall(r':(\d+)\s*[–-]\s*(\d+)',label):
                ranges_checked+=1
                if any('L'+str(n) not in parsed[name].ids for n in range(int(start),int(end)+1)):
                    errors.append('Incomplete cited source range: '+source+' -> '+ref)
    if errors:
        print('\n'.join(sorted(set(errors))));raise SystemExit(1)
    SITE.mkdir(exist_ok=True)
    allowed=set(files)|GENERATED
    extras=[p.relative_to(SITE).as_posix() for p in SITE.rglob('*') if p.is_file() and p.relative_to(SITE).as_posix() not in allowed]
    if extras:raise SystemExit('Staging has unlisted files; review and remove explicitly: '+', '.join(extras))
    for name in files:
        dst=SITE/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}
    (SITE/'site/file-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    (SITE/'downloads').mkdir(exist_ok=True)
    archive=SITE/'downloads/lintel-techshots-offline.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name in files:
            content=(SITE/name).read_bytes()
            if name.endswith('.html') or name=='show/app.js':
                text=content.decode('utf-8-sig')
                text=re.sub(r'(?:\.\./)*downloads/lintel-techshots-offline\.zip',PUBLIC_URL+'downloads/lintel-techshots-offline.zip',text)
                content=text.encode('utf-8')
            z.writestr(name,content)
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise SystemExit('Offline archive failed integrity check')
        if set(z.namelist())!=set(files):raise SystemExit('Offline archive differs from public allowlist')
    print(json.dumps({'public_files':len(files),'local_links_checked':count,'cited_ranges_checked':ranges_checked,'slides':len(slides),'themes':['neon','paper','fluent'],'core_minutes':50,'technical_minutes':18,'product_minutes':6,'archive_bytes':archive.stat().st_size,'result':'PASS'}))
if __name__=='__main__':main()
