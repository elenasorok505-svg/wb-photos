// Цена «этого же товара» на WB: поиск по фото через вкладку https://www.wildberries.ru/ (главная).
// Нужны wsl() и __J3=[[ключ,'путь/в/репо/фото.jpg'],...]. Запуск: imgRun7([0,1,2],'__IR7A'). Результат __IR7[ключ]={res:[[цена ₽,nm]...14],url,ok}.
// Цена товара = медиана первых 8 ненулевых (pricing_v2.analog_median); если по фото > 1,5× медианы категории — берём категорию и потолок.
{const src='onmessage=e=>setTimeout(()=>postMessage(e.data.id),e.data.ms)';window.__wk=new Worker(URL.createObjectURL(new Blob([src],{type:'text/javascript'})));window.__wkcb={};__wk.onmessage=e=>{const f=__wkcb[e.data];delete __wkcb[e.data];f&&f()};window.__wkid=0;}
window.wsl=ms=>new Promise(r=>{const id=++__wkid;__wkcb[id]=r;__wk.postMessage({id,ms})});
// v7: rAF через Worker (скрытая вкладка) + проверка, что на WB ушло новое фото (хэш загрузки ≠ прошлому)
if(!window.__rafp){window.__rafp=1;let n=0;const cbs={};window.requestAnimationFrame=function(cb){const id=++n;cbs[id]=cb;wsl(16).then(()=>{const f=cbs[id];delete cbs[id];f&&f(performance.now())});return id};window.cancelAnimationFrame=function(id){delete cbs[id]};}
window.__jobn=window.__jobn||0; window.__cz={job:0,ids:null,prods:{},lists:0,t:0,h:null}; window.__lastH=window.__lastH||'';
async function __hash(bl){const buf=await bl.arrayBuffer();const d=await crypto.subtle.digest('SHA-1',buf);return [...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,'0')).join('')}
if(!window.__fh7){window.__fh7=1;const of=window.fetch;window.fetch=async function(a,b){const u=(typeof a=='string'?a:a.url);const job=__cz.job;
  if(/search-by-photo\.wb\.ru\/uploadsearch/.test(u)&&b&&b.body instanceof FormData){const v=b.body.get('image');if(v)__hash(v).then(h=>{if(__cz.job===job)__cz.h=h})}
  const r=await of.apply(this,arguments);try{if(/search-by-photo\.wb\.ru\/uploadsearch/.test(u)){r.clone().json().then(j=>{if(__cz.job===job){__cz.ids=(j.result||[]).map(x=>x.im_name);__cz.t=Date.now()}})}else if(/u-card\/cards\/v4\/list/.test(u)){r.clone().json().then(j=>{if(__cz.job===job){for(const p of (j.products||[]))__cz.prods[p.id]=p;__cz.lists++;__cz.t=Date.now()}})}}catch(e){};return r};}
window.imgOne7=async function(path){
  const b=await (await fetch('https://raw.githubusercontent.com/elenasorok505-svg/wb-photos/main/'+path)).blob();
  for(let attempt=0;attempt<3;attempt++){
    const cl=document.querySelector('.popup-crop-search-image .popup__close'); if(cl){cl.click(); await wsl(800);}
    const f=new File([b],'p'+Date.now()+'.jpg',{type:'image/jpeg'});const dt=new DataTransfer();dt.items.add(f);
    __cz={job:++__jobn,ids:null,prods:{},lists:0,t:0,h:null};
    const inp=document.querySelector('input[type=file][name=photo]');inp.value='';inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
    let btn=null;for(let t=0;t<60&&!btn;t++){await wsl(250);btn=document.querySelector('.popup-crop-search-image__button')}
    if(!btn){continue}
    await wsl(600); btn.click();
    for(let t=0;t<160;t++){await wsl(250); if(__cz.ids&&__cz.lists>=1&&__cz.h&&Date.now()-__cz.t>2000)break;}
    if(!__cz.h||__cz.h===__lastH){ await wsl(1500); continue; }   // ушло старое фото — повтор
    __lastH=__cz.h;
    const ids=(__cz.ids||[]).slice(0,14);
    const res=ids.map(i=>{const p=__cz.prods[i];if(!p)return [0,String(i)];const s=(p.sizes||[]).find(s=>s.price)||{};return [Math.round(((s.price||{}).product||0)/100),String(i)]});
    __cz={job:-1,ids:null,prods:{},lists:0,t:0,h:null};
    return {res,url:location.href,ok:res.filter(x=>x[0]>0).length>=3,att:attempt};
  }
  return {err:'stale'};
};
window.__IR7=window.__IR7||{};
window.imgRun7=async function(list,key){for(const i of list){const [k,p]=__J3[i]; let r=null;for(let tr=0;tr<2;tr++){try{r=await imgOne7(p);}catch(e){r={err:String(e)}} if(r&&r.ok)break; await wsl(1500);} __IR7[k]=r; try{localStorage[key]=JSON.stringify(__IR7)}catch(e){} await wsl(500);} window.__ir7done=true;};
"ok7"
