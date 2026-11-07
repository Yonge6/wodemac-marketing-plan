// "复制文案" buttons on material cards. Uses the Clipboard API, falls back to execCommand for older
// in-app browsers (WeChat on some phones), and as a last resort selects the text for a long-press copy.
(()=>{
  const fallback=text=>{
    const area=document.createElement('textarea');
    area.value=text;area.setAttribute('readonly','');area.style.cssText='position:fixed;top:0;left:0;opacity:0;font-size:16px';
    document.body.append(area);area.select();area.setSelectionRange(0,text.length);
    let ok=false;try{ok=document.execCommand('copy');}catch{}
    area.remove();return ok;
  };
  document.addEventListener('click',async e=>{
    const button=e.target.closest('.asset-copy');if(!button)return;
    const box=button.closest('.asset-promo').querySelector('.asset-promo-text');
    const text=box.textContent.trim();
    let ok=false;
    try{await navigator.clipboard.writeText(text);ok=true;}catch{ok=fallback(text);}
    if(!ok){const range=document.createRange();range.selectNodeContents(box);const sel=getSelection();sel.removeAllRanges();sel.addRange(range);}
    button.textContent=ok?'已复制 ✓':'已选中，请长按复制';button.classList.toggle('copied',ok);
    clearTimeout(button._t);button._t=setTimeout(()=>{button.textContent='复制文案';button.classList.remove('copied');},1800);
  });
})();
