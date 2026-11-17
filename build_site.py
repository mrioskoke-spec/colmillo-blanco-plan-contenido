#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — genera index.html (sitio web real, GitHub Pages) a partir
del HTML maestro de la quincena activa, usando archivos de imagen/video
reales (rutas relativas) en vez de base64, y agregando CSS responsive
para que se vea bien en pantallas angostas (celular).

Uso: python3 build_site.py "<ruta al html maestro de la quincena>"
"""

import sys, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
IMG  = "assets/img"
VID  = "assets/video"

if len(sys.argv) < 2:
    print("Uso: python3 build_site.py <ruta_html_maestro>")
    sys.exit(1)

SRC = sys.argv[1]
DST = os.path.join(BASE, "index.html")

with open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

# ── 1. CSS extra: piezas (visual real) + responsive ────────────────────

EXTRA_CSS = """
    /* ── IMAGEN INDIVIDUAL 4:5 (posts) ───────── */
    .post-img-wrap {
      width: 100%;
      aspect-ratio: 4 / 5;
      overflow: hidden;
      border-radius: 6px;
      display: block;
    }
    .post-img-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center top;
      display: block;
    }

    /* ── REEL CON VIDEO REAL 9:16 ────────────── */
    .reel-video-wrap {
      width: 100%;
      aspect-ratio: 9 / 16;
      overflow: hidden;
      border-radius: 6px;
      display: block;
      background: #000;
    }
    .reel-video-wrap video {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    /* ── CARRUSEL HORIZONTAL ─────────────────── */
    .car-wrap { width: 100%; }
    .car-track {
      display: flex;
      flex-direction: row;
      overflow-x: auto;
      overflow-y: hidden;
      scroll-snap-type: x mandatory;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      gap: 0;
      border-radius: 6px;
      cursor: grab;
    }
    .car-track:active { cursor: grabbing; }
    .car-track::-webkit-scrollbar { display: none; }
    .car-slide {
      flex: 0 0 100%;
      scroll-snap-align: start;
      aspect-ratio: 4 / 5;
      overflow: hidden;
    }
    .car-slide img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center top;
      display: block;
      pointer-events: none;
    }
    .car-indicators {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 6px;
      padding: 10px 0 2px;
    }
    .car-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--gray-line);
      display: inline-block;
      transition: background 0.2s;
    }
    .car-dot:first-child {
      background: var(--gold);
      width: 18px;
      border-radius: 3px;
    }

    /* ══════════════════════════════════════════════════════
       RESPONSIVE — pantallas angostas (celular, ~700px y menos)
       ══════════════════════════════════════════════════════ */
    @media (max-width: 760px) {
      .header-inner { grid-template-columns: 1fr; min-height: 0; }
      .header-nameplate { border-right: none; border-bottom: 3px solid var(--gold); }
      .header-period { font-size: 26px; }
      .header-stats { flex-wrap: wrap; gap: 20px; }

      .estr-hero { padding: 32px 22px 28px; }
      .estr-quote { font-size: 20px; max-width: 100%; }
      .estr-desc { max-width: 100%; }
      .estr-objs { grid-template-columns: 1fr; }
      .eobj { border-right: none; border-bottom: 1px solid rgba(255,255,255,0.055); }
      .eobj:last-child { border-bottom: none; }

      /* Calendario: la fila se vuelve una tarjeta apilada */
      .cal-head { display: none; }
      .cal-row {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
        padding: 14px 18px;
      }
      .cal-row > div { width: 100%; }
      .cal-tema { font-size: 14px; }
      .cal-horario { text-align: left; }

      /* Pieza: header y body se apilan */
      .pieza-head { grid-template-columns: 56px 4px 1fr; }
      .ph-time { display: none; } /* el horario ya está en el calendario de arriba */
      .pieza-body { grid-template-columns: 1fr !important; }

      .resumen-nums { flex-wrap: wrap; }
      .pilares { flex-wrap: wrap; }
    }
"""

html = html.replace("  </style>", EXTRA_CSS + "\n  </style>", 1)

# ── 2. Reemplaza el cuerpo de cada pieza con Visual real + Caption ─────

def wrap_img(path, alt=""):
    return f'<div class="post-img-wrap"><img src="{path}" alt="{alt}" loading="lazy"></div>'

def wrap_reel(video_path, poster_path, alt=""):
    return (
        f'<div class="reel-video-wrap">'
        f'<video src="{video_path}" poster="{poster_path}" controls playsinline '
        f'preload="metadata" style="width:100%;height:100%;object-fit:cover;display:block;"></video>'
        f'</div>'
    )

def wrap_carousel(paths):
    slides = "\n".join(
        f'    <div class="car-slide"><img src="{p}" alt="Slide {i+1}" loading="lazy"></div>'
        for i, p in enumerate(paths)
    )
    dots = "".join('<span class="car-dot"></span>' for _ in paths)
    return (
        f'<div class="car-wrap">'
        f'<div class="car-track">\n{slides}\n  </div>'
        f'<div class="car-indicators">{dots}</div>'
        f'</div>'
    )

def build_body(left_html, caption_text, left_label="Visual"):
    return f"""<div class="pieza-body">
        <div class="pcol">
          <div class="pcol-label">{left_label}</div>
          {left_html}
        </div>
        <div class="pcol">
          <div class="pcol-label">Caption</div>
          <div class="copy-block cc">{caption_text}</div>
        </div>
      </div>"""

def find_div_end(s, start):
    pos = s.index('>', start) + 1
    depth = 1
    while depth > 0 and pos < len(s):
        nxt_o = s.find('<div', pos)
        nxt_c = s.find('</div>', pos)
        if nxt_c == -1:
            break
        if nxt_o != -1 and nxt_o < nxt_c:
            depth += 1; pos = nxt_o + 4
        else:
            depth -= 1; pos = nxt_c + 6
    return pos

def extract_caption(body_html):
    m = re.search(r'<div class="copy-block cc">(.*?)</div>', body_html, re.DOTALL)
    return m.group(1).strip() if m else ""

def replace_body(s, marker, make_body):
    anchor = s.find(marker)
    if anchor == -1:
        print(f"  ⚠  No encontré: {marker}"); return s
    pb_start = s.find('<div class="pieza-body">', anchor)
    if pb_start == -1:
        print(f"  ⚠  No hay pieza-body: {marker}"); return s
    pb_end  = find_div_end(s, pb_start)
    caption = extract_caption(s[pb_start:pb_end])
    return s[:pb_start] + make_body(caption) + s[pb_end:]

PIECES = [
    ("17/11", "post",     lambda: wrap_img(f"{IMG}/24.png", "17 de noviembre")),
    ("18/11", "reel",     lambda: wrap_reel(f"{VID}/puntos_venta.mp4", f"{IMG}/poster_puntos_venta.jpg", "18 de noviembre")),
    ("20/11", "carrusel", lambda: wrap_carousel([f"{IMG}/25.png", f"{IMG}/26.png", f"{IMG}/27.png"])),
    ("22/11", "post",     lambda: wrap_img(f"{IMG}/28.png", "22 de noviembre")),
    ("23/11", "post",     lambda: wrap_img(f"{IMG}/29.png", "23 de noviembre")),
    ("25/11", "reel",     lambda: wrap_reel(f"{VID}/kike_plato.mp4", f"{IMG}/poster_kike_plato.jpg", "25 de noviembre")),
    ("27/11", "carrusel", lambda: wrap_carousel([f"{IMG}/30.png", f"{IMG}/31.png", f"{IMG}/32.png"])),
    ("29/11", "post",     lambda: wrap_img(f"{IMG}/33.png", "29 de noviembre")),
]

for date, kind, visual_fn in PIECES:
    label = "Reel" if kind == "reel" else ("Carrusel — 3 slides" if kind == "carrusel" else "Visual")
    print(f"{date} — {kind}")
    html = replace_body(html, f"<!-- {date} -->",
        lambda cap, v=visual_fn, l=label: build_body(v(), cap, left_label=l))

with open(DST, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n✓ index.html generado ({os.path.getsize(DST)/1024:.0f} KB)")
