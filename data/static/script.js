let current=null; const demo=`Rucha Kothari
Email: rucha@example.com | Phone: 9876543210
Summary
Computer Engineering student interested in Artificial Intelligence and Data Science.
Education
B.Tech Computer Engineering, AIML Honors
Skills
Python, Java, SQL, Machine Learning, Data Analysis, Pandas, NumPy, Git, HTML, CSS
Experience
AI/ML Intern — Built a machine learning prediction project and analyzed datasets.
Projects
Diabetes Risk Prediction, AI Career Recommendation System, Web Dashboard
Certifications
Python and Data Science certification
`;
const demoJob=`We are looking for a Data Science Intern with Python, SQL, machine learning, statistics, pandas and data analysis skills. The candidate should communicate insights, work with datasets and build predictive models. Git experience is preferred.`;
function go(p){document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));document.getElementById(p).classList.add('active');document.querySelectorAll('nav button,aside .side-foot>button').forEach(x=>x.classList.toggle('active',x.dataset.page===p));document.getElementById('crumb').textContent=p.replace('-', ' ').replace(/\b\w/g,m=>m.toUpperCase());if(p==='paths')loadCareers();if(p==='jobs')loadJobs();window.scrollTo(0,0)}
document.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>go(b.dataset.page)));
function show(p){go(p)}
async function loadDashboard(){let r=await fetch('/api/careers');let cs=await r.json();document.getElementById('careerList').innerHTML=cs.slice(0,5).map((c,i)=>`<div class="pred"><div class="dot">${i+1}</div><div><b>${c.title}</b><small>${c.desc}</small></div><strong>${[87,82,78,74,70][i]}%</strong></div>`).join('')}
loadDashboard();
document.getElementById('file').addEventListener('change',e=>document.getElementById('filename').textContent=e.target.files[0]?.name||'Choose a file');
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{let parent=b.parentElement;parent.querySelectorAll('button').forEach(x=>x.classList.remove('active'));b.classList.add('active');if(b.dataset.tab==='txt')document.getElementById('txtbox').classList.remove('hidden');else document.getElementById('txtbox').classList.add('hidden')});
async function analyze(){let fd=new FormData();let f=document.getElementById('file').files[0];let text=document.getElementById('resume').value;if(f)fd.append('file',f);if(text)fd.append('text',text);if(!f&&!text)text=demo,fd.append('text',text);let m=document.getElementById('msg');m.textContent='Analyzing profile…';try{let r=await fetch('/api/analyze',{method:'POST',body:fd}),d=await r.json();if(!r.ok)throw Error(d.error);current=d;renderAnalysis(d);m.textContent='';localStorage.setItem('careerai_last',JSON.stringify(d));}catch(e){m.textContent=e.message}}
function renderAnalysis(d){let p=d.predictions[0];document.getElementById('analysisRing').innerHTML=`${p.score}%<small>Career Match</small>`;document.getElementById('analysisRing').style.background=`conic-gradient(var(--purple) 0 ${p.score}%,#e9eaf0 ${p.score}% 100%)`;document.getElementById('career').textContent=p.title;document.getElementById('careerDesc').textContent=p.desc;document.getElementById('resultTitle').textContent='Profile analyzed';document.getElementById('resultTag').textContent='COMPLETE';document.getElementById('quality').textContent=d.quality_score+'/100';document.getElementById('words').textContent=d.word_count;document.getElementById('skillnum').textContent=d.skills.length;document.getElementById('skills').innerHTML=d.skills.map(s=>`<span>${s}</span>`).join('')||'<small>No skills detected</small>';document.getElementById('sections').innerHTML=Object.entries(d.sections).map(([k,v])=>`<span class="${v?'ok':'no'}">${v?'✓':'○'} ${k}</span>`).join('');document.getElementById('predictions').innerHTML=d.predictions.map((x,i)=>`<div class="pred"><div class="dot">${i+1}</div><div><b>${x.title}</b><small>${x.desc}</small></div><strong>${x.score}%</strong></div>`).join('');document.getElementById('tips').innerHTML=d.tips.map(x=>`<li>${x}</li>`).join('');document.getElementById('dashScore').textContent=p.score+'%';document.getElementById('kpiMatch').textContent=p.score+'%';document.getElementById('kpiGap').textContent=(100-p.score)+'%';}
function loadDemo(){document.getElementById('resume').value=demo;go('analysis');analyze()}
function loadMatchDemo(){document.getElementById('resume').value=demo;document.getElementById('jobText').value=demoJob}
async function loadCareers(){let r=await fetch('/api/careers'),cs=await r.json();document.getElementById('allCareers').innerHTML=cs.map((c,i)=>`<div class="career-card"><div class="icon">✦</div><div><h3>${c.title}</h3><p>${c.desc}</p><div class="chips">${c.skills.slice(0,5).map(s=>`<span>${s}</span>`).join('')}</div></div><div class="score">${[87,82,78,74,70,66,61][i]}%</div></div>`).join('')}
async function loadJobs(){let r=await fetch('/api/jobs'),js=await r.json();document.getElementById('jobList').innerHTML=js.map(j=>`<div class="job"><div class="icon">${j.company[0]}</div><div><h3>${j.title}</h3><p>${j.company} · ${j.location} · ${j.mode}</p></div><span class="score">${j.match}% match</span><button class="ghost">View</button></div>`).join('')}
async function downloadReport(){if(!current){current={score:87,career:'Data Scientist',skills:['Python','SQL','Machine Learning','Data Analysis'],missing:['Deep Learning','NLP']}}let r=await fetch('/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({score:current.predictions?.[0]?.score||current.score,career:current.predictions?.[0]?.title||current.career,skills:current.skills,missing:['Deep Learning','NLP','MLOps']})});let b=await r.blob();let a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='CareerAI_Report.pdf';a.click()}
function toggleTheme(){document.body.classList.toggle('dark');localStorage.setItem('theme',document.body.classList.contains('dark')?'dark':'light')}
document.getElementById('theme').onclick=toggleTheme;if(localStorage.getItem('theme')==='dark')document.body.classList.add('dark');
