(async()=>{
  const grid=document.getElementById('asset-grid');
  const filters=document.getElementById('asset-filters');
  const count=document.getElementById('asset-count');
  try{
    const response=await fetch('materials.json');
    if(!response.ok)throw new Error('Materials unavailable');
    const catalog=await response.json();
    const groups=new Map(catalog.groups.map(group=>[group.id,group.name]));
    let selected='all';
    const create=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;if(text)el.textContent=text;return el;};
    function render(){
      const items=catalog.items.filter(item=>selected==='all'||item.group===selected);
      filters.querySelectorAll('button').forEach(button=>{const on=button.dataset.group===selected;button.setAttribute('aria-pressed',String(on));button.classList.toggle('active',on);});
      const ready=items.filter(item=>item.image).length;
      count.textContent=ready?`${items.length} 项素材 · ${ready} 项已上架`:`${items.length} 个素材位 · 图片待上架`;
      grid.replaceChildren();
      items.forEach((item,i)=>{
        const card=create('article','asset-card');
        const poster=create('div','poster-preview '+item.group);
        poster.style.aspectRatio=catalog.format.width+'/'+catalog.format.height;
        if(item.image){
          const img=create('img');img.src=item.image;img.alt=item.title;img.loading='lazy';img.width=catalog.format.width;img.height=catalog.format.height;poster.append(img);
        }else{
          poster.setAttribute('role','img');poster.setAttribute('aria-label',item.title+'，iPhone 竖版图片待上架');
          const top=create('div','placeholder-top');top.append(create('span','placeholder-brand','wodeMac'),create('span','placeholder-index',String(i+1).padStart(2,'0')));
          const center=create('div','placeholder-center');center.append(create('span','phone-outline'),create('span','placeholder-label','iPhone 竖版海报'),create('span','placeholder-state','图片待上架'));
          const bottom=create('div','placeholder-bottom');bottom.append(create('span','',groups.get(item.group)),create('span','',catalog.format.width+' × '+catalog.format.height));
          poster.append(top,center,bottom);
        }
        const details=create('div','asset-details');
        details.append(create('p','asset-category',groups.get(item.group)),create('h2','',item.title),create('p','asset-description',item.description));
        let action;
        if(item.image){action=create('a','asset-download','下载图片 ↓');action.href=item.download||item.image;action.setAttribute('download','');}
        else{action=create('button','asset-download','素材待上架');action.type='button';action.disabled=true;}
        details.append(action);card.append(poster,details);grid.append(card);
      });
    }
    [{id:'all',name:'全部素材'},...catalog.groups].forEach(group=>{
      const button=create('button','asset-filter',group.name);button.type='button';button.dataset.group=group.id;
      button.addEventListener('click',()=>{selected=group.id;render();});filters.append(button);
    });
    render();
  }catch(error){count.textContent='素材暂未加载';document.getElementById('library-error').hidden=false;}
})();
