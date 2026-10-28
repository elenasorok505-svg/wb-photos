window.__jobn=window.__jobn||0; window.__cy={job:0,ids:null,prods:{},lists:0,t:0};
if(!window.__fh6){window.__fh6=1;const of=window.fetch;window.fetch=async function(a,b){const u=(typeof a=='string'?a:a.url);const job=__cy.job;const r=await of.apply(this,arguments);try{if(/search-by-photo\.wb\.ru\/uploadsearch/.test(u)){r.clone().json().then(j=>{if(__cy.job===job){__cy.ids=(j.result||[]).map(x=>x.im_name);__cy.t=Date.now()}})}else if(/u-card\/cards\/v4\/list/.test(u)){r.clone().json().then(j=>{if(__cy.job===job){for(const p of (j.products||[]))__cy.prods[p.id]=p;__cy.lists++;__cy.t=Date.now()}})}}catch(e){};return r};}
window.imgOne4=async function(path){
  const b=await (await fetch('https://raw.githubusercontent.com/elenasorok505-svg/wb-photos/main/'+path)).blob();
  const f=new File([b],'p.jpg',{type:'image/jpeg'});const dt=new DataTransfer();dt.items.add(f);
  __cy={job:++__jobn,ids:null,prods:{},lists:0,t:0};
  const inp=document.querySelector('input[type=file][name=photo]');inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
  let btn=null;for(let t=0;t<60&&!btn;t++){await wsl(250);btn=document.querySelector('.popup-crop-search-image__button')}
  if(!btn) return {err:'nobtn'};
  btn.click();
  for(let t=0;t<160;t++){await wsl(250); if(__cy.ids&&__cy.lists>=1&&Date.now()-__cy.t>2000)break;}
  const ids=(__cy.ids||[]).slice(0,14);
  const res=ids.map(i=>{const p=__cy.prods[i];if(!p)return [0,String(i)];const s=(p.sizes||[]).find(s=>s.price)||{};return [Math.round(((s.price||{}).product||0)/100),String(i)]});
  const job=__cy.job; __cy={job:-1,ids:null,prods:{},lists:0,t:0};
  return {res,url:location.href,ok:res.filter(x=>x[0]>0).length>=3,job};
};
window.__IR5={};window.__irlog5=[];
window.imgRun5=async function(list,key){for(const i of list){const [k,p]=__J3[i]; let r=null;for(let tr=0;tr<2;tr++){try{r=await imgOne4(p);}catch(e){r={err:String(e)}} if(r&&r.ok)break; await wsl(2000);} __IR5[k]=r; __irlog5.push(i); try{localStorage[key]=JSON.stringify(__IR5)}catch(e){} await wsl(1500);} window.__ir5done=true;};
"ok"
