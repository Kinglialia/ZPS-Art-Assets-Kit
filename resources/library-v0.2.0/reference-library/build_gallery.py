from pathlib import Path
import json,html,math
r=Path(__file__).resolve().parent;d=json.loads((r/'library.json').read_text());esc=html.escape
parts=['<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Art Director Reference Library</title><style>body{font-family:system-ui;background:#141820;color:#eee;margin:16px}a{color:#9de1ff}nav{margin:12px 0;line-height:2}main{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}article{background:#242b36;padding:10px;border-radius:8px}img{width:100%;height:180px;object-fit:contain;background:#0b0d11}h2{font-size:14px;margin:5px 0}p{font-size:12px;margin:6px 0}details{font-size:12px}li{margin:6px 0}@media(max-width:800px){main{grid-template-columns:repeat(2,1fr)}}@media(max-width:480px){main{grid-template-columns:1fr}}</style>',f'<h1>Art Director · {len(d["entries"])} styles</h1><p>Reference v{esc(d["release"])} · Mở card để đọc nguồn, giới hạn và đề xuất. Ảnh không phải asset có license sản xuất.</p><nav>']
for p in range(math.ceil(len(d['entries'])/8)):parts.append(f'<a href="?page={p}">Nhóm {p+1}</a> &nbsp; ')
parts.append('</nav><main>')
for i,e in enumerate(d['entries']):
 if not e.get('media'):continue
 m=e['media'][0]
 parts.append(f'<article data-page="{i//8}"><h2>{i+1}. {esc(e["name"])}</h2><a href="{esc(m["file"])}"><img alt="{esc(m["game"])}" src="{esc(m["file"])}"></a><p>{esc(m["game"])} — {esc(m["credit"])}</p><p>{esc(e["source_summary"])}</p><p><a href="{esc(e["card"])}">Đọc hồ sơ</a></p><details><summary>{len(e["media"])} ảnh</summary><ul>')
 for m in e['media']:parts.append(f'<li><a href="{esc(m["file"])}">{esc(m["game"])} · {m["width"]}×{m["height"]}</a></li>')
 parts.append('</ul></details></article>')
parts.append('</main><script>const p=new URLSearchParams(location.search).get("page")||"0";document.querySelectorAll("article").forEach(e=>{if(e.dataset.page!==p)e.remove()})</script></html>')
(r/'gallery.html').write_text(''.join(parts))
