"""Hand-made cattle illustrations (inline SVG, no internet or image files needed)."""
import base64

def _cattle(kind="cow", scale=1.0, x=0, y=0, flip=False):
    """Returns an SVG <g> group of a side-view animal, drawn inside a 300x200 box, facing right."""
    cfg = {
        "cow":     dict(body="#FFFFFF", patch="#3B3B3B", head="#FFFFFF", muzzle="#F2B8B0", horn="#E8DFC8", hoof="#3A3A3A", udder=True,  bighorn=False),
        "bull":    dict(body="#9C5B34", patch="#6E3A1D", head="#9C5B34", muzzle="#E9B7A0", horn="#EFE6CF", hoof="#2E2E2E", udder=False, bighorn=True),
        "calf":    dict(body="#C98B5A", patch="#FFFFFF", head="#C98B5A", muzzle="#F2B8B0", horn="#C98B5A", hoof="#3A3A3A", udder=False, bighorn=False),
        "buffalo": dict(body="#3E3E45", patch="#2B2B31", head="#2F2F36", muzzle="#8C8C94", horn="#CFC8B5", hoof="#1D1D20", udder=True,  bighorn=True),
    }[kind]
    c = cfg
    body_path = "M60 95 Q60 62 100 62 L175 62 Q215 62 215 95 Q215 140 175 142 L100 142 Q60 140 60 95 Z"
    parts = []
    parts.append(f'<ellipse cx="140" cy="186" rx="100" ry="9" fill="#000" opacity=".15"/>')
    # tail
    parts.append(f'<path d="M62 85 C40 90 38 120 46 145" stroke="{c["patch"] if kind!="calf" else "#8B5A36"}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    parts.append(f'<ellipse cx="46" cy="150" rx="7" ry="11" fill="{c["patch"] if kind!="calf" else "#8B5A36"}"/>')
    # back legs / front legs
    for lx in (72, 98, 172, 196):
        parts.append(f'<rect x="{lx}" y="125" width="17" height="55" rx="6" fill="{c["body"]}" stroke="#00000022"/>')
        parts.append(f'<rect x="{lx}" y="170" width="17" height="11" rx="3" fill="{c["hoof"]}"/>')
    # neck
    parts.append(f'<path d="M185 70 Q222 60 240 78 L240 135 Q215 140 190 130 Z" fill="{c["body"]}"/>')
    # body
    parts.append(f'<path d="{body_path}" fill="{c["body"]}" stroke="#00000022"/>')
    # patches (clipped to body)
    parts.append('<clipPath id="bc%s"><path d="%s"/></clipPath>' % (kind, body_path))
    if kind == "cow":
        parts.append('<g clip-path="url(#bccow)"><ellipse cx="95" cy="85" rx="28" ry="20" fill="%s"/><ellipse cx="160" cy="115" rx="30" ry="18" fill="%s"/><ellipse cx="190" cy="75" rx="18" ry="14" fill="%s"/></g>' % ((c["patch"],)*3))
    elif kind == "calf":
        parts.append('<g clip-path="url(#bccalf)"><ellipse cx="120" cy="120" rx="30" ry="16" fill="%s" opacity=".9"/></g>' % c["patch"])
    elif kind == "bull":
        parts.append('<g clip-path="url(#bcbull)"><ellipse cx="190" cy="85" rx="30" ry="22" fill="%s" opacity=".55"/></g>' % c["patch"])
    # hump for bull
    if kind == "bull":
        parts.append(f'<path d="M165 64 Q185 38 208 66 Z" fill="{c["body"]}"/>')
    # udder
    if c["udder"]:
        parts.append('<ellipse cx="128" cy="147" rx="15" ry="9" fill="#F4B6AE"/>')
    # head
    hy = 100 if kind != "buffalo" else 108
    parts.append(f'<ellipse cx="243" cy="{hy}" rx="30" ry="27" fill="{c["head"]}" stroke="#00000022"/>')
    if kind == "cow":
        parts.append(f'<ellipse cx="236" cy="90" rx="13" ry="14" fill="{c["patch"]}"/>')
    # ears
    parts.append(f'<ellipse cx="216" cy="{hy-18}" rx="16" ry="7" fill="{c["head"]}" stroke="#00000033" transform="rotate(25 216 {hy-18})"/>')
    parts.append(f'<ellipse cx="216" cy="{hy-18}" rx="9" ry="4" fill="{c["muzzle"] if kind!="buffalo" else "#55555D"}" transform="rotate(25 216 {hy-18})"/>')
    # horns
    if kind == "buffalo":
        parts.append(f'<path d="M232 {hy-22} C205 {hy-45} 190 {hy-20} 205 {hy-2}" stroke="{c["horn"]}" stroke-width="9" fill="none" stroke-linecap="round"/>')
    elif c["bighorn"]:
        parts.append(f'<path d="M232 {hy-24} C225 {hy-50} 245 {hy-52} 252 {hy-40}" stroke="{c["horn"]}" stroke-width="8" fill="none" stroke-linecap="round"/>')
    elif kind == "cow":
        parts.append(f'<path d="M234 {hy-24} C232 {hy-36} 242 {hy-38} 244 {hy-30}" stroke="{c["horn"]}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    # muzzle
    parts.append(f'<ellipse cx="266" cy="{hy+12}" rx="17" ry="14" fill="{c["muzzle"]}"/>')
    parts.append(f'<circle cx="262" cy="{hy+10}" r="2.6" fill="#00000066"/><circle cx="273" cy="{hy+10}" r="2.6" fill="#00000066"/>')
    parts.append(f'<path d="M258 {hy+20} Q266 {hy+25} 274 {hy+20}" stroke="#00000055" stroke-width="2" fill="none" stroke-linecap="round"/>')
    # eye
    parts.append(f'<circle cx="246" cy="{hy-8}" r="4.5" fill="#fff"/><circle cx="247" cy="{hy-8}" r="2.6" fill="#111"/>')
    flip_t = f"translate({x + 300*scale},{y}) scale({-scale},{scale})" if flip else f"translate({x},{y}) scale({scale})"
    return f'<g transform="{flip_t}">' + "".join(parts) + "</g>"


def _goat_parts():
    body, dark, horn, beard = "#C58A4B", "#6B3F1F", "#D9CDB0", "#EADFC8"
    p = ['<ellipse cx="150" cy="186" rx="88" ry="8" fill="#000" opacity=".15"/>']
    p.append(f'<path d="M70 94 L50 70 L78 84 Z" fill="{dark}"/>')
    for lx in (88, 108, 184, 204):
        p.append(f'<rect x="{lx}" y="118" width="11" height="55" rx="5" fill="{body}"/>')
        p.append(f'<rect x="{lx}" y="164" width="11" height="10" rx="3" fill="{dark}"/>')
    bp = "M68 100 Q68 70 105 70 L188 70 Q226 70 226 102 Q226 136 188 138 L105 138 Q68 136 68 100 Z"
    p.append(f'<path d="M198 80 Q226 52 246 60 L252 122 Q226 134 200 124 Z" fill="{body}"/>')
    p.append(f'<path d="{bp}" fill="{body}" stroke="#00000022"/>')
    p.append(f'<clipPath id="bcgoat"><path d="{bp}"/></clipPath>')
    p.append(f'<g clip-path="url(#bcgoat)"><ellipse cx="140" cy="76" rx="70" ry="9" fill="{dark}" opacity=".55"/><ellipse cx="100" cy="122" rx="26" ry="14" fill="#FFFFFF" opacity=".85"/><ellipse cx="190" cy="118" rx="22" ry="13" fill="#FFFFFF" opacity=".7"/></g>')
    p.append(f'<path d="M262 96 Q258 120 266 128 Q274 118 272 98 Z" fill="{beard}" stroke="#00000022"/>')
    p.append(f'<ellipse cx="252" cy="80" rx="22" ry="19" fill="{body}" stroke="#00000022"/>')
    p.append(f'<ellipse cx="270" cy="92" rx="13" ry="11" fill="#E8C9A6"/>')
    p.append(f'<path d="M246 64 C240 34 214 34 206 50" stroke="{horn}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    p.append(f'<ellipse cx="234" cy="78" rx="17" ry="6" fill="{dark}" transform="rotate(22 234 78)"/>')
    p.append('<circle cx="258" cy="76" r="4.2" fill="#fff"/><circle cx="259" cy="76" r="2.4" fill="#111"/>')
    p.append('<circle cx="277" cy="89" r="2" fill="#00000077"/><path d="M265 99 Q271 102 277 98" stroke="#00000055" stroke-width="2" fill="none" stroke-linecap="round"/>')
    return p


def _sheep_parts():
    wool, face, dark = "#F5F1E4", "#4A4038", "#3A3A3A"
    p = ['<ellipse cx="150" cy="186" rx="88" ry="8" fill="#000" opacity=".15"/>']
    for lx in (96, 116, 186, 206):
        p.append(f'<rect x="{lx}" y="130" width="10" height="46" rx="4" fill="{dark}"/>')
    p.append(f'<circle cx="64" cy="102" r="11" fill="{wool}" stroke="#00000018"/>')
    for cx, cy, r in [(88,104,27),(112,90,30),(148,86,32),(184,90,30),(206,104,27),(98,120,26),(140,122,29),(180,121,27),(124,106,30),(166,104,30)]:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{wool}" stroke="#00000018"/>')
    p.append(f'<circle cx="222" cy="98" r="22" fill="{wool}" stroke="#00000018"/>')
    p.append(f'<ellipse cx="244" cy="110" rx="21" ry="20" fill="{face}" stroke="#00000033"/>')
    p.append(f'<ellipse cx="226" cy="98" rx="14" ry="6" fill="{face}" transform="rotate(30 226 98)"/>')
    p.append('<ellipse cx="260" cy="118" rx="10" ry="9" fill="#6B5C50"/>')
    p.append('<circle cx="250" cy="103" r="4.2" fill="#fff"/><circle cx="251" cy="103" r="2.4" fill="#111"/>')
    p.append('<circle cx="264" cy="115" r="2" fill="#00000088"/><path d="M254 124 Q260 127 266 123" stroke="#00000066" stroke-width="2" fill="none" stroke-linecap="round"/>')
    p.append(f'<circle cx="236" cy="86" r="9" fill="{wool}" stroke="#00000018"/>')
    return p


def _animal(kind="cow", scale=1.0, x=0, y=0, flip=False):
    if kind not in ("goat", "sheep"):
        return _cattle(kind, scale, x, y, flip)
    parts = _goat_parts() if kind == "goat" else _sheep_parts()
    t = f"translate({x + 300*scale},{y}) scale({-scale},{scale})" if flip else f"translate({x},{y}) scale({scale})"
    return f'<g transform="{t}">' + "".join(parts) + "</g>"


def _wrap(w, h, inner, bg=None):
    bgrect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{bgrect}{inner}</svg>'


def animal_svg(kind):
    kind = {"Cow": "cow", "Buffalo": "buffalo", "Bull": "bull", "Calf": "calf", "Goat": "goat", "Sheep": "sheep"}.get(kind, "cow")
    sc = 0.7 if kind == "calf" else 1.0
    yy = 40 if kind == "calf" else 0
    return _wrap(300, 200, _animal(kind, scale=sc, y=yy))


def scene_svg():
    """Wide farm landscape with a cow, a buffalo, a sheep and a goat."""
    inner = """
    <defs>
      <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE3F5"/><stop offset="1" stop-color="#F4F9E9"/></linearGradient>
      <linearGradient id="h1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7DBE6B"/><stop offset="1" stop-color="#4E9B4A"/></linearGradient>
      <linearGradient id="h2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5BAA55"/><stop offset="1" stop-color="#2F7F3E"/></linearGradient>
    </defs>
    <rect width="900" height="360" fill="url(#sky)"/>
    <circle cx="780" cy="70" r="38" fill="#FFD966"/><circle cx="780" cy="70" r="52" fill="#FFD966" opacity=".25"/>
    <g fill="#fff" opacity=".9"><ellipse cx="150" cy="70" rx="55" ry="16"/><ellipse cx="185" cy="58" rx="36" ry="14"/><ellipse cx="520" cy="95" rx="60" ry="15"/><ellipse cx="555" cy="84" rx="34" ry="12"/></g>
    <path d="M0 230 Q150 150 320 215 T640 200 T900 215 L900 360 L0 360 Z" fill="url(#h1)"/>
    <path d="M0 290 Q200 235 420 285 T900 270 L900 360 L0 360 Z" fill="url(#h2)"/>
    <g stroke="#8B5E3C" stroke-width="5" stroke-linecap="round" opacity=".85"><path d="M600 245 H890"/><path d="M600 262 H890"/><path d="M620 235 V275"/><path d="M690 235 V275"/><path d="M760 235 V275"/><path d="M830 235 V275"/></g>
    <g><rect x="40" y="170" width="95" height="70" fill="#C0392B"/><path d="M30 172 L87 128 L145 172 Z" fill="#8E2A20"/><rect x="68" y="200" width="38" height="40" fill="#F7E7C6"/></g>
    """
    inner += _animal("buffalo", scale=0.9, x=300, y=135)
    inner += _animal("cow", scale=0.95, x=60, y=150)
    inner += _animal("sheep", scale=0.62, x=555, y=200)
    inner += _animal("goat", scale=0.62, x=705, y=198)
    return _wrap(900, 360, inner)


def to_data_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
