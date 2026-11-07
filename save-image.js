// In-app browsers (WeChat, QQ, Weibo, DingTalk, Alipay) ignore <a download>, so a tap either does nothing
// or opens a page the user cannot save from. There we show the original image full screen and ask for a
// long-press, which saves it to the phone's album. Other browsers keep the normal download.
(()=>{
  const inApp=/MicroMessenger|QQ\/|MQQBrowser|Weibo|DingTalk|AlipayClient|AliApp/i.test(navigator.userAgent);
  if(!inApp)return;
  document.documentElement.classList.add('in-app-browser');
  let layer,img,title,lastFocus;
  const close=()=>{if(!layer||layer.hidden)return;layer.hidden=true;document.documentElement.classList.remove('save-image-open');img.removeAttribute('src');lastFocus&&lastFocus.focus&&lastFocus.focus();};
  const build=()=>{
    layer=document.createElement('div');layer.className='save-image-layer';layer.hidden=true;
    layer.setAttribute('role','dialog');layer.setAttribute('aria-modal','true');layer.setAttribute('aria-label','保存图片');
    layer.innerHTML='<div class="save-image-bar"><p><b>长按图片</b>，选择「保存图片」</p><button type="button" class="save-image-close" aria-label="关闭">完成</button></div><div class="save-image-stage"><img alt=""></div><p class="save-image-tip"></p>';
    img=layer.querySelector('img');title=layer.querySelector('.save-image-tip');
    layer.querySelector('.save-image-close').addEventListener('click',close);
    layer.addEventListener('click',e=>{if(e.target===layer||e.target.classList.contains('save-image-stage'))close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape')close();});
    document.body.append(layer);
  };
  document.addEventListener('click',e=>{
    const link=e.target.closest('a[download]');
    if(!link||!/\.(png|jpe?g|webp|gif)(\?|#|$)/i.test(link.getAttribute('href')||''))return;
    e.preventDefault();
    if(!layer)build();
    lastFocus=link;
    title.textContent='原图较大，显示需要几秒。保存后可直接转发给客户。';
    img.alt=link.getAttribute('aria-label')||link.closest('article,figure,section')?.querySelector('h2,h3')?.textContent||'图片';
    img.src=link.href;
    layer.hidden=false;document.documentElement.classList.add('save-image-open');
    layer.querySelector('.save-image-close').focus();
  });
})();
