// Хелперы для встроенного браузера. Вставить целиком через javascript_tool во вкладку
// https://detail.1688.com/robots.txt (там работают fetch к офферам и картинкам alicdn).
// Поиск (searchApi) — во вкладке https://s.1688.com/... (нужен вход в аккаунт 1688).
window.getCtx=async(id)=>{const h=await (await fetch('/offer/'+id+'.html')).text();const i=h.indexOf('window.context=');if(i<0)return null;const e=h.indexOf('</script>',i);const W={};new Function('window',h.slice(i,e))(W);return W.context;};
window.grab=(s,key,open,close)=>{const k=s.indexOf('"'+key+'":'+open);if(k<0)return null;let depth=0,j=k+key.length+3;for(;j<s.length;j++){if(s[j]==open)depth++;else if(s[j]==close){depth--;if(depth==0)break;}}try{return JSON.parse(s.slice(k+key.length+3,j+1));}catch(e){return null}};
window.info=async(id)=>{const c=await getCtx(id);if(!c)return null;const r=c.result,d=r.data||{},g=r.global?.globalData?.model||{},tm=g.tradeModel||{};const t=d.productTitle?.fields||{};const pi=d.productPackInfo?.fields||{};const s=JSON.stringify(r);
const fa=Object.fromEntries([...s.matchAll(/"name":"([^"]{1,30})","outputType":\d+,"value":"([^"]{1,160})"/g)].map(m=>[m[1],m[2]]));
const sp=grab(s,'skuProps','[',']');const sim=grab(s,'skuInfoMap','{','}');
return {id,title:t.title||d.gallery?.fields?.subject,sold:t.saleNum,price:[tm.minPrice,tm.maxPrice],begin:tm.beginAmount,
sp:sp?sp.map(p=>({prop:p.prop,v:(p.value||[]).map(v=>[v.name,v.imageUrl||''])})):null,
sim:sim?Object.fromEntries(Object.entries(sim).map(([k,v])=>[k.replace(/&gt;/g,'>'),[v.price||v.discountPrice,v.canBookCount]])):null,
pk:(pi.pieceWeightScale?.pieceWeightScaleInfo||[]).map(x=>({l:x.length,w:x.width,h:x.height,g:x.weight,sku:x.sku1||x.skuName||x.specAttrs||''})),uw:pi.unitWeight,
fa,imgs:(d.gallery?.fields?.offerImgList||[]),desc:d.description?.fields?.detailUrl||null,grade:t.rateInfo?.goodsGrade,company:t.shopInfo?.companyName};};
// обход офферов: пишет в localStorage.__bags; прогресс window.__blog, конец window.__bdone; ':BLOCK' = капча/запрет, ждать ~30 мин
window.crawlBg=async(ids,delay)=>{const all=JSON.parse(localStorage.getItem('__bags')||'{}');window.__blog=[];window.__bdone=false;for(const id of ids){if(all[id]||(window.__skip||[]).includes(id))continue;let x=null;try{x=await info(id);}catch(e){window.__blog.push(id+':ERR');continue;}
if(!x){const t=await (await fetch('/offer/'+id+'.html')).text(); if(t.length<2000){window.__blog.push(id+':BLOCK');break;} window.__blog.push(id+':NULL'); (window.__skip=window.__skip||[]).push(id); continue;}
const fa={};for(const k of ['材质','里料材质','闭合方式','箱包外袋种类','内部结构','提拎部件','肩带样式','款式','大小','适用场景','颜色','尺寸','箱包硬度','形状','风格','图案','流行元素','箱包重量'])if(x.fa[k])fa[k]=x.fa[k];
for(const k in x.fa){if(/尺寸|长|宽|高|规格|重量|容量/.test(k))fa[k]=x.fa[k];}
x.fa=fa; x.imgs=x.imgs.slice(0,12); all[id]=x;localStorage.setItem('__bags',JSON.stringify(all));window.__blog.push(id+':ok');await new Promise(r=>setTimeout(r,delay+Math.random()*4000));}window.__bdone=true;};
// картинки → бинарь → строка из иероглифов (14 бит/символ) в window.__E, манифест window.__M
window.toBytes=async(url,q,max)=>{const b=await (await fetch(url)).blob();const bm=await createImageBitmap(b);const s=Math.min(1,max/Math.max(bm.width,bm.height));const c=document.createElement('canvas');c.width=Math.round(bm.width*s);c.height=Math.round(bm.height*s);c.getContext('2d').drawImage(bm,0,0,c.width,c.height);const bl=await new Promise(r=>c.toBlob(r,'image/webp',q));return new Uint8Array(await bl.arrayBuffer());};
window.encJobs=async(jobs,q,max)=>{const res=[];for(let i=0;i<jobs.length;i+=8){const part=await Promise.all(jobs.slice(i,i+8).map(async([k,u])=>{try{return [k,await toBytes(u,q,max)]}catch(e){return [k,null]}}));res.push(...part);}
const man=res.filter(r=>r[1]).map(r=>[r[0],r[1].length]);const tot=man.reduce((a,b)=>a+b[1],0);const all=new Uint8Array(tot);let p=0;for(const r of res)if(r[1]){all.set(r[1],p);p+=r[1].length;}
let out=[];let acc=0,nb=0;for(let i=0;i<all.length;i++){acc=(acc<<8)|all[i];nb+=8;if(nb>=14){nb-=14;out.push(String.fromCharCode(0x4E00+((acc>>nb)&0x3FFF)));acc&=(1<<nb)-1;}}
if(nb>0)out.push(String.fromCharCode(0x4E00+((acc<<(14-nb))&0x3FFF)));window.__E=out.join('');window.__M=man;return {n:man.length,fail:res.filter(r=>!r[1]).map(r=>r[0]),bytes:tot,chars:window.__E.length};};
window.__ck=(t,i)=>t+i+'|'+window.__E.slice(195000+(i-1)*200000,195000+i*200000)+'~END|';
// миниатюры SKU (200px) + 3 главных фото для офферов с индексами a..b-1 в localStorage.__bids → ключи B{n}_{k}, B{n}m{i}
window.thumbs=async(a,b)=>{const B=JSON.parse(localStorage.__bags); const ids=JSON.parse(localStorage.__bids); const jobs=[];
for(let n=a;n<b;n++){const x=B[ids[n]]; if(!x) continue; const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1])); if(sp) sp.v.slice(0,10).forEach((v,k)=>{if(v[1]) jobs.push(['B'+n+'_'+k, v[1]+'_200x200.jpg'])}); (x.imgs||[]).slice(0,3).forEach((u,i)=>jobs.push(['B'+n+'m'+i,u+'_200x200.jpg']));}
return await encJobs(jobs,0.7,200);};
// полноразмерные (900px) по ключам 'B{n}_{k}' / 'B{n}m{i}'
window.full=async(keys)=>{const B=JSON.parse(localStorage.__bags); const ids=JSON.parse(localStorage.__bids); const jobs=[];
for(const k of keys){const m=k.match(/^B(\d+)(_|m)(\d+)$/); const x=B[ids[+m[1]]]; if(m[2]=='m'){jobs.push([k,x.imgs[+m[3]]]);continue;} const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1])); jobs.push([k, sp.v[+m[3]][1]]);}
return await encJobs(jobs,0.82,900);};
// ПОИСК (вкладка s.1688.com): JSON-API, 20 офферов на запрос, 2 страницы × 3 порции = 120 на запрос.
// window.__QS=['腋下包女','托特包女',...]; searchApi(); итог в window.__api {запрос:[{id,t,p,s,s90,img,b,cc,ad}]}
window.searchApi=async()=>{window.__api=window.__api||{};window.__alog=[];window.__adone=false;for(const q of __QS){if(__api[q])continue;const out=[];for(const pg of [1,2])for(const si of [0,20,40]){try{const u='https://search.1688.com/service/marketOfferResultViewService?keywords='+encodeURIComponent(q)+'&charset=utf8&beginPage='+pg+'&pageSize=60&async=true&asyncCount=20&pageName=major&offset=0&startIndex='+si+'&sortType=va_rmdarkgmv';const j=await (await fetch(u,{credentials:'include'})).json();const L=(j.data&&j.data.data&&j.data.data.offerList)||[];for(const o of L){try{out.push({id:String(o.id),t:(o.information.subject||'').replace(/<[^>]+>/g,''),p:parseFloat(o.tradePrice.offerPrice.priceInfo.price),s:o.tradeQuantity.saleQuantity||0,s90:+(o.tradeQuantity.vaSales90||0),img:o.image.imgUrl,b:(o.information.brief||'').slice(0,300),cc:o.information.colorCount||0,ad:!!(o.trackInfoModel&&JSON.stringify(o.trackInfoModel).includes('p4p'))})}catch(e){}}}catch(e){__alog.push(q+' ERR '+e)}await new Promise(r=>setTimeout(r,1200+Math.random()*800));}__api[q]=out;__alog.push(q+':'+out.length);}window.__adone=true;};
'ok';
const b=new Blob(["onmessage=e=>setTimeout(()=>postMessage(e.data[0]),e.data[1])"]);window.__wk2=new Worker(URL.createObjectURL(b));window.__wcb={};window.__wid=0;__wk2.onmessage=e=>{const f=__wcb[e.data];delete __wcb[e.data];f&&f();};
window.wsl=ms=>new Promise(r=>{const id=++__wid;__wcb[id]=r;__wk2.postMessage([id,ms]);});
window.crawlT=async(ids,delay)=>{const all=JSON.parse(localStorage.getItem('__tee')||'{}');window.__tlog=[];window.__tdone=false;for(const id of ids){if(all[id])continue;let x=null;try{x=await info(id);}catch(e){__tlog.push(id+':ERR');continue;}
if(!x){const t=await (await fetch('/offer/'+id+'.html')).text();if(t.length<2000){__tlog.push(id+':BLOCK');break;}__tlog.push(id+':NULL');continue;}
delete x.sim;delete x.sold;x.imgs=x.imgs.slice(0,10);all[id]=x;localStorage.setItem('__tee',JSON.stringify(all));__tlog.push(id+':ok');await wsl(delay+Math.random()*4000);}window.__tdone=true;};
window.__ck5=(t,i)=>t+i+'|'+window.__E.slice(195000+(i-1)*200000,195000+i*200000)+'~END|';
window.thumbsT=async(a,b)=>{const T=JSON.parse(localStorage.__tee);const ids=JSON.parse(localStorage.__tids);const jobs=[];
for(let n=a;n<b;n++){const x=T[ids[n]];if(!x)continue;const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));if(sp)sp.v.slice(0,12).forEach((v,k)=>{if(v[1])jobs.push(['T'+n+'_'+k,v[1]+'_200x200.jpg'])});(x.imgs||[]).slice(0,3).forEach((u,i)=>jobs.push(['T'+n+'m'+i,u+'_200x200.jpg']));}
return await encJobs(jobs,0.7,200);};
window.fullT=async(keys)=>{const T=JSON.parse(localStorage.__tee);const ids=JSON.parse(localStorage.__tids);const jobs=[];
for(const k of keys){const m=k.match(/^T(\d+)(_|m)(\d+)$/);const x=T[ids[+m[1]]];if(m[2]=='m'){jobs.push([k,x.imgs[+m[3]]]);continue;}const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));jobs.push([k,sp.v[+m[3]][1]]);}
return await encJobs(jobs,0.85,1200);};
'okT';
const b=new Blob(["onmessage=e=>setTimeout(()=>postMessage(e.data[0]),e.data[1])"]);window.__wk2=new Worker(URL.createObjectURL(b));window.__wcb={};window.__wid=0;__wk2.onmessage=e=>{const f=__wcb[e.data];delete __wcb[e.data];f&&f();};
window.wsl=ms=>new Promise(r=>{const id=++__wid;__wcb[id]=r;__wk2.postMessage([id,ms]);});
window.crawlT=async(ids,delay)=>{const all=JSON.parse(localStorage.getItem('__tee')||'{}');window.__tlog=[];window.__tdone=false;for(const id of ids){if(all[id])continue;let x=null;try{x=await info(id);}catch(e){__tlog.push(id+':ERR');continue;}
if(!x){const t=await (await fetch('/offer/'+id+'.html')).text();if(t.length<2000){__tlog.push(id+':BLOCK');break;}__tlog.push(id+':NULL');continue;}
delete x.sim;delete x.sold;x.imgs=x.imgs.slice(0,10);all[id]=x;localStorage.setItem('__tee',JSON.stringify(all));__tlog.push(id+':ok');await wsl(delay+Math.random()*4000);}window.__tdone=true;};
window.__ck5=(t,i)=>t+i+'|'+window.__E.slice(195000+(i-1)*200000,195000+i*200000)+'~END|';
window.thumbsT=async(a,b)=>{const T=JSON.parse(localStorage.__tee);const ids=JSON.parse(localStorage.__tids);const jobs=[];
for(let n=a;n<b;n++){const x=T[ids[n]];if(!x)continue;const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));if(sp)sp.v.slice(0,12).forEach((v,k)=>{if(v[1])jobs.push(['T'+n+'_'+k,v[1]+'_200x200.jpg'])});(x.imgs||[]).slice(0,3).forEach((u,i)=>jobs.push(['T'+n+'m'+i,u+'_200x200.jpg']));}
return await encJobs(jobs,0.7,200);};
window.fullT=async(keys)=>{const T=JSON.parse(localStorage.__tee);const ids=JSON.parse(localStorage.__tids);const jobs=[];
for(const k of keys){const m=k.match(/^T(\d+)(_|m)(\d+)$/);const x=T[ids[+m[1]]];if(m[2]=='m'){jobs.push([k,x.imgs[+m[3]]]);continue;}const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));jobs.push([k,sp.v[+m[3]][1]]);}
return await encJobs(jobs,0.85,1200);};
'okT';
window.fullT2=async(keys)=>{const T=JSON.parse(localStorage.__tee);const ids=JSON.parse(localStorage.__tids);const jobs=[];for(const k of keys){const m=k.match(/^T(\d+)(_|m)(\d+)$/);const x=T[ids[+m[1]]];if(m[2]=='m'){jobs.push([k,x.imgs[+m[3]]]);continue;}const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));if(!sp||!sp.v[+m[3]]||!sp.v[+m[3]][1])continue;jobs.push([k,sp.v[+m[3]][1]]);}return await encJobs(jobs,0.86,900);};
window.__ckall=()=>Math.max(0,Math.ceil((window.__E.length-195000)/200000));
window.dxT=(ns)=>{const T=JSON.parse(localStorage.__tee);const ids=JSON.parse(localStorage.__tids);const d={};for(const n of ns){const x=T[ids[n]];if(x)d[ids[n]]=x;}return JSON.stringify({ids,d});};
'okALL';
