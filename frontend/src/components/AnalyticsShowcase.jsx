import {useEffect,useRef,useState} from 'react';
import {ArrowUpRight,Play} from 'lucide-react';
import {NavLink} from 'react-router-dom';
import {get} from '../services/api';

const segmentColors={Champions:'#d8b54b','Loyal Customers':'#5b9a88','Potential Loyalists':'#8b79c6','New Customers':'#4a9da0','At Risk':'#dc9144','Lost Customers':'#bb6870'};

function CuboidChart({items=[],nameKey,valueKey,color='#bf8d3d'}){
  const max=Math.max(1,...items.map(x=>Number(x[valueKey])||0));
  return <svg className="showcase-svg" viewBox="0 0 360 210" role="img" aria-label={`Three dimensional ${valueKey} chart from data`}>
    <path d="M42 169 124 124 319 124 237 169Z" fill="#f0e4d1" stroke="#d8c4a4"/>
    {[0,1,2,3].map(i=><path key={i} d={`M${62+i*48} ${158-i*11} 144 ${113-i*11}`} stroke="#d6c5aa"/>)}
    {items.slice(0,6).map((item,i)=>{const x=65+i*42,h=Math.max(4,(Number(item[valueKey])||0)/max*94),y=157-h;return <g key={`${item[nameKey]}-${i}`}>
      <path d={`M${x} ${y} ${x+10} ${y-6} ${x+27} ${y-6} ${x+17} ${y}Z`} fill="#e0bc75"/>
      <path d={`M${x+17} ${y} ${x+27} ${y-6} ${x+27} 151 ${x+17} 157Z`} fill="#78562f"/>
      <rect x={x} y={y} width="17" height={157-y} fill={color} rx="1"/>
      <text x={x+8} y="177" textAnchor="middle" fontSize="8" fill="#796b58">{String(item[nameKey]||'').slice(0,7)}</text>
    </g>})}
    <path d="M42 169 42 60M42 169 236 169M42 169 124 124" stroke="#9d896a" fill="none" strokeWidth="1.2"/>
    {!items.length&&<text x="180" y="104" textAnchor="middle" fontSize="11" fill="#75664e">Import data to populate this 3D view</text>}
  </svg>
}

function CustomerCloud({rows=[],large=false}){
  const maxR=Math.max(1,...rows.map(x=>x.recency||0)),maxF=Math.max(1,...rows.map(x=>x.frequency||0)),maxM=Math.max(1,...rows.map(x=>x.monetary||0));
  return <svg className={large?'showcase-svg cloud-svg':'showcase-svg'} viewBox="0 0 360 210" role="img" aria-label="Three dimensional customer RFM scatter from data">
    <path d="M51 165 132 118 314 118 232 165Z" fill="#392b20" stroke="#b99b69" strokeOpacity=".55"/>
    <path d="M51 165V54M51 165H232M51 165 132 118" stroke="#e1c88f" fill="none" strokeWidth="1.2"/>
    {rows.slice(0,260).map((r,i)=>{const x=(r.recency||0)/maxR,y=(r.frequency||0)/maxF,z=(r.monetary||0)/maxM;const sx=145+(x-.5)*154-(z-.5)*62+(y-.5)*24,sy=111-(y*70)-(z-.5)*53;return <circle key={`${r.customer_id}-${i}`} cx={sx} cy={sy} r={large?3.7:3} fill={segmentColors[r.segment]||'#e3be69'} fillOpacity=".88"><title>{`${r.customer_id}: ${r.segment}; ${r.recency} days recency, ${r.frequency} orders, ${r.monetary} spend`}</title></circle>})}
    <text x="228" y="181" fill="#ead8ad" fontSize="8">Recency</text><text x="128" y="112" fill="#ead8ad" fontSize="8">Frequency</text><text x="38" y="54" fill="#ead8ad" fontSize="8">Spend</text>
    {!rows.length&&<text x="180" y="104" textAnchor="middle" fontSize="11" fill="#ead8ad">Customer points appear after import</text>}
  </svg>
}

function VideoPreview({title,series=[],accent='#d6ad58'}){
  const canvasRef=useRef(null),videoRef=useRef(null),[videoUrl,setVideoUrl]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState('');
  useEffect(()=>()=>{if(videoUrl)URL.revokeObjectURL(videoUrl)},[videoUrl]);
  function makeVideo(){
    const canvas=canvasRef.current;if(!canvas||!series.length)return;
    if(!canvas.captureStream||!window.MediaRecorder){setError('This browser cannot record the video preview.');return}
    setError('');setBusy(true);if(videoUrl){URL.revokeObjectURL(videoUrl);setVideoUrl('')}
    try{
      const ctx=canvas.getContext('2d'),stream=canvas.captureStream(24),mime=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(x=>window.MediaRecorder.isTypeSupported(x));
      const recorder=new MediaRecorder(stream,mime?{mimeType:mime}:undefined),chunks=[];recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
      recorder.onerror=()=>{stream.getTracks().forEach(t=>t.stop());setBusy(false);setError('Could not render the preview on this browser.')};
      recorder.onstop=()=>{stream.getTracks().forEach(t=>t.stop());const url=URL.createObjectURL(new Blob(chunks,{type:recorder.mimeType||'video/webm'}));setVideoUrl(url);setBusy(false);setTimeout(()=>videoRef.current?.play(),80)};
      const values=series.slice(0,8).map(x=>Number(x.value)||0),max=Math.max(1,...values),start=performance.now(),duration=5600;recorder.start(150);
      function frame(now){const progress=Math.min(1,(now-start)/duration),w=640,h=360;ctx.setTransform(canvas.width/640,0,0,canvas.height/360,0,0);ctx.fillStyle='#2c211a';ctx.fillRect(0,0,w,h);ctx.fillStyle='#f3e4c0';ctx.font='600 17px Arial';ctx.fillText(`NORTHSTAR  /  ${title.toUpperCase()}`,38,43);ctx.fillStyle='#d8b54b';ctx.font='11px Arial';ctx.fillText('3D VISUAL ANALYSIS',492,43);ctx.strokeStyle='#ffffff20';ctx.lineWidth=1;for(let i=0;i<5;i++){const y=95+i*51;ctx.beginPath();ctx.moveTo(52,y);ctx.lineTo(595,y);ctx.stroke()}const shown=Math.max(1,Math.ceil(progress*values.length));values.slice(0,shown).forEach((v,i)=>{const barH=24+(v/max)*160,x=85+i*61,y=304-barH;ctx.fillStyle=accent;ctx.fillRect(x,y,29,barH);ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+12,y-8);ctx.lineTo(x+41,y-8);ctx.lineTo(x+29,y);ctx.closePath();ctx.fillStyle='#f1d891';ctx.fill();ctx.beginPath();ctx.moveTo(x+29,y);ctx.lineTo(x+41,y-8);ctx.lineTo(x+41,296);ctx.lineTo(x+29,304);ctx.closePath();ctx.fillStyle='#78562f';ctx.fill();ctx.fillStyle='#d6c8ad';ctx.font='9px Arial';ctx.fillText(series[i]?.label?.slice(0,9)||'',x-3,326)});ctx.fillStyle='#fff8ea';ctx.font='700 22px Arial';ctx.fillText(`${shown} ${title.toLowerCase()} records`,38,350);if(progress<1)requestAnimationFrame(frame);else recorder.stop()}
      requestAnimationFrame(frame);
    }catch{setBusy(false);setError('Could not render the preview. Try the latest Edge or Chrome browser.')}
  }
  return <div className="video-stage"><canvas ref={canvasRef} width="960" height="480" className="video-render-canvas" aria-hidden="true"/>{videoUrl?<video ref={videoRef} className="sample-video" src={videoUrl} controls playsInline/>:<div className="video-poster"><div className="video-poster-grid"/><div className="poster-kicker">3D ANALYTICS · PLAYABLE SAMPLE</div><div className="poster-bars">{series.slice(0,7).map((x,i)=><span key={`${x.label}-${i}`} style={{height:`${Math.max(9,20+(Number(x.value)||0)/Math.max(1,...series.map(v=>Number(v.value)||0))*72)}%`,background:accent,transform:`translateZ(${i*7}px)`}}/>)}</div><div className="poster-months">{series.slice(0,7).map((x,i)=><span key={`${x.label}-${i}`}>{x.label.slice(0,7)}</span>)}</div><div className="poster-callout">{series.length?`${series.length} records in view`:'Import a file to create video'}</div></div>}
    <button className="video-play" disabled={!series.length||busy} onClick={makeVideo}><Play size={15} fill="currentColor"/>{busy?'Rendering 3D video…':videoUrl?'Regenerate video':'Play 3D video'}</button>{error&&<span className="video-error">{error}</span>}</div>
}

function toSeries(items,labelKey,valueKey){return items.slice(0,8).map(x=>({label:String(x[labelKey]||''),value:Number(x[valueKey])||0}))}

export default function AnalyticsShowcase({data,products}){
  const [customers,setCustomers]=useState([]),[demo,setDemo]=useState(null);useEffect(()=>{get('/analytics/customers').then(x=>setCustomers(x.rfm||[])).catch(()=>setCustomers([]))},[]);
  useEffect(()=>{let active=true;fetch('/sample_dataset.csv').then(r=>r.ok?r.text():'').then(csv=>{if(!active||!csv)return;const lines=csv.trim().split(/\r?\n/).slice(1),months=new Map(),productsMap=new Map(),customerMap=new Map();for(const line of lines){const row=line.split(',');if(row.length<10)continue;const[cid,, ,pid,pname,,oid,date,quantity,price]=row,qty=Number(quantity),unit=Number(price),revenue=qty*unit;if(!cid||!date||!Number.isFinite(revenue))continue;const month=date.slice(0,7);months.set(month,(months.get(month)||0)+revenue);const product=productsMap.get(pid)||{product_id:pid,product_name:pname,revenue:0,units:0};product.revenue+=revenue;product.units+=qty;productsMap.set(pid,product);const customer=customerMap.get(cid)||{customer_id:cid,recency:0,frequency:0,monetary:0,_last:'',_orders:new Set()};customer.monetary+=revenue;customer._orders.add(oid);if(date>customer._last)customer._last=date;customerMap.set(cid,customer)}const dates=lines.map(x=>x.split(',')[7]).filter(Boolean).sort(),latest=dates.at(-1);const rfm=[...customerMap.values()].map(c=>{c.frequency=c._orders.size;c.recency=Math.max(0,(Date.parse(latest)-Date.parse(c._last))/86400000|0);delete c._last;delete c._orders;c.segment=c.frequency>=4&&c.recency<=30?'Champions':c.frequency>=3?'Loyal Customers':c.frequency===2&&c.recency<=60?'Potential Loyalists':c.frequency===1&&c.recency<=30?'New Customers':c.recency<=90?'At Risk':'Lost Customers';return c});setDemo({monthly_revenue:[...months].sort(([a],[b])=>a.localeCompare(b)).map(([month,total_amount])=>({month,total_amount})),top_products:[...productsMap.values()].sort((a,b)=>b.revenue-a.revenue).slice(0,10),rfm})}).catch(()=>{});return()=>{active=false}},[]);
  const usingLive=Boolean(data?.monthly_revenue?.length),months=usingLive?data.monthly_revenue:(demo?.monthly_revenue||[]),top=products?.top_products?.length?products.top_products:(demo?.top_products||[]),rfm=customers.length?customers:(demo?.rfm||[]),segments=[...rfm.reduce((m,x)=>m.set(x.segment,(m.get(x.segment)||0)+1),new Map())].map(([label,value])=>({label,value}));
  return <section className="showcase-section"><div className="showcase-heading"><div><div className="eyebrow">VISUAL ANALYTICS STUDIO</div><h2>Explore your business in 3D.</h2><p>{usingLive?'3D visuals use your imported database records.':'Preview the bundled sample file, or import a spreadsheet to view your own business data.'}</p></div><div className="showcase-actions"><span className={usingLive?'source-badge live':'source-badge demo'}>{usingLive?'LIVE DATABASE':'DEMO SAMPLE'}</span><a className="text-link" href="/sample_dataset.csv" download>Download sample <ArrowUpRight size={14}/></a><NavLink className="text-link" to="/customers">Open full customer analysis <ArrowUpRight size={14}/></NavLink></div></div>
    <article className="showcase-hero-image"><div className="hero-image-copy"><span className="hero-image-tag">01 / FULL 3D CUSTOMER MAP</span><h3>Every customer,<br/>in a new dimension.</h3><p>Explore purchase recency, frequency, and monetary value as a rotatable customer cloud.</p><NavLink to="/customers" className="hero-image-link">Open interactive RFM analysis <ArrowUpRight size={15}/></NavLink></div><div className="hero-cloud"><CustomerCloud rows={rfm} large/></div><div className="hero-image-source">{usingLive?'LIVE DATABASE':'DEMO SAMPLE'} · {rfm.length.toLocaleString()} CUSTOMER POINTS</div></article>
    <div className="sample-image-row"><article className="showcase-card"><div className="showcase-meta"><span>02 / 3D IMAGE ANALYSIS</span><b>Revenue towers</b></div><div className="showcase-visual"><CuboidChart items={months.slice(-6)} nameKey="month" valueKey="total_amount"/></div><p>Monthly revenue rendered as a 3D column image from {usingLive?'your stored data.':'the demo spreadsheet.'}</p></article><article className="showcase-card"><div className="showcase-meta"><span>03 / 3D IMAGE ANALYSIS</span><b>Product demand blocks</b></div><div className="showcase-visual"><CuboidChart items={top.slice(0,6)} nameKey="product_name" valueKey="revenue" color="#668c77"/></div><p>Product blocks ranked by revenue from {usingLive?'your order lines.':'the bundled sample file.'}</p></article></div>
    <div className="video-gallery-heading"><div><div className="eyebrow">THREE FULL-WIDTH 3D ANALYSIS VIDEOS</div><h3>Watch each analysis unfold.</h3></div><span>{usingLive?'Videos are generated from your database results.':'Videos are generated from calculated demo sample data.'}</span></div>
    <div className="video-gallery"><article className="showcase-card wide-video-card"><div className="showcase-meta wide-video-meta"><span>VIDEO 01 / REVENUE</span><b>Revenue timeline</b></div><VideoPreview title="Revenue timeline" series={toSeries(months.slice(-8),'month','total_amount')} accent="#d7b14c"/><p>Monthly sales and revenue movement.</p></article>
      <article className="showcase-card wide-video-card"><div className="showcase-meta wide-video-meta"><span>VIDEO 02 / PRODUCTS</span><b>Product performance</b></div><VideoPreview title="Product performance" series={toSeries(top,'product_name','revenue')} accent="#6c9c83"/><p>Top product revenue by product.</p></article>
      <article className="showcase-card wide-video-card"><div className="showcase-meta wide-video-meta"><span>VIDEO 03 / CUSTOMERS</span><b>Customer segments</b></div><VideoPreview title="Customer segments" series={segments} accent="#bd8652"/><p>RFM customer segment distribution.</p></article></div>
  </section>
}
