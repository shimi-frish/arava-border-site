/* Israel–Jordan Arava project viewer. Plain JS + Leaflet, works from file:// and from any static host. */
(function(){
'use strict';
var CFG = window.__CFG || {tree:[],raster:{},vector:{}};
var FILES = window.__FILES || {name:'root',dirs:[],files:[]};
var $ = function(s,el){return (el||document).querySelector(s);};
var $$ = function(s,el){return Array.prototype.slice.call((el||document).querySelectorAll(s));};
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function fmtSize(b){if(b==null)return '';if(b<1024)return b+' B';if(b<1048576)return (b/1024).toFixed(0)+' KB';if(b<1073741824)return (b/1048576).toFixed(1)+' MB';return (b/1073741824).toFixed(2)+' GB';}
function fmtDate(t){if(!t)return '';var d=new Date(t*1000);return d.toLocaleDateString('he-IL');}
function enc(p){return p.split('/').map(encodeURIComponent).join('/');}

/* ---------------- tabs ---------------- */
var tabInit={};
function showTab(name){
  $$('.tabs button').forEach(function(b){b.classList.toggle('on',b.dataset.tab===name);});
  $$('.tab').forEach(function(t){t.classList.toggle('on',t.id==='tab-'+name);});
  if(name==='map' && map) setTimeout(function(){map.invalidateSize();},50);
  if(!tabInit[name]){tabInit[name]=1; if(name==='docs')initDocs(); if(name==='files')initFiles();}
  try{history.replaceState(null,'','#'+name);}catch(e){}
}
$$('.tabs button').forEach(function(b){b.onclick=function(){showTab(b.dataset.tab);};});

/* ---------------- map ---------------- */
var map = L.map('map',{zoomControl:true,preferCanvas:true,minZoom:6,maxZoom:18});
map.fitBounds([[29.45,34.8],[31.35,35.7]]);
L.control.scale({imperial:false,position:'bottomleft'}).addTo(map);
var bases={
  osm:L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap'}),
  sat:L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:18,attribution:'Esri World Imagery'}),
  topo:L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',{maxZoom:17,attribution:'© OpenTopoMap, © OpenStreetMap'}),
  light:L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{maxZoom:19,attribution:'© OpenStreetMap, © CARTO'})
};
var curBase=null;
function setBase(k){ if(curBase){map.removeLayer(curBase);curBase=null;} if(bases[k]){curBase=bases[k].addTo(map);} }
$('#basemap').onchange=function(){setBase(this.value);};

/* ITM coordinates */
var itm=null;
if(window.proj4){ proj4.defs('EPSG:2039','+proj=tmerc +lat_0=31.7343936111111 +lon_0=35.2045169444444 +k=1.0000067 +x_0=219529.584 +y_0=626907.39 +ellps=GRS80 +towgs84=-24.0024,-17.1032,-17.8444,-0.33077,-1.85269,1.66969,5.4248 +units=m +no_defs'); itm=proj4('EPSG:4326','EPSG:2039'); }
map.on('mousemove',function(e){
  var s='WGS84 '+e.latlng.lat.toFixed(5)+', '+e.latlng.lng.toFixed(5);
  if(itm){var p=itm.forward([e.latlng.lng,e.latlng.lat]); s+='  |  ITM '+Math.round(p[0])+' / '+Math.round(p[1]);}
  $('#coords').textContent=s;
});

/* flatten tree */
var LAYERS={}, ORDER=[], GROUPS=[];
(function walk(items,parent){
  items.forEach(function(it){
    if(it.g!==undefined){ it.parent=parent; it.isGroup=true; it.def=it.on; GROUPS.push(it); walk(it.c,it); }
    else { it.parent=parent; it.def=it.on; LAYERS[it.id]=it; ORDER.push(it); }
  });
})(CFG.tree,null);
// base map layer from QGIS: drive the basemap select instead of an overlay
ORDER.forEach(function(l){ if(l.type==='xyz'){ l.isBase=true; } });

/* panes: top of the QGIS tree drawn on top */
var N=ORDER.length;
ORDER.forEach(function(l,i){ var p=map.createPane('p_'+l.id); p.style.zIndex=String(300+(N-i)); });

function wpx(w){ if(w==null) return 1.5; return Math.max(0.6,Math.min(6,w*0.6)); }
function dashOf(d){ return d==='dash'?'6 4':d==='dot'?'1 4':d==='dash dot'?'6 3 1 3':d==='markerline'?'2 6':null; }
function styleOf(s){
  if(!s) return {color:'#3388ff',weight:1.5};
  var o={};
  if(s.k==='fill'){ o.fillColor=s.fill||'#000'; o.fillOpacity=s.fill?(s.fo==null?1:s.fo):0; o.fill=!!s.fill && o.fillOpacity>0;
    if(s.w>0&&s.stroke){o.stroke=true;o.color=s.stroke;o.opacity=s.so==null?1:s.so;o.weight=wpx(s.w);} else {o.stroke=false;} }
  else if(s.k==='line'){ o.color=s.stroke||'#333'; o.opacity=s.so==null?1:s.so; o.weight=wpx(s.w); o.fill=false; if(s.dash==='markerline'){o.weight=4;o.lineCap='butt';} }
  else { o.radius=Math.max(2.5,Math.min(9,(s.size||6)*0.45)); o.fillColor=s.fill||'#888'; o.fillOpacity=s.fo==null?1:s.fo; o.color=s.stroke||'#222'; o.weight=1; o.opacity=s.so==null?1:s.so;
    if(o.fillOpacity===0 && o.opacity===0){o.fillOpacity=0;o.opacity=0;} }
  var d=dashOf(s.dash); if(d) o.dashArray=d;
  return o;
}
function catIndex(l){ if(l._ci) return l._ci; var m={}; (l.cats||[]).forEach(function(c){ m[String(c.v)]=c; }); l._ci=m; return m; }
function featStyle(l,f){
  if(l.cats){ var v=f.properties?f.properties[l.attr]:undefined; var c=catIndex(l)[String(v==null?'':v)] || catIndex(l)['']; if(!c||!c.on) return null; return styleOf(c.s); }
  return styleOf(l.sym);
}
function popupHtml(l,f){
  var p=f.properties||{}, rows='';
  Object.keys(p).forEach(function(k){ var v=p[k]; if(v===null||v===''||k==='fid')return; rows+='<tr><td>'+esc(k)+'</td><td>'+esc(v)+'</td></tr>'; });
  return '<div class="pop"><h4>'+esc(l.name)+'</h4>'+(rows?'<table>'+rows+'</table>':'<span class="muted">אין מאפיינים</span>')+'</div>';
}
var pending={};
window.__V=function(id,gj){ var l=LAYERS[id]; if(!l) return; l.data=gj; var cb=pending[id]; delete pending[id]; if(cb) cb(); };
function loadScript(src,onerr){ var s=document.createElement('script'); s.src=src; s.onerror=onerr; document.body.appendChild(s); }
function buildVector(l){
  var pane='p_'+l.id, rend=L.canvas({pane:pane,padding:0.3,tolerance:4});
  var opac=l.op==null?1:l.op;
  var g=L.geoJSON(l.data,{
    pane:pane,
    filter:function(f){ return !l.cats || featStyle(l,f)!==null; },
    style:function(f){ var s=featStyle(l,f)||{}; s.renderer=rend; s.pane=pane; if(opac<1){ if(s.opacity!=null)s.opacity*=opac; if(s.fillOpacity!=null)s.fillOpacity*=opac;} return s; },
    pointToLayer:function(f,ll){ var s=featStyle(l,f)||{}; s.renderer=rend; s.pane=pane; return L.circleMarker(ll,s); },
    onEachFeature:function(f,lay){
      lay.on('click',function(e){ L.popup({maxWidth:380}).setLatLng(e.latlng).setContent(popupHtml(l,f)).openOn(map); });
      if(l.label && f.properties){ var t=f.properties[l.label.field]; if(t!=null&&t!==''){ lay.bindTooltip(esc(t),{permanent:true,direction:'top',className:'lbl',pane:'tooltipPane',offset:[0,-4]}); } }
    }
  });
  return g;
}
function buildRaster(l){
  var m=CFG.raster[l.id]; if(!m||!m.file) return null;
  return L.imageOverlay('data/raster/'+m.file,m.bounds,{pane:'p_'+l.id,opacity:l.op==null?1:l.op,interactive:false});
}
function effOn(it){ if(!it.on) return false; var p=it.parent; while(p){ if(!p.on) return false; p=p.parent; } return true; }
function ensureLayer(l,cb){
  if(l.leaf){cb();return;}
  if(l.type==='raster'){ l.leaf=buildRaster(l); cb(); return; }
  if(l.type==='vector'){
    var vm=CFG.vector[l.id]; if(!vm||vm.error){ l.leaf=null; cb(); return; }
    if(l.data){ l.leaf=buildVector(l); cb(); return; }
    if(pending[l.id]){ var old=pending[l.id]; pending[l.id]=function(){old();}; return; }
    $('#loading').hidden=false;
    pending[l.id]=function(){ $('#loading').hidden=true; l.leaf=buildVector(l); cb(); };
    loadScript('data/vector/'+l.id+'.js',function(){ $('#loading').hidden=true; delete pending[l.id]; alert('לא ניתן לטעון את השכבה'); });
    return;
  }
  cb();
}
function refresh(){
  ORDER.forEach(function(l){
    if(l.isBase) return;
    var want=effOn(l);
    if(want){ ensureLayer(l,function(){ if(effOn(l) && l.leaf && !map.hasLayer(l.leaf)) l.leaf.addTo(map); }); }
    else if(l.leaf && map.hasLayer(l.leaf)) map.removeLayer(l.leaf);
  });
  $$('#tree [data-id]').forEach(function(row){ var it=row._it; row.classList.toggle('dim',!effOn(it)&&it.on); });
}
function zoomTo(l){
  var b=null;
  if(l.type==='raster' && CFG.raster[l.id] && CFG.raster[l.id].bounds) b=L.latLngBounds(CFG.raster[l.id].bounds);
  else if(l.type==='vector' && CFG.vector[l.id] && CFG.vector[l.id].bounds){ var x=CFG.vector[l.id].bounds; b=L.latLngBounds([[x[1],x[0]],[x[3],x[2]]]); }
  if(b && b.isValid()) map.fitBounds(b,{maxZoom:15,padding:[20,20]});
}

/* ---------------- layer tree UI ---------------- */
function swatch(l){
  if(l.type==='raster') {
    if(l.ramp){ return '<span class="sw" style="background:linear-gradient(90deg,'+l.ramp.map(function(r){return r[1];}).join(',')+')"></span>'; }
    return '<span class="sw ras"></span>';
  }
  var s=l.sym || (l.cats&&l.cats[0]&&l.cats[0].s);
  if(l.cats) return '<span class="sw" style="background:conic-gradient('+l.cats.slice(0,6).map(function(c){var s=c.s||{};return (s.k==='line'?s.stroke:s.fill)||'#999';}).join(',')+')"></span>';
  if(!s) return '<span class="sw"></span>';
  if(s.k==='line') return '<span class="sw line" style="background:'+s.stroke+'"></span>';
  if(s.k==='marker') return '<span class="sw pt" style="background:'+s.fill+';border:1px solid '+s.stroke+'"></span>';
  var fill=s.fill&&s.fo>0?s.fill:'transparent';
  return '<span class="sw" style="background:'+fill+';opacity:'+(s.fo>0?Math.max(.4,s.fo):1)+';border:2px solid '+(s.stroke||'transparent')+'"></span>';
}
function legendHtml(l){
  var h='';
  if(l.cats){ h+='<div class="leg">'; l.cats.forEach(function(c){ if(!c.on) return; var s=c.s||{}; var col=(s.k==='line'?s.stroke:s.fill)||'#999';
      var cls=s.k==='line'?'sw line':s.k==='marker'?'sw pt':'sw'; h+='<div><span class="'+cls+'" style="background:'+col+'"></span>'+esc(c.l||c.v||'(ללא ערך)')+'</div>'; }); h+='</div>'; }
  if(l.ramp){ h+='<div class="ramp" style="background:linear-gradient(90deg,'+l.ramp.map(function(r){return r[1];}).join(',')+')"></div><div class="ramp-l" style="direction:ltr"><span>'+esc(l.ramp[0][0])+'</span><span>'+esc(l.ramp[l.ramp.length-1][0])+'</span></div>'; }
  if(l.gray){ h+='<div class="ramp" style="background:linear-gradient(90deg,#000,#fff)"></div><div class="ramp-l" style="direction:ltr"><span>'+l.gray.min+'</span><span>'+l.gray.max+'</span></div>'; }
  return h;
}
function layerInfo(l){
  if(l.type==='raster'){ var m=CFG.raster[l.id]; if(!m) return ''; if(m.error) return 'לא הומר'; return 'רסטר · ~'+m.res_m+' מ\' לפיקסל'; }
  if(l.type==='vector'){ var v=CFG.vector[l.id]; if(!v) return ''; if(v.error) return 'לא הומר'; return v.n+' ישויות'+(v.tol?' · הוחלק':''); }
  return '';
}
function renderTree(){
  var root=$('#tree'); root.innerHTML='';
  function node(it,parentEl){
    if(it.isGroup){
      var g=document.createElement('div'); g.className='grp'+(it.open?'':' closed');
      var cnt=0; (function c(x){x.c.forEach(function(y){ if(y.isGroup)c(y); else cnt++; });})(it);
      g.innerHTML='<div class="ghead"><span class="caret">▼</span><input type="checkbox"'+(it.on?' checked':'')+'><span class="gname">'+esc(it.g)+'</span> <small class="muted">('+cnt+')</small></div><div class="gbody"></div>';
      var head=$('.ghead',g), cb=$('input',g);
      head.onclick=function(e){ if(e.target===cb) return; g.classList.toggle('closed'); };
      cb.onchange=function(){ it.on=cb.checked; refresh(); };
      it.el=g; it.cb=cb; parentEl.appendChild(g);
      it.c.forEach(function(ch){ node(ch,$('.gbody',g)); });
      return;
    }
    var l=it;
    var row=document.createElement('div'); row.className='lyr'; row.dataset.id=l.id; row._it=l;
    var isBase=l.isBase;
    var dl=(l.type==='vector'&&CFG.vector[l.id]&&!CFG.vector[l.id].error)?'<a href="data/vector/'+l.id+'.geojson" download="'+esc(l.name.replace(/[\\/:*?"<>|]/g,'_'))+'.geojson" title="הורדה כ-GeoJSON">⤓</a>':'';
    row.innerHTML='<input type="checkbox"'+(l.on?' checked':'')+'>'+swatch(l)+'<span class="nm">'+esc(l.name)+(isBase?'':' <small>'+esc(layerInfo(l))+'</small>')+'</span><span class="acts">'+(isBase?'':'<button class="z" title="התמקדות בשכבה">⌖</button>')+dl+'<button class="x" title="פרטים, שקיפות ומקרא">⋯</button></span>';
    var extra=document.createElement('div'); extra.className='lyr-extra';
    extra.innerHTML=(isBase?'מפת הרקע נבחרת בתפריט "רקע" למעלה.':'שקיפות: <input type="range" min="0" max="100" value="'+Math.round((l.op==null?1:l.op)*100)+'">')+legendHtml(l)+'<div class="path">מקור: '+esc(l.src||'')+(l.lyr?' › '+esc(l.lyr):'')+'</div>';
    var cb=$('input',row);
    cb.onchange=function(){ l.on=cb.checked; if(isBase){ $('#basemap').value=l.on?'osm':'none'; setBase($('#basemap').value); } refresh(); };
    $('.nm',row).onclick=function(){ cb.checked=!cb.checked; cb.onchange(); };
    if(!isBase) $('.z',row).onclick=function(){ if(!l.on){cb.checked=true;cb.onchange();} zoomTo(l); };
    $('.x',row).onclick=function(){ row.classList.toggle('exp'); };
    var rng=$('input[type=range]',extra);
    if(rng) rng.oninput=function(){ l.op=rng.value/100; if(l.leaf){ if(l.type==='raster') l.leaf.setOpacity(l.op); else { map.removeLayer(l.leaf); l.leaf=null; refresh(); } } };
    l.el=row; l.cb=cb; parentEl.appendChild(row); parentEl.appendChild(extra);
  }
  CFG.tree.forEach(function(it){ node(it,root); });
}
renderTree();
// basemap default from QGIS
(function(){ var b=ORDER.filter(function(l){return l.isBase;})[0]; var on=b?effOn(b):true; $('#basemap').value=on?'osm':'none'; setBase($('#basemap').value); })();
refresh();

$('#btnAllOff').onclick=function(){ ORDER.forEach(function(l){ if(!l.isBase){ l.on=false; l.cb.checked=false; } }); refresh(); };
$('#btnDefault').onclick=function(){ ORDER.forEach(function(l){ l.on=l.def; l.cb.checked=l.def; }); GROUPS.forEach(function(g){ g.on=g.def; g.cb.checked=g.def; }); refresh(); };
$('#lsearch').oninput=function(){
  var q=this.value.trim().toLowerCase();
  ORDER.forEach(function(l){ var hit=!q || l.name.toLowerCase().indexOf(q)>=0 || (l.src||'').toLowerCase().indexOf(q)>=0; l.el.classList.toggle('hidden',!hit); l.el.nextSibling.classList.toggle('hidden',!hit); });
  GROUPS.slice().reverse().forEach(function(g){ var any=$$('.lyr:not(.hidden)',g.el).length>0; g.el.classList.toggle('hidden',!any); if(q&&any) g.el.classList.remove('closed'); });
};
$('#sideToggle').onclick=function(){ $('#side').classList.toggle('hide'); setTimeout(function(){map.invalidateSize();},50); };
if(window.innerWidth<800) $('#side').classList.add('hide');

function showOnMap(ids){
  showTab('map');
  ids.forEach(function(id){ var l=LAYERS[id]; if(!l) return; l.on=true; l.cb.checked=true; var p=l.parent; while(p){ p.on=true; p.cb.checked=true; p.el.classList.remove('closed'); p=p.parent; } });
  refresh(); var l=LAYERS[ids[0]]; if(l){ zoomTo(l); l.el.scrollIntoView({block:'center'}); l.el.style.background='#fff3c4'; setTimeout(function(){l.el.style.background='';},2000); }
}

/* ---------------- viewer ---------------- */
function openViewer(f,url,kind){
  $('#vtitle').textContent=f.name; var body=$('#vbody'); body.innerHTML='';
  $('#vdl').href=url; $('#vdl').setAttribute('download',f.name); $('#vnew').href=url;
  var ext=(f.name.split('.').pop()||'').toLowerCase();
  if(kind==='pdf'){ body.innerHTML='<iframe src="'+url+'"></iframe>'; }
  else if(kind==='image'){ body.innerHTML='<img src="'+url+'" alt="">'; }
  else if(kind==='text'){
    body.innerHTML='<pre>טוען…</pre>';
    fetch(url).then(function(r){return r.text();}).then(function(t){
      if(ext==='csv'){ var rows=t.split(/\r?\n/).filter(Boolean).slice(0,1500).map(function(r){return r.split(',');});
        var h='<table class="csv"><thead><tr>'+rows[0].map(function(c){return '<th>'+esc(c)+'</th>';}).join('')+'</tr></thead><tbody>';
        rows.slice(1).forEach(function(r){ h+='<tr>'+r.map(function(c){return '<td>'+esc(c)+'</td>';}).join('')+'</tr>'; }); body.innerHTML=h+'</tbody></table>'; }
      else if(ext==='md'){ body.innerHTML='<div class="md">'+mdToHtml(t)+'</div>'; }
      else body.innerHTML='<pre>'+esc(t)+'</pre>';
    }).catch(function(){ body.innerHTML='<iframe src="'+url+'"></iframe>'; });
  }
  $('#viewer').hidden=false;
}
$('#vclose').onclick=function(){ $('#viewer').hidden=true; $('#vbody').innerHTML=''; };
$('#viewer').onclick=function(e){ if(e.target.id==='viewer') $('#vclose').onclick(); };
document.addEventListener('keydown',function(e){ if(e.key==='Escape' && !$('#viewer').hidden) $('#vclose').onclick(); });
function mdToHtml(t){
  var lines=t.split(/\r?\n/), out='', inT=false, inL=false;
  function inl(s){ return esc(s).replace(/\*\*(.+?)\*\*/g,'<b>$1</b>').replace(/`(.+?)`/g,'<code>$1</code>'); }
  lines.forEach(function(ln){
    if(/^\|/.test(ln)){ if(/^\|[\s\-:|]+\|$/.test(ln)) return; if(!inT){out+='<table class="csv" style="direction:rtl">';inT=true;} out+='<tr>'+ln.replace(/^\||\|$/g,'').split('|').map(function(c){return '<td>'+inl(c.trim())+'</td>';}).join('')+'</tr>'; return; }
    if(inT){out+='</table>';inT=false;}
    if(/^\s*[-*] /.test(ln)){ if(!inL){out+='<ul>';inL=true;} out+='<li>'+inl(ln.replace(/^\s*[-*] /,''))+'</li>'; return; }
    if(inL){out+='</ul>';inL=false;}
    var m=ln.match(/^(#{1,4}) (.*)/); if(m){ out+='<h'+(m[1].length+1)+'>'+inl(m[2])+'</h'+(m[1].length+1)+'>'; return; }
    if(ln.trim()) out+='<p>'+inl(ln)+'</p>';
  });
  if(inT)out+='</table>'; if(inL)out+='</ul>'; return out;
}

/* ---------------- files ---------------- */
var ALLF=[];
(function walk(n,path){ n.path=path; n.files.forEach(function(f){ f.dir=path; ALLF.push(f); }); n.dirs.forEach(function(d){ d.parentNode=n; walk(d,path?path+'/'+d.name:d.name); }); })(FILES,'');
function icon(f){ var e=(f.name.split('.').pop()||'').toLowerCase();
  if(f.kind==='gdb')return '🗄️'; if(e==='pdf')return '📕'; if(['png','jpg','jpeg','gif','webp'].indexOf(e)>=0)return '🖼️'; if(['tif','tiff','img','hgt','vrt'].indexOf(e)>=0)return '🗺️';
  if(['shp','gpkg','geojson','zip','kml','kmz'].indexOf(e)>=0)return '📐'; if(['qgz','qgs'].indexOf(e)>=0)return '🧭'; if(['docx','doc'].indexOf(e)>=0)return '📘'; if(['csv','xlsx'].indexOf(e)>=0)return '📊'; return '📄'; }
function fileActions(f){
  var a='';
  if(f.view && f.view!=='download') a+='<button class="btn v">צפייה</button>';
  if(f.url) a+='<a class="btn" href="'+enc(f.url)+'" download>הורדה</a>';
  if(f.layers){
    a+='<button class="btn m">הצגה במפה</button>';
    f.layers.forEach(function(id){ var l=LAYERS[id]; if(l&&l.type==='raster'&&CFG.raster[id]&&CFG.raster[id].file&&!f._pv){ f._pv=id; a+='<button class="btn p">תצוגה מקדימה</button>'; } });
    var vec=f.layers.filter(function(id){return LAYERS[id]&&LAYERS[id].type==='vector'&&CFG.vector[id]&&!CFG.vector[id].error;});
    if(vec.length===1) a+='<a class="btn" href="data/vector/'+vec[0]+'.geojson" download="'+esc(f.name)+'.geojson">GeoJSON</a>';
  }
  return a;
}
var curDir=FILES, fq='';
function renderFTree(){
  var el=$('#ftree'); el.innerHTML='';
  function add(n,parent,depth){
    var d=document.createElement('div'); d.className='fd'+(n===curDir?' sel':''); d.textContent=(depth? '📁 ':'🏠 ')+(depth?n.name:'תיקיית הפרויקט');
    d.onclick=function(){ curDir=n; fq=''; $('#fsearch').value=''; renderFiles(); };
    parent.appendChild(d);
    if(n.dirs.length && (depth<1 || isAnc(n,curDir))){ var s=document.createElement('div'); s.className='sub'; parent.appendChild(s); n.dirs.forEach(function(c){ add(c,s,depth+1); }); }
  }
  add(FILES,el,0);
}
function isAnc(a,b){ while(b){ if(a===b) return true; b=b.parentNode; } return false; }
function dirSize(n){ if(n._sz!=null) return n._sz; var s=0; n.files.forEach(function(f){s+=f.size||0;}); n.dirs.forEach(function(d){s+=dirSize(d);}); n._sz=s; return s; }
function dirCount(n){ var c=n.files.filter(function(f){return !f.aux;}).length; n.dirs.forEach(function(d){c+=dirCount(d);}); return c; }
function renderFiles(){
  renderFTree();
  var aux=$('#showAux').checked, tb=$('#flist'); tb.innerHTML='';
  var cr=$('#crumbs'); cr.innerHTML='';
  var chain=[]; var x=curDir; while(x){chain.unshift(x); x=x.parentNode;}
  chain.forEach(function(n,i){ var s=document.createElement('span'); s.textContent=i?n.name:'תיקיית הפרויקט'; s.onclick=function(){curDir=n;fq='';$('#fsearch').value='';renderFiles();}; cr.appendChild(s); if(i<chain.length-1) cr.appendChild(document.createTextNode(' › ')); });
  var list;
  if(fq){ cr.innerHTML='תוצאות חיפוש: "'+esc(fq)+'"'; list=ALLF.filter(function(f){ return (aux||!f.aux) && (f.name.toLowerCase().indexOf(fq)>=0 || f.dir.toLowerCase().indexOf(fq)>=0); }).slice(0,500); }
  else {
    curDir.dirs.forEach(function(d){
      var tr=document.createElement('tr'); tr.innerHTML='<td class="nm dir"><span class="ico">📁</span>'+esc(d.name)+'</td><td class="sz">'+fmtSize(dirSize(d))+'</td><td class="dt">'+dirCount(d)+' קבצים</td><td></td>';
      tr.onclick=function(){curDir=d;renderFiles();}; tb.appendChild(tr);
    });
    list=curDir.files.filter(function(f){return aux||!f.aux;});
  }
  list.forEach(function(f){
    var tr=document.createElement('tr'); if(f.aux) tr.className='aux';
    tr.innerHTML='<td class="nm"><span class="ico">'+icon(f)+'</span>'+esc(f.name)+(fq?'<div class="path">'+esc(f.dir||'/')+'</div>':'')+'</td><td class="sz">'+fmtSize(f.size)+'</td><td class="dt">'+fmtDate(f.mtime)+'</td><td class="acts2">'+fileActions(f)+'</td>';
    var v=$('.v',tr); if(v) v.onclick=function(){ openViewer(f,enc(f.url),f.view); };
    var m=$('.m',tr); if(m) m.onclick=function(){ showOnMap(f.layers); };
    var p=$('.p',tr); if(p) p.onclick=function(){ openViewer(f,'data/raster/'+CFG.raster[f._pv].file,'image'); };
    tb.appendChild(tr);
  });
  var hiddenAux=(fq?0:curDir.files.filter(function(f){return f.aux;}).length);
  $('#fnote').textContent=(hiddenAux&&!aux?hiddenAux+' קבצי עזר מוסתרים (כמו ‎.aux.xml, ‎.shx, ‎.dbf). ':'')+'קבצים בלי כפתור "צפייה" זמינים בתיקיית הפרויקט המקורית; שכבות GIS ניתנות לצפייה דרך "הצגה במפה". תיקיית הארכיון (99_Archive) לא נכללת.';
}
function initFiles(){
  renderFiles();
  $('#showAux').onchange=renderFiles;
  var tmr; $('#fsearch').oninput=function(){ var v=this.value; clearTimeout(tmr); tmr=setTimeout(function(){ fq=v.trim().toLowerCase(); renderFiles(); },200); };
}

/* ---------------- docs & gallery ---------------- */
function initDocs(){
  var docs=ALLF.filter(function(f){ return (f.view==='pdf') || (f.view==='download' && /\.docx$/i.test(f.name)); });
  // group pdf+docx with same base name
  var by={}; docs.forEach(function(f){ var k=f.dir+'/'+f.name.replace(/\.(pdf|docx)$/i,''); (by[k]=by[k]||[]).push(f); });
  var keys=Object.keys(by).sort(function(a,b){ var A=/before_David/.test(a), B=/before_David/.test(b); if(A!==B) return A?1:-1; var ma=Math.max.apply(null,by[a].map(function(f){return f.mtime||0;})), mb=Math.max.apply(null,by[b].map(function(f){return f.mtime||0;})); return mb-ma; });
  var el=$('#docList'); el.innerHTML='';
  if(!docs.length) el.innerHTML='<p class="muted">הדוחות אינם מפורסמים באתר כרגע.</p>';
  keys.forEach(function(k){
    var fs=by[k], pdf=fs.filter(function(f){return f.view==='pdf';})[0], doc=fs.filter(function(f){return /\.docx$/i.test(f.name);})[0], f0=pdf||doc;
    var old=/before_David/.test(k);
    var c=document.createElement('div'); c.className='card';
    c.innerHTML='<div class="ttl">'+esc(f0.name.replace(/\.(pdf|docx)$/i,'').replace(/_/g,' '))+'</div><div class="meta">'+esc(f0.dir)+' · '+fmtDate(f0.mtime)+(old?' · גרסה קודמת (לפני עדכון הגופן)':'')+'</div><div class="row">'+
      (pdf?'<button class="btn v">קריאה (PDF)</button><a class="btn" href="'+enc(pdf.url)+'" download>הורדת PDF</a>':'')+(doc?'<a class="btn" href="'+enc(doc.url)+'" download>הורדת Word</a>':'')+'</div>';
    if(pdf) $('.v',c).onclick=function(){ openViewer(pdf,enc(pdf.url),'pdf'); };
    el.appendChild(c);
  });
  var seen={}, imgs=ALLF.filter(function(f){ if(f.view!=='image') return false; var k=f.name.replace(/['_]/g,'')+'|'+f.size; if(seen[k]) return false; seen[k]=1; return !/_grid_check|_work/.test(f.dir); });
  var groups={}; imgs.forEach(function(f){ var g=f.dir.split('/').slice(0,2).join(' / ')||'ראשי'; (groups[g]=groups[g]||[]).push(f); });
  var gal=$('#gallery'); gal.innerHTML='';
  Object.keys(groups).sort(function(a,b){ var A=a.indexOf('06_')===0, B=b.indexOf('06_')===0; if(A!==B) return A?-1:1; return a<b?-1:1; }).forEach(function(g){
    var h=document.createElement('h3'); h.textContent=g+' ('+groups[g].length+')'; h.style.gridColumn='1/-1'; h.style.margin='14px 0 0'; gal.appendChild(h);
    groups[g].forEach(function(f){ var fig=document.createElement('figure'); fig.innerHTML='<img loading="lazy" src="'+enc(f.url)+'" alt=""><figcaption>'+esc(f.name)+'<small>'+esc(f.dir)+'</small></figcaption>'; fig.onclick=function(){ openViewer(f,enc(f.url),'image'); }; gal.appendChild(fig); });
  });
}

/* about info */
(function(){ var nV=ORDER.filter(function(l){return l.type==='vector';}).length, nR=ORDER.filter(function(l){return l.type==='raster';}).length;
  $('#buildInfo').textContent='בנוי מתוך Israel_Jordan_Arava_MASTER.qgz: '+nV+' שכבות וקטוריות, '+nR+' שכבות רסטר, '+ALLF.length+' קבצים בעץ התיקיות. עודכן: '+(CFG.built||'')+'.'; })();

var h=(location.hash||'').replace('#',''); showTab(['map','docs','files','about'].indexOf(h)>=0?h:'map');
})();
