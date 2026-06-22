/* =================================================================
   TESLA FUTURE LAB — animation wiring (defensive, multi-library)
   GSAP+ScrollTrigger · Lenis · tsParticles · anime.js · CountUp ·
   Typed · ApexCharts · AOS · Splitting · custom canvas
   ================================================================= */
(function(){
"use strict";
var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var has = function(n){ return typeof window[n] !== 'undefined'; };

/* ---------- GSAP / ScrollTrigger / Lenis ---------- */
if(has('gsap') && has('ScrollTrigger')) gsap.registerPlugin(ScrollTrigger);
var lenis = null;
if(has('Lenis') && !reduce){
  lenis = new Lenis({ duration:1.1, smoothWheel:true, wheelMultiplier:1 });
  if(has('ScrollTrigger')) lenis.on('scroll', ScrollTrigger.update);
  if(has('gsap')){ gsap.ticker.add(function(t){ lenis.raf(t*1000); }); gsap.ticker.lagSmoothing(0); }
  else { (function raf(t){ lenis.raf(t); requestAnimationFrame(raf); })(); }
}
function scrollToEl(target){
  var el = document.querySelector(target); if(!el) return;
  if(lenis) lenis.scrollTo(el, { offset:-70 });
  else el.scrollIntoView({ behavior: reduce?'auto':'smooth' });
}

/* ---------- NAV ---------- */
var nav = document.getElementById('nav');
function onScroll(){ nav.classList.toggle('scrolled', window.scrollY > 30); }
onScroll(); window.addEventListener('scroll', onScroll, {passive:true});

document.querySelectorAll('a[href^="#"]').forEach(function(a){
  a.addEventListener('click', function(e){
    var href = a.getAttribute('href');
    if(href.length>1){ e.preventDefault(); scrollToEl(href); closeMenu(); }
  });
});

/* active link via IntersectionObserver */
var links = {}, navLinks = document.querySelectorAll('.nav__menu a');
navLinks.forEach(function(a){ var id=a.getAttribute('href').slice(1); if(document.getElementById(id)) links[id]=a; });
var spy = new IntersectionObserver(function(es){
  es.forEach(function(e){ if(e.isIntersecting){ var a=links[e.target.id];
    if(a){ navLinks.forEach(function(l){l.classList.remove('active');}); a.classList.add('active'); } } });
}, {rootMargin:'-45% 0px -50% 0px'});
Object.keys(links).forEach(function(id){ spy.observe(document.getElementById(id)); });

/* burger + mobile menu */
var burger=document.getElementById('burger'), mmenu=document.getElementById('mmenu');
function closeMenu(){ mmenu.classList.remove('open'); mmenu.setAttribute('aria-hidden','true');
  burger.setAttribute('aria-expanded','false'); document.body.style.overflow=''; }
burger.addEventListener('click', function(){
  var open=!mmenu.classList.contains('open');
  mmenu.classList.toggle('open',open); mmenu.setAttribute('aria-hidden',String(!open));
  burger.setAttribute('aria-expanded',String(open)); document.body.style.overflow=open?'hidden':'';
});
document.querySelectorAll('[data-mm]').forEach(function(a){ a.addEventListener('click', closeMenu); });
document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeMenu(); });

/* lang toast */
var toast=document.getElementById('toast'), tt;
document.getElementById('lang').addEventListener('click', function(){
  toast.textContent='Английская и сербская версии скоро. Молния не ждёт перевода.';
  toast.classList.add('show'); clearTimeout(tt); tt=setTimeout(function(){toast.classList.remove('show');},2600);
});

/* ---------- progress bar ---------- */
var progress=document.getElementById('progress');
function onProg(){ var h=document.documentElement; var max=h.scrollHeight-h.clientHeight;
  progress.style.width=(max>0?(h.scrollTop/max*100):0)+'%'; }
onProg(); window.addEventListener('scroll', onProg, {passive:true});

/* ---------- cursor glow (pointer devices) ---------- */
var cursor=document.getElementById('cursor');
if(matchMedia('(pointer:fine)').matches && !reduce){
  window.addEventListener('pointermove', function(e){
    cursor.style.transform='translate('+e.clientX+'px,'+e.clientY+'px) translate(-50%,-50%)';
  });
  document.querySelectorAll('a,button,.glass,.idea,.acard').forEach(function(el){
    el.addEventListener('pointerenter', function(){cursor.classList.add('big');});
    el.addEventListener('pointerleave', function(){cursor.classList.remove('big');});
  });
} else { cursor.style.display='none'; }

/* ---------- AOS ---------- */
if(has('AOS')) AOS.init({ duration:800, easing:'ease-out-cubic', once:true, offset:90, disable:reduce });

/* ---------- Splitting (white headings) + GSAP char reveal ---------- */
if(has('Splitting') && has('gsap') && !reduce){
  var whites=document.querySelectorAll('#ideas h2, #coil h2, #city h2');
  if(whites.length){
    try{ Splitting({ target:whites, by:'chars' }); }catch(e){}
    whites.forEach(function(h){
      var chars=h.querySelectorAll('.char'); if(!chars.length) return;
      gsap.from(chars,{ yPercent:110, opacity:0, stagger:0.02, duration:0.6, ease:'power3.out',
        scrollTrigger:{ trigger:h, start:'top 85%' } });
    });
  }
}
/* metal/gradient headings: whole-element reveal (keeps gradient intact) */
if(has('gsap') && !reduce){
  document.querySelectorAll('[data-splitting]').forEach(function(el){
    gsap.from(el,{ yPercent:10, opacity:0, duration:1, ease:'power3.out',
      scrollTrigger:{ trigger:el, start:'top 88%' } });
  });
}

/* ---------- tsParticles network background ---------- */
if(has('tsParticles') && !reduce){
  tsParticles.load({ id:'tsparticles', options:{
    fpsLimit:60, detectRetina:true, background:{ color:'transparent' },
    particles:{
      number:{ value:46, density:{ enable:true, area:900 } },
      color:{ value:['#4f8dff','#9a7cff','#46d6ff'] },
      links:{ enable:true, distance:140, color:'#6a8fe0', opacity:0.16, width:1 },
      move:{ enable:true, speed:0.45, outModes:{ default:'out' } },
      opacity:{ value:{ min:0.15, max:0.5 } },
      size:{ value:{ min:1, max:2.4 } }
    },
    interactivity:{ events:{ onHover:{ enable:true, mode:'grab' } },
      modes:{ grab:{ distance:160, links:{ opacity:0.35 } } } }
  }}).catch(function(){});
}

/* ---------- CountUp on view ---------- */
function fmt(v,d){ var s=(d?v.toFixed(d):Math.round(v).toString());
  return s.replace(/\B(?=(\d{3})+(?!\d))/g,' '); }
function runCount(el){
  var end=parseFloat(el.dataset.count), dec=parseInt(el.dataset.decimals||'0',10);
  if(reduce){ el.textContent=fmt(end,dec); return; }
  if(has('countUp') && window.countUp.CountUp){
    var c=new countUp.CountUp(el,end,{ duration:2, separator:' ', decimalPlaces:dec });
    if(!c.error){ c.start(); return; }
  }
  el.textContent=fmt(end,dec);
}
var countIO=new IntersectionObserver(function(es){ es.forEach(function(e){
  if(e.isIntersecting){ runCount(e.target); countIO.unobserve(e.target); } }); }, {threshold:0.4});
document.querySelectorAll('.count').forEach(function(el){ countIO.observe(el); });

/* ---------- Typed.js ---------- */
if(has('Typed') && document.getElementById('typed')){
  new Typed('#typed', { strings:['невозможно','безумие','фантастика','гениально'],
    typeSpeed:65, backSpeed:32, backDelay:1500, startDelay:400, loop:true, smartBackspace:true });
}

/* ---------- ApexCharts (deterministic series) ---------- */
function rng(seed){ var s=seed%2147483647; if(s<=0)s+=2147483646;
  return function(){ s=(s*16807)%2147483647; return (s-1)/2147483646; }; }
function series(seed,n,up){ var r=rng(seed*7+11), a=[], v=24+r()*22;
  for(var i=0;i<n;i++){ v+=(r()-(up?0.32:0.5))*16; v=Math.max(8,Math.min(96,v)); a.push(Math.round(v)); } return a; }
function drawChart(el){
  if(!has('ApexCharts')) return;
  var color=el.dataset.color||'#4f8dff', seed=parseInt(el.dataset.seed||'1',10),
      bar=el.dataset.type==='bar', h=el.clientHeight||64, n=bar?9:14;
  var opts={
    chart:{ type:bar?'bar':'area', height:h, sparkline:{enabled:true},
      animations:{ enabled:!reduce, speed:1100, easing:'easeinout' } },
    series:[{ data: bar? series(seed,n,true) : series(seed,n,true) }],
    stroke:{ curve:'smooth', width:2 }, colors:[color],
    fill: bar ? { opacity:0.85 } :
      { type:'gradient', gradient:{ shadeIntensity:1, opacityFrom:0.45, opacityTo:0.02, stops:[0,100] } },
    plotOptions: bar ? { bar:{ columnWidth:'52%', borderRadius:2 } } : {},
    tooltip:{ enabled:false }, dataLabels:{ enabled:false },
    grid:{ show:false, padding:{top:0,right:0,bottom:0,left:0} }
  };
  try{ new ApexCharts(el,opts).render(); }catch(e){}
}
// render charts when near viewport (perf)
var chartIO=new IntersectionObserver(function(es){ es.forEach(function(e){
  if(e.isIntersecting){ drawChart(e.target); chartIO.unobserve(e.target); } }); }, {rootMargin:'120px'});
document.querySelectorAll('[data-chart],[data-spark]').forEach(function(el){ chartIO.observe(el); });

/* ---------- Timeline fill (GSAP) ---------- */
(function(){
  var fill=document.getElementById('tlFill'), track=document.getElementById('tlTrack');
  if(!fill||!track) return;
  if(reduce){ fill.style.width='100%'; return; }
  if(has('gsap')) gsap.to(fill,{ width:'100%', ease:'none',
    scrollTrigger:{ trigger:track, start:'top 80%', end:'bottom 60%', scrub:true } });
  else fill.style.width='100%';
})();

/* ---------- Parallax (GSAP) ---------- */
if(has('gsap') && !reduce){
  document.querySelectorAll('[data-parallax]').forEach(function(el){
    var amt=parseFloat(el.dataset.parallax)||20;
    gsap.fromTo(el,{ y:-amt },{ y:amt, ease:'none',
      scrollTrigger:{ trigger:el.closest('section'), start:'top bottom', end:'bottom top', scrub:true } });
  });
  document.querySelectorAll('[data-parallax-x]').forEach(function(el){
    var amt=parseFloat(el.dataset.parallaxX)||30, dir=amt>0?1:-1;
    gsap.fromTo(el,{ xPercent:-6*dir },{ xPercent:6*dir, ease:'none',
      scrollTrigger:{ trigger:el.closest('section'), start:'top bottom', end:'bottom top', scrub:true } });
  });
}

/* ---------- Coil explode on scroll (GSAP) ---------- */
(function(){
  var stage=document.getElementById('coilStage'); if(!stage) return;
  var parts=stage.querySelectorAll('.part'); if(!parts.length) return;
  if(reduce || !has('gsap')) return;
  parts.forEach(function(p){
    gsap.fromTo(p,{ y:0 },{ y:parseFloat(p.dataset.explode)||0, ease:'none',
      scrollTrigger:{ trigger:stage, start:'top 75%', end:'bottom 35%', scrub:true } });
  });
})();

/* ---------- Magnetic buttons (GSAP) ---------- */
if(has('gsap') && matchMedia('(pointer:fine)').matches && !reduce){
  document.querySelectorAll('.btn').forEach(function(b){
    b.addEventListener('pointermove', function(e){ var r=b.getBoundingClientRect();
      gsap.to(b,{ x:(e.clientX-r.left-r.width/2)*0.25, y:(e.clientY-r.top-r.height/2)*0.3, duration:0.4 }); });
    b.addEventListener('pointerleave', function(){ gsap.to(b,{ x:0, y:0, duration:0.5, ease:'elastic.out(1,0.4)' }); });
  });
}

/* =================================================================
   CANVAS ENGINE — register animations, run only when visible
   ================================================================= */
var scenes=[];
function register(canvas, draw, init){
  if(!canvas) return;
  var ctx=canvas.getContext('2d'), dpr=Math.min(window.devicePixelRatio||1,2), W=0,H=0, t=0, active=false, state={};
  function size(){ var r=canvas.getBoundingClientRect(); W=r.width; H=r.height;
    canvas.width=Math.max(1,Math.floor(W*dpr)); canvas.height=Math.max(1,Math.floor(H*dpr));
    ctx.setTransform(dpr,0,0,dpr,0,0); if(init) init(ctx,W,H,state); }
  size(); window.addEventListener('resize', size);
  var io=new IntersectionObserver(function(es){ es.forEach(function(e){ active=e.isIntersecting; }); }, {threshold:0.02});
  io.observe(canvas);
  scenes.push({ tick:function(){ if(!active) return; t+=1; ctx.clearRect(0,0,W,H); draw(ctx,W,H,t,state); },
    get W(){return W;}, get H(){return H;}, still:function(){ ctx.clearRect(0,0,W,H); draw(ctx,W,H,1,state); } });
}
function loop(){ for(var i=0;i<scenes.length;i++) scenes[i].tick(); requestAnimationFrame(loop); }
if(!reduce) requestAnimationFrame(loop);

/* lightning bolt path */
function bolt(ctx,x1,y1,x2,y2,disp,detail){
  var pts=[{x:x1,y:y1},{x:x2,y:y2}];
  for(var d=0; d<detail; d++){ var np=[]; for(var i=0;i<pts.length-1;i++){ np.push(pts[i]);
    np.push({ x:(pts[i].x+pts[i+1].x)/2+(Math.random()-0.5)*disp, y:(pts[i].y+pts[i+1].y)/2+(Math.random()-0.5)*disp }); }
    np.push(pts[pts.length-1]); pts=np; disp*=0.55; }
  ctx.beginPath(); ctx.moveTo(pts[0].x,pts[0].y);
  for(var k=1;k<pts.length;k++) ctx.lineTo(pts[k].x,pts[k].y); ctx.stroke();
}

/* --- coil arcs --- */
function coilScene(id){
  var c=document.getElementById(id); register(c, function(ctx,W,H,t,s){
    var cx=W*0.5, top=H*0.18;
    if(t-s.last>26+Math.random()*30){ s.last=t; s.bolts.push({life:1,
      x2:cx+(Math.random()-0.5)*W*0.7, y2:top+(Math.random()*0.5+0.1)*H }); if(s.bolts.length>4)s.bolts.shift(); }
    for(var i=s.bolts.length-1;i>=0;i--){ var b=s.bolts[i];
      ctx.strokeStyle='rgba(150,190,255,'+(0.12*b.life)+')'; ctx.lineWidth=5; bolt(ctx,cx,top,b.x2,b.y2,W*0.18,5);
      ctx.strokeStyle='rgba(220,235,255,'+(0.7*b.life)+')'; ctx.lineWidth=1.3; bolt(ctx,cx,top,b.x2,b.y2,W*0.18,5);
      b.life-=0.05; if(b.life<=0) s.bolts.splice(i,1); }
  }, function(ctx,W,H,s){ s.bolts=[]; s.last=0; });
}
coilScene('coilCanvas'); coilScene('impCanvas');

/* --- influence map: node network --- */
register(document.getElementById('mapCanvas'), function(ctx,W,H,t,s){
  ctx.lineWidth=1;
  for(var i=0;i<s.n.length;i++){ for(var j=i+1;j<s.n.length;j++){ var a=s.n[i],b=s.n[j];
    var dx=a.x*W-b.x*W, dy=a.y*H-b.y*H, d=Math.hypot(dx,dy);
    if(d<W*0.22){ ctx.strokeStyle='rgba(110,150,230,'+(0.18*(1-d/(W*0.22)))+')';
      ctx.beginPath(); ctx.moveTo(a.x*W,a.y*H); ctx.lineTo(b.x*W,b.y*H); ctx.stroke(); } } }
  for(var k=0;k<s.n.length;k++){ var p=s.n[k], pulse=0.5+0.5*Math.sin(t*0.04+p.ph);
    var col=p.c; ctx.fillStyle=col;
    ctx.shadowBlur=10*pulse+4; ctx.shadowColor=col;
    ctx.beginPath(); ctx.arc(p.x*W,p.y*H,1.6+pulse*1.6,0,7); ctx.fill(); ctx.shadowBlur=0; }
}, function(ctx,W,H,s){ s.n=[]; var cols=['#4f8dff','#9a7cff','#46d6ff'];
  for(var i=0;i<46;i++) s.n.push({ x:Math.random(), y:Math.random(), ph:Math.random()*6, c:cols[i%3] }); });

/* --- analytics wave --- */
register(document.getElementById('waveCanvas'), function(ctx,W,H,t,s){
  var mid=H*0.5;
  for(var w=0;w<3;w++){ var col=['rgba(79,141,255,','rgba(154,124,255,','rgba(70,210,255,'][w];
    ctx.strokeStyle=col+(0.5-w*0.12)+')'; ctx.lineWidth=2-w*0.4; ctx.beginPath();
    for(var x=0;x<=W;x+=6){ var y=mid + Math.sin(x*0.014 + t*0.03 + w*1.1)*(H*0.22)*Math.sin(x*0.003+t*0.01)
        + Math.sin(x*0.05+t*0.05+w)*8;
      x===0?ctx.moveTo(x,y):ctx.lineTo(x,y); } ctx.stroke(); }
  // sparkle dots
  for(var i=0;i<s.d.length;i++){ var p=s.d[i]; var yy=mid+Math.sin(p.x*0.014+t*0.03)*(H*0.22)*Math.sin(p.x*0.003+t*0.01);
    var pl=0.5+0.5*Math.sin(t*0.06+p.ph); ctx.fillStyle='rgba(200,225,255,'+pl+')';
    ctx.shadowBlur=8; ctx.shadowColor='#6aa6ff'; ctx.beginPath(); ctx.arc(p.x,yy,1.4+pl,0,7); ctx.fill(); ctx.shadowBlur=0; }
}, function(ctx,W,H,s){ s.d=[]; for(var i=0;i<26;i++) s.d.push({ x:Math.random()*W, ph:Math.random()*6 }); });

/* --- lab card vizes --- */
document.querySelectorAll('.labViz').forEach(function(c){
  var kind=c.dataset.viz;
  register(c, function(ctx,W,H,t,s){
    if(kind==='coil'){ var cx=W*0.5, top=H*0.3;
      if(t-s.last>30+Math.random()*30){ s.last=t; s.b.push({life:1,x2:cx+(Math.random()-0.5)*W*0.6,y2:top+Math.random()*H*0.5}); if(s.b.length>3)s.b.shift(); }
      ctx.fillStyle='#9fb0d0'; ctx.fillRect(cx-3,top,6,H*0.5);
      for(var i=s.b.length-1;i>=0;i--){ var b=s.b[i]; ctx.strokeStyle='rgba(170,200,255,'+(0.7*b.life)+')'; ctx.lineWidth=1.2; bolt(ctx,cx,top,b.x2,b.y2,W*0.16,4); b.life-=0.05; if(b.life<=0)s.b.splice(i,1); } }
    else if(kind==='globe'){ var cx=W*0.5, cy=H*0.5, r=Math.min(W,H)*0.32;
      ctx.strokeStyle='rgba(110,150,230,0.5)'; ctx.lineWidth=1;
      ctx.beginPath(); ctx.arc(cx,cy,r,0,7); ctx.stroke();
      for(var m=0;m<4;m++){ var rx=r*Math.abs(Math.cos(t*0.01+m*0.8)); ctx.beginPath(); ctx.ellipse(cx,cy,rx,r,0,0,7); ctx.stroke(); }
      ctx.beginPath(); ctx.ellipse(cx,cy,r,r*0.34,0,0,7); ctx.stroke();
      ctx.fillStyle='#6aa6ff'; for(var k=0;k<5;k++){ var a=t*0.02+k*1.3; ctx.beginPath(); ctx.arc(cx+Math.cos(a)*r, cy+Math.sin(a)*r*0.34,2,0,7); ctx.fill(); } }
    else { // city skyline pulse
      ctx.fillStyle='rgba(79,141,255,0.5)';
      for(var i2=0;i2<s.bld.length;i2++){ var bd=s.bld[i2]; var hh=bd.h*(0.85+0.15*Math.sin(t*0.05+bd.ph));
        ctx.globalAlpha=0.5+0.4*Math.sin(t*0.05+bd.ph); ctx.fillRect(bd.x, H-hh, bd.w, hh); }
      ctx.globalAlpha=1; }
  }, function(ctx,W,H,s){ s.b=[]; s.last=0; s.bld=[]; for(var i=0;i<14;i++) s.bld.push({x:i*(W/14)+2,w:W/14-4,h:H*(0.2+Math.random()*0.6),ph:Math.random()*6}); });
});

/* =================================================================
   CITY isometric SVG (build + anime.js draw)
   ================================================================= */
(function(){
  var svg=document.getElementById('citySvg'); if(!svg) return;
  var slabs=svg.querySelector('#citySlabs'), blds=svg.querySelector('#cityBuildings'), nodes=svg.querySelector('#cityNodes');
  var NS='http://www.w3.org/2000/svg';
  function el(n,attrs){ var e=document.createElementNS(NS,n); for(var k in attrs) e.setAttribute(k,attrs[k]); return e; }
  // 3 stacked iso slabs
  var cx=300, top=120, w=210, hh=110, depth=64, gap=92;
  function slab(oy,fillTop){
    var p1=cx, q1=oy; // build a diamond (iso top) + sides
    var dx=w, dy=hh;
    var top=[ [cx, oy-dy/2],[cx+dx, oy],[cx, oy+dy/2],[cx-dx, oy] ];
    var poly=el('polygon',{ points:top.map(function(p){return p.join(',');}).join(' '),
      fill:fillTop, stroke:'rgba(120,160,255,0.35)','stroke-width':1 });
    slabs.appendChild(poly);
    // left + right faces
    var lf=el('polygon',{ points:[ [cx-dx,oy],[cx,oy+dy/2],[cx,oy+dy/2+depth],[cx-dx,oy+depth] ].map(function(p){return p.join(',');}).join(' '),
      fill:'url(#slabSide)', stroke:'rgba(120,160,255,0.18)','stroke-width':1 });
    var rf=el('polygon',{ points:[ [cx+dx,oy],[cx,oy+dy/2],[cx,oy+dy/2+depth],[cx+dx,oy+depth] ].map(function(p){return p.join(',');}).join(' '),
      fill:'#070c1a', stroke:'rgba(120,160,255,0.12)','stroke-width':1 });
    slabs.appendChild(lf); slabs.appendChild(rf);
  }
  slab(top, 'url(#slabTop)'); slab(top+gap, '#0c1530'); slab(top+gap*2, '#0a1126');
  // buildings on top slab
  for(var i=0;i<10;i++){ var bx=cx+(Math.random()-0.5)*w*1.1, by=top+(Math.random()-0.5)*hh*0.7;
    var bw=10+Math.random()*16, bh=18+Math.random()*64;
    var b=el('polygon',{ points:[ [bx,by-bh],[bx+bw,by-bh+bw*0.5],[bx+bw,by+bw*0.5],[bx,by],[bx-bw,by+bw*0.5*0],[bx-bw,by-bh+bw*0.5*0] ]
      .map(function(p){return p.join(',');}).join(' '), fill:'url(#bld)', stroke:'rgba(120,170,255,0.4)','stroke-width':0.8, opacity:0.9 });
    // simpler box: front + top
    var front=el('polygon',{ points:[ [bx-bw,by-bh],[bx,by-bh+bw*0.5],[bx,by+bw*0.5],[bx-bw,by] ].map(function(p){return p.join(',');}).join(' '),
      fill:'#16224a', stroke:'rgba(120,170,255,0.3)','stroke-width':0.7 });
    var side=el('polygon',{ points:[ [bx,by-bh+bw*0.5],[bx+bw,by-bh],[bx+bw,by],[bx,by+bw*0.5] ].map(function(p){return p.join(',');}).join(' '),
      fill:'#0e1733', stroke:'rgba(120,170,255,0.22)','stroke-width':0.7 });
    blds.appendChild(side); blds.appendChild(front); }
  // glowing nodes (7) anchored near layers, lines to right margin
  var anchors=[ [cx+30,top-30],[cx-90,top-6],[cx+120,top+50],[cx-120,top+gap+10],[cx+130,top+gap+50],[cx-40,top+gap*2-6],[cx+150,top+gap*2+30] ];
  anchors.forEach(function(a,idx){
    var line=el('path',{ d:'M'+a[0]+','+a[1]+' L'+(560)+','+(60+idx*64), fill:'none',
      stroke:'rgba(130,165,255,0.5)','stroke-width':1, 'stroke-dasharray':'3 4', class:'cityLine' });
    nodes.appendChild(line);
    var halo=el('circle',{ cx:a[0], cy:a[1], r:9, fill:'rgba(79,141,255,0.18)', class:'cityHalo' });
    var dot=el('circle',{ cx:a[0], cy:a[1], r:4, fill:'#6aa6ff', class:'cityDot' });
    var num=el('text',{ x:a[0], y:a[1]+3.2, 'text-anchor':'middle', 'font-size':'7', fill:'#001', 'font-family':'Manrope', 'font-weight':'800' });
    num.textContent=(idx+1); nodes.appendChild(halo); nodes.appendChild(dot); nodes.appendChild(num);
  });
  // animate with anime.js when in view
  var done=false;
  new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting && !done){ done=true;
    if(has('anime') && !reduce){
      anime({ targets:'.cityLine', strokeDashoffset:[anime.setDashoffset,0], easing:'easeInOutSine', duration:900, delay:anime.stagger(90) });
      anime({ targets:'.cityHalo', r:[2,9], opacity:[0,0.18], easing:'easeOutQuad', duration:700, delay:anime.stagger(90,{start:300}) });
      anime({ targets:'.cityDot', scale:[0,1], easing:'easeOutBack', duration:600, delay:anime.stagger(90,{start:300}) });
      anime({ targets:'.cityHalo', r:[8,12], opacity:[0.22,0.06], direction:'alternate', loop:true, easing:'easeInOutSine', duration:1500, delay:anime.stagger(120) });
    }
  } }); }, {threshold:0.2}).observe(svg);
})();

/* refresh ScrollTrigger after load (fonts/charts shift layout) */
window.addEventListener('load', function(){ if(has('ScrollTrigger')) setTimeout(function(){ScrollTrigger.refresh();},300); });
})();
