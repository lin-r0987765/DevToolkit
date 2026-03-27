import argparse
import json
import io
import contextlib
import sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from devtoolkit.core.plugin import BaseTool
import devtoolkit.main as core_main

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevToolkit ⚡</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0a0e1a;
            --bg-glass: rgba(15, 20, 35, 0.7);
            --border-glass: rgba(255,255,255,0.06);
            --border-glow: rgba(139,92,246,0.5);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent: #8b5cf6;
            --accent2: #06b6d4;
            --accent3: #f472b6;
            --gradient: linear-gradient(135deg, #8b5cf6, #06b6d4);
            --gradient2: linear-gradient(135deg, #f472b6, #8b5cf6);
            --success: #34d399;
            --error: #f87171;
        }
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Inter',sans-serif;background:var(--bg-base);color:var(--text-primary);min-height:100vh;overflow-x:hidden}
        canvas#particles{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}

        /* Header */
        header{position:sticky;top:0;z-index:100;padding:1rem 2.5rem;display:flex;align-items:center;justify-content:space-between;
            background:rgba(10,14,26,0.8);backdrop-filter:blur(20px);border-bottom:1px solid var(--border-glass)}
        .logo{display:flex;align-items:center;gap:.8rem;font-family:'Outfit';font-weight:800;font-size:1.6rem}
        .logo-icon{font-size:1.8rem;animation:bounce 2s infinite}
        .logo-text{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .logo-tagline{font-size:.8rem;color:var(--text-muted);font-weight:400;margin-left:.5rem;letter-spacing:1px}
        .header-right{display:flex;align-items:center;gap:1rem}
        .tool-count{background:var(--gradient);padding:.3rem .8rem;border-radius:20px;font-size:.75rem;font-weight:700;letter-spacing:1px}
        @keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}

        /* Layout */
        main{position:relative;z-index:1;display:grid;grid-template-columns:300px 1fr;gap:1.5rem;max-width:1600px;margin:0 auto;padding:1.5rem 2.5rem;width:100%;height:calc(100vh - 65px)}
        .glass{background:var(--bg-glass);border:1px solid var(--border-glass);border-radius:16px;backdrop-filter:blur(20px)}

        /* Sidebar */
        .sidebar{display:flex;flex-direction:column;overflow:hidden}
        .sidebar-top{padding:1rem 1rem .5rem}
        .search-box{width:100%;padding:.65rem 1rem .65rem 2.4rem;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.08);border-radius:10px;color:var(--text-primary);font-size:.85rem;outline:none;transition:all .2s;font-family:'Inter'}
        .search-box:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(139,92,246,.15)}
        .search-box::placeholder{color:rgba(148,163,184,.4)}
        .search-wrap{position:relative}
        .search-wrap::before{content:'🔍';position:absolute;left:.75rem;top:50%;transform:translateY(-50%);font-size:.8rem}
        #tools-list{flex:1;overflow-y:auto;padding:.5rem 1rem 1rem;display:flex;flex-direction:column;gap:4px}

        .tool-btn{background:transparent;border:1px solid transparent;color:var(--text-primary);padding:.75rem 1rem;text-align:left;border-radius:12px;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:.75rem;position:relative;overflow:hidden}
        .tool-btn:hover{background:rgba(139,92,246,.06);border-color:rgba(139,92,246,.15);transform:translateX(3px)}
        .tool-btn.active{background:rgba(139,92,246,.12);border-color:var(--border-glow);box-shadow:0 0 15px rgba(139,92,246,.1)}
        .tool-emoji{font-size:1.4rem;flex-shrink:0;width:36px;height:36px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.04);border-radius:10px}
        .tool-info{flex:1;min-width:0}
        .tool-name{font-family:'Outfit';font-weight:600;font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .tool-btn.active .tool-name{color:var(--accent)}
        .tool-desc{font-size:.7rem;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}

        /* Content */
        .content{display:flex;flex-direction:column;gap:1.5rem;overflow:hidden}
        .config-panel{flex-shrink:0;padding:2rem;max-height:50%;overflow-y:auto}
        .config-header{margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem}
        .config-header h2{font-family:'Outfit';font-size:1.8rem;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
        .config-header p{color:var(--text-secondary);font-size:.9rem;flex:1}
        .form-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}
        .form-group{display:flex;flex-direction:column;gap:.5rem;background:rgba(0,0,0,.2);padding:1rem;border-radius:10px;border:1px solid rgba(255,255,255,.03);transition:all .2s}
        .form-group:focus-within{border-color:rgba(139,92,246,.4);background:rgba(139,92,246,.03)}
        label{font-family:'Outfit';font-size:.85rem;font-weight:600;color:var(--text-primary);letter-spacing:.3px}
        .help-text{font-size:.75rem;color:var(--text-muted);line-height:1.3}
        input[type="text"],input[type="number"],select{background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.08);color:var(--text-primary);padding:.7rem .85rem;border-radius:8px;font-size:.9rem;outline:none;transition:all .2s;width:100%;font-family:'Inter'}
        input[type="text"]:focus,input[type="number"]:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(139,92,246,.12)}
        input::placeholder{color:rgba(148,163,184,.35)}
        .checkbox-wrapper{display:flex;align-items:center;justify-content:space-between;cursor:pointer;width:100%}
        .checkbox-wrapper span{font-family:'Outfit';font-weight:600;font-size:.9rem}
        input[type="checkbox"]{appearance:none;-webkit-appearance:none;width:42px;height:22px;background:rgba(255,255,255,.1);border-radius:11px;position:relative;cursor:pointer;outline:none;border:none;transition:background .3s;flex-shrink:0}
        input[type="checkbox"]::after{content:'';position:absolute;top:2px;left:2px;width:18px;height:18px;background:#fff;border-radius:50%;transition:transform .3s cubic-bezier(.4,0,.2,1);box-shadow:0 1px 3px rgba(0,0,0,.3)}
        input[type="checkbox"]:checked{background:var(--accent)}
        input[type="checkbox"]:checked::after{transform:translateX(20px)}

        .action-row{display:flex;justify-content:space-between;align-items:center;margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border-glass)}
        .shortcut-hint{font-size:.75rem;color:var(--text-muted)}
        .shortcut-hint kbd{background:rgba(255,255,255,.08);padding:2px 6px;border-radius:4px;font-family:'SFMono-Regular',Consolas,monospace;font-size:.7rem;border:1px solid rgba(255,255,255,.1)}
        .btn-run{background:var(--gradient);color:white;border:none;padding:.85rem 2.5rem;border-radius:12px;font-size:1rem;font-family:'Outfit';font-weight:700;cursor:pointer;transition:all .3s cubic-bezier(.175,.885,.32,1.275);box-shadow:0 6px 20px rgba(139,92,246,.35);display:flex;align-items:center;gap:.6rem;position:relative;overflow:hidden;letter-spacing:.5px}
        .btn-run:hover{transform:translateY(-2px) scale(1.03);box-shadow:0 10px 25px rgba(139,92,246,.45)}
        .btn-run:active{transform:translateY(1px) scale(.98)}
        .btn-run:disabled{opacity:.5;cursor:not-allowed;transform:none;box-shadow:none}
        .loader{display:none;width:16px;height:16px;border:2px solid rgba(255,255,255,.3);border-radius:50%;border-top-color:#fff;animation:spin .8s linear infinite}
        .btn-run.loading .loader{display:block}
        .btn-run.loading .btn-text{display:none}
        @keyframes spin{to{transform:rotate(360deg)}}

        /* Terminal */
        .output-panel{flex:1;display:flex;flex-direction:column;overflow:hidden;background:#0c1018;border:1px solid var(--border-glass);border-radius:16px;box-shadow:inset 0 2px 15px rgba(0,0,0,.4)}
        .output-header{display:flex;justify-content:space-between;align-items:center;padding:.75rem 1.2rem;background:rgba(15,20,30,.95);border-bottom:1px solid rgba(255,255,255,.04)}
        .mac-controls{display:flex;gap:7px}
        .mac-btn{width:11px;height:11px;border-radius:50%}
        .mac-close{background:#ff5f56}
        .mac-min{background:#ffbd2e}
        .mac-max{background:#27c93f}
        .output-title{font-family:'SFMono-Regular',Consolas,monospace;font-size:.8rem;color:var(--text-muted);flex:1;text-align:center}
        .terminal{flex:1;padding:1rem 1.2rem;overflow-y:auto;font-family:'JetBrains Mono','Fira Code','SFMono-Regular',Consolas,monospace;font-size:.85rem;line-height:1.6;color:#a5d6ff;white-space:pre-wrap;word-wrap:break-word}
        .terminal .prompt{color:#34d399;font-weight:bold}
        .terminal.error{color:#f87171}
        .btn-clear{background:transparent;border:1px solid rgba(255,255,255,.08);color:var(--text-muted);cursor:pointer;font-size:.7rem;padding:.3rem .6rem;border-radius:5px;transition:all .2s;font-family:'Outfit';font-weight:600}
        .btn-clear:hover{background:rgba(255,255,255,.05);color:var(--text-primary)}

        /* Toast */
        .toast{position:fixed;bottom:2rem;right:2rem;padding:.8rem 1.5rem;border-radius:12px;font-size:.85rem;font-family:'Outfit';font-weight:600;z-index:999;animation:toastIn .4s ease-out;display:flex;align-items:center;gap:.5rem;box-shadow:0 8px 30px rgba(0,0,0,.4);backdrop-filter:blur(10px)}
        .toast-success{background:rgba(52,211,153,.15);border:1px solid rgba(52,211,153,.3);color:#34d399}
        .toast-error{background:rgba(248,113,113,.15);border:1px solid rgba(248,113,113,.3);color:#f87171}
        @keyframes toastIn{from{opacity:0;transform:translateY(20px) scale(.9)}to{opacity:1;transform:translateY(0) scale(1)}}
        @keyframes toastOut{from{opacity:1;transform:translateY(0)}to{opacity:0;transform:translateY(-10px)}}

        /* Confetti */
        .confetti{position:fixed;top:0;left:0;width:100%;height:100%;z-index:998;pointer-events:none}
        .confetti-piece{position:absolute;width:8px;height:8px;border-radius:2px;animation:confettiFall 1.5s ease-out forwards}
        @keyframes confettiFall{0%{opacity:1;transform:translateY(0) rotate(0deg) scale(1)}100%{opacity:0;transform:translateY(80vh) rotate(720deg) scale(0)}}

        /* Scrollbar */
        ::-webkit-scrollbar{width:6px;height:6px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:rgba(255,255,255,.08);border-radius:10px}
        ::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.15)}

        @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        @media(max-width:1024px){main{grid-template-columns:1fr;height:auto;padding:1rem}.sidebar{max-height:300px}}
    </style>
</head>
<body>
    <canvas id="particles"></canvas>

    <header>
        <div class="logo">
            <span class="logo-icon">⚡</span>
            <span class="logo-text">DevToolkit</span>
            <span class="logo-tagline">你的瑞士刀 🇨🇭</span>
        </div>
        <div class="header-right">
            <span class="tool-count" id="tool-count">🧰 載入中...</span>
        </div>
    </header>

    <main>
        <aside class="glass sidebar">
            <div class="sidebar-top">
                <div class="search-wrap">
                    <input type="text" class="search-box" id="search-input" placeholder="搜尋工具..." autocomplete="off">
                </div>
            </div>
            <div id="tools-list"></div>
        </aside>

        <section class="content">
            <div class="glass config-panel">
                <div id="empty-state" style="text-align:center;color:var(--text-muted);padding:3rem 2rem;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center">
                    <div style="font-size:3.5rem;margin-bottom:1rem" id="greeting-emoji">👋</div>
                    <h3 style="font-family:'Outfit';font-size:1.5rem;font-weight:800;color:var(--text-primary);margin-bottom:.4rem" id="greeting-text">嗨！選一個工具玩玩吧</h3>
                    <p style="font-size:.9rem">從左邊選一個工具，右邊會自動出現設定項 ✨</p>
                </div>

                <div id="tool-config" style="display:none">
                    <div class="config-header">
                        <h2 id="current-tool-title">工具</h2>
                        <p id="current-tool-desc">描述</p>
                    </div>
                    <form id="config-form" class="form-grid"></form>
                    <div class="action-row">
                        <div class="shortcut-hint">💡 快捷鍵: <kbd>Ctrl</kbd> + <kbd>Enter</kbd></div>
                        <button id="run-btn" class="btn-run" type="button">
                            <span class="btn-text">🚀 開始執行</span>
                            <span class="loader"></span>
                        </button>
                    </div>
                </div>
            </div>

            <div class="output-panel">
                <div class="output-header">
                    <div class="mac-controls">
                        <div class="mac-btn mac-close"></div>
                        <div class="mac-btn mac-min"></div>
                        <div class="mac-btn mac-max"></div>
                    </div>
                    <div class="output-title">終端機 — DevToolkit</div>
                    <button type="button" class="btn-clear" id="clear-btn">清除</button>
                </div>
                <div id="terminal-out" class="terminal"><span class="prompt">❯</span> 準備就緒 ✅
</div>
            </div>
        </section>
    </main>

    <script>
        // Particle background
        (function(){
            const c=document.getElementById('particles'),ctx=c.getContext('2d');
            let w,h,dots=[];
            function resize(){w=c.width=innerWidth;h=c.height=innerHeight;dots=[];for(let i=0;i<60;i++)dots.push({x:Math.random()*w,y:Math.random()*h,r:Math.random()*1.5+.5,dx:(Math.random()-.5)*.3,dy:(Math.random()-.5)*.3,o:Math.random()*.3+.1})}
            function draw(){ctx.clearRect(0,0,w,h);dots.forEach(d=>{d.x+=d.dx;d.y+=d.dy;if(d.x<0||d.x>w)d.dx*=-1;if(d.y<0||d.y>h)d.dy*=-1;ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,Math.PI*2);ctx.fillStyle=`rgba(139,92,246,${d.o})`;ctx.fill()});requestAnimationFrame(draw)}
            resize();draw();addEventListener('resize',resize);
        })();

        // Toast system
        function showToast(msg,type='success'){
            const t=document.createElement('div');t.className='toast toast-'+type;t.innerHTML=msg;document.body.appendChild(t);
            setTimeout(()=>{t.style.animation='toastOut .3s ease-out forwards';setTimeout(()=>t.remove(),300)},2500);
        }

        // Confetti
        function confetti(){
            const container=document.createElement('div');container.className='confetti';document.body.appendChild(container);
            const colors=['#8b5cf6','#06b6d4','#f472b6','#34d399','#fbbf24','#f87171'];
            for(let i=0;i<40;i++){const p=document.createElement('div');p.className='confetti-piece';p.style.left=Math.random()*100+'%';p.style.top=-10+'px';p.style.background=colors[i%colors.length];p.style.animationDelay=Math.random()*.5+'s';p.style.animationDuration=(1+Math.random())+'s';container.appendChild(p)}
            setTimeout(()=>container.remove(),2500);
        }

        let allTools=[],filteredTools=[],currentTool=null,execCount=0;

        const greetings=['👋 嗨！選一個工具玩玩吧','🎯 今天想用哪個工具？','🔥 來點刺激的吧！','💡 選個工具來試試手氣','🎮 工具箱已就緒，開始吧！','🌟 有什麼需要幫忙的？'];

        async function fetchTools(){
            try{
                const r=await fetch('/api/tools');allTools=await r.json();filteredTools=[...allTools];
                document.getElementById('tool-count').textContent='🧰 '+allTools.length+' 個工具';
                renderToolsList();
                if(allTools.length>0)selectTool(allTools[0]);
                showToast('🎉 已載入 '+allTools.length+' 個工具！');
            }catch(e){
                console.error(e);
                document.getElementById('tools-list').innerHTML='<div style="color:var(--error);padding:2rem;text-align:center">😵 載入失敗<br><small>後端是不是還沒開？</small></div>';
                document.getElementById('tool-count').textContent='❌ 離線';
            }
        }

        function renderToolsList(){
            const list=document.getElementById('tools-list');list.innerHTML='';
            const emojiMap={'base64':'🔐','baseconv':'🔢','colorconv':'🎨','cronhelp':'⏰','dice':'🎲','epoch':'🕐','hashit':'🔑','jsonfmt':'📋','lorem':'📝','note':'🗒️','passgen':'🔒','rot13':'🔄','sysinfo':'💻','timer':'⏱️','uuidgen':'🆔','weather':'🌤️','webui':'🌐','wordcount':'📊'};
            filteredTools.forEach((tool,i)=>{
                const btn=document.createElement('button');btn.className='tool-btn';btn.id='btn-'+tool.name;
                btn.style.animation='fadeIn .25s ease-out forwards '+(i*0.03)+'s';btn.style.opacity='0';
                btn.onclick=()=>selectTool(tool);
                const emoji=emojiMap[tool.name]||'🔧';
                const nameEl=document.createElement('div');nameEl.className='tool-emoji';nameEl.textContent=emoji;
                const info=document.createElement('div');info.className='tool-info';
                info.innerHTML='<div class="tool-name">'+tool.name+'</div><div class="tool-desc">'+tool.description+'</div>';
                btn.appendChild(nameEl);btn.appendChild(info);list.appendChild(btn);
            });
        }

        document.getElementById('search-input').addEventListener('input',function(){
            const q=this.value.toLowerCase();
            filteredTools=allTools.filter(t=>t.name.toLowerCase().includes(q)||t.description.toLowerCase().includes(q));
            renderToolsList();
        });

        function selectTool(tool){
            currentTool=tool;
            document.querySelectorAll('.tool-btn').forEach(b=>b.classList.remove('active'));
            const ab=document.getElementById('btn-'+tool.name);if(ab)ab.classList.add('active');
            document.getElementById('empty-state').style.display='none';
            const cfg=document.getElementById('tool-config');cfg.style.display='block';
            cfg.style.animation='none';void cfg.offsetWidth;cfg.style.animation='fadeIn .3s ease-out forwards';
            document.getElementById('current-tool-title').innerText=tool.name;
            document.getElementById('current-tool-desc').innerText=tool.description;
            renderForm(tool.args);
        }

        function renderForm(args){
            const form=document.getElementById('config-form');form.innerHTML='';let has=false;
            args.forEach(arg=>{
                has=true;const g=document.createElement('div');g.className='form-group';
                let name=arg.dest;const isFlag=arg.flags&&arg.flags.length>0;
                let labelName=isFlag?arg.flags.join(', '):name.toUpperCase();
                const helpText=arg.help||'';const type=arg.type||'str';
                const isBool=(arg.nargs===0||type==='bool'||arg.action==='store_true'||arg.action==='store_false');
                if(isBool){g.innerHTML='<label class="checkbox-wrapper" for="input-'+name+'"><span>'+labelName+'</span><input type="checkbox" id="input-'+name+'" name="'+name+'"></label>'+(helpText?'<div class="help-text">'+helpText+'</div>':'')}
                else if(arg.choices){let opts=arg.choices.map(c=>'<option value="'+c+'"'+(arg.default===c?' selected':'')+'>'+c+'</option>').join('');g.innerHTML='<label for="input-'+name+'">'+labelName+'</label><select id="input-'+name+'" name="'+name+'"><option value="">-- 請選擇 --</option>'+opts+'</select>'+(helpText?'<div class="help-text">'+helpText+'</div>':'')}
                else{const it=(type==='int'||type==='float')?'number':'text';let ph=arg.default!==null&&arg.default!==undefined?'預設: '+arg.default:'請輸入...';g.innerHTML='<label for="input-'+name+'">'+labelName+'</label><input type="'+it+'" id="input-'+name+'" name="'+name+'" placeholder="'+ph+'">'+(helpText?'<div class="help-text">'+helpText+'</div>':'')}
                form.appendChild(g);
            });
            if(!has)form.innerHTML='<div style="color:var(--text-muted);grid-column:1/-1;padding:1.5rem;text-align:center;border:1px dashed rgba(255,255,255,.08);border-radius:10px">🎯 此工具不需要額外參數，直接執行就好！</div>';
        }

        async function executeTool(){
            if(!currentTool)return;
            const btn=document.getElementById('run-btn'),term=document.getElementById('terminal-out');
            const formObj=new FormData(document.getElementById('config-form')),data={};
            currentTool.args.forEach(arg=>{
                const isBool=(arg.nargs===0||arg.type==='bool'||arg.action==='store_true'||arg.action==='store_false');
                if(isBool){data[arg.dest]=document.getElementById('input-'+arg.dest)?.checked||false}
                else{const v=formObj.get(arg.dest);if(v)data[arg.dest]=v}
            });
            btn.classList.add('loading');btn.disabled=true;term.classList.remove('error');
            term.innerHTML+='\n<span class="prompt">❯</span> <span style="color:#8b5cf6">devtoolkit '+currentTool.name+'</span>\n';
            term.scrollTop=term.scrollHeight;
            try{
                const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool:currentTool.name,args:data})});
                const result=await r.json();
                if(r.ok){
                    let out=result.output||'(無輸出)';out=out.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
                    term.innerHTML+=out;execCount++;confetti();
                    showToast('✅ '+currentTool.name+' 執行成功！ (第 '+execCount+' 次)');
                }else{
                    term.classList.add('error');
                    let e='❌ 錯誤: '+(result.error||'未知錯誤');e=e.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
                    term.innerHTML+=e+'\n'+(result.output?result.output.replace(/</g,'&lt;'):'');
                    showToast('💥 執行失敗了...','error');
                }
                term.scrollTop=term.scrollHeight;
            }catch(e){term.classList.add('error');term.innerHTML+='🌐 網路錯誤: '+e.message+'\n';showToast('📡 連不上伺服器','error')}
            finally{btn.classList.remove('loading');btn.disabled=false}
        }

        document.getElementById('run-btn').addEventListener('click',executeTool);
        document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();executeTool()}});

        document.getElementById('clear-btn').addEventListener('click',()=>{
            document.getElementById('terminal-out').innerHTML='<span class="prompt">❯</span> 已清除 🧹\n';
            showToast('🧹 終端機已清除');
        });

        // Random greeting
        const ge=document.getElementById('greeting-emoji'),gt=document.getElementById('greeting-text');
        const g=greetings[Math.floor(Math.random()*greetings.length)];
        if(gt)gt.textContent=g;
        if(ge){const emojis=['👋','🎯','🔥','💡','🎮','🌟'];ge.textContent=emojis[Math.floor(Math.random()*emojis.length)]}

        fetchTools().catch(console.error);
    </script>
</body>
</html>"""

class SafeArgumentParser(argparse.ArgumentParser):
    """An ArgumentParser that raises exceptions instead of exiting sys.exit() on error."""
    def error(self, message):
         raise Exception(message)
    def exit(self, status=0, message=None):
         if status != 0:
             raise Exception(message if message else f"Exit with status {status}")

class WebUIHandler(BaseHTTPRequestHandler):
    tools_cache = None
    
    def log_message(self, format, *args):
        pass

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            body = HTML_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True
        elif self.path.startswith('/api/tools'):
            if WebUIHandler.tools_cache is None:
                WebUIHandler.tools_cache = core_main.discover_tools()
            
            tool_list = []
            for name, tool in sorted(WebUIHandler.tools_cache.items()):
                if name == "webui": continue
                
                parser = SafeArgumentParser()
                tool.add_arguments(parser)
                
                args_info = []
                for action in parser._actions:
                    if action.dest == 'help': continue
                    args_info.append({
                        "flags": action.option_strings,
                        "dest": action.dest,
                        "help": action.help,
                        "default": action.default if not callable(action.default) else None,
                        "type": action.type.__name__ if hasattr(action.type, '__name__') else "str",
                        "choices": action.choices,
                        "required": action.required,
                        "nargs": action.nargs,
                        "action": action.__class__.__name__.lower()
                    })
                
                tool_list.append({
                    "name": name,
                    "description": tool.description,
                    "args": args_info
                })
            
            body = json.dumps(tool_list).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == '/api/run':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                try:
                    data = json.loads(body)
                except Exception:
                    data = {}
            else:
                data = {}

            tool_name = data.get('tool')
            if not tool_name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Missing tool name"}')
                return

            if WebUIHandler.tools_cache is None:
                WebUIHandler.tools_cache = core_main.discover_tools()

            tool = WebUIHandler.tools_cache.get(tool_name)
            if not tool:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "Tool not found"}')
                return

            parser = SafeArgumentParser()
            tool.add_arguments(parser)
            
            cli_args = []
            provided_args = data.get('args', {})
            
            for action in parser._actions:
                if action.dest == 'help': continue
                val = provided_args.get(action.dest)
                
                if val is not None and val != "":
                    is_bool_action = ('store_true' in action.__class__.__name__.lower() or
                                      'store_false' in action.__class__.__name__.lower())
                                      
                    if action.option_strings: # Flag
                        if isinstance(val, bool) or is_bool_action:
                            if val:
                                cli_args.append(action.option_strings[0])
                        elif action.nargs in ['?', '*']:
                            cli_args.append(action.option_strings[0])
                            cli_args.append(str(val))
                        elif action.nargs == '+':
                            cli_args.append(action.option_strings[0])
                            if isinstance(val, list):
                                cli_args.extend([str(v) for v in val])
                            else:
                                cli_args.append(str(val))
                        else:
                            cli_args.append(action.option_strings[0])
                            cli_args.append(str(val))
                    else: # Positional argument
                        if isinstance(val, list):
                            cli_args.extend([str(v) for v in val])
                        else:
                            cli_args.append(str(val))

            try:
                parsed_args = parser.parse_args(cli_args)
            except Exception as e:
                 self.send_response(400)
                 self.end_headers()
                 self.wfile.write(json.dumps({"error": f"Invalid arguments ({str(e)})"}).encode('utf-8'))
                 return

            # Capture stdout
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                try:
                    tool.run(parsed_args)
                except Exception as e:
                    print(f"Error during execution: {e}")

            output = f.getvalue()
            
            body = json.dumps({"output": output}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True
        else:
            self.send_response(404)
            self.end_headers()

class WebUITool(BaseTool):
    name = "webui"
    description = "開啟 DevToolkit 的精美網頁介面"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-p", "--port", type=int, default=8080, help="網頁伺服器運作的埠號")
        parser.add_argument("--host", default="127.0.0.1", help="伺服器要綁定的主機介面")

    def run(self, args: argparse.Namespace) -> None:
        server_address = (args.host, args.port)
        httpd = ThreadingHTTPServer(server_address, WebUIHandler)
        print(f"\n[WebUI] Starting DevToolkit Web UI on http://{args.host}:{args.port}\n")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down web server...")
            httpd.server_close()
