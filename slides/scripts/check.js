// Measures one rendered slide against the design system's rules. Runs in the page.
// window.__RULES is set by the runner from tokens.json. The result goes into a hidden pre element with id __check.
(function () {
  const R = window.__RULES;
  const W = R.width, H = R.height;
  const root = document.querySelector('section') || [...document.body.children].find(e => !['STYLE', 'LINK', 'SCRIPT', 'PRE'].includes(e.tagName));
  const S = root.getBoundingClientRect();
  const box = r => ({ x: r.left - S.left, y: r.top - S.top, r: r.right - S.left, b: r.bottom - S.top, w: r.width, h: r.height });
  const rect = e => box(e.getBoundingClientRect());
  const cs = e => getComputedStyle(e);
  const ctx = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
  const rgb = c => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1); const d = ctx.getImageData(0, 0, 1, 1).data; return d[3] === 0 ? 'rgba(0,0,0,0)' : `rgb(${d[0]},${d[1]},${d[2]})`; };
  const txt = e => (e.innerText ?? e.textContent ?? '').trim();  // SVG elements have no innerText
  const label = e => (e.innerText || e.textContent || e.tagName).trim().replace(/\s+/g, ' ').slice(0, 50) || e.tagName;
  const visible = e => { const c = cs(e); const b = e.getBoundingClientRect(); return c.display !== 'none' && c.visibility !== 'hidden' && parseFloat(c.opacity) > 0 && b.width > 0 && b.height > 0; };
  const all = [...root.querySelectorAll('*')].filter(e => !e.closest('aside')).filter(e => !e.closest('svg') || e.tagName.toLowerCase() === 'svg').filter(visible);
  const ownText = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const textEls = all.filter(ownText);
  // Line boxes of an element's own text (inline descendants included).
  const lines = e => {
    const rg = document.createRange(); rg.selectNodeContents(e);
    const rs = [...rg.getClientRects()].filter(q => q.width > 0.5).map(box);
    const byTop = [];
    rs.forEach(q => { const l = byTop.find(t => Math.abs(t.y - q.y) < q.h / 2); if (l) { l.x = Math.min(l.x, q.x); l.r = Math.max(l.r, q.r); l.b = Math.max(l.b, q.b); } else byTop.push({ ...q }); });
    byTop.forEach(l => l.w = l.r - l.x);
    return byTop;
  };
  const inkOf = e => { const ls = lines(e); if (!ls.length) return null; return { x: Math.min(...ls.map(l => l.x)), r: Math.max(...ls.map(l => l.r)), y: Math.min(...ls.map(l => l.y)), b: Math.max(...ls.map(l => l.b)) }; };
  const errors = [];
  const add = (code, el, detail) => errors.push({ code, element: el ? label(el) : '', detail });

  const bg = rgb(cs(root).backgroundColor);
  const contentSlide = (bg === rgb(R.surface) || bg === 'rgba(0,0,0,0)') && cs(root).backgroundImage === 'none';
  // The footer rule: a full-width line of navy near the bottom.
  const footerRule = all.find(e => { const b = rect(e); return b.h <= 4 && b.w > W * 0.8 && Math.abs((H - b.y) - R.footerRule) <= 3; });
  const footerTop = footerRule ? rect(footerRule).y : H - R.marginBottom;
  const title = root.querySelector('h1, h2');

  // 1. OVERFLOW: content clipped by its box, or beyond the canvas.
  all.forEach(e => {
    const c = cs(e);
    const clips = c.overflow !== 'visible' || c.overflowX !== 'visible' || c.overflowY !== 'visible';
    if (e !== root && clips && (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1))
      add('OVERFLOW', e, `content ${e.scrollWidth}×${e.scrollHeight}px is cut off by its ${e.clientWidth}×${e.clientHeight}px box`);
  });
  textEls.forEach(e => {
    const ink = inkOf(e); if (!ink) return;
    if (ink.x < -1 || ink.y < -1 || ink.r > W + 1 || ink.b > H + 1) add('OVERFLOW', e, `text runs off the ${W}×${H} slide`);
    // text that spills out of a fixed-height parent box with a fill or border
    const p = e.parentElement; if (!p || p === root) return;
    const pc = cs(p); const pb = rect(p);
    const framed = rgb(pc.backgroundColor) !== 'rgba(0,0,0,0)' || parseFloat(pc.borderTopWidth) > 0;
    if (framed && pc.overflow === 'visible' && (ink.b > pb.b + 1 || ink.r > pb.r + 1)) add('OVERFLOW', e, `text spills ${Math.round(Math.max(ink.b - pb.b, ink.r - pb.r))}px out of its box`);
  });

  if (contentSlide) {
    // 2. MARGIN: body content outside the side margins, above the top margin (except the sticker), or into the footer.
    const left = R.marginSide, right = W - R.marginSide;
    const flagged = new Set();
    all.forEach(e => {
      if (e === footerRule) return;
      for (let p = e.parentElement; p && p !== root; p = p.parentElement) if (flagged.has(p)) { flagged.add(e); return; }
      const before = errors.length;
      // an unpainted text box counts by its visible text, not its empty width
      const ec = cs(e);
      const painted = rgb(ec.backgroundColor) !== 'rgba(0,0,0,0)' || ['Top', 'Right', 'Bottom', 'Left'].some(s => parseFloat(ec['border' + s + 'Width']) > 0);
      const kids = [...e.children].every(k => ['B', 'BR', 'SPAN', 'I', 'U', 'A'].includes(k.tagName));
      const ink = !painted && kids && txt(e) ? inkOf(e) : null;
      const b = ink ? { ...ink, w: ink.r - ink.x, h: ink.b - ink.y } : rect(e);
      const sticker = b.b <= R.marginTop && b.x >= W / 2;
      if (sticker) { if (b.r > right + 1) add('MARGIN', e, `sticker ends at x=${Math.round(b.r)}, past the right margin ${right}`); return; }
      if (b.x < left - 1 || b.r > right + 1) add('MARGIN', e, `spans x=${Math.round(b.x)}–${Math.round(b.r)}, outside the margins ${left}–${right}`);
      else if (b.y < R.marginTop - 1) add('MARGIN', e, `starts at y=${Math.round(b.y)}, above the top margin ${R.marginTop}`);
      else if (b.y < footerTop - 1 && b.b > footerTop + 1) add('MARGIN', e, `runs ${Math.round(b.b - footerTop)}px into the footer below the rule at y=${Math.round(footerTop)}`);
      if (errors.length > before) flagged.add(e);
    });
    if (!footerRule) add('FOOTER', null, `no footer rule ${R.footerRule}px from the bottom`);
  }

  // 3. TITLE: at most two lines, no line wider than the share of the content width.
  if (title) {
    const ls = lines(title);
    const maxW = (W - 2 * R.marginSide) * R.titleLineMax;
    if (contentSlide && ls.length > R.titleMaxLines) add('TITLE_LINES', title, `${ls.length} lines, at most ${R.titleMaxLines}`);
    ls.forEach((l, i) => { if (l.w > maxW + 0.5) add('TITLE_WIDTH', title, `line ${i + 1} is ${Math.round(l.w)}px, more than ${Math.round(R.titleLineMax * 100)}% of ${W - 2 * R.marginSide}px (${Math.round(maxW)}px)`); });
  } else if (contentSlide) add('TITLE_MISSING', null, 'no h1 or h2 action title');

  // 4. ANNOTATION_RULE: a note's rule must be exactly as wide as its longest text line.
  const muted = rgb(R.muted);
  all.forEach(e => {
    const c = cs(e);
    const onlyBottom = parseFloat(c.borderBottomWidth) > 0 && !(parseFloat(c.borderTopWidth) > 0) && !(parseFloat(c.borderLeftWidth) > 0) && !(parseFloat(c.borderRightWidth) > 0);
    if (onlyBottom && rgb(c.borderBottomColor) === muted && txt(e)) {
      const ink = inkOf(e) || rect(e); const b = rect(e);
      const diff = b.w - (ink.r - ink.x);
      if (Math.abs(diff) > R.annotationTolerance) add('ANNOTATION_RULE', e, `rule ${Math.round(b.w)}px, text ${Math.round(ink.r - ink.x)}px`);
    }
  });
  // a separate thin muted line right under a text element
  all.filter(e => { const b = rect(e); return b.h <= 3 && b.w > 20 && !txt(e) && rgb(cs(e).backgroundColor) === muted; }).forEach(line => {
    const lb = rect(line);
    const text = textEls.map(t => ({ t, ink: inkOf(t) })).filter(o => o.ink && lb.y - o.ink.b >= -2 && lb.y - o.ink.b <= 10 && o.ink.x < lb.r && o.ink.r > lb.x).sort((a, b) => b.ink.b - a.ink.b)[0];
    if (text) { const tw = text.ink.r - text.ink.x; if (Math.abs(lb.w - tw) > R.annotationTolerance) add('ANNOTATION_RULE', text.t, `rule ${Math.round(lb.w)}px, text ${Math.round(tw)}px`); }
  });

  // 5. FONT_MIN: no text below the smallest size.
  textEls.forEach(e => { const fs = parseFloat(cs(e).fontSize); if (fs < R.minFont - 0.1) add('FONT_MIN', e, `${fs}px, at least ${R.minFont}px`); });

  // 6. MINUS: negatives use a real minus sign.
  textEls.forEach(e => {
    const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('');
    const m = own.match(/(^|[\s(:→])[-–]\d/);
    if (m) add('MINUS', e, `"${m[0].trim()}" uses a hyphen or dash, not U+2212`);
  });

  // 7. TEXT_OVERLAP: text lines of different elements must not cross.
  const inks = textEls.map(e => ({ e, ls: lines(e) }));
  for (let i = 0; i < inks.length; i++) for (let j = i + 1; j < inks.length; j++) {
    const a = inks[i], b = inks[j];
    if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
    const hit = a.ls.some(p => b.ls.some(q => Math.min(p.r, q.r) - Math.max(p.x, q.x) > 2 && Math.min(p.b, q.b) - Math.max(p.y, q.y) > 2));
    if (hit) add('TEXT_OVERLAP', a.e, `overlaps "${label(b.e)}"`);
  }

  // One error per code and element: the same defect is not counted twice.
  const seen = new Set();
  const out = errors.filter(x => { const k = x.code + '|' + x.element; if (seen.has(k)) return false; seen.add(k); return true; });
  const pre = document.createElement('pre'); pre.id = '__check'; pre.style.display = 'none';
  pre.textContent = JSON.stringify({ fontsLoaded: window.__FONTS, kind: contentSlide ? 'content' : 'full-bleed', title: title ? title.innerText.trim() : null, errors: out });
  document.body.appendChild(pre);
})();
