#!/usr/bin/env python3
"""Build, verify, and serve one offline Principia & Atlas product bundle."""
from __future__ import annotations

import argparse, errno, hashlib, html, http.client, json, mimetypes, os, re, shutil, stat, tempfile, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from urllib.parse import unquote, urlsplit

try:
    from software.product_alpha import package_integrity
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "product_alpha"))
    import package_integrity

CONTRACT="principia-atlas-product-bundle/0.1"; MANIFEST="principia-atlas-manifest.json"
ATLAS_REPORT="atlas-workspace-shell-build-report/0.1"; ATLAS_SHELL="atlas-workspace-shell-data/0.1"
ATLAS_EXPORT="atlas-research-workspace-export/0.1"; ATLAS_MANIFEST="atlas-research-workspace-manifest/0.1"
ATLAS_FILES=("index.html","styles.css","app.js","data/workspace-shell-data.json","data/workspace-export.json","data/workspace-manifest.json")
MAX_JSON=4*1024*1024; MAX_ASSET=32*1024*1024; MAX_FILES=160; MAX_BYTES=128*1024*1024
HOST="127.0.0.1"; DEFAULT_PORT=8010; SHA=re.compile(r"^[0-9a-f]{64}$")
CSP="default-src 'self'; base-uri 'none'; connect-src 'self'; form-action 'none'; frame-ancestors 'none'; img-src 'self' data:; object-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
HEADERS={"cache-control":"no-store","pragma":"no-cache","x-content-type-options":"nosniff","referrer-policy":"no-referrer","cross-origin-opener-policy":"same-origin","cross-origin-resource-policy":"same-origin","x-frame-options":"DENY","content-security-policy":CSP,"permissions-policy":"camera=(), display-capture=(), geolocation=(), microphone=(), payment=(), serial=(), usb=()"}

LAUNCHER='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="One local product bundle joining Principia learning with Atlas exact-revision evidence."><title>Principia &amp; Atlas</title><style>:root{color-scheme:light;--ink:#17221d;--muted:#607069;--paper:#f3f5f1;--card:#fff;--line:#d8e0db;--p:#0f5c4d;--ps:#dceee8;--a:#334c73;--as:#e2e9f4;--gold:#c88b28;--shadow:0 24px 70px #152a221f}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 12% 0,#0f5c4d1a,transparent 28rem),radial-gradient(circle at 92% 5%,#334c731f,transparent 30rem),linear-gradient(180deg,#fafbf8,#f3f5f1);color:var(--ink);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}.skip{position:fixed;top:.75rem;left:1rem;transform:translateY(-180%);background:var(--ink);color:#fff;padding:.7rem 1rem;border-radius:.7rem}.skip:focus{transform:none}.shell{width:min(1180px,calc(100% - 2rem));margin:auto;padding:clamp(2rem,6vw,5rem) 0 3rem}.brand{display:flex;align-items:center;gap:.8rem;margin-bottom:clamp(2.5rem,7vw,5.5rem)}.mark{display:grid;place-items:center;width:3rem;height:3rem;border-radius:1rem;background:linear-gradient(135deg,var(--p),var(--a));color:#fff;font:600 1.1rem Georgia}.brand strong{display:block}.brand small{color:var(--muted);font-weight:800;letter-spacing:.1em;text-transform:uppercase}.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:clamp(2rem,6vw,5rem);align-items:end}.eyebrow{margin:0;color:var(--p);font-size:.73rem;font-weight:900;letter-spacing:.15em;text-transform:uppercase}h1,h2{font-family:Georgia,"Times New Roman",serif;letter-spacing:-.035em;line-height:1.02}h1{max-width:13ch;margin:.55rem 0 1.2rem;font-size:clamp(3rem,8vw,6.6rem)}.lede{max-width:63ch;color:var(--muted);font-size:clamp(1rem,2vw,1.2rem)}.identity{border:1px solid var(--line);border-radius:1.25rem;background:#ffffffc7;box-shadow:var(--shadow);padding:1.2rem}.identity div{display:grid;grid-template-columns:7.5rem 1fr;gap:.8rem;padding:.55rem 0;border-top:1px solid var(--line)}.identity div:first-child{border-top:0}.identity dt{color:var(--muted);font-size:.72rem;font-weight:850;text-transform:uppercase}.identity dd{margin:0;overflow-wrap:anywhere;font-size:.82rem;font-weight:750}.spaces{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:clamp(2rem,6vw,4rem)}.space{display:grid;min-height:24rem;border:1px solid var(--line);border-radius:1.5rem;background:var(--card);box-shadow:var(--shadow);padding:clamp(1.3rem,3vw,2rem);text-decoration:none;color:inherit}.space:focus-visible,.tool:focus-visible{outline:4px solid var(--gold);outline-offset:4px}.space h2{max-width:12ch;margin:1.3rem 0 .8rem;font-size:clamp(2.1rem,4vw,3.4rem)}.space p{color:var(--muted)}.space ul{display:grid;gap:.45rem;padding-left:1.15rem}.num{display:grid;place-items:center;width:2.6rem;height:2.6rem;border-radius:.8rem;font-weight:950}.p .num{background:var(--ps);color:var(--p)}.a .num{background:var(--as);color:var(--a)}.head{display:flex;justify-content:space-between}.cta{align-self:end;display:flex;justify-content:space-between;border-radius:.9rem;padding:.8rem 1rem;color:#fff;font-weight:900}.p .cta{background:var(--p)}.a .cta{background:var(--a)}.tools{display:flex;flex-wrap:wrap;gap:.7rem;margin-top:1rem}.tool{display:inline-flex;align-items:center;min-height:2.8rem;border:1px solid #b8c7bf;border-radius:.8rem;background:#fff;padding:.65rem .85rem;color:inherit;text-decoration:none;font-weight:850}.boundary{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem;margin-top:1rem}.boundary div{border:1px solid var(--line);border-radius:1rem;background:#ffffffbf;padding:.9rem}.boundary strong{display:block;font:600 1.2rem Georgia}.boundary span{color:var(--muted);font-size:.76rem}.foot{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;margin-top:3rem;border-top:1px solid var(--line);padding-top:1.2rem;color:var(--muted);font-size:.8rem}@media(max-width:820px){.hero,.spaces{grid-template-columns:1fr}.boundary{grid-template-columns:1fr 1fr}}@media(max-width:520px){.shell{width:min(100% - 1rem,1180px)}.boundary{grid-template-columns:1fr}.identity div{grid-template-columns:1fr;gap:.2rem}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}</style></head><body><a class="skip" href="#spaces">Skip to product spaces</a><main class="shell"><header class="brand"><span class="mark">P+A</span><span><strong>Principia &amp; Atlas</strong><small>Learning connected to exact evidence</small></span></header><section class="hero"><div><p class="eyebrow">Unified offline product bundle</p><h1>Understand systems. Inspect what supports them.</h1><p class="lede">Principia turns mechanisms into guided learning and design work. Atlas exposes the exact-revision research package behind the evidence boundary. Both remain independently authoritative, but now run as one navigable product.</p></div><dl class="identity"><div><dt>Principia route</dt><dd>{route}</dd></div><div><dt>Principia build</dt><dd><code>{principia_id}</code></dd></div><div><dt>Atlas workspace</dt><dd>{workspace}@{revision}</dd></div><div><dt>Atlas build</dt><dd><code>{atlas_id}</code></dd></div></dl></section><section class="spaces" id="spaces"><a class="space p" href="principia/index.html"><div><div class="head"><p class="eyebrow">Principia · Learn</p><span class="num">01</span></div><h2>Build a causal model.</h2><p>Move through observe, map, model, diagnose, and redesign.</p><ul><li>Guided five-step learning cockpit</li><li>Interactive model and diagnosis</li><li>Private reflection and evidence boundaries</li></ul></div><span class="cta">Open learning experience <span>→</span></span></a><a class="space a" href="atlas/index.html"><div><div class="head"><p class="eyebrow">Atlas · Research</p><span class="num">02</span></div><h2>Inspect exact evidence.</h2><p>Read exact revisions, provenance, warnings, and unresolved candidates.</p><ul><li>Exact-revision research entries</li><li>Visible provenance and lifecycle state</li><li>Read-only decisions</li></ul></div><span class="cta">Open research workspace <span>→</span></span></a></section><nav class="tools" aria-label="Principia operational tools"><a class="tool" href="principia/facilitator.html?build_id={principia_id}">Facilitator recorder</a><a class="tool" href="principia/pilot-lab.html?build_id={principia_id}">Pilot Lab</a></nav><section class="boundary"><div><strong>One runtime</strong><span>Shared launcher and navigation.</span></div><div><strong>Two authorities</strong><span>No status inheritance.</span></div><div><strong>Exact snapshots</strong><span>Both packages are hash-verified.</span></div><div><strong>Zero live calls</strong><span>No account, cloud, or repo network dependency.</span></div></section><footer class="foot"><span>Principia pedagogy remains Principia-owned.</span><span>Atlas knowledge status remains Atlas-owned.</span></footer></main></body></html>'''
NAV_STYLE='<style id="pa-suite-style">.pa-suite{position:fixed;right:1rem;bottom:1rem;z-index:2147483000;display:flex;flex-wrap:wrap;gap:.3rem;max-width:calc(100vw - 2rem);border:1px solid #14211b38;border-radius:.9rem;background:#fffffff5;box-shadow:0 14px 38px #14211b2e;padding:.45rem;font:700 12px/1.2 system-ui}.pa-suite a,.pa-suite span{display:inline-flex;align-items:center;min-height:2.2rem;border-radius:.62rem;padding:.5rem .7rem;color:#17221d;text-decoration:none}.pa-suite a:focus-visible{outline:2px solid #0f5c4d}.pa-suite a[aria-current=page]{background:#17221d;color:#fff}@media(max-width:620px){.pa-suite{left:.5rem;right:.5rem;bottom:.5rem;justify-content:center}}</style>'

def canon(v): return (json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
def digest(raw): return hashlib.sha256(raw).hexdigest()
def json_digest(v,field):
    x=dict(v); x.pop(field,None); return digest(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
def pairs(items):
    out={}
    for k,v in items:
        if k in out: raise ValueError(f"duplicate JSON key: {k!r}")
        out[k]=v
    return out
def reject_constant(v): raise ValueError(f"non-finite JSON constant: {v}")
def decode(raw,label):
    try: value=json.loads(raw.decode(),object_pairs_hook=pairs,parse_constant=reject_constant)
    except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise ValueError(f"{label} is not valid UTF-8 JSON") from exc
    if not isinstance(value,dict): raise ValueError(f"{label} must be an object")
    return value
def read_regular(path,label,limit=MAX_ASSET):
    flags=os.O_RDONLY|getattr(os,"O_BINARY",0)|getattr(os,"O_CLOEXEC",0)|getattr(os,"O_NONBLOCK",0); nofollow=getattr(os,"O_NOFOLLOW",0)
    if nofollow: flags|=nofollow
    elif path.is_symlink(): raise ValueError(f"{label} must be a regular file")
    try: fd=os.open(path,flags)
    except OSError as exc:
        if exc.errno==errno.ELOOP: raise ValueError(f"{label} must be a regular file") from exc
        raise
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode): raise ValueError(f"{label} must be a regular file")
        with os.fdopen(fd,"rb",closefd=False) as stream: raw=stream.read(limit+1)
    finally: os.close(fd)
    if len(raw)>limit: raise ValueError(f"{label} exceeds the byte limit")
    return raw
def safe(value,label="bundle"):
    if not isinstance(value,str) or not value: raise ValueError(f"{label} path is invalid")
    p=PurePosixPath(value)
    if p.is_absolute() or value!=p.as_posix() or "\\" in value or any(x in {"",".",".."} for x in p.parts): raise ValueError(f"{label} path is unsafe")
    return value
def actual(root,label):
    if root.is_symlink() or not root.is_dir(): raise ValueError(f"{label} must be a regular directory")
    out=set()
    for p in root.rglob("*"):
        rel=p.relative_to(root).as_posix()
        if p.is_symlink(): raise ValueError(f"{label} entry must not be a symlink: {rel}")
        if p.is_dir(): continue
        if not p.is_file(): raise ValueError(f"{label} entry must be regular: {rel}")
        out.add(rel)
    return out
def sealed(record,field,label):
    value=record.get(field)
    if not isinstance(value,str) or not SHA.fullmatch(value) or json_digest(record,field)!=value: raise ValueError(f"{label} digest is invalid")
    return value

def load_atlas(root,report_path):
    report_raw=read_regular(report_path,"Atlas report",MAX_JSON); report=decode(report_raw,"Atlas report")
    if report.get("contract")!=ATLAS_REPORT: raise ValueError("Atlas report contract is invalid")
    report_id=sealed(report,"report_digest","Atlas report")
    if any(report.get(k) is not False for k in ("external_network_required","canonical_mutation","repository_mutation","live_principia_dependency")): raise ValueError("Atlas report violates offline boundaries")
    if report.get("static_assets")!=list(ATLAS_FILES[:3]) or report.get("generated_files")!=list(ATLAS_FILES[3:]): raise ValueError("Atlas package shape is incompatible")
    files=set(ATLAS_FILES); seen=actual(root,"Atlas package"); allowed=set(files)
    if "README.md" in seen: allowed.add("README.md")
    try: allowed.add(safe(report_path.relative_to(root).as_posix(),"Atlas report"))
    except ValueError: pass
    if seen!=allowed: raise ValueError("Atlas package file set is incompatible")
    package={p:read_regular(root.joinpath(*PurePosixPath(p).parts),f"Atlas asset {p}") for p in files}
    if "README.md" in seen: package["README.md"]=read_regular(root/"README.md","Atlas README")
    shell=decode(package[ATLAS_FILES[3]],"Atlas shell data"); export=decode(package[ATLAS_FILES[4]],"Atlas export"); manifest=decode(package[ATLAS_FILES[5]],"Atlas manifest")
    if shell.get("contract")!=ATLAS_SHELL or export.get("contract")!=ATLAS_EXPORT or manifest.get("contract")!=ATLAS_MANIFEST: raise ValueError("Atlas package contract is incompatible")
    shell_id=sealed(shell,"build_digest","Atlas shell")
    auth=shell.get("authority")
    required={"accepted_export_only":True,"exact_revision_required":True,"principia_status_separate":True,"zero_external_requests_required":True,"canonical_mutation":False,"repository_mutation":False,"live_principia_dependency":False}
    if not isinstance(auth,dict) or any(auth.get(k)!=v for k,v in required.items()): raise ValueError("Atlas authority boundary is incompatible")
    for record,raw,label in ((shell.get("accepted_export"),package[ATLAS_FILES[4]],"export"),(shell.get("accepted_manifest"),package[ATLAS_FILES[5]],"manifest")):
        artifact=record.get("artifact") if isinstance(record,dict) else None
        if not isinstance(artifact,dict) or artifact.get("bytes")!=len(raw) or artifact.get("sha256")!=digest(raw): raise ValueError(f"Atlas accepted {label} identity is invalid")
    workspace=shell.get("workspace"); refs=export.get("principia_references")
    if report.get("shell_build_digest")!=shell_id or report.get("export_digest")!=export.get("report_digest") or report.get("manifest_digest")!=manifest.get("report_digest"): raise ValueError("Atlas report binding is invalid")
    if not isinstance(workspace,dict) or export.get("workspace")!=workspace or report.get("workspace_id")!=workspace.get("id") or report.get("workspace_revision")!=workspace.get("revision"): raise ValueError("Atlas workspace identity is inconsistent")
    if not isinstance(refs,list) or not refs or any(not isinstance(r,dict) or r.get("principia_status_separate") is not True or r.get("live") is not False or r.get("automatic_status_inheritance") is not False for r in refs): raise ValueError("Atlas Principia reference violates the bridge boundary")
    return {"shell_id":shell_id,"report_id":report_id,"workspace":workspace,"refs":len(refs)},package,report_raw

def launcher(principia,principia_id,atlas):
    doc=LAUNCHER
    values=(("{route}",html.escape(str(principia["route_id"]))),("{principia_id}",html.escape(principia_id)),("{workspace}",html.escape(str(atlas["workspace"]["id"]))),("{revision}",html.escape(str(atlas["workspace"]["revision"]))),("{atlas_id}",html.escape(atlas["shell_id"])))
    for marker,value in values:
        if marker not in doc: raise ValueError(f"launcher marker is missing: {marker}")
        doc=doc.replace(marker,value)
    return doc.encode()
def write_snapshot(output,prefix,files,records):
    for rel,raw in sorted(files.items()):
        path=f"{prefix}/{rel}"; target=output.joinpath(*PurePosixPath(path).parts); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw); records.append({"path":path,"bytes":len(raw),"sha256":digest(raw)})

def build_bundle(principia_root,atlas_root,atlas_report,output):
    pm,pm_raw,ps=package_integrity.load_verified_package(principia_root); pid=digest(pm_raw); am,aps,report_raw=load_atlas(atlas_root,atlas_report); home=launcher(pm,pid,am)
    if output.is_symlink(): raise ValueError("bundle output must not be a symlink")
    if output.exists():
        if not output.is_dir(): raise ValueError("bundle output must be a directory")
        shutil.rmtree(output)
    output.mkdir(parents=True); records=[{"path":"index.html","bytes":len(home),"sha256":digest(home)}]; (output/"index.html").write_bytes(home); write_snapshot(output,"principia",ps,records); write_snapshot(output,"atlas",aps,records)
    report_rel="atlas/workspace-shell-build-report.json"; (output/report_rel).write_bytes(report_raw); records.append({"path":report_rel,"bytes":len(report_raw),"sha256":digest(report_raw)}); records.sort(key=lambda x:x["path"])
    total=sum(x["bytes"] for x in records)
    if len(records)>MAX_FILES or total>MAX_BYTES: raise ValueError("bundle resource limit exceeded")
    unsigned={"contract":CONTRACT,"product":"Principia & Atlas","mode":"offline-exact-snapshots","principia":{"repository":"Rhodan-lab/principle-to-system","path":"principia/","build_contract":pm["contract"],"route_id":pm["route_id"],"build_id":pid,"file_count":len(ps)},"atlas":{"repository":"Rhodan-lab/Atlas","path":"atlas/","shell_contract":ATLAS_SHELL,"shell_build_digest":am["shell_id"],"report_digest":am["report_id"],"workspace":am["workspace"],"principia_reference_count":am["refs"],"file_count":len(aps)+1},"integration":{"authorities_separate":True,"status_inheritance":"prohibited","live_cross_repository_dependency":False,"external_network_required":False,"canonical_mutation":False,"repository_mutation":False,"suite_navigation":"deterministic-runtime-chrome"},"file_count":len(records),"total_bytes":total,"files":records}
    manifest=dict(unsigned); manifest["bundle_id"]=digest(canon(unsigned)); (output/MANIFEST).write_bytes(canon(manifest)); verify_bundle(output); return manifest

def verify_bundle(root):
    raw=read_regular(root/MANIFEST,"bundle manifest",MAX_JSON); manifest=decode(raw,"bundle manifest")
    if manifest.get("contract")!=CONTRACT: raise ValueError("bundle contract is invalid")
    bid=manifest.get("bundle_id"); unsigned=dict(manifest); unsigned.pop("bundle_id",None)
    if not isinstance(bid,str) or not SHA.fullmatch(bid) or digest(canon(unsigned))!=bid: raise ValueError("bundle ID is invalid")
    entries=manifest.get("files")
    if not isinstance(entries,list) or manifest.get("file_count")!=len(entries) or len(entries)>MAX_FILES: raise ValueError("bundle file count is invalid")
    declared={}
    for e in entries:
        if not isinstance(e,dict) or set(e)!={"path","bytes","sha256"}: raise ValueError("bundle file entry is invalid")
        rel=safe(e.get("path")); size=e.get("bytes"); sha=e.get("sha256")
        if rel==MANIFEST or rel in declared or not isinstance(size,int) or not 0<=size<=MAX_ASSET or not isinstance(sha,str) or not SHA.fullmatch(sha): raise ValueError("bundle file identity is invalid")
        declared[rel]=e
    if actual(root,"bundle")!=set(declared)|{MANIFEST}: raise ValueError("bundle file set does not match manifest")
    snapshot={MANIFEST:raw}; total=0
    for rel,e in declared.items():
        data=read_regular(root.joinpath(*PurePosixPath(rel).parts),f"bundle asset {rel}")
        if len(data)!=e["bytes"] or digest(data)!=e["sha256"]: raise ValueError(f"bundle asset identity mismatch: {rel}")
        snapshot[rel]=data; total+=len(data)
    if total!=manifest.get("total_bytes") or total>MAX_BYTES: raise ValueError("bundle byte count is invalid")
    expected_integration={"authorities_separate":True,"status_inheritance":"prohibited","live_cross_repository_dependency":False,"external_network_required":False,"canonical_mutation":False,"repository_mutation":False,"suite_navigation":"deterministic-runtime-chrome"}
    if manifest.get("product")!="Principia & Atlas" or manifest.get("mode")!="offline-exact-snapshots" or manifest.get("integration")!=expected_integration: raise ValueError("bundle authority boundary is invalid")
    pm,pm_raw,ps=package_integrity.load_verified_package(root/"principia"); pid=digest(pm_raw)
    am,aps,_=load_atlas(root/"atlas",root/"atlas"/"workspace-shell-build-report.json")
    expected_principia={"repository":"Rhodan-lab/principle-to-system","path":"principia/","build_contract":pm["contract"],"route_id":pm["route_id"],"build_id":pid,"file_count":len(ps)}
    expected_atlas={"repository":"Rhodan-lab/Atlas","path":"atlas/","shell_contract":ATLAS_SHELL,"shell_build_digest":am["shell_id"],"report_digest":am["report_id"],"workspace":am["workspace"],"principia_reference_count":am["refs"],"file_count":len(aps)+1}
    if manifest.get("principia")!=expected_principia or manifest.get("atlas")!=expected_atlas: raise ValueError("bundle source identity is invalid")
    return manifest,snapshot

def check_determinism(principia,atlas,report):
    with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
        ma=build_bundle(principia,atlas,report,Path(a)); mb=build_bundle(principia,atlas,report,Path(b)); _,sa=verify_bundle(Path(a)); _,sb=verify_bundle(Path(b))
        if ma!=mb or sa!=sb: raise ValueError("bundle build is not deterministic")
def request_path(raw):
    value=unquote(urlsplit(raw).path)
    if "\x00" in value or "\\" in value: raise ValueError("unsafe path")
    if value=="/": return "index.html"
    if value.endswith("/"): value+="index.html"
    value=value.lstrip("/"); return safe(value,"request")
def nav_link(href,label,current=False): return f'<a href="{html.escape(href,quote=True)}"'+(' aria-current="page"' if current else '')+f'>{html.escape(label)}</a>'
def inject_nav(rel,raw,pid):
    if rel=="index.html" or not rel.endswith(".html") or not rel.startswith(("principia/","atlas/")): return raw
    doc=raw.decode();
    if doc.count("</head>")!=1 or doc.count("</body>")!=1 or "class=\"pa-suite\"" in doc: raise ValueError("HTML boundary is invalid")
    nav='<nav class="pa-suite" aria-label="Principia and Atlas product navigation"><span>Principia &amp; Atlas</span>'+nav_link("/","Home")+nav_link("/principia/index.html","Learn",rel.startswith("principia/"))+nav_link("/atlas/index.html","Research",rel.startswith("atlas/"))+nav_link(f"/principia/facilitator.html?build_id={pid}","Recorder")+nav_link(f"/principia/pilot-lab.html?build_id={pid}","Pilot Lab")+'</nav>'
    return doc.replace("</head>",NAV_STYLE+"</head>",1).replace("</body>",nav+"</body>",1).encode()

class Handler(BaseHTTPRequestHandler):
    snapshot={}; manifest={}; quiet=False
    def trusted(self):
        port=int(self.server.server_address[1]); return self.headers.get("Host","") in {HOST,f"{HOST}:{port}"}
    def send_bundle_headers(self,status,ctype,length):
        self.send_response(status)
        for k,v in HEADERS.items(): self.send_header(k,v)
        self.send_header("content-type",ctype); self.send_header("content-length",str(length)); self.end_headers()
    def serve(self,body):
        if not self.trusted(): data=b"Loopback Host header required\n"; self.send_bundle_headers(421,"text/plain; charset=utf-8",len(data)); return self.wfile.write(data) if body else None
        try: rel=request_path(self.path)
        except ValueError: rel=""
        raw=self.snapshot.get(rel)
        if raw is None: data=b"Not found\n"; self.send_bundle_headers(404,"text/plain; charset=utf-8",len(data)); return self.wfile.write(data) if body else None
        pid=self.manifest["principia"]["build_id"]
        try: data=inject_nav(rel,raw,pid)
        except (UnicodeDecodeError,ValueError): data=b"Bundle HTML boundary invalid\n"; self.send_bundle_headers(500,"text/plain; charset=utf-8",len(data)); return self.wfile.write(data) if body else None
        ctype=mimetypes.guess_type(rel)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in {"application/javascript","application/json"}: ctype+="; charset=utf-8"
        self.send_bundle_headers(200,ctype,len(data)); return self.wfile.write(data) if body else None
    def do_GET(self): self.serve(True)
    def do_HEAD(self): self.serve(False)
    def log_message(self,fmt,*args):
        if not self.quiet: super().log_message(fmt,*args)
def create_server(root,port=DEFAULT_PORT,quiet=False):
    if not 0<=port<=65535: raise ValueError("port must be between 0 and 65535")
    manifest,snapshot=verify_bundle(root)
    class Bound(Handler): pass
    Bound.snapshot=snapshot; Bound.manifest=manifest; Bound.quiet=quiet; server=ThreadingHTTPServer((HOST,port),Bound); server.daemon_threads=True; return server
def fetch(port,path,host=None):
    last=None
    for _ in range(20):
        c=http.client.HTTPConnection(HOST,port,timeout=5)
        try:
            c.request("GET",path,headers={} if host is None else {"Host":host}); r=c.getresponse(); return r.status,{k.lower():v for k,v in r.getheaders()},r.read()
        except OSError as exc: last=exc; time.sleep(.02)
        finally: c.close()
    raise ConnectionError(last)
def smoke(root):
    manifest,_=verify_bundle(root); server=create_server(root,0,True); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    try:
        port=int(server.server_address[1]); targets=(("/",b"Principia &amp; Atlas"),("/principia/index.html",b"class=\"pa-suite\""),("/atlas/index.html",b"class=\"pa-suite\""),(f"/{MANIFEST}",CONTRACT.encode()))
        for path,marker in targets:
            status,headers,body=fetch(port,path)
            if status!=200 or marker not in body or any(headers.get(k)!=v for k,v in HEADERS.items()): raise ValueError(f"suite smoke failed: {path}")
        if fetch(port,"/",host="example.test")[0]!=421: raise ValueError("untrusted Host was not rejected")
        return {"contract":"principia-atlas-suite-smoke/0.1","bundle_id":manifest["bundle_id"],"targets":len(targets),"loopback_only":True}
    finally: server.shutdown(); server.server_close(); thread.join(timeout=5)
def required(args):
    if None in (args.principia,args.atlas,args.atlas_report): raise SystemExit("--principia, --atlas, and --atlas-report are required")
    return args.principia,args.atlas,args.atlas_report
def parse(argv:Sequence[str]|None=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("command",choices=("build","verify","check","serve")); p.add_argument("--principia",type=Path); p.add_argument("--atlas",type=Path); p.add_argument("--atlas-report",type=Path); p.add_argument("--output",type=Path); p.add_argument("--bundle",type=Path); p.add_argument("--port",type=int,default=DEFAULT_PORT); p.add_argument("--open",action="store_true"); p.add_argument("--quiet",action="store_true"); return p.parse_args(argv)
def main(argv:Sequence[str]|None=None):
    args=parse(argv)
    if args.command=="build":
        p,a,r=required(args)
        if args.output is None: raise SystemExit("--output is required")
        m=build_bundle(p,a,r,args.output); print(f"Built Principia & Atlas bundle {m['bundle_id']} -> {args.output}"); return 0
    if args.command=="verify":
        if args.bundle is None: raise SystemExit("--bundle is required")
        m,_=verify_bundle(args.bundle); print(f"Verified Principia & Atlas bundle {m['bundle_id']}"); return 0
    if args.command=="check":
        if args.bundle is not None: result=smoke(args.bundle); print(f"Principia & Atlas suite smoke passed: {result['bundle_id']}"); return 0
        p,a,r=required(args); check_determinism(p,a,r); print("Principia & Atlas deterministic build passed"); return 0
    if args.bundle is None: raise SystemExit("--bundle is required")
    manifest,_=verify_bundle(args.bundle); server=create_server(args.bundle,args.port,args.quiet); port=int(server.server_address[1]); pid=manifest["principia"]["build_id"]; home=f"http://{HOST}:{port}/"; print(f"Principia & Atlas: {home}"); print(f"Learn: {home}principia/index.html"); print(f"Research: {home}atlas/index.html"); print(f"Recorder: {home}principia/facilitator.html?build_id={pid}"); print(f"Pilot Lab: {home}principia/pilot-lab.html?build_id={pid}")
    if args.open: webbrowser.open(home)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0
if __name__=="__main__": raise SystemExit(main())
