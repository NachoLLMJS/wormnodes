(()=>{
  const storageKey='wormnodes-language';
  const readLanguage=()=>{
    try{
      const saved=localStorage.getItem(storageKey);
      return saved==='en'||saved==='zh'?saved:'zh';
    }catch{return 'zh'}
  };
  let current=readLanguage();

  const apply=(language,{persist=true}={})=>{
    current=language==='en'?'en':'zh';
    document.documentElement.lang=current==='zh'?'zh-CN':'en';
    document.querySelectorAll('[data-en][data-zh]').forEach(node=>{
      const value=current==='en'?node.dataset.en:node.dataset.zh;
      if(value.includes('<'))node.innerHTML=value;
      else node.textContent=value;
    });
    document.querySelectorAll('[data-lang-toggle]').forEach(button=>{
      const face=button.querySelector('.sticker-btn-face, .docs-sticker-face')||button;
      face.textContent=current==='zh'?'EN':'中文';
      button.setAttribute('aria-label',current==='zh'?'Switch to English':'切换到中文');
    });
    const titles={
      '/':{en:'WORMNODES | Stake Apple Nodes',zh:'WORMNODES | 苹果节点质押'},
      '/profile/':{en:'WORMNODES Profile',zh:'WORMNODES 个人资料'}
    };
    const entry=titles[location.pathname];
    if(entry)document.title=entry[current];
    if(persist){
      try{localStorage.setItem(storageKey,current)}catch{}
    }
    window.dispatchEvent(new CustomEvent('wormnodes:languagechange',{detail:{language:current}}));
  };

  window.WormnodesLanguage={get:()=>current,apply};
  document.querySelectorAll('[data-lang-toggle]').forEach(button=>button.addEventListener('click',()=>apply(current==='zh'?'en':'zh')));
  apply(current,{persist:false});
})();
