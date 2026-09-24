from pathlib import Path
from bs4 import BeautifulSoup, Comment
import shutil

ROOT=Path(__file__).parent
HTML=ROOT/'site'/'index.html'
BACKUP=ROOT/'site'/'index-before-wormnodes-rebrand.html'
if not BACKUP.exists(): shutil.copy2(HTML,BACKUP)
soup=BeautifulSoup(HTML.read_text('utf8'),'html.parser')

# Metadata and local stylesheet.
soup.html['lang']='zh-CN'
soup.title.string='WORMNODES | 苹果节点质押'
for meta in list(soup.find_all('meta')):
    content=meta.get('content','')
    prop=(meta.get('property') or meta.get('name') or '').lower()
    if prop in {'description','og:description','twitter:description'}:
        meta['content']='使用 AAPLB 质押 ROYAL、FUJI 与 GOLDEN 苹果节点并获得收益'
    elif prop in {'og:title','twitter:title'}:
        meta['content']='WORMNODES | 苹果节点质押'
    elif prop in {'og:url','twitter:url','og:image','twitter:image','keywords'}:
        meta.decompose()
    elif 'pull.fun' in content.lower() or 'pull fun' in content.lower() or 'pullfun' in content.lower():
        meta['content']='WORMNODES'
for old_css in list(soup.head.find_all('link')):
    if 'wormnodes.css' in (old_css.get('href') or ''): old_css.decompose()
css=soup.new_tag('link',rel='stylesheet',href='/editable/wormnodes.css?v=12')
soup.head.append(css)

# Remove old icon links and install a local apple icon.
for link in list(soup.head.find_all('link')):
    rel=' '.join(link.get('rel',[])).lower()
    if 'icon' in rel:
        link.decompose()
icon=soup.new_tag('link',rel='icon',type='image/png',href='/assets/media/wormnodes-favicon.png?v=2')
soup.head.append(icon)

# Replace complete header to guarantee no legacy links or labels remain.
old_header=soup.find('header')
header_html='''<header id="top" class="fixed left-0 top-0 z-50 w-full">
<div class="relative w-full overflow-hidden py-2 select-none"><div class="flex w-max animate-[ticker_72s_linear_infinite] motion-reduce:animate-none"><span class="flex shrink-0 items-center gap-8 pr-8">'''+''.join('<span class="font-pixel text-[10px] uppercase leading-none tracking-[0.12em] text-black sm:text-[11px]" data-en="STAKE NODES · GROW YIELD · HARVEST APPLES · REPEAT" data-zh="质押节点 · 增长收益 · 收获苹果 · 循环">质押节点 · 增长收益 · 收获苹果 · 循环</span>' for _ in range(8))+'''</span></div></div>
<div class="wn-header-shell"><div class="flex w-full items-center gap-3 px-4 min-h-16 sm:min-h-[4.5rem] sm:px-6 xl:px-8"><a aria-label="WORMNODES home" href="#top"><img class="wn-header-logo" src="/assets/media/wormnodes-logo.png?v=3" alt="WORMNODES" width="1200" height="300" loading="eager"/></a><div class="flex-1"></div><nav class="wn-header-actions" aria-label="Primary navigation"><button class="sticker-btn wn-yellow-sticker wn-nav-link wn-language-button" type="button" data-lang-toggle aria-label="Switch to English"><span class="sticker-btn-face px-5 py-2 font-heading text-xs font-black uppercase tracking-wide text-white">EN</span></button><a class="sticker-btn wn-yellow-sticker wn-nav-link" href="/profile/" aria-label="Open WORMNODES profile"><span class="sticker-btn-face px-5 py-2 font-heading text-xs font-black uppercase tracking-wide text-white" data-en="PROFILE" data-zh="个人中心">个人中心</span></a><a class="sticker-btn wn-yellow-sticker wn-nav-link" href="https://x.com/WormNodes" target="_blank" rel="noopener noreferrer" aria-label="WORMNODES Twitter"><span class="sticker-btn-face px-5 py-2 font-heading text-xs font-black uppercase tracking-wide text-white">TWITTER</span></a></nav></div></div>
</header>'''
old_header.replace_with(BeautifulSoup(header_html,'html.parser').header)

# Hero copy.
h1=soup.find('h1')
if h1:
    h1.clear(); h1['data-en']='YOUR NEXT NODE<br>IS ONE APPLE AWAY!'; h1['data-zh']='你的下一个节点<br>只差一个苹果'; h1.append(BeautifulSoup('你的下一个节点<br/>只差一个苹果','html.parser'))
hero_list=soup.find('h1').find_next('ul') if soup.find('h1') else None
if hero_list:
    hero_list['class']=list(dict.fromkeys(hero_list.get('class',[])+['wn-hero-features']))
hero_items=hero_list.find_all('li') if hero_list else []
for li,en,zh in zip(hero_items,['STAKE WITH AAPLB','RUN YOUR NODE','HARVEST YIELD'],['使用 AAPLB 质押','运行你的节点','收获收益']):
    li.string=zh; li['data-en']=en; li['data-zh']=zh

# Remove the old yellow section label while preserving the #nodes anchor.
section_title=soup.select_one('.wn-section-title')
if section_title:
    section_title.decompose()
open_img=soup.find('img',alt='Open packs')
if open_img:
    open_img.decompose()
pack_grid=soup.select_one('#apple-pack-grid') or soup.select_one('#nodes')
if pack_grid:
    pack_grid['id']='apple-pack-grid'
    pack_grid['class']=[c for c in pack_grid.get('class',[]) if c != 'mt-7']
    pack_grid.find_parent('section')['id']='nodes'

# Three generated node tiers.
configs={
 'route one':dict(name='ROYAL',aaplb='0.022',lock='1 day',lock_zh='1 天',tier='ROYAL NODE',tier_zh='ROYAL 节点',mode='Daily yield',mode_zh='每日收益',image='/assets/media/node-pack-royal.png?v=2'),
 'victory road':dict(name='FUJI',aaplb='0.293',lock='1 week',lock_zh='1 周',tier='FUJI NODE',tier_zh='FUJI 节点',mode='Weekly yield',mode_zh='每周收益',image='/assets/media/node-pack-fuji.png?v=2'),
 'mt. silver':dict(name='GOLDEN',aaplb='2.95',lock='1 month',lock_zh='1 个月',tier='GOLDEN NODE',tier_zh='GOLDEN 节点',mode='Monthly yield',mode_zh='每月收益',image='/assets/media/node-pack-golden.png?v=2'),
 'royal':dict(name='ROYAL',aaplb='0.022',lock='1 day',lock_zh='1 天',tier='ROYAL NODE',tier_zh='ROYAL 节点',mode='Daily yield',mode_zh='每日收益',image='/assets/media/node-pack-royal.png?v=2'),
 'fuji':dict(name='FUJI',aaplb='0.293',lock='1 week',lock_zh='1 周',tier='FUJI NODE',tier_zh='FUJI 节点',mode='Weekly yield',mode_zh='每周收益',image='/assets/media/node-pack-fuji.png?v=2'),
 'golden':dict(name='GOLDEN',aaplb='2.95',lock='1 month',lock_zh='1 个月',tier='GOLDEN NODE',tier_zh='GOLDEN 节点',mode='Monthly yield',mode_zh='每月收益',image='/assets/media/node-pack-golden.png?v=2'),
}
grid=soup.select_one('#apple-pack-grid')
if not grid: raise RuntimeError('apple pack grid missing')
for heading in grid.find_all('h3'):
    key=heading.get_text(' ',strip=True).lower()
    cfg=configs.get(key)
    if not cfg: continue
    card=heading.find_parent('a')
    card['href']='#node-'+cfg['name'].lower()
    card['role']='button';card['tabindex']='0'
    card['data-node-name']=cfg['name'];card['data-node-aaplb']=cfg['aaplb'];card['data-node-lock']=cfg['lock'];card['data-node-lock-zh']=cfg['lock_zh'];card['data-node-tier']=cfg['tier'];card['data-node-tier-zh']=cfg['tier_zh'];card['data-node-mode']=cfg['mode'];card['data-node-mode-zh']=cfg['mode_zh'];card['data-node-image']=cfg['image']
    card.attrs.pop('data-node-price',None);card.attrs.pop('data-node-usd',None)
    heading.string=cfg['name']
    pack=next(i for i in card.find_all('img') if 'tile-pack' in ' '.join(i.get('class',[])))
    pack['src']=cfg['image'];pack.attrs.pop('srcset',None);pack['alt']=cfg['name']+' apple node package';pack.attrs.pop('aria-hidden',None)
    overlay=heading.parent
    badge=overlay.find('span',recursive=False)
    badge.clear()
    strong=soup.new_tag('span');strong['class']=['font-heading','text-base','font-black','leading-none','tracking-normal','text-white','sm:text-lg'];strong.string=cfg['aaplb']+' AAPLB'
    badge.append(strong)
    face=card.select_one('.sticker-btn-face')
    if face:
        face.string='查看节点'; face['data-en']='VIEW NODE'; face['data-zh']='查看节点'
        face.parent['class']=list(dict.fromkeys(face.parent.get('class',[])+['wn-yellow-sticker']))

# Remove every original post-pack section and replace with node-specific value section.
pack_section=grid.find_parent('section')
for sibling in list(pack_section.find_next_siblings()): sibling.decompose()
yield_html='''<section class="wn-yield-section" aria-labelledby="yield-title"><h2 id="yield-title" data-en="STAKE YOUR NODE<br><span>GROW YOUR YIELD</span>" data-zh="质押你的节点<br><span>增长你的收益</span>">质押你的节点<br/><span>增长你的收益</span></h2><p data-en="Stake AAPLB in a Royal, Fuji or Golden apple node, keep it locked for the selected period, and harvest rewards from the same dashboard" data-zh="在 ROYAL、FUJI 或 GOLDEN 苹果节点中质押 AAPLB，在指定周期内保持锁定，并通过同一控制面板收获收益">在 ROYAL、FUJI 或 GOLDEN 苹果节点中质押 AAPLB，在指定周期内保持锁定，并通过同一控制面板收获收益</p><div class="wn-benefits"><article class="wn-benefit"><strong data-en="Stake AAPLB" data-zh="质押 AAPLB">质押 AAPLB</strong><span data-en="Each package locks a defined amount of AAPLB for its node period" data-zh="每个节点包会在对应周期内锁定指定数量的 AAPLB">每个节点包会在对应周期内锁定指定数量的 AAPLB</span></article><article class="wn-benefit"><strong data-en="Run the node" data-zh="运行节点">运行节点</strong><span data-en="Your selected node remains staked and tracks its yield status continuously" data-zh="所选节点保持质押状态，并持续追踪收益进度">所选节点保持质押状态，并持续追踪收益进度</span></article><article class="wn-benefit"><strong data-en="Harvest yield" data-zh="收获收益">收获收益</strong><span data-en="Review accumulated rewards and harvest when node settlement is enabled" data-zh="查看累计奖励，并在节点结算启用后执行收获">查看累计奖励，并在节点结算启用后执行收获</span></article></div></section>'''
pack_section.insert_after(BeautifulSoup(yield_html,'html.parser').section)

# Replace footer action with same-tab documentation navigation.
old_footer=soup.find('footer')
footer_html='''<footer class="wn-footer"><a class="sticker-btn wn-yellow-sticker wn-twitter" href="/docs/" aria-label="Open WORMNODES docs"><span class="sticker-btn-face px-7 py-2.5 font-heading text-sm font-black uppercase tracking-wide text-white sm:text-base" data-en="DOCS" data-zh="文档">文档</span></a></footer>'''
if old_footer: old_footer.replace_with(BeautifulSoup(footer_html,'html.parser').footer)

# Remove legacy floating music control.
for button in list(soup.find_all('button')):
    if (button.get('aria-label') or '').lower() in {'music','close'} or button.get_text(' ',strip=True).lower()=='music':
        button.decompose()

# Honest local AAPLB checkout modal; no transaction is fabricated.
old_modal=soup.select_one('#node-modal')
if old_modal: old_modal.decompose()
modal_html='''<div id="node-modal" class="wn-modal" hidden><div class="wn-modal-backdrop" data-close-modal></div><section class="wn-dialog" role="dialog" aria-modal="true" aria-labelledby="node-modal-title"><button class="wn-close" type="button" aria-label="Close node staking" data-close-modal>×</button><div class="wn-modal-art"><img id="node-modal-image" src="/assets/media/node-pack-royal.png?v=2" alt="Royal node package"/></div><div class="wn-modal-copy"><span class="wn-kicker" data-en="AAPLB NODE STAKING" data-zh="AAPLB 节点质押">AAPLB 节点质押</span><h2 id="node-modal-title">ROYAL</h2><p data-en="Stake AAPLB for the selected lock period, run your apple node, and receive yield through the WORMNODES node cycle" data-zh="在所选锁定周期内质押 AAPLB，运行你的苹果节点，并通过 WORMNODES 节点周期获得收益">在所选锁定周期内质押 AAPLB，运行你的苹果节点，并通过 WORMNODES 节点周期获得收益</p><div class="wn-node-stats"><div class="wn-stat"><small data-en="Node tier" data-zh="节点等级">节点等级</small><b id="node-modal-tier">ROYAL 节点</b></div><div class="wn-stat"><small data-en="Yield mode" data-zh="收益模式">收益模式</small><b id="node-modal-mode">每日收益</b></div><div class="wn-stat"><small data-en="Staked asset" data-zh="质押资产">质押资产</small><b>AAPLB</b></div><div class="wn-stat"><small data-en="Lock period" data-zh="锁定周期">锁定周期</small><b id="node-modal-lock">1 天</b></div></div><div class="wn-price"><span data-en="AAPLB stake" data-zh="AAPLB 质押数量">AAPLB 质押数量</span><strong id="node-modal-price">0.022 AAPLB</strong></div><button id="node-modal-pay" class="sticker-btn wn-yellow-sticker wn-pay-button" type="button"><span class="sticker-btn-face px-7 py-2.5 font-heading text-sm font-black uppercase tracking-wide text-white sm:text-base">质押 0.022 AAPLB</span></button><p id="node-payment-status" class="wn-payment-status" aria-live="polite"></p></div></section></div>'''
soup.body.append(BeautifulSoup(modal_html,'html.parser').div)
for old_js in list(soup.find_all('script')):
    if 'wormnodes.js' in (old_js.get('src') or '') or 'wormnodes-lang.js' in (old_js.get('src') or ''): old_js.decompose()
lang_js=soup.new_tag('script',src='/editable/wormnodes-lang.js?v=2',defer=True);soup.body.append(lang_js)
js=soup.new_tag('script',src='/editable/wormnodes.js?v=9',defer=True);soup.body.append(js)

# Remove all HTML comments and any residual attributes that point at the old site.
for c in soup.find_all(string=lambda x:isinstance(x,Comment)): c.extract()
for tag in soup.find_all(True):
    for attr,val in list(tag.attrs.items()):
        text=' '.join(val) if isinstance(val,list) else str(val)
        if 'pull.fun' in text.lower() or 'pulldotfun' in text.lower() or 'pullfun' in text.lower():
            del tag.attrs[attr]

HTML.write_text(str(soup),'utf8')
print('WORMNODES rebrand applied')
