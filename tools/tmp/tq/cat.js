// хелперы для новых категорий: хранение в IndexedDB (localStorage переполнен). Требует info, encJobs, wsl из seedall.js
window.idb=()=>new Promise((res,rej)=>{const r=indexedDB.open('anx',1);r.onupgradeneeded=()=>r.result.createObjectStore('kv');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error);});
window.iget=async k=>{const d=await idb();return await new Promise(r=>{const q=d.transaction('kv').objectStore('kv').get(k);q.onsuccess=()=>r(q.result);q.onerror=()=>r(undefined);});};
window.iset=async(k,v)=>{const d=await idb();return await new Promise(r=>{const t=d.transaction('kv','readwrite');t.objectStore('kv').put(v,k);t.oncomplete=()=>r(true);t.onerror=()=>r(false);});};
// st = 'R' (дорожки) / 'K' (беговелы); ids в iget(st+'ids'), данные iget(st+'d')
window.crawlX=async(st,ids,delay)=>{const all=(await iget(st+'d'))||{};window.__xlog=[];window.__xdone=false;for(const id of ids){if(all[id])continue;let x=null;try{x=await info(id);}catch(e){__xlog.push(id+':ERR');continue;}
if(!x){const t=await (await fetch('/offer/'+id+'.html')).text();if(t.length<2000){__xlog.push(id+':BLOCK');break;}__xlog.push(id+':NULL');all[id]={id,null:1};continue;}
delete x.sold;x.imgs=x.imgs.slice(0,12);all[id]=x;await iset(st+'d',all);__xlog.push(id+':ok');await wsl(delay+Math.random()*4000);}window.__xdone=true;};
window.thumbsX=async(st,a,b)=>{const T=await iget(st+'d');const ids=await iget(st+'ids');const jobs=[];
for(let n=a;n<b;n++){const x=T[ids[n]];if(!x||x.null)continue;const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));if(sp)sp.v.slice(0,12).forEach((v,k)=>{if(v[1])jobs.push([st+n+'_'+k,v[1]+'_200x200.jpg'])});(x.imgs||[]).slice(0,6).forEach((u,i)=>jobs.push([st+n+'m'+i,u+'_200x200.jpg']));}
return await encJobs(jobs,0.7,200);};
window.fullX=async(st,keys)=>{const T=await iget(st+'d');const ids=await iget(st+'ids');const jobs=[];for(const k of keys){const m=k.match(/^[A-Z](\d+)(_|m)(\d+)$/);const x=T[ids[+m[1]]];if(!x)continue;if(m[2]=='m'){if(x.imgs[+m[3]])jobs.push([k,x.imgs[+m[3]]]);continue;}const sp=(x.sp||[]).find(p=>p.v.some(v=>v[1]));if(!sp||!sp.v[+m[3]]||!sp.v[+m[3]][1])continue;jobs.push([k,sp.v[+m[3]][1]]);}return await encJobs(jobs,0.88,1000);};
window.dxX=async(st)=>{const T=await iget(st+'d');const ids=await iget(st+'ids');return JSON.stringify({ids,d:T});};
'okX';
