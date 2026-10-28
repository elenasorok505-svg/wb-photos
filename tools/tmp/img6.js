// свежий экземпляр сайта WB в iframe на каждое фото — без «залипания» состояния попапа
window.imgOne6=async function(path){
  const b=await (await fetch('https://raw.githubusercontent.com/elenasorok505-svg/wb-photos/main/'+path)).blob();
  const fr=document.createElement('iframe'); fr.style.cssText='width:1280px;height:900px;position:fixed;left:-3000px;top:0'; fr.src='/?r='+Date.now(); document.body.appendChild(fr);
  try{
    let inp=null; for(let t=0;t<120&&!inp;t++){await wsl(250); try{inp=fr.contentDocument.querySelector('input[type=file][name=photo]')}catch(e){}}
    if(!inp) return {err:'noinput'};
    const W=fr.contentWindow; const cy={ids:null,prods:{},lists:0,t:0};
    const of=W.fetch; W.fetch=async function(a,o){const u=(typeof a=='string'?a:a.url);const r=await of.apply(this,arguments);try{if(/uploadsearch/.test(u)){r.clone().json().then(j=>{cy.ids=(j.result||[]).map(x=>x.im_name);cy.t=Date.now()})}else if(/u-card\/cards\/v4\/list/.test(u)){r.clone().json().then(j=>{for(const p of (j.products||[]))cy.prods[p.id]=p;cy.lists++;cy.t=Date.now()})}}catch(e){};return r};
    const f=new W.File([b],'p.jpg',{type:'image/jpeg'});const dt=new W.DataTransfer();dt.items.add(f);
    inp.files=dt.files;inp.dispatchEvent(new W.Event('change',{bubbles:true}));
    let btn=null;for(let t=0;t<80&&!btn;t++){await wsl(250);btn=fr.contentDocument.querySelector('.popup-crop-search-image__button')}
    if(!btn) return {err:'nobtn'};
    btn.click();
    for(let t=0;t<160;t++){await wsl(250); if(cy.ids&&cy.lists>=1&&Date.now()-cy.t>2000)break;}
    const ids=(cy.ids||[]).slice(0,14);
    const res=ids.map(i=>{const p=cy.prods[i];if(!p)return [0,String(i)];const s=(p.sizes||[]).find(s=>s.price)||{};return [Math.round(((s.price||{}).product||0)/100),String(i)]});
    let url='';try{url=fr.contentWindow.location.href}catch(e){}
    return {res,url,ok:res.filter(x=>x[0]>0).length>=3};
  } finally { fr.remove(); }
};
window.__IR6=window.__IR6||{};
window.imgRun6=async function(list,key){for(const i of list){const [k,p]=__J3[i]; let r=null;for(let tr=0;tr<2;tr++){try{r=await imgOne6(p);}catch(e){r={err:String(e)}} if(r&&r.ok)break; await wsl(1500);} __IR6[k]=r; try{localStorage[key]=JSON.stringify(__IR6)}catch(e){} await wsl(500);} window.__ir6done=true;};
"ok6"
