(()=>{
  const modal=document.getElementById('node-modal');
  if(!modal)return;
  const title=document.getElementById('node-modal-title');
  const image=document.getElementById('node-modal-image');
  const tier=document.getElementById('node-modal-tier');
  const price=document.getElementById('node-modal-price');
  const mode=document.getElementById('node-modal-mode');
  const lock=document.getElementById('node-modal-lock');
  const pay=document.getElementById('node-modal-pay');
  const status=document.getElementById('node-payment-status');
  const pendingTwitter=document.querySelector('[data-twitter-pending]');
  let noticeTimer;
  let lastTrigger=null;
  let statusActive=false;

  const language=()=>window.WormnodesLanguage?.get?.()||'zh';
  const isChinese=()=>language()==='zh';
  const twitterMessage=()=>isChinese()?'WORMNODES 官方 Twitter 链接尚未配置':'Official WORMNODES Twitter link has not been configured yet';
  const paymentMessage=()=>isChinese()
    ?'AAPLB 质押预览已准备就绪 — 由于 AAPLB 代币合约和质押合约尚未配置，因此未发送任何交易'
    :'AAPLB staking preview ready — no transaction was sent because the AAPLB token contract and staking contract have not been configured yet';

  let notice=null;
  if(pendingTwitter){
    notice=document.createElement('div');
    notice.className='wn-social-notice';
    notice.id='twitter-not-configured';
    notice.setAttribute('role','status');
    notice.textContent=twitterMessage();
    document.body.appendChild(notice);
    pendingTwitter.addEventListener('click',event=>{
      event.preventDefault();
      notice.textContent=twitterMessage();
      notice.classList.add('is-visible');
      clearTimeout(noticeTimer);
      noticeTimer=setTimeout(()=>notice.classList.remove('is-visible'),3200);
    });
  }

  const renderModal=trigger=>{
    const zh=isChinese();
    title.textContent=trigger.dataset.nodeName;
    tier.textContent=zh?trigger.dataset.nodeTierZh:trigger.dataset.nodeTier;
    price.textContent=`${trigger.dataset.nodeAaplb} AAPLB`;
    mode.textContent=zh?trigger.dataset.nodeModeZh:trigger.dataset.nodeMode;
    lock.textContent=zh?trigger.dataset.nodeLockZh:trigger.dataset.nodeLock;
    image.src=trigger.dataset.nodeImage;
    image.alt=zh?`${trigger.dataset.nodeName} 节点包`:`${trigger.dataset.nodeName} node package`;
    pay.querySelector('.sticker-btn-face').textContent=`${zh?'质押':'STAKE'} ${trigger.dataset.nodeAaplb} AAPLB`;
    if(statusActive)status.textContent=paymentMessage();
  };

  const open=trigger=>{
    lastTrigger=trigger;
    statusActive=false;
    status.textContent='';
    renderModal(trigger);
    modal.hidden=false;
    document.body.classList.add('wn-modal-open');
    modal.querySelector('.wn-close').focus();
  };
  const close=()=>{
    modal.hidden=true;
    document.body.classList.remove('wn-modal-open');
    if(lastTrigger)lastTrigger.focus();
  };

  document.querySelectorAll('[data-node-name]').forEach(trigger=>{
    trigger.addEventListener('click',event=>{event.preventDefault();open(trigger)});
    trigger.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();open(trigger)}});
  });
  modal.querySelectorAll('[data-close-modal]').forEach(element=>element.addEventListener('click',close));
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!modal.hidden)close()});
  pay.addEventListener('click',()=>{
    statusActive=true;
    status.textContent=paymentMessage();
  });
  window.addEventListener('wormnodes:languagechange',()=>{
    if(notice)notice.textContent=twitterMessage();
    if(lastTrigger&&!modal.hidden)renderModal(lastTrigger);
  });
  const deepLinked=location.hash&&document.querySelector(`[data-node-name][href="${location.hash}"]`);
  if(deepLinked)open(deepLinked);
})();
