// Медиана цены топ-30 на WB (сортировка «по популярности»). API search.wb.ru отдаёт 403 → читаем DOM.
// 1) navigate вкладку WB на: https://www.wildberries.ru/catalog/0/search.aspx?search=<запрос>&sort=popular
// 2) подождать 3–5 с, выполнить этот код → {n, med}. Записать в wb_med.json как {"запрос": [med, n]}.
(()=>{const pr=[...document.querySelectorAll('.product-card')].slice(0,30).map(c=>{const e=c.querySelector('ins')||[...c.querySelectorAll('*')].find(x=>x.children.length==0&&/₽/.test(x.textContent));return e?parseInt(e.textContent.replace(/[^\d]/g,'')):0}).filter(x=>x>0).sort((a,b)=>a-b);return JSON.stringify({n:pr.length,med:pr[Math.floor(pr.length/2)]})})()
