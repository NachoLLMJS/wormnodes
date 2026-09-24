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
  let walletPending=false;
  let connectedAccount='';
  let walletStatus='';

  const language=()=>window.WormnodesLanguage?.get?.()||'zh';
  const isChinese=()=>language()==='zh';
  const twitterMessage=()=>isChinese()?'WORMNODES 官方 Twitter 链接尚未配置':'Official WORMNODES Twitter link has not been configured yet';
  const walletMissingMessage=()=>isChinese()
    ?'未检测到钱包。请安装 MetaMask 或其他兼容钱包后重试'
    :'No wallet detected. Install MetaMask or another compatible wallet and try again';
  const walletRejectedMessage=()=>isChinese()
    ?'钱包连接已取消。点击质押按钮可重试'
    :'Wallet connection was cancelled. Click the stake button to try again';
  const walletFailedMessage=()=>isChinese()
    ?'无法连接钱包。请在钱包中重试'
    :'Could not connect the wallet. Please try again in your wallet';
  const walletConnectedMessage=account=>{
    const short=`${account.slice(0,6)}…${account.slice(-4)}`;
    return isChinese()
      ?`钱包已连接：${short} — 质押合约配置完成前不会发送交易`
      :`Wallet connected: ${short} — no transaction will be sent until the staking contracts are configured`;
  };
  const currentWalletMessage=()=>{
    if(connectedAccount)return walletConnectedMessage(connectedAccount);
    if(walletStatus==='missing')return walletMissingMessage();
    if(walletStatus==='rejected')return walletRejectedMessage();
    if(walletStatus==='failed')return walletFailedMessage();
    return '';
  };

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
    if(statusActive)status.textContent=currentWalletMessage();
  };

  const open=trigger=>{
    lastTrigger=trigger;
    statusActive=false;
    walletStatus='';
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
  pay.addEventListener('click',async()=>{
    if(walletPending)return;
    statusActive=true;
    if(connectedAccount){
      walletStatus='connected';
      status.textContent=walletConnectedMessage(connectedAccount);
      return;
    }
    const provider=window.ethereum;
    if(!provider||typeof provider.request!=='function'){
      walletStatus='missing';
      status.textContent=walletMissingMessage();
      return;
    }
    walletPending=true;
    pay.disabled=true;
    pay.setAttribute('aria-busy','true');
    try{
      const accounts=await provider.request({method:'eth_requestAccounts'});
      const account=Array.isArray(accounts)&&typeof accounts[0]==='string'?accounts[0]:'';
      connectedAccount=/^0x[a-fA-F0-9]{40}$/.test(account)?account:'';
      walletStatus=connectedAccount?'connected':'failed';
      status.textContent=currentWalletMessage();
    }catch(error){
      walletStatus=error&&error.code===4001?'rejected':'failed';
      status.textContent=currentWalletMessage();
    }finally{
      walletPending=false;
      pay.disabled=false;
      pay.removeAttribute('aria-busy');
    }
  });
  window.addEventListener('wormnodes:languagechange',()=>{
    if(notice)notice.textContent=twitterMessage();
    if(lastTrigger&&!modal.hidden)renderModal(lastTrigger);
  });
  const deepLinked=location.hash&&document.querySelector(`[data-node-name][href="${location.hash}"]`);
  if(deepLinked)open(deepLinked);
})();
