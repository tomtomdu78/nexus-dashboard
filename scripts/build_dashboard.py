"""
NEXUS — Génération du dashboard HTML à partir de data.json.

Lit public/data.json (produit par fetch_data.py) et écrit public/index.html,
la console NEXUS que GitHub Pages servira. Le design (HUD cyan) est identique
à la version validée ; seules les données changent chaque jour.
"""

import os
import json


def eur(v):
    return f"{round(v):,}".replace(",", " ")


def build(data):
    stores_js = json.dumps(data["stores"], ensure_ascii=False)
    gen = data["generatedAt"]
    # Les valeurs de synthèse
    ca = eur(data["totalCA"])
    orders = data["totalOrders"]
    basket = f"{data['avgBasket']:.1f}".replace(".", ",")
    retpct = f"{data['returnPct']:.1f}".replace(".", ",")
    active = data["activeCount"]
    total = data["storeCount"]

    return HTML_TEMPLATE.format(
        stores_js=stores_js, gen=gen, ca=ca, orders=orders,
        basket=basket, retpct=retpct, active=active, total=total,
    )


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS — Console des boutiques</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{{--bg:#04070d;--bg2:#070d18;--panel:rgba(10,20,36,.55);--cyan:#3ff0ff;--cyan-dim:#1a8a99;--amber:#ffb547;--red:#ff5a4d;--green:#4dffb0;--grid:rgba(63,240,255,.08);--line:rgba(63,240,255,.22);--txt:#c7f2f8;--txt-dim:#6a8a95;}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:'Rajdhani',sans-serif;background:var(--bg);color:var(--txt);min-height:100vh;overflow-x:hidden;position:relative}}
  body::before{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(63,240,255,.10),transparent 60%),linear-gradient(180deg,var(--bg),var(--bg2))}}
  body::after{{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.5;background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(ellipse 90% 80% at 50% 30%,#000 40%,transparent);mask-image:radial-gradient(ellipse 90% 80% at 50% 30%,#000 40%,transparent)}}
  .scan{{position:fixed;left:0;right:0;height:2px;z-index:1;pointer-events:none;background:linear-gradient(90deg,transparent,rgba(63,240,255,.5),transparent);animation:scan 8s linear infinite;opacity:.35}}
  @keyframes scan{{0%{{top:-2px}}100%{{top:100%}}}}
  .wrap{{max-width:1180px;margin:0 auto;padding:0 28px;position:relative;z-index:2}}
  .bracket{{position:relative}}
  .bracket::before,.bracket::after{{content:'';position:absolute;width:14px;height:14px;border:1px solid var(--cyan);opacity:.6}}
  .bracket::before{{top:-1px;left:-1px;border-right:0;border-bottom:0}}
  .bracket::after{{bottom:-1px;right:-1px;border-left:0;border-top:0}}
  header{{padding:38px 0 26px;border-bottom:1px solid var(--line)}}
  .head-row{{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}}
  .sys{{display:flex;align-items:center;gap:18px}}
  .reactor{{width:56px;height:56px;position:relative;flex-shrink:0}}
  .reactor .ring{{position:absolute;inset:0;border-radius:50%;border:2px solid var(--cyan);opacity:.85;box-shadow:0 0 18px rgba(63,240,255,.55),inset 0 0 12px rgba(63,240,255,.35)}}
  .reactor .ring2{{position:absolute;inset:9px;border-radius:50%;border:1px solid var(--cyan);border-top-color:transparent;border-left-color:transparent;animation:spin 3.5s linear infinite}}
  .reactor .core{{position:absolute;inset:20px;border-radius:50%;background:var(--cyan);box-shadow:0 0 16px var(--cyan);animation:pulse 2.2s ease-in-out infinite}}
  @keyframes spin{{to{{transform:rotate(360deg)}}}}
  @keyframes pulse{{0%,100%{{opacity:.6;transform:scale(.85)}}50%{{opacity:1;transform:scale(1.05)}}}}
  .eyebrow{{font-family:'Share Tech Mono',monospace;font-size:11px;letter-spacing:.4em;color:var(--cyan-dim);margin-bottom:4px}}
  h1{{font-family:'Orbitron',sans-serif;font-size:24px;font-weight:700;letter-spacing:.11em;color:#eafcff;text-shadow:0 0 18px rgba(63,240,255,.4)}}
  h1 span{{color:var(--cyan)}}
  .status{{text-align:right;font-family:'Share Tech Mono',monospace;font-size:11px;line-height:1.9;color:var(--txt-dim)}}
  .status .on{{color:var(--green)}}
  .status .live{{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);margin-right:6px;animation:blink 1.4s infinite;vertical-align:middle}}
  @keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
  .sec{{padding:34px 0 4px}}
  .sec-h{{display:flex;align-items:center;gap:12px;margin-bottom:20px;font-family:'Share Tech Mono',monospace}}
  .sec-h .tag{{font-size:11px;letter-spacing:.3em;color:var(--cyan);text-transform:uppercase}}
  .sec-h .dash{{flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}}
  .sec-h .idx{{font-size:11px;color:var(--txt-dim)}}
  .kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
  .kpi{{background:var(--panel);border:1px solid var(--line);padding:20px;backdrop-filter:blur(6px);position:relative;overflow:hidden;transition:.3s}}
  .kpi:hover{{border-color:var(--cyan);box-shadow:0 0 24px rgba(63,240,255,.12)}}
  .k-label{{font-family:'Share Tech Mono',monospace;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--txt-dim);margin-bottom:14px}}
  .k-val{{font-family:'Orbitron',sans-serif;font-size:26px;font-weight:600;color:#eafcff;text-shadow:0 0 14px rgba(63,240,255,.35);line-height:1}}
  .k-val.warn{{color:var(--amber);text-shadow:0 0 14px rgba(255,181,71,.35)}}
  .k-unit{{font-size:14px;color:var(--cyan-dim);margin-left:2px}}
  .k-sub{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--cyan-dim);margin-top:10px;letter-spacing:.08em}}
  .panel-c{{background:var(--panel);border:1px solid var(--line);padding:24px;backdrop-filter:blur(6px)}}
  .pc-head{{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:6px}}
  .pc-title{{font-family:'Orbitron',sans-serif;font-size:15px;font-weight:500;letter-spacing:.06em;color:#eafcff}}
  .pc-sub{{font-family:'Share Tech Mono',monospace;font-size:10px;color:var(--cyan-dim);letter-spacing:.1em}}
  .cbox{{position:relative;width:100%;height:300px}}
  .snode{{background:var(--panel);border:1px solid var(--line);backdrop-filter:blur(6px);margin-bottom:12px;transition:.3s}}
  .snode.open{{border-color:var(--cyan);box-shadow:0 0 30px rgba(63,240,255,.1)}}
  .snode.dimn{{opacity:.65}}
  .shead{{display:flex;align-items:center;gap:16px;padding:16px 20px;cursor:pointer;user-select:none}}
  .shead:hover .node-name{{color:var(--cyan)}}
  .node-id{{width:44px;height:44px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-family:'Orbitron',sans-serif;font-weight:700;font-size:14px;border:1px solid var(--cyan);color:var(--cyan)}}
  .node-id.dim{{border-color:var(--cyan-dim);color:var(--cyan-dim)}}
  .shead-main{{flex:1;min-width:0}}
  .node-name{{font-family:'Rajdhani';font-weight:700;font-size:17px;letter-spacing:.02em;color:#eafcff;transition:.2s}}
  .node-cat{{font-family:'Share Tech Mono',monospace;font-size:9px;color:var(--txt-dim);letter-spacing:.05em;text-transform:uppercase;margin-top:1px}}
  .shead-stats{{display:flex;gap:26px;align-items:center}}
  .hstat{{text-align:right}}
  .hstat .hv{{font-family:'Orbitron';font-size:16px;font-weight:600;color:var(--cyan)}}
  .hstat .hv.warn{{color:var(--amber)}}.hstat .hv.hot{{color:var(--red)}}
  .hstat .hl{{font-family:'Share Tech Mono';font-size:9px;color:var(--txt-dim);letter-spacing:.05em;text-transform:uppercase;margin-top:2px}}
  .chev{{color:var(--cyan-dim);font-size:20px;transition:.3s;width:16px;text-align:center}}
  .snode.open .chev{{transform:rotate(90deg);color:var(--cyan)}}
  .sbody{{max-height:0;overflow:hidden;transition:max-height .45s cubic-bezier(.2,.7,.2,1)}}
  .sbody-inner{{padding:4px 22px 24px;border-top:1px solid var(--line)}}
  .dgrid{{display:grid;grid-template-columns:1.1fr .9fr;gap:20px;margin-top:20px}}
  @media(max-width:760px){{.dgrid{{grid-template-columns:1fr}}.shead-stats{{display:none}}}}
  .dcard-t{{font-family:'Share Tech Mono';font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--cyan);margin-bottom:14px}}
  .mini-chart{{position:relative;width:100%;height:170px}}
  .flow{{display:flex;flex-direction:column;gap:9px;margin-top:4px}}
  .frow{{display:flex;align-items:center;gap:10px}}
  .frow .fl{{width:88px;flex-shrink:0;color:var(--txt-dim);font-family:'Share Tech Mono';font-size:10px;text-transform:uppercase}}
  .fbar-wrap{{flex:1;height:16px;background:rgba(63,240,255,.06)}}
  .fbar{{height:100%}}
  .fbar.gr{{background:linear-gradient(90deg,rgba(63,240,255,.5),rgba(63,240,255,.75))}}
  .fbar.rd{{background:linear-gradient(90deg,rgba(255,90,77,.4),rgba(255,90,77,.7))}}
  .fbar.am{{background:linear-gradient(90deg,rgba(255,181,71,.35),rgba(255,181,71,.6))}}
  .fbar.nt{{background:linear-gradient(90deg,rgba(77,255,176,.4),rgba(77,255,176,.7))}}
  .fval{{width:78px;text-align:right;flex-shrink:0;font-family:'Orbitron';font-size:12px;color:var(--txt)}}
  .plist{{display:flex;flex-direction:column;gap:8px}}
  .prow{{display:flex;align-items:center;gap:10px}}
  .prow .pn{{flex:1;min-width:0;font-size:13px;color:var(--txt);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .prow .pbar{{height:5px;background:linear-gradient(90deg,rgba(63,240,255,.2),var(--cyan));flex-shrink:0;box-shadow:0 0 6px rgba(63,240,255,.4)}}
  .prow .pv{{font-family:'Orbitron';font-size:11px;color:var(--cyan);width:56px;text-align:right;flex-shrink:0}}
  footer{{border-top:1px solid var(--line);margin-top:46px;padding:22px 0 40px;text-align:center;position:relative;z-index:2}}
  footer p{{font-family:'Share Tech Mono';font-size:10px;color:var(--txt-dim);letter-spacing:.1em}}
  @media(max-width:820px){{.kpis{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:18px}}}}
  @media(max-width:520px){{.wrap{{padding:0 16px}}.kpis{{grid-template-columns:1fr}}.status{{text-align:left}}}}
  @media(prefers-reduced-motion:reduce){{.scan,.reactor .ring2,.reactor .core,.live{{animation:none}}}}
</style>
</head>
<body>
<div class="scan"></div>
<div class="wrap">
  <header><div class="head-row">
    <div class="sys">
      <div class="reactor"><div class="ring"></div><div class="ring2"></div><div class="core"></div></div>
      <div><div class="eyebrow">SYSTÈME NEXUS // COMMERCE</div><h1>CONSOLE <span>BOUTIQUES</span></h1></div>
    </div>
    <div class="status">
      <div><span class="live"></span><span class="on">EN LIGNE</span> · {total} NŒUDS</div>
      <div>EXERCICE 2026 · EUR</div>
      <div>SYNC AUTO : {gen}</div>
    </div>
  </div></header>

  <section class="sec">
    <div class="sec-h"><span class="tag">Indicateurs primaires · consolidés</span><span class="dash"></span><span class="idx">SEC.01</span></div>
    <div class="kpis">
      <div class="kpi bracket"><div class="k-label">CA net total</div><div class="k-val">{ca}<span class="k-unit">€</span></div><div class="k-sub">{total} NŒUDS · {active} ACTIFS</div></div>
      <div class="kpi bracket"><div class="k-label">Commandes</div><div class="k-val">{orders}</div><div class="k-sub">FLUX TOTAL</div></div>
      <div class="kpi bracket"><div class="k-label">Panier moyen</div><div class="k-val">{basket}<span class="k-unit">€</span></div><div class="k-sub">MOYENNE PONDÉRÉE</div></div>
      <div class="kpi bracket"><div class="k-label">Taux de retour</div><div class="k-val warn">{retpct}<span class="k-unit">%</span></div><div class="k-sub">SURVEILLANCE</div></div>
    </div>
  </section>

  <section class="sec">
    <div class="sec-h"><span class="tag">Flux temporel consolidé</span><span class="dash"></span><span class="idx">SEC.02</span></div>
    <div class="panel-c"><div class="pc-head"><div class="pc-title">CA MENSUEL · TOUTES BOUTIQUES</div><div class="pc-sub">ANNÉE EN COURS</div></div>
    <div class="cbox"><canvas id="monthlyAll" role="img" aria-label="CA mensuel consolidé"></canvas></div></div>
  </section>

  <section class="sec">
    <div class="sec-h"><span class="tag">Analyse par nœud · déplier pour détail</span><span class="dash"></span><span class="idx">SEC.03</span></div>
    <div id="storeList"></div>
  </section>
</div>
<footer><div class="wrap"><p>MISE À JOUR AUTOMATIQUE · {gen} · SOURCE SHOPIFY · GÉNÉRÉ PAR NEXUS</p></div></footer>

<script>
const CY='#3ff0ff',AM='#ffb547',GRID='rgba(63,240,255,.10)',TXD='#6a8a95';
Chart.defaults.font.family="'Rajdhani',sans-serif";Chart.defaults.color=TXD;
const eur=v=>Math.round(v).toLocaleString('fr-FR');
const M=['JAN','FÉV','MAR','AVR','MAI','JUIN','JUIL','AOÛ','SEP','OCT','NOV','DÉC'];
const stores={stores_js};

const maxCA=Math.max(...stores.map(s=>s.ca),1);
const list=document.getElementById('storeList');
stores.forEach((s,i)=>{{
  const node=document.createElement('div');
  node.className='snode'+(s.boot?' dimn':'');
  const initials=s.name.replace(/[^A-Za-zÀ-ÿ ]/g,'').split(' ').filter(Boolean).slice(0,2).map(w=>w[0]).join('').toUpperCase()||'??';
  const hot=s.returnPct>=25?'hot':(s.returnPct>=15?'warn':'');
  const pmax=s.products.length?Math.max(...s.products.map(p=>p[1])):1;
  node.innerHTML=`
    <div class="shead" data-i="${{i}}">
      <div class="node-id${{s.boot?' dim':''}}">${{initials}}</div>
      <div class="shead-main"><div class="node-name">${{s.name}}</div><div class="node-cat">${{s.category||''}}</div></div>
      <div class="shead-stats">
        <div class="hstat"><div class="hv">${{s.boot?'—':eur(s.ca)+' €'}}</div><div class="hl">CA net</div></div>
        <div class="hstat"><div class="hv">${{s.boot?'—':s.orders}}</div><div class="hl">Cmd</div></div>
        <div class="hstat"><div class="hv ${{hot}}">${{s.boot?'—':Math.round(s.returnPct)+'%'}}</div><div class="hl">Retour</div></div>
      </div>
      <div class="chev">▶</div>
    </div>
    <div class="sbody"><div class="sbody-inner">
      ${{s.boot?'<p style="padding:16px 0;color:var(--txt-dim);font-family:Share Tech Mono;font-size:12px">// Nœud en initialisation — aucune vente à ce jour.</p>':`
      <div class="dgrid">
        <div>
          <div class="dcard-t">Évolution mensuelle · CA €</div>
          <div class="mini-chart"><canvas id="mc${{i}}"></canvas></div>
          <div class="dcard-t" style="margin-top:22px">Décomposition brut → net</div>
          <div class="flow">
            <div class="frow"><span class="fl">Brut</span><div class="fbar-wrap"><div class="fbar gr" style="width:100%"></div></div><span class="fval">${{eur(s.gross)}} €</span></div>
            <div class="frow"><span class="fl">Remises</span><div class="fbar-wrap"><div class="fbar am" style="width:${{s.gross?(s.discounts/s.gross*100):0}}%"></div></div><span class="fval">−${{eur(s.discounts)}} €</span></div>
            <div class="frow"><span class="fl">Retours</span><div class="fbar-wrap"><div class="fbar rd" style="width:${{s.gross?(s.returns/s.gross*100):0}}%"></div></div><span class="fval">−${{eur(s.returns)}} €</span></div>
            <div class="frow"><span class="fl">CA net</span><div class="fbar-wrap"><div class="fbar nt" style="width:${{s.gross?(s.ca/s.gross*100):0}}%"></div></div><span class="fval">${{eur(s.ca)}} €</span></div>
          </div>
        </div>
        <div>
          <div class="dcard-t">Top produits · ventes brutes</div>
          <div class="plist">${{s.products.map(p=>`<div class="prow"><span class="pn">${{p[0]}}</span><span class="pbar" style="width:${{Math.max(8,p[1]/pmax*90)}}px"></span><span class="pv">${{eur(p[1])}} €</span></div>`).join('')}}</div>
          <div style="margin-top:20px"><div class="hl" style="font-family:Share Tech Mono;font-size:9px;color:var(--txt-dim);text-transform:uppercase">Panier moyen</div><div style="font-family:Orbitron;font-size:20px;color:var(--cyan);margin-top:3px">${{eur(s.aov)}} €</div></div>
        </div>
      </div>`}}
    </div></div>`;
  list.appendChild(node);
}});

const charts={{}};
function renderMini(i){{
  if(charts[i])return;
  const s=stores[i],el=document.getElementById('mc'+i);if(!el)return;
  charts[i]=new Chart(el,{{type:'bar',data:{{labels:M.slice(0,s.monthly.length),datasets:[{{data:s.monthly.map(v=>Math.round(v)),borderColor:CY,borderWidth:1,borderRadius:2,barPercentage:.6,backgroundColor:c=>c.raw<0?'rgba(255,90,77,.6)':'rgba(63,240,255,.55)',hoverBackgroundColor:AM}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>eur(c.raw)+' €'}}}}}},scales:{{x:{{grid:{{display:false}},ticks:{{font:{{size:9,family:'Share Tech Mono'}},color:TXD}}}},y:{{grid:{{color:GRID}},border:{{display:false}},ticks:{{font:{{size:9,family:'Share Tech Mono'}},color:TXD,callback:v=>eur(v)}}}}}}}}}});
}}
document.querySelectorAll('.shead').forEach(h=>h.addEventListener('click',()=>{{
  const n=h.parentElement,b=n.querySelector('.sbody'),i=+h.dataset.i;
  if(n.classList.toggle('open')){{b.style.maxHeight=b.scrollHeight+'px';renderMini(i);setTimeout(()=>{{if(n.classList.contains('open'))b.style.maxHeight='2000px'}},460);}}
  else b.style.maxHeight='0';
}}));

const monthlyAll=[];
stores.forEach(s=>s.monthly.forEach((v,mi)=>{{monthlyAll[mi]=(monthlyAll[mi]||0)+v}}));
new Chart(document.getElementById('monthlyAll'),{{type:'bar',data:{{labels:M.slice(0,monthlyAll.length),datasets:[{{data:monthlyAll.map(v=>Math.round(v)),borderColor:CY,borderWidth:1,borderRadius:2,barPercentage:.62,backgroundColor:c=>{{const{{ctx,chartArea}}=c.chart;if(!chartArea)return CY;const g=ctx.createLinearGradient(0,chartArea.top,0,chartArea.bottom);g.addColorStop(0,'rgba(63,240,255,.85)');g.addColorStop(1,'rgba(63,240,255,.12)');return g;}},hoverBackgroundColor:AM}}]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:c=>eur(c.raw)+' €'}}}}}},scales:{{x:{{grid:{{display:false}},border:{{color:'rgba(63,240,255,.25)'}},ticks:{{font:{{size:11,family:'Share Tech Mono'}},color:TXD}}}},y:{{grid:{{color:GRID}},border:{{display:false}},ticks:{{font:{{size:10,family:'Share Tech Mono'}},color:TXD,callback:v=>eur(v)}}}}}}}}}});
</script>
</body>
</html>"""


def main():
    here = os.path.dirname(__file__)
    data_path = os.path.abspath(os.path.join(here, "..", "public", "data.json"))
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    html = build(data)
    out = os.path.abspath(os.path.join(here, "..", "public", "index.html"))
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Dashboard généré: {out}")


if __name__ == "__main__":
    main()
