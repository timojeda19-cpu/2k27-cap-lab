"use strict";
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const TIERS = ["—", "Bronze", "Silver", "Gold", "HOF", "Legend"];
const TAB = ["", "B", "S", "G", "HOF", "LEG"];
const DISC = [["F","Finishing"],["S","Shooting"],["P","Playmaking"],["D","Defense"],["R","Rebounding"],["Y","Physicals"]];
const CAT2D = {Finishing:"F",Shooting:"S",Playmaking:"P",Defense:"D",Rebounding:"R",Physicals:"Y"};
const ATTR = D.attrs.map(a => a[0]);
const ANAME = Object.fromEntries(D.attrs.map(a => [a[0], a[1]]));
const BADGE = Object.fromEntries(D.badges.map(b => [b.n, b]));
const BUILD = Object.fromEntries(D.builds.map(b => [b.id, b]));
const MAXCB = 28, PER = 5;
const hs = i => `${Math.floor(i / 12)}'${i % 12}"`;
const clone = o => JSON.parse(JSON.stringify(o));
const toast = m => { const t = $("#toast"); t.textContent = m; t.classList.add("on"); clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove("on"), 1600); };

/* ---------------- state ---------------- */
let S;
function fresh(id, mode) {
  const b = BUILD[id] || D.builds[0];
  mode = mode || "rec";
  const lo = b.lo[mode] || b.lo.rec || {eq:{}, fuse:[], tk:["","","","",""]};
  return {tab: S ? S.tab : "sim", b: b.id, pos: b.pos, h: b.h, wt: b.wt, ws: b.ws, a: clone(b.a), cap: clone(b.cap), lad: clone(b.lad), cb: {},
    earned: S ? S.earned : {rep: 3, season: 1, crew: 0, life: 0, spec: 0}, mode, eq: clone(lo.eq), fuse: clone(lo.fuse), tk: clone(lo.tk || ["","","","",""]),
    pools: clone(b.pools), p1: Math.max(4, (lo.fuse || []).filter(f => f[2] === 1).length), p2: (lo.fuse || []).filter(f => f[2] === 2).length,
    mx: S ? S.mx : {m: "badges", cat: "All", st: "all", q: ""}, bf: S ? S.bf : "all"};
}
const enc = o => btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const dec = s => JSON.parse(decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/")))));
function stateLink() { const u = new URL(location.href); u.hash = `tab=${S.tab}&s=${enc(packS())}`; return u.toString(); }
function packS() { const o = clone(S); delete o.mx; delete o.bf; return o; }
let saveT;
function save() { clearTimeout(saveT); saveT = setTimeout(() => { try { history.replaceState(null, "", `#tab=${S.tab}&s=${enc(packS())}`); localStorage.setItem("2k27lab", JSON.stringify(S)); } catch (e) {} }, 120); }
function load() {
  const h = new URLSearchParams(location.hash.slice(1)); const q = new URLSearchParams(location.search);
  let st = null;
  const s = h.get("s") || q.get("s");
  if (s) { try { st = dec(s); } catch (e) { st = null; } }
  if (!st) { try { st = JSON.parse(localStorage.getItem("2k27lab") || "null"); } catch (e) { st = null; } }
  S = null; S = fresh(h.get("b") || q.get("b") || (st && st.b) || "hash63");
  if (st && BUILD[st.b] && !(h.get("b") || q.get("b"))) Object.assign(S, st);
  if (!S.mx) S.mx = {m: "badges", cat: "All", st: "all", q: ""};
  S.tab = h.get("tab") || q.get("tab") || S.tab || "sim";
  if (S.tab === "simulator") S.tab = "sim";
  if (h.get("mode") || q.get("mode")) { const m = h.get("mode") || q.get("mode"); if (m === "3s" || m === "rec") S.mode = m; }
}

/* ---------------- engine ---------------- */
function estLadder(v) { const g = []; let x = v, last = 99;
  for (let i = 0; i < PER && x < 99; i++) { let k = x < 40 ? 14 : x < 50 ? 12 : x < 60 ? 10 : x < 70 ? 7 : x < 75 ? 5 : x < 80 ? 4 : x < 85 ? 3 : x < 90 ? 2 : 1; k = Math.min(k, last, 99 - x); g.push(k); last = k; x += k; }
  return g; }
function ladder(k) { const L = S.lad[k]; if (L && L.length) return {g: L.slice(0, PER), est: false}; return {g: estLadder(S.a[k]), est: true}; }
function locked(k) { return S.cap[k] != null && S.a[k] < S.cap[k]; }
function effAttrs(cb) { const o = {}; for (const k of ATTR) { const n = (cb || {})[k] || 0; const L = ladder(k).g; let v = S.a[k]; for (let i = 0; i < n && i < L.length; i++) v += L[i]; o[k] = Math.min(99, v); } return o; }
function tierOf(b, A, h) { if (h < b.mn || h > b.mx) return -1; let t = b.op === "AND" ? 9 : 0;
  for (const [k, th] of b.r) { const v = A[k]; let n = 0; for (const x of th) if (v >= x) n++; t = b.op === "AND" ? Math.min(t, n) : Math.max(t, n); } return t; }
function animOK(a, A, h) { if (h < a.mn || h > a.mx) return {ok: false, hf: true, gap: 0};
  const shot = Math.max(A.MID, A["3PT"]); let gaps = [];
  for (const [k, v] of Object.entries(a.req)) { const have = k === "SHOT" ? shot : A[k]; gaps.push(Math.max(0, v - have)); }
  if (!gaps.length) return {ok: true, gap: 0};
  const gap = a.mode === "OR" ? Math.min(...gaps) : gaps.reduce((s, x) => s + x, 0);
  return {ok: gap === 0, gap, hf: false}; }
function tkOK(t, A) { if (t.op === "NA") return null; if (!t.r.length) return true; const f = ([k, v]) => A[k] >= v; return t.op === "OR" ? t.r.some(f) : t.r.every(f); }
const cbUsed = () => Object.values(S.cb).reduce((s, x) => s + x, 0);
const cbAvail = () => Math.min(MAXCB, D.cbSources.reduce((s, c) => s + Math.min(c.max, S.earned[c.id] || 0), 0));
function costPt(v) { return v <= 69 ? 1 : v <= 84 ? 2 : v <= 94 ? 3 : 4; }
function diffs(A0, A1, h) {
  const out = {b: [], a: [], t: []};
  for (const b of D.badges) { const t0 = tierOf(b, A0, h), t1 = tierOf(b, A1, h); if (t1 > t0 && t1 > 0) out.b.push([b, Math.max(0, t0), t1]); }
  for (const a of D.anims) { if (animOK(a, A1, h).ok && !animOK(a, A0, h).ok) out.a.push(a); }
  for (const t of D.takeovers) { if (tkOK(t, A1) === true && tkOK(t, A0) !== true) out.t.push(t); }
  return out;
}
const tb = t => t < 0 ? `<span class="tb t0">height</span>` : `<span class="tb t${t}">${t ? TIERS[t] : "—"}</span>`;

/* ---------------- SIMULATOR ---------------- */
function renderPresets() {
  $("#presets").innerHTML = D.builds.map(b => `<button class="preset ${S.b === b.id ? "on" : ""}" data-b="${b.id}" type="button"><b>${esc(b.name.split(" (")[0].split(" · ")[0])}</b><span>${b.pos} · ${hs(b.h)} · ${b.kind === "mine" ? "your build" : b.kind === "pro" ? "creator build" : "meta template"}</span></button>`).join("");
}
function renderBody() {
  $("#p-pos").value = S.pos; $("#p-h").value = S.h; $("#p-wt").value = S.wt;
  const ws = $("#p-ws"); ws.innerHTML = ""; for (let i = S.h - 6; i <= S.h + 8; i++) ws.insertAdjacentHTML("beforeend", `<option value="${i}">${hs(i)} (${i - S.h >= 0 ? "+" : ""}${i - S.h})</option>`);
  if (S.ws < S.h - 6 || S.ws > S.h + 8) S.ws = S.h; ws.value = S.ws;
  const b = BUILD[S.b];
  $("#body-note").innerHTML = `${esc(b.note)}${b.bodyEst ? ` <b class="t3">Weight / wingspan not on file — set yours.</b>` : ""} <span class="dim">Source: ${esc(b.src)}</span><br><span class="dim">Height/weight/wingspan set the caps in the real Builder; this sim uses the ratings, caps and gain ladders you enter.</span>`;
  $("#k-sub").textContent = `${b.name.split(" (")[0]} · ${S.pos} ${hs(S.h)}`;
}
function renderCB() {
  const used = cbUsed(), av = cbAvail();
  $("#cb-used").textContent = used; $("#cb-av").textContent = av; $("#cb-n").textContent = `${MAXCB - used} of 28 unused`;
  const m = $("#cb-meter"); m.classList.toggle("over", used > av); m.firstElementChild.style.width = Math.min(100, used / Math.max(1, av) * 100) + "%";
  $("#cb-src").innerHTML = D.cbSources.map(c => `<div class="cbsrc"><b>${esc(c.n)}</b><div class="st"><button data-src="${c.id}" data-d="-1" type="button">−</button><b>${S.earned[c.id] || 0}/${c.max}</b><button data-src="${c.id}" data-d="1" type="button">+</button></div><small>${esc(c.note)}</small></div>`).join("");
  $("#cb-warn").innerHTML = used > av ? `<div class="warn">You've applied ${used} breakers but only marked ${av} as earned. Raise a source above or remove some.</div>` : "";
}
function renderAttrs() {
  const A1 = effAttrs(S.cb); let html = "";
  for (const [dk, dn] of DISC) {
    const ks = D.attrs.filter(a => a[2] === dk).map(a => a[0]); if (!ks.length) continue;
    html += `<div class="small" style="margin:10px 0 2px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--tx3)">${dn}</div>`;
    for (const k of ks) {
      const v = S.a[k], n = S.cb[k] || 0, L = ladder(k), lk = locked(k), e = A1[k];
      const sweet = v >= 85 && v <= 94;
      const canAdd = !lk && n < L.g.length && n < PER && cbUsed() < MAXCB;
      let pips = ""; for (let i = 0; i < PER; i++) { if (i < L.g.length) pips += `<span class="pip ${i < n ? "on" : ""} ${L.est ? "est" : ""}">+${L.g[i]}</span>`; else pips += `<span class="pip cap" title="Hard cap">🔒</span>`; }
      let nxt = "";
      if (canAdd) { const cb2 = Object.assign({}, S.cb, {[k]: n + 1}); const d = diffs(A1, effAttrs(cb2), S.h);
        const parts = [...d.b.map(([b, , t]) => `${b.n} ${TAB[t]}`), ...d.t.map(t => `⚡${t.n}`)]; const an = d.a.length;
        if (parts.length || an) nxt = `<div class="nxt">Next +${L.g[n]} → <b>${esc(parts.slice(0, 4).join(", "))}${parts.length > 4 ? ` +${parts.length - 4}` : ""}</b>${an ? ` ${parts.length ? "· " : ""}<b>${an} animation${an > 1 ? "s" : ""}</b>` : ""}</div>`; }
      html += `<div class="attr2 ${sweet ? "sweet" : ""}"><div class="nm">${esc(ANAME[k])} ${lk ? `<span class="lk" data-max="${k}" title="Max with MyPoints first (cap ${S.cap[k]}) — tap to max">🔒 ${S.cap[k]}</span>` : ""}</div>
        <input type="number" min="25" max="99" value="${v}" data-a="${k}" aria-label="${esc(ANAME[k])}">
        <div class="ctl"><span class="eff ${e >= 99 ? "v99" : e >= 90 ? "v90" : e >= 85 ? "v85" : e >= 80 ? "v80" : "vlo"}">${e}${n ? `<sup>+${e - v}</sup>` : ""}</span><button data-cb="${k}" data-d="-1" ${n ? "" : "disabled"} type="button" aria-label="remove breaker">−</button><button class="plus" data-cb="${k}" data-d="1" ${canAdd ? "" : "disabled"} type="button" aria-label="add breaker">+</button></div>
        <div class="lad">${pips}</div>${nxt}</div>`;
    }
  }
  $("#attrs").innerHTML = html;
}
function renderUnlocks() {
  const A0 = effAttrs({}), A1 = effAttrs(S.cb), d = diffs(A0, A1, S.h);
  $("#un-n").textContent = `${d.b.length} badge tiers · ${d.a.length} animations · ${d.t.length} takeovers`;
  let h = "";
  if (!cbUsed()) h = `<div class="note">Tap <b>+</b> on any attribute. Each row also previews what the <i>next</i> breaker would unlock.</div>`;
  h += d.t.map(t => `<div class="diff tk"><b>⚡ ${esc(t.n)}</b><span class="tag y">Takeover · ${esc(t.cat)}</span><span class="small dim">${esc(t.note)}</span></div>`).join("");
  h += d.b.map(([b, t0, t1]) => { const c0 = t0 ? D.cost[b.c][t0 - 1] : 0, c1 = D.cost[b.c][t1 - 1];
    return `<div class="diff"><b>${esc(b.n)}</b>${tb(t0)}<span class="arr">→</span>${tb(t1)}<span class="tag">${esc(b.cat)}</span><span class="small dim">+${c1 - c0} token${c1 - c0 === 1 ? "" : "s"} to equip</span></div>`; }).join("");
  const byCat = {}; d.a.forEach(a => (byCat[a.cat] = byCat[a.cat] || []).push(a));
  h += Object.entries(byCat).map(([c, l]) => `<div class="diff an"><b>${esc(c)}</b><span class="tag c">${l.length}</span><span class="small" style="flex-basis:100%;color:var(--tx2)">${esc(l.slice(0, 14).map(a => a.n).join(" · "))}${l.length > 14 ? ` · +${l.length - 14} more` : ""}</span></div>`).join("");
  $("#unlocks").innerHTML = h;
  // takeovers
  $("#tk-n").textContent = `${D.takeovers.filter(t => tkOK(t, A1) === true).length} unlocked`;
  $("#tks").innerHTML = D.takeovers.map(t => { const ok = tkOK(t, A1), was = tkOK(t, A0); const req = t.r.map(([k, v]) => `<span class="rqi ${A1[k] >= v ? "m" : "x"}">${k} ${v} <span class="dim">(${A1[k]})</span></span>`).join(t.op === "OR" ? " or " : " ");
    return `<div class="diff ${ok && !was ? "tk" : ""}" style="${ok === null ? "opacity:.55" : ""}"><b>${ok ? "✓" : ok === null ? "?" : "✕"} ${esc(t.n)}</b><span class="tag ${ok ? "g" : ""}">${esc(t.cat)}</span>${req}${t.note ? `<span class="small dim" style="flex-basis:100%">${esc(t.note)}</span>` : ""}</div>`; }).join("");
  // cost saved
  let pts = 0, w = 0; for (const k of ATTR) { for (let v = S.a[k]; v < A1[k]; v++) { pts++; w += costPt(v); } }
  const tok = d.b.reduce((s, [b, t0, t1]) => s + D.cost[b.c][t1 - 1] - (t0 ? D.cost[b.c][t0 - 1] : 0), 0);
  $("#save-k").innerHTML = `<div class="kpi"><small>Rating pts</small><b>+${pts}</b></div><div class="kpi"><small>Cost ≈</small><b>${w}</b></div><div class="kpi"><small>Tiers</small><b>+${d.b.length}</b></div><div class="kpi"><small>Tokens</small><b>${tok}</b></div>`;
  // card
  const b = BUILD[S.b];
  const cbl = Object.entries(S.cb).filter(([, n]) => n).map(([k, n]) => `${ANAME[k]} +${n} (${S.a[k]}→${A1[k]})`);
  $("#bcard").textContent = `NBA 2K27 · ${b.name}\n${S.pos} · ${hs(S.h)} · ${S.wt} lb · WS ${hs(S.ws)}\nCap breakers ${cbUsed()}/${cbAvail()}: ${cbl.join(", ") || "none"}\nUnlocks: ${d.b.map(([x, , t]) => `${x.n} ${TAB[t]}`).join(", ") || "—"}${d.t.length ? `\nTakeovers: ${d.t.map(t => t.n).join(", ")}` : ""}${d.a.length ? `\n+${d.a.length} animations` : ""}`;
}
function autoSpend() {
  // greedy: each step pick the breaker that adds the most badge tier value (+ takeovers/animations)
  let guard = 0;
  while (cbUsed() < cbAvail() && guard++ < 40) {
    const A1 = effAttrs(S.cb); let best = null, bs = 0;
    for (const k of ATTR) { const n = S.cb[k] || 0, L = ladder(k); if (locked(k) || n >= L.g.length || n >= PER) continue;
      const cb2 = Object.assign({}, S.cb, {[k]: n + 1}); const d = diffs(A1, effAttrs(cb2), S.h);
      const sc = d.b.reduce((s, [, t0, t1]) => s + (t1 - t0) * 10, 0) + d.t.length * 25 + d.a.length;
      if (sc > bs) { bs = sc; best = k; } }
    if (!best) break; S.cb[best] = (S.cb[best] || 0) + 1;
  }
}
function renderSim() { renderPresets(); renderBody(); renderCB(); renderAttrs(); renderUnlocks(); }

/* ---------------- MATRIX ---------------- */
function renderMatrix() {
  const M = S.mx, A = effAttrs(S.cb), h = S.h; $$("#mx-mode button").forEach(b => b.classList.toggle("on", b.dataset.m === M.m)); $("#mx-q").value = M.q || "";
  const q = (M.q || "").toLowerCase().trim(); let cats = [], sts = [], out = "", info = "";
  if (M.m === "badges") {
    cats = ["All", ...DISC.map(d => d[1])]; sts = [["all", "All"], ["elig", `Fits ${hs(h)}`], ["has", "Unlocked"], ["near", "Next tier ≤3"]];
    let L = D.badges.filter(b => (M.cat === "All" || b.cat === M.cat) && (!q || (b.n + " " + b.r.map(r => r[0] + " " + ANAME[r[0]]).join(" ") + " " + b.cat).toLowerCase().includes(q)));
    L = L.filter(b => { const t = tierOf(b, A, h); if (M.st === "elig") return t >= 0; if (M.st === "has") return t > 0; if (M.st === "near") { if (t < 0 || t >= 4) return false; return b.r.some(([k, th]) => th[t] - A[k] <= 3 && th[t] - A[k] > 0); } return true; });
    info = `${L.length} badges · your ratings incl. breakers · token cost per tier B/S/G/HOF · Legend only via Fuse`;
    out = `<div class="card"><div class="tw" style="max-height:70vh"><table class="tbl mx"><thead><tr><th>Badge</th><th>Attr</th><th>You</th><th>B</th><th>S</th><th>G</th><th>HOF</th><th>Height</th><th>Tokens</th><th>Tier</th></tr></thead><tbody>${L.map(b => { const t = tierOf(b, A, h);
      return b.r.map(([k, th], i) => `<tr class="${t < 0 ? "inel" : ""}">${i === 0 ? `<td class="bn" rowspan="${b.r.length}">${esc(b.n)}<div class="small dim">${esc(b.cat)}${b.r.length > 1 ? " · " + b.op : ""}</div></td>` : ""}<td class="ak">${k}</td><td class="me">${A[k]}</td>${th.map(x => `<td class="${A[k] >= x ? "hit" : "no"}">${x > 99 ? "—" : x}</td>`).join("")}${i === 0 ? `<td rowspan="${b.r.length}">${b.mn > 69 || b.mx < 88 ? (b.mn > 69 ? "≥" + hs(b.mn) : "≤" + hs(b.mx)) : "all"}</td><td rowspan="${b.r.length}" class="mono">${D.cost[b.c].join("/")}</td><td rowspan="${b.r.length}">${tb(t)}</td>` : ""}</tr>`).join(""); }).join("")}</tbody></table></div>
      <div class="small dim" style="margin-top:8px">Descriptions: ${D.badges.filter(b => b.d && L.includes(b)).map(b => `<b>${esc(b.n)}</b> — ${esc(b.d)}`).join(" · ")}</div></div>`;
  } else if (M.m === "anims") {
    const groups = [...new Set(D.anims.map(a => a.g))]; cats = ["All", ...groups];
    sts = [["all", "All"], ["ok", "Unlocked"], ["near", "Within 5"], ["fit", `Fits ${hs(h)}`]];
    let L = D.anims.filter(a => (M.cat === "All" || a.g === M.cat) && (!q || (a.n + " " + a.cat + " " + Object.keys(a.req).join(" ")).toLowerCase().includes(q)));
    const st = L.map(a => [a, animOK(a, A, h)]);
    let F = st.filter(([a, r]) => M.st === "ok" ? r.ok : M.st === "near" ? (!r.ok && !r.hf && r.gap <= 5) : M.st === "fit" ? !r.hf : true);
    F.sort((x, y) => (y[1].ok - x[1].ok) || (x[1].hf - y[1].hf) || (x[1].gap - y[1].gap));
    info = `${F.length} of ${D.anims.length} gates · LockerCodes (Sep 3, 2026; Patch 2.0 changed no thresholds). Jump-shot bases use the higher of Mid / 3PT. Jump-shot (100/781) and motion (100/353) lists are partial.`;
    const show = F.slice(0, 240);
    out = `<div class="grid g3">${show.map(([a, r]) => `<div class="an ${r.ok ? "ok" : (!r.hf && r.gap <= 5) ? "near" : ""}"><b>${esc(a.n)}</b><span>${r.ok ? '<span class="tag g">✓</span>' : r.hf ? '<span class="tag r">height</span>' : `<span class="tag y">−${r.gap}</span>`}</span><span class="h">${esc(a.cat)} · ${Object.entries(a.req).map(([k, v]) => `${k === "SHOT" ? "Shot (Mid/3PT)" : k} ${v}`).join(a.mode === "OR" ? " or " : " + ") || "no rating gate"} · ${hs(a.mn)}–${hs(a.mx)}</span></div>`).join("")}</div>${F.length > show.length ? `<div class="note">Showing 240 of ${F.length}. Search or filter to narrow.</div>` : ""}
      <div class="card" style="margin-top:12px"><h2>Asked about but not in our verified data</h2>${D.unverified.map(u => `<div class="diff"><b>${esc(u.n)}</b><span class="small dim">${esc(u.note)}</span></div>`).join("")}</div>`;
  } else if (M.m === "tk") {
    out = `<div class="grid g2">${D.takeovers.map(t => { const ok = tkOK(t, A); return `<div class="diff ${ok ? "tk" : ""}"><b>${ok ? "✓" : ok === null ? "?" : "✕"} ${esc(t.n)}</b><span class="tag">${esc(t.cat)}</span>${t.r.map(([k, v]) => `<span class="rqi ${A[k] >= v ? "m" : "x"}">${esc(ANAME[k])} ${v} (${A[k]})</span>`).join(t.op === "OR" ? " or " : " ")}<span class="small dim" style="flex-basis:100%">${esc(t.note)}</span></div>`; }).join("")}</div><div class="note">Default Takeover in each discipline gives +30 to that discipline's attributes, capped at 80. Patch 2.0: Shot Artist, Calibrated and Navigator windows retimed; Airspace nerfed.</div>`;
  } else {
    out = `<div class="card"><h2>Legacy badge names → 2K27</h2>${D.aliases.map(a => `<div class="diff"><b>${esc(a.a)}</b><span class="arr">→</span><b class="t3">${esc(a.to)}</b><span class="small dim" style="flex-basis:100%">${esc(a.note)}</span></div>`).join("")}<div class="note">Sites still listing Anchor, Rebound Chaser, Boxout Beast or Catch and Shoot are using 2K25/26 data.</div></div>`;
  }
  $("#mx-cat").innerHTML = cats.map(c => `<button class="chip ${M.cat === c ? "on" : ""}" data-c="${esc(c)}" type="button">${esc(c)}</button>`).join("");
  $("#mx-st").innerHTML = sts.map(([k, n]) => `<button class="chip ${M.st === k ? "on" : ""}" data-s="${k}" type="button">${esc(n)}</button>`).join("");
  $("#mx-info").textContent = info; $("#mx-out").innerHTML = out;
}

/* ---------------- LOADOUT ---------------- */
function fuseOf(n) { return S.fuse.find(f => f[0] === n); }
function reactOf(n) { return S.fuse.find(f => f[1] === n); }
function maxTier(n, A) { return tierOf(BADGE[n], A, S.h); }
function loCalc() {
  const A = effAttrs(S.cb), used = {}, rows = {};
  for (const [dk] of DISC) { used[dk] = 0; rows[dk] = []; }
  for (const [n, t0] of Object.entries(S.eq)) { const b = BADGE[n]; if (!b) continue; const dk = CAT2D[b.cat]; const mt = maxTier(n, A); const t = Math.max(0, Math.min(t0, mt)); const fz = fuseOf(n), rx = reactOf(n);
    const cost = fz || t === 0 ? 0 : D.cost[b.c][t - 1]; used[dk] += cost; const boost = fz ? fz[2] : rx ? rx[2] : 0;
    rows[dk].push({n, b, t, mt, cost, fz, rx, fin: t ? Math.min(5, t + boost) : 0}); }
  return {A, used, rows};
}
function renderLoadout() {
  $("#lo-b").innerHTML = D.builds.map(b => `<option value="${b.id}">${esc(b.name)}</option>`).join(""); $("#lo-b").value = S.b;
  $$("#lo-mode button").forEach(b => b.classList.toggle("on", b.dataset.m === S.mode));
  const bl = BUILD[S.b], lo = bl.lo[S.mode] || bl.lo.rec; $("#lo-why").innerHTML = lo ? esc(lo.why) : `No saved loadout for this build yet — use <b>Auto-fill</b> or add badges. Token pools are estimates; set yours from the Builder.`;
  const {A, used, rows} = loCalc(); let html = "", tot = 0, pool = 0;
  for (const [dk, dn] of DISC) {
    const bs = D.badges.filter(b => CAT2D[b.cat] === dk); const free = bs.filter(b => !(b.n in S.eq) && maxTier(b.n, A) > 0);
    tot += used[dk]; pool += S.pools[dk] || 0;
    html += `<div class="disc"><h3>${dn}<span class="n ${used[dk] > (S.pools[dk] || 0) ? "over" : ""}">${used[dk]} / <input type="number" data-pool="${dk}" value="${S.pools[dk] || 0}" min="0" max="40" style="width:56px;min-height:28px;padding:2px 4px;display:inline-block;text-align:center"> tokens</span></h3>
      ${rows[dk].sort((a, b) => b.fin - a.fin).map(r => `<div class="eqr"><div class="nm" title="${esc(r.n)}">${esc(r.n)}${r.fz ? `<span class="fz">FUSE +${r.fz[2]}</span>` : r.rx ? `<span class="fz">REACT +${r.rx[2]}</span>` : ""}</div>
        <select data-eq="${esc(r.n)}">${[1, 2, 3, 4].map(t => `<option value="${t}" ${t === r.t ? "selected" : ""} ${t > r.mt ? "disabled" : ""}>${TIERS[t]}${t > r.mt ? " 🔒" : ""}</option>`).join("")}</select>
        <span class="c">${r.fin > r.t ? `<span class="t${r.fin}">${TAB[r.fin]}</span>` : r.fz ? "0" : r.cost}</span><button class="x" data-rm="${esc(r.n)}" type="button" aria-label="remove">✕</button></div>${r.t0 === 0 ? "" : ""}`).join("") || `<div class="small dim">No badges.</div>`}
      ${free.length ? `<select data-add="${dk}" style="min-height:36px;padding:4px 8px;font-size:13px;margin-top:4px"><option value="">+ Add ${dn} badge…</option>${free.map(b => `<option value="${esc(b.n)}">${esc(b.n)} (max ${TIERS[maxTier(b.n, A)]} · ${D.cost[b.c].join("/")})</option>`).join("")}</select>` : ""}</div>`;
  }
  $("#lo-disc").innerHTML = html; $("#lo-tot").textContent = `${tot} / ${pool} tokens`;
  // fuse
  $("#fz-p1").value = S.p1; $("#fz-p2").value = S.p2;
  const eqn = Object.keys(S.eq).sort(); const n1 = S.fuse.filter(f => f[2] === 1).length, n2 = S.fuse.filter(f => f[2] === 2).length;
  $("#fz-n").textContent = `+1: ${n1}/${S.p1} · +2: ${n2}/${S.p2}`;
  $("#fz-rows").innerHTML = S.fuse.map((f, i) => { const seen = D.pairs.find(p => p[0] === f[0] && p[1] === f[1]);
    return `<div class="fz-row"><select data-fz="${i}" data-k="0"><option value="">Fuse…</option>${eqn.map(n => `<option ${n === f[0] ? "selected" : ""}>${esc(n)}</option>`).join("")}</select>
      <select data-fz="${i}" data-k="2"><option value="1" ${f[2] === 1 ? "selected" : ""}>+1</option><option value="2" ${f[2] === 2 ? "selected" : ""}>+2</option></select>
      <select data-fz="${i}" data-k="1"><option value="">Reaction…</option>${eqn.filter(n => n !== f[0]).map(n => `<option ${n === f[1] ? "selected" : ""}>${esc(n)}</option>`).join("")}</select>
      <button class="x eqr" data-fzrm="${i}" type="button" style="width:30px;height:30px;border-radius:9px;border:1px solid var(--line2);background:var(--card);padding:0">✕</button>
      <div class="small" style="grid-column:1/-1;margin:-2px 0 4px;color:${seen ? "var(--neon)" : "var(--tx3)"}">${seen ? `✓ seen: ${esc(seen[2])}` : "not verified — confirm the Builder allows this pair"}</div></div>`; }).join("") +
    (n1 > S.p1 || n2 > S.p2 ? `<div class="warn">More Fuse pairs than unlocked slots.</div>` : "");
  // takeovers
  const tkd = ["Shooting", "Finishing", "Playmaking", "Defense", "Rebounding"];
  $("#lo-tk").innerHTML = tkd.map((c, i) => { const opts = D.takeovers.filter(t => (t.cat === c || t.cat === "Any") && t.op !== "NA");
    return `<div class="tkrow"><span>${c}</span><select data-tk="${i}"><option value="">Default (+30, cap 80)</option>${opts.map(t => { const ok = tkOK(t, A); return `<option value="${esc(t.n)}" ${S.tk[i] === t.n ? "selected" : ""} ${ok ? "" : "disabled"}>${esc(t.n)}${ok ? "" : " 🔒"}</option>`; }).join("")}</select></div>`; }).join("");
  // card
  let card = `NBA 2K27 · ${bl.name} · ${S.mode === "3s" ? "3s" : "Rec"}\n`;
  for (const [dk, dn] of DISC) if (rows[dk].length) card += `${dn} (${used[dk]}/${S.pools[dk] || 0}): ${rows[dk].map(r => `${r.n} ${TAB[r.fin] || "—"}${r.fz ? "*" : ""}`).join(", ")}\n`;
  card += `Fuse→React: ${S.fuse.filter(f => f[0]).map(f => `${f[0]} (+${f[2]})→${f[1] || "—"}`).join(" · ") || "—"}\nTakeovers: ${S.tk.filter(Boolean).join(" / ") || "Default"}\n* = Fuse (0 tokens)`;
  $("#lo-card").textContent = card;
}
function autoFill() {
  const A = effAttrs(S.cb); const keep = new Set(S.fuse.map(f => f[0]).filter(Boolean));
  const eq = {}; keep.forEach(n => { if (BADGE[n]) eq[n] = Math.max(1, maxTier(n, A)); });
  const PRI = ["Set and Fire","Deadeye","Limitless Range","Arc Cadence","Mini Marksman","Handles for Days","Pace","Lightning Launch","Ankle Assassin","Dimer","Break Starter","Versatile Visionary","Layup Mixmaster","Aerial Wizard","Posterizer","Rise Up","Paint Prodigy","Off-Ball Pest","Interceptor","Glove","Challenger","Seatbelt","Paint Patroller","High-Flying Denier","Post Lockdown","Immovable Enforcer","Sync Snatcher","Possession Closer","Crasher","Breaker","Boxout Boss","Flash","Work Horse","Pogo Stick","Bruiser","Brick Wall","Static Middy","Smooth Operator","Float Game","Physical Finisher","Strong Handle","Pick Dodger","Ankle Braces","Slippery Off-Ball","Wall Up","Quick Trigger","Bail Out","Hook Specialist","Ghost Stepper","Post Powerhouse","Post Spin Catalyst","Post Fade Phenom","Unpluckable"];
  const left = Object.assign({}, S.pools);
  for (const n of PRI) { const b = BADGE[n]; if (!b || n in eq) continue; const mt = maxTier(n, A); if (mt <= 0) continue; const dk = CAT2D[b.cat];
    for (let t = mt; t >= 1; t--) { const c = D.cost[b.c][t - 1]; if (c <= (left[dk] || 0)) { eq[n] = t; left[dk] -= c; break; } } }
  S.eq = eq;
}

/* ---------------- BUILDS ---------------- */
function renderBuilds() {
  const f = S.bf || "all";
  $("#bf").innerHTML = [["all", "All"], ["mine", "Your builds"], ["meta", "Meta templates"], ["pro", "Creator builds"]].map(([k, n]) => `<button class="chip ${f === k ? "on" : ""}" data-bf="${k}" type="button">${n}</button>`).join("");
  const keys = ["3PT", "MID", "DD", "DL", "BH", "PA", "PERD", "INTD"];
  $("#b-list").innerHTML = D.builds.filter(b => f === "all" || b.kind === f).map(b => {
    const A = b.a; const top = D.badges.map(x => [x, tierOf(x, A, b.h)]).filter(([, t]) => t >= 3).sort((x, y) => y[1] - x[1]).slice(0, 8);
    const tks = D.takeovers.filter(t => tkOK(t, A) === true && t.r.length).map(t => t.n);
    return `<div class="card bld"><div class="hd"><div class="av ${b.kind}">${hs(b.h)}</div><div style="min-width:0"><h3 style="margin:0">${esc(b.name)}</h3><div class="row" style="margin-top:4px"><span class="tag ${b.kind === "mine" ? "g" : b.kind === "pro" ? "y" : "v"}">${b.kind === "mine" ? "Your build" : b.kind === "pro" ? "Creator" : "Template"}</span><span class="tag">${b.pos}</span><span class="tag">${b.wt} lb</span><span class="tag">WS ${hs(b.ws)}</span>${b.lo.rec ? `<span class="tag c">Rec${b.lo["3s"] ? " + 3s" : ""} loadout</span>` : ""}</div></div></div>
      <div class="stat8">${keys.map(k => `<div><small>${k}</small><b class="${A[k] >= 90 ? "v90" : A[k] >= 85 ? "v85" : A[k] >= 80 ? "v80" : "vlo"}">${A[k]}</b></div>`).join("")}</div>
      <div class="small muted" style="margin-top:8px">${esc(b.note)}</div>
      <div class="row" style="margin-top:8px;gap:4px">${top.map(([x, t]) => `<span class="tb t${t}">${esc(x.n)}</span>`).join("")}</div>
      ${tks.length ? `<div class="small" style="margin-top:6px;color:var(--gold)">⚡ ${esc(tks.join(" · "))}</div>` : ""}
      <div class="row" style="margin-top:10px"><button class="btn s p" data-load="${b.id}" data-to="sim" type="button">Cap Breakers</button><button class="btn s" data-load="${b.id}" data-to="loadout" type="button">Loadout</button><button class="btn s" data-load="${b.id}" data-to="matrix" type="button">Matrix</button></div>
      <div class="src">${esc(b.src)}</div></div>`; }).join("");
}

/* ---------------- PASSING ---------------- */
function renderPassing() {
  $("#pass-set").innerHTML = D.pass.rows.map(([n, v, w]) => `<div class="setrow"><b>${esc(n)}</b><span class="v">${esc(v)}</span>${w ? `<span class="w">${esc(w)}</span>` : ""}</div>`).join("") +
    `<div class="note">Why: Direction high + Distance/Openness low = the game sends the icon / flick pass where you aim, even to a teammate already down court, instead of the closest or "most open" guard. Your current 64 / 32 / 4 leans toward the nearer teammate.</div>`;
  $("#pass-in").innerHTML = `<thead><tr><th>Action</th><th>PlayStation</th><th>Xbox</th></tr></thead><tbody>${D.pass.inputs.map(r => `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td>${esc(r[2])}</td></tr>`).join("")}</tbody>`;
  const A = effAttrs(S.cb), L = D.anims.filter(a => a.cat === "Pass Style").sort((a, b) => a.req.PA - b.req.PA);
  $("#ps-n").textContent = `${L.length} styles · your Pass Acc ${A.PA}`;
  $("#pass-styles").innerHTML = L.map(a => { const r = animOK(a, A, S.h); const note = D.passNotes[a.n];
    return `<div class="an ${r.ok ? "ok" : r.gap <= 5 ? "near" : ""}"><b>${esc(a.n)}</b><span>${r.ok ? '<span class="tag g">✓</span>' : `<span class="tag y">−${r.gap}</span>`} <span class="tag">${a.req.PA}</span></span>${note ? `<span class="h" style="grid-column:1/-1;color:var(--tx2)">${esc(note)}</span>` : ""}</div>`; }).join("");
  $("#srcs").innerHTML = [...D.sources, ...D.pass.src.map(u => [u.replace(/^https?:\/\/(www\.)?/, "").split("/")[0], u])].map(([n, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(n)} — ${esc(u)}</a>`).join("");
}

/* ---------------- shell ---------------- */
function render() {
  $$("nav.tabs a").forEach(a => a.classList.toggle("on", a.dataset.t === S.tab));
  $$(".view").forEach(v => v.classList.toggle("on", v.id === "v-" + S.tab));
  if (S.tab === "sim") renderSim(); else if (S.tab === "matrix") renderMatrix(); else if (S.tab === "loadout") renderLoadout(); else if (S.tab === "builds") renderBuilds(); else renderPassing();
  $("#foot").textContent = `${D.badges.length} badges · ${D.anims.length} animation gates · ${D.takeovers.length} takeovers · ${D.builds.length} builds · ${D.checked}`;
  save();
}
function loadBuild(id, tab) { const keep = {earned: S.earned, mx: S.mx, bf: S.bf}; const tabNow = tab || S.tab; S = Object.assign(fresh(id, S.mode), keep); S.tab = tabNow; render(); window.scrollTo(0, 0); }
function init() {
  for (let i = 69; i <= 87; i++) $("#p-h").insertAdjacentHTML("beforeend", `<option value="${i}">${hs(i)}</option>`);
  load();
  document.addEventListener("click", e => {
    const t = e.target.closest("button,a,[data-max]"); if (!t) return;
    if (t.matches("nav.tabs a")) { e.preventDefault(); S.tab = t.dataset.t; render(); window.scrollTo(0, 0); return; }
    if (t.dataset.b) return loadBuild(t.dataset.b);
    if (t.dataset.load) return loadBuild(t.dataset.load, t.dataset.to);
    if (t.dataset.max) { S.a[t.dataset.max] = S.cap[t.dataset.max]; toast(`${ANAME[t.dataset.max]} maxed with MyPoints`); return render(); }
    if (t.dataset.cb) { const k = t.dataset.cb, d = +t.dataset.d, n = S.cb[k] || 0; const nn = Math.max(0, Math.min(PER, ladder(k).g.length, n + d)); if (d > 0 && cbUsed() >= MAXCB) return toast("28 is the max"); S.cb[k] = nn; if (!nn) delete S.cb[k]; return render(); }
    if (t.dataset.src) { const c = D.cbSources.find(x => x.id === t.dataset.src); S.earned[c.id] = Math.max(0, Math.min(c.max, (S.earned[c.id] || 0) + +t.dataset.d)); return render(); }
    if (t.id === "cb-reset") { S.cb = {}; return render(); }
    if (t.id === "cb-best") { S.cb = {}; autoSpend(); toast(`Spent ${cbUsed()} breakers`); return render(); }
    if (t.id === "b-link" || t.id === "lo-link") { navigator.clipboard && navigator.clipboard.writeText(stateLink()).catch(() => {}); return toast("Share link copied"); }
    if (t.id === "b-card") { navigator.clipboard && navigator.clipboard.writeText($("#bcard").textContent).catch(() => {}); return toast("Build card copied"); }
    if (t.id === "lo-copy") { navigator.clipboard && navigator.clipboard.writeText($("#lo-card").textContent).catch(() => {}); return toast("Loadout copied"); }
    if (t.closest("#mx-mode")) { S.mx = {m: t.dataset.m, cat: "All", st: "all", q: S.mx.q}; return render(); }
    if (t.dataset.c != null && t.closest("#mx-cat")) { S.mx.cat = t.dataset.c; return render(); }
    if (t.dataset.s && t.closest("#mx-st")) { S.mx.st = t.dataset.s; return render(); }
    if (t.closest("#lo-mode")) { const m = t.dataset.m; const keep = {cb: S.cb, a: S.a, earned: S.earned, h: S.h, pos: S.pos, wt: S.wt, ws: S.ws}; S = Object.assign(fresh(S.b, m), keep); S.tab = "loadout"; return render(); }
    if (t.dataset.rm) { delete S.eq[t.dataset.rm]; S.fuse = S.fuse.filter(f => f[0] !== t.dataset.rm); S.fuse.forEach(f => { if (f[1] === t.dataset.rm) f[1] = ""; }); return render(); }
    if (t.dataset.fzrm != null) { S.fuse.splice(+t.dataset.fzrm, 1); return render(); }
    if (t.id === "fz-add") { S.fuse.push(["", "", S.fuse.filter(f => f[2] === 2).length < S.p2 ? 2 : 1]); return render(); }
    if (t.id === "lo-auto") { autoFill(); toast("Filled within pools"); return render(); }
    if (t.id === "lo-reset") { const lo = BUILD[S.b].lo[S.mode] || BUILD[S.b].lo.rec; if (lo) { S.eq = clone(lo.eq); S.fuse = clone(lo.fuse); S.tk = clone(lo.tk); } S.pools = clone(BUILD[S.b].pools); return render(); }
    if (t.id === "lo-clear") { S.eq = {}; S.fuse = []; return render(); }
    if (t.dataset.bf) { S.bf = t.dataset.bf; return render(); }
  });
  document.addEventListener("change", e => {
    const t = e.target;
    if (t.dataset.a) { S.a[t.dataset.a] = Math.max(25, Math.min(99, parseInt(t.value) || 25)); if (S.cap[t.dataset.a] != null && S.a[t.dataset.a] > S.cap[t.dataset.a]) S.cap[t.dataset.a] = S.a[t.dataset.a]; delete S.lad[t.dataset.a]; return render(); }
    if (t.id === "p-pos") { S.pos = t.value; return render(); }
    if (t.id === "p-h") { S.h = +t.value; return render(); }
    if (t.id === "p-wt") { S.wt = +t.value; return render(); }
    if (t.id === "p-ws") { S.ws = +t.value; return render(); }
    if (t.id === "lo-b") return loadBuild(t.value, "loadout");
    if (t.dataset.pool) { S.pools[t.dataset.pool] = Math.max(0, +t.value || 0); return render(); }
    if (t.dataset.eq) { S.eq[t.dataset.eq] = +t.value; return render(); }
    if (t.dataset.add) { if (t.value) S.eq[t.value] = Math.max(1, maxTier(t.value, effAttrs(S.cb))); return render(); }
    if (t.dataset.fz != null) { const f = S.fuse[+t.dataset.fz], k = +t.dataset.k; f[k] = k === 2 ? +t.value : t.value; return render(); }
    if (t.id === "fz-p1") { S.p1 = Math.max(0, Math.min(12, +t.value || 0)); return render(); }
    if (t.id === "fz-p2") { S.p2 = Math.max(0, Math.min(4, +t.value || 0)); return render(); }
    if (t.dataset.tk != null) { S.tk[+t.dataset.tk] = t.value; return render(); }
  });
  $("#mx-q").addEventListener("input", e => { S.mx.q = e.target.value; clearTimeout(init._q); init._q = setTimeout(() => { renderMatrix(); save(); const q = $("#mx-q"); q.focus(); }, 160); });
  window.addEventListener("hashchange", () => { const h = new URLSearchParams(location.hash.slice(1)); const tab = h.get("tab"); if (tab && tab !== S.tab) { S.tab = tab; render(); } });
  const net = () => { $("#net").textContent = navigator.onLine ? "Offline-ready" : "Offline"; }; window.addEventListener("online", net); window.addEventListener("offline", net); net();
  render();
}
init();
