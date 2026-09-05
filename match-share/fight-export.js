/* BEACN match GIF frame renderer. No network, DOM snapshots, or live data reads.
 * Caller supplies a frozen {data,event,meta:{kind,result,title,outcomeCaption},logo}.
 * Scores are the supplied snapshot; event outcomes describe a historical replay.
 * Render time is normalized 0..1: 0.6s hold, 1.3s action, 1.1s final hold.
 */
(function (global) {
  'use strict';
  const WIDTH=800, HEIGHT=600, FPS=12, FRAME_COUNT=36, DURATION_MS=3000;
  const C={bg:'#08121f',panel:'#0d1c2c',line:'#294257',white:'#edf5fc',muted:'#adc0d2',cyan:'#5cddf4',amber:'#ffc166',red:'#ff8294',green:'#6cdeb1',black:'#03080e'};
  const MONO='ui-monospace,Consolas,"Liberation Mono",monospace', SANS='system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif';
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const num=(v,d=2)=>finite(v)?v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
  const amount=v=>!finite(v)?'—':Math.abs(v)>0&&Math.abs(v)<.000001?v.toExponential(2):num(v,Math.abs(v)>0&&Math.abs(v)<.01?6:2);
  const signed=v=>(v>0?'+':'')+amount(v);
  const name=id=>id==='beacn'?'BEACNbot':'grokbot';
  function utc(value,compact=false) {
    const date=new Date(typeof value==='number'?value*1000:value);
    if(!Number.isFinite(date.getTime()))return 'Time unavailable';
    const iso=date.toISOString();
    return compact?iso.slice(5,10)+' '+iso.slice(11,16)+' UTC':iso.slice(0,10)+' '+iso.slice(11,19)+' UTC';
  }
  function rounded(c,x,y,w,h,r,fill,stroke,width=1) {
    c.beginPath();c.roundRect(x,y,w,h,r);
    if(fill){c.fillStyle=fill;c.fill();}
    if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}
  }
  function text(c,value,x,y,size,color=C.white,align='left',weight=700,maxWidth=752,mono=false) {
    c.save();c.textAlign=align;c.textBaseline='alphabetic';c.fillStyle=color;
    let px=size;const str=String(value??'');
    c.font=`${weight} ${px}px ${mono?MONO:SANS}`;
    while(c.measureText(str).width>maxWidth&&px>9){px--;c.font=`${weight} ${px}px ${mono?MONO:SANS}`;}
    c.fillText(str,x,y);c.restore();
  }
  function lines(c,value,x,y,maxWidth,size,color,maxLines=2) {
    c.save();c.font=`600 ${size}px ${SANS}`;
    const words=String(value??'').split(/\s+/), rows=[];let row='';
    for(const word of words){const next=row?row+' '+word:word;if(c.measureText(next).width>maxWidth&&row){rows.push(row);row=word;}else row=next;}
    if(row)rows.push(row);
    const shown=rows.slice(0,maxLines);
    if(rows.length>maxLines){let last=shown[maxLines-1];while(c.measureText(last+'…').width>maxWidth&&last.length)last=last.slice(0,-1);shown[maxLines-1]=last+'…';}
    shown.forEach((line,i)=>text(c,line,x,y+i*(size+5),size,color,'left',600,maxWidth));c.restore();
  }
  const gloveShell=new Path2D('M23 58C12 53 9 46 10 31 10 14 19 7 36 7h10c15 0 23 10 23 23v14c0 12-7 19-15 23l-2 13H24Z');
  const gloveThumb=new Path2D('M22 54c-6-13-4-24 2-26 7-3 12 5 13 13l2 9');
  const gloveShine=new Path2D('M31 15c11-3 23 0 27 9M44 54l14-4');
  const gloveCuff=new Path2D('m23 64 32 2-3 16-28-2Z');
  const gloveCuffLine=new Path2D('m29 72 17 1');
  const grokCloud=new Path2D('M17 38c-5.5-8.4 2-17.7 10.6-14.7C31.8 13 47 16.4 47 27.7c8.8 2.9 6.7 16.3-2.5 16.3H22c-4.2 0-7.6-2.5-8-6Z');
  const grokBolt=new Path2D('m35 22-9 13h7l-3 10 10-14h-7Z');
  function glove(c,x,y,color,angle,scale=.57) {
    c.save();c.translate(x,y);c.rotate(angle);c.scale(scale,scale);c.translate(-40,-45);
    c.fillStyle=color;c.strokeStyle=C.black;c.lineWidth=3;c.lineCap='round';
    c.fill(gloveShell);c.stroke(gloveShell);c.fill(gloveThumb);c.stroke(gloveThumb);
    c.strokeStyle='#eff6fc';c.globalAlpha=.45;c.stroke(gloveShine);c.globalAlpha=1;
    c.fillStyle='#e5eaf0';c.strokeStyle=C.black;c.fill(gloveCuff);c.stroke(gloveCuff);
    c.strokeStyle='#344656';c.stroke(gloveCuffLine);c.restore();
  }
  function grok(c,x,y,color) {
    c.save();c.translate(x-47,y-47);c.scale(94/64,94/64);
    c.strokeStyle=color;c.lineWidth=1.7;c.setLineDash([3,5]);c.beginPath();c.arc(32,32,25,0,Math.PI*2);c.stroke();c.setLineDash([]);
    c.fillStyle=color;c.globalAlpha=.13;c.fill(grokCloud);c.globalAlpha=1;c.lineWidth=2;c.stroke(grokCloud);c.fill(grokBolt);
    c.beginPath();c.arc(8,32,2,0,Math.PI*2);c.arc(55,21,2,0,Math.PI*2);c.fill();c.restore();
  }
  function prepare(model) {
    const data=model?.data||{}, event=model?.event||{}, meta=model?.meta||model?.metadata||{};
    const agents=Array.isArray(data.agents)?data.agents:[];
    const a=agents.find(a=>a.id==='beacn')||{id:'beacn'},b=agents.find(a=>a.id==='grokbot')||{id:'grokbot'};
    const marked=data.price?.available===true&&[a,b].every(a=>finite(a.score_ada_eq));
    const actor=event.agent==='grokbot'?'grokbot':'beacn';
    let kind=['profit','loss','trade','setup','order','even'].includes(meta.kind)?meta.kind:
      ['supply','redeem','receipt','stake','cancel'].includes(event.kind)?'setup':event.kind==='order'?'order':'trade';
    let result=finite(meta.result)?meta.result:null;
    const verified=['fill','swap'].includes(event.kind)&&event.effect?.type==='realized_spot_pnl'&&event.effect?.status==='verified';
    if((kind==='profit'||kind==='loss'||kind==='even')&&(!verified||result===null))kind='trade';
    if(kind==='profit'&&result<=0||kind==='loss'&&result>=0||kind==='even'&&result!==0)kind='trade';
    if(!['profit','loss','even'].includes(kind))result=null;
    const attacker=kind==='loss'?(actor==='beacn'?'grokbot':'beacn'):actor;
    const target=attacker==='beacn'?'grokbot':'beacn';
    const identity={beacn:{x:182,color:C.cyan,direction:1},grokbot:{x:618,color:C.amber,direction:-1}};
    const neutral=model?.snapshotState==='stale'||model?.snapshotState==='unavailable';
    const leader=marked&&!neutral&&['beacn','grokbot'].includes(data.leader)?data.leader:null;
    const gap=marked&&finite(data.gap_ada_eq)?Math.abs(data.gap_ada_eq):null;
    const defaultTitle=event.kind==='cancel'?'Cancelled a swap order':event.title||'Recorded on-chain move';
    let outcome=meta.outcomeCaption||meta.outcomecaption||meta.outcome||'';
    if(!outcome){outcome=kind==='profit'?`${name(actor)} lands a hit · ${signed(result)} ADA realized on this sale.`:
      kind==='loss'?`${name(actor)} takes the hit · ${signed(result)} ADA realized on this sale.`:
      kind==='even'?'Trade closed at break-even.':kind==='order'?'Order placed; waiting for a fill.':kind==='setup'?'Position setup. No realized points awarded.':'Trade filled; realized result not attributed.';}
    return {data,event,meta,a,b,marked,actor,kind,result,attacker,target,identity,leader,gap,neutral,logo:model?.logo,title:meta.title||defaultTitle,outcome};
  }
  function pose(p,id,action) {
    const base=p.identity[id],leading=p.leader===id;
    const phase=clamp(action,0,1), setup=['setup','order','even'].includes(p.kind), own=p.actor===id;
    const lift=setup&&own?Math.sin(phase*Math.PI)*10:0;
    return {...base,headY:192,innerX:base.x+base.direction*81,innerY:251-lift,
      outerX:base.x-base.direction*79,outerY:leading?177:258,leading};
  }
  function fighter(c,p,id,action,hideInner,recoil) {
    const q=pose(p,id,action), color=p.neutral?'#8fa4b7':q.color;
    c.save();
    c.fillStyle=C.black;c.beginPath();c.ellipse(q.x,299,92,10,0,0,Math.PI*2);c.fill();
    rounded(c,q.x-33,268,21,28,7,'#203548',color);rounded(c,q.x+12,268,21,28,7,'#203548',color);
    rounded(c,q.x-41,244,82,33,11,'#132a3b',color,1.5);rounded(c,q.x-42,261,84,8,2,color);
    c.strokeStyle=color;c.lineWidth=12;c.lineCap='round';c.beginPath();c.moveTo(q.x-q.direction*33,252);c.quadraticCurveTo(q.x-q.direction*69,272,q.outerX,q.outerY+11);c.stroke();
    glove(c,q.outerX,q.outerY,color,-q.direction*.22);
    if(!hideInner){c.beginPath();c.moveTo(q.x+q.direction*33,252);c.quadraticCurveTo(q.x+q.direction*66,266,q.innerX,q.innerY+10);c.stroke();glove(c,q.innerX,q.innerY,color,q.direction*.24);}
    c.translate(q.x+recoil, q.headY);c.rotate(recoil*.006);
    c.fillStyle=C.black;c.beginPath();c.arc(0,0,58,0,Math.PI*2);c.fill();c.strokeStyle=q.leading?q.color:C.line;c.lineWidth=q.leading?3:2;c.stroke();
    if(id==='beacn'){
      let drawn=false;
      if(p.logo&&(p.logo.naturalWidth||p.logo.width)){
        c.save();
        try{c.beginPath();c.arc(0,0,54,0,Math.PI*2);c.clip();c.drawImage(p.logo,-58,-58,116,116);drawn=true;}
        catch{ /* A failed asset keeps a labeled medallion without corrupting the canvas state. */ }
        finally{c.restore();}
      }
      if(!drawn)text(c,'BEACN',0,6,16,color,'center',900,104,true);
    }else grok(c,0,0,color);
    c.restore();
  }
  function drawFrame(c,t,p) {
    const normalized=clamp(finite(t)?t:0,0,1), milliseconds=normalized*DURATION_MS;
    const action=clamp((milliseconds-600)/1300,0,1);
    const strike=['profit','loss','trade'].includes(p.kind), active=strike&&milliseconds>=600&&milliseconds<=1900;
    const progress=action<.12?-.06*Math.sin(action/.12*Math.PI):action<.38?1-Math.pow(1-(action-.12)/.26,3):action<.52?1:action<.78?Math.pow(1-(action-.52)/.26,3):0;
    const hit=active&&action>=.37&&action<.65, reaction=active&&action>=.38&&action<.71?Math.sin((action-.38)/.33*Math.PI):0;
    const strength=p.result===null?.15:clamp(Math.abs(p.result)/Math.max(1,(Number(p.data.start?.equalized_score_ada_eq)||907)*.02),0,1);
    c.save();c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.fillStyle=C.bg;c.fillRect(0,0,WIDTH,HEIGHT);
    // Opaque, limited-palette scenery compresses cleanly in a GIF.
    c.fillStyle='#0b2030';c.fillRect(16,78,300,233);c.fillStyle='#241f18';c.fillRect(484,78,300,233);
    rounded(c,16,16,768,568,15,null,C.line);
    text(c,'BEACN MAINNET ARENA',32,40,15,C.cyan,'left',900,370,true);
    text(c,'HISTORICAL REPLAY',768,40,12,C.muted,'right',800,300,true);
    text(c,'Snapshot '+utc(p.data.generated_at_unix||p.data.generated_at),32,61,12,C.muted,'left',600,500,true);
    text(c,'Book values at snapshot',768,61,10,C.muted,'right',600,268,true);
    for(const y of [171,218,265]){c.strokeStyle=C.line;c.lineWidth=2;c.beginPath();c.moveTo(46,y);c.lineTo(754,y);c.stroke();}
    for(const [x,color] of [[48,C.cyan],[752,C.amber]]){rounded(c,x-4,147,8,147,3,'#132436',color);for(const y of [164,211,258])rounded(c,x-9,y,18,15,3,C.bg,color);}
    for(const id of ['beacn','grokbot']){const q=p.identity[id];text(c,name(id),q.x,103,24,q.color,'center',900,270);text(c,p.leader===id?'LEADING THIS SNAPSHOT':'',q.x,122,9,q.color,'center',800,230,true);}
    text(c,'VS',400,196,43,active?'#3c4b5a':'#91a3b5','center',950,112);
    text(c,p.gap===null?'NO PRICE MARK':num(p.gap)+' ADA-eq GAP',400,292,11,C.muted,'center',800,235,true);
    const targetRecoil=p.kind==='trade'?0:reaction*(3+strength*5)*(p.attacker==='beacn'?1:-1);
    fighter(c,p,'beacn',action,active&&p.attacker==='beacn',p.target==='beacn'?targetRecoil:0);
    fighter(c,p,'grokbot',action,active&&p.attacker==='grokbot',p.target==='grokbot'?targetRecoil:0);
    if(active){
      const a=pose(p,p.attacker,action),b=pose(p,p.target,action), blocked=p.kind==='trade';
      const direction=a.direction, contact={x:blocked?b.innerX-direction*15:b.x-direction*53,y:blocked?b.innerY:193};
      const scale=.6, end={x:contact.x-direction*38*scale,y:contact.y};
      const x=a.innerX+(end.x-a.innerX)*progress,y=a.innerY+(end.y-a.innerY)*progress-7*Math.sin(clamp(progress,0,1)*Math.PI);
      const wristX=x-direction*21, sx=a.x+direction*33,sy=252;
      c.lineCap='round';for(const [color,width] of [[C.black,18],[a.color,13],['#e7f3fa',2]]){c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.moveTo(sx,sy);c.quadraticCurveTo(sx+(wristX-sx)*.55,Math.max(sy,y)+12,wristX,y);c.stroke();}
      glove(c,x,y,a.color,direction*Math.PI/2,scale);
      if(hit){c.save();c.translate(contact.x,contact.y);c.strokeStyle=p.kind==='loss'?C.red:C.amber;c.lineWidth=2;for(let n=0;n<7;n++){const angle=n*Math.PI*2/7;c.beginPath();c.moveTo(Math.cos(angle)*13,Math.sin(angle)*13);c.lineTo(Math.cos(angle)*(21+strength*5),Math.sin(angle)*(21+strength*5));c.stroke();}c.restore();}
      if(action>=.37&&action<.94){text(c,p.result===null?'GUARDED':signed(p.result)+' ADA',400,150,18,p.result<0?C.red:a.color,'center',900,276,true);}
    }
    for(const ag of [p.a,p.b]){
      const q=p.identity[ag.id], pnl=ag.vs_equalized_start_ada_eq??ag.vs_start_ada_eq;
      rounded(c,q.x-150,319,300,86,11,C.panel,C.line);
      text(c,p.marked?num(ag.score_ada_eq):num(ag.ada_total),q.x,353,35,C.white,'center',850,250,true);
      text(c,p.marked?'ADA-equivalent book':'ADA held · token value unmarked',q.x,373,10,C.muted,'center',700,284,true);
      text(c,p.marked&&finite(pnl)?signed(pnl)+' ADA-eq since start':'P&L unavailable',q.x,394,12,p.marked&&finite(pnl)?pnl<0?C.red:pnl>0?C.green:C.muted:C.muted,'center',800,282,true);
    }
    rounded(c,32,424,736,120,11,C.panel,C.line);
    const tag={profit:'REALIZED GAIN',loss:'REALIZED LOSS',even:'BREAK-EVEN',trade:'GUARDED TRADE',setup:p.event.kind==='cancel'?'ORDER CANCELLED':'POSITION SETUP',order:'ORDER PLACED'}[p.kind];
    const eventColor=p.kind==='loss'?C.red:p.kind==='profit'?C.green:p.identity[p.actor].color;
    rounded(c,45,438,4,88,2,eventColor);
    text(c,name(p.actor)+' · '+utc(p.event.time,true),60,449,12,p.identity[p.actor].color,'left',800,440,true);
    text(c,tag,752,449,10,eventColor,'right',800,220,true);
    text(c,p.title,60,476,20,C.white,'left',800,690);
    lines(c,p.outcome,60,501,686,13,eventColor,2);
    text(c,'Trade result is separate from match P&L. Replays do not transfer ADA.',400,563,10,C.muted,'center',600,734);
    text(c,'beacnpool.github.io/ABCDE/match.html',400,579,10,C.cyan,'center',800,730,true);
    c.restore();
  }
  function renderFrame(ctx,tNormalized,model) {
    if(!ctx||typeof ctx.fillRect!=='function')throw new TypeError('Canvas 2D context required');
    drawFrame(ctx,tNormalized,prepare(model));
  }
  function createRenderer(model) {
    const prepared=prepare(model);
    const canvas=global.document?global.document.createElement('canvas'):new global.OffscreenCanvas(WIDTH,HEIGHT);
    canvas.width=WIDTH;canvas.height=HEIGHT;
    const ctx=canvas.getContext('2d',{alpha:false});
    if(!ctx)throw new Error('Canvas 2D context unavailable');
    return {canvas,width:WIDTH,height:HEIGHT,render(tNormalized){drawFrame(ctx,tNormalized,prepared);return canvas;}};
  }
  global.MatchFightExport=Object.freeze({width:WIDTH,height:HEIGHT,fps:FPS,frameCount:FRAME_COUNT,durationMs:DURATION_MS,renderFrame,createRenderer});
})(typeof window!=='undefined'?window:globalThis);
