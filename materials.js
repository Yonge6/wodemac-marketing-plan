(async()=>{
  const grid=document.getElementById('asset-grid');
  const filters=document.getElementById('asset-filters');
  const count=document.getElementById('asset-count');
  const isCases=document.body.dataset.library==='cases';
  const label=isCases?'案例':'素材';
  try{
    const response=await fetch(isCases?'cases.json':'materials.json');
    if(!response.ok)throw new Error('Materials unavailable');
    const catalog=await response.json();
    const groups=new Map(catalog.groups.map(group=>[group.id,group.name]));
    const groupFromHash=()=>groups.has(location.hash.slice(1))?location.hash.slice(1):'all';
    let selected=groupFromHash();
    const create=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text)el.textContent=text;return el;};
    function render(){
      const items=catalog.items.filter(item=>selected==='all'||item.group===selected);
      filters.querySelectorAll('button').forEach(button=>{const on=button.dataset.group===selected;button.setAttribute('aria-pressed',String(on));button.classList.toggle('active',on);});
      const ready=items.filter(item=>item.image).length;
      count.textContent=ready?`${items.length} 项${label} · ${ready} 项已上架`:`${items.length} 个${label}位 · ${isCases?'照片待补充':'图片待上架'}`;
      grid.replaceChildren();
      items.forEach((item,i)=>{
        const card=create('article','asset-card');
        const poster=create(item.image?'a':'div','poster-preview '+item.group);
        poster.style.aspectRatio=catalog.format.width+'/'+catalog.format.height;
        if(item.image){
          poster.href=item.download||item.image;poster.target='_blank';poster.rel='noopener';poster.setAttribute('aria-label','查看原图：'+item.title);
          const img=create('img');img.src=item.image;img.alt=item.title;img.loading='lazy';img.width=catalog.format.width;img.height=catalog.format.height;poster.append(img);
        }else{
          poster.setAttribute('role','img');poster.setAttribute('aria-label',item.title+(isCases?'，客户案例照片待补充':'，iPhone 竖版图片待上架'));
          const top=create('div','placeholder-top');top.append(create('span','placeholder-brand','wodeMac'),create('span','placeholder-index',String(i+1).padStart(2,'0')));
          const center=create('div','placeholder-center');center.append(create('span','phone-outline'),create('span','placeholder-label',isCases?'客户案例照片':'iPhone 竖版海报'),create('span','placeholder-state',isCases?'照片待补充':'图片待上架'));
          const bottom=create('div','placeholder-bottom');bottom.append(create('span','',groups.get(item.group)),create('span','',isCases?'案例说明待补充':catalog.format.width+' × '+catalog.format.height));
          poster.append(top,center,bottom);
        }
        const details=create('div','asset-details');
        details.append(create('p','asset-category',groups.get(item.group)),create('h2','',item.title),create('p','asset-description',item.description));
        let action;
        if(item.image){action=create('a','asset-download','下载图片 ↓');action.href=item.download||item.image;action.setAttribute('download','');}
        else{action=create('button','asset-download',isCases?'案例待补充':'素材待上架');action.type='button';action.disabled=true;}
        details.append(action);card.append(poster,details);grid.append(card);
      });
    }
    [{id:'all',name:'全部'+label},...catalog.groups].forEach(group=>{
      const button=create('button','asset-filter',group.name);button.type='button';button.dataset.group=group.id;
      button.addEventListener('click',()=>{selected=group.id;history.replaceState(null,'',location.pathname+location.search+(selected==='all'?'':'#'+selected));render();});filters.append(button);
    });
    window.addEventListener('hashchange',()=>{selected=groupFromHash();render();});
    render();
  }catch(error){count.textContent=label+'暂未加载';document.getElementById('library-error').hidden=false;}
})();
