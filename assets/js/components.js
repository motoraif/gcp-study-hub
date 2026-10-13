/* GCP Study Hub - Shared Navbar + Footer */
(function(){
  try {
    if (localStorage.getItem('theme') === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  } catch(e) {}

  const segs=location.pathname.split('/').filter(Boolean);
  const inDocs=segs.includes('docs');
  const root=inDocs?'../':'./';

  const nav=`<nav class="navbar"><div class="container navbar-inner">
  <a class="navbar-brand" href="${root}index.html"><span class="g-blue">G</span><span class="g-red">C</span><span class="g-yellow">P</span>&nbsp;<span style="color:var(--text)">Study Hub</span></a>
  <button class="nav-toggle" id="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
  <div class="nav-links" id="nav-links">
    <a href="${root}index.html">Home</a>
    <div class="nav-dropdown">
      <button class="nav-dropdown-btn">Foundations <span class="caret">&#9662;</span></button>
      <div class="nav-dropdown-menu">
        <a href="${root}docs/foundations-linux.html">&#128039; Linux Fundamentals</a>
        <a href="${root}docs/foundations-networking.html">&#127760; Networking Fundamentals</a>
      </div>
    </div>
    <div class="nav-dropdown">
      <button class="nav-dropdown-btn">Certifications <span class="caret">&#9662;</span></button>
      <div class="nav-dropdown-menu nav-dropdown-menu-wide">
        <div class="nav-col">
          <span class="nav-col-title">Foundational</span>
          <a href="${root}docs/cloud-digital-leader.html">Cloud Digital Leader</a>
          <span class="nav-col-title">Associate</span>
          <a href="${root}docs/associate-cloud-engineer.html">Associate Cloud Engineer</a>
          <a href="${root}docs/associate-data-practitioner.html">Associate Data Practitioner <span class="nav-pill nav-pill-new">New</span></a>
          <a href="${root}docs/associate-workspace-administrator.html">Workspace Administrator <span class="nav-pill nav-pill-new">New</span></a>
        </div>
        <div class="nav-col">
          <span class="nav-col-title">Professional</span>
          <a href="${root}docs/professional-cloud-architect.html">Cloud Architect</a>
          <a href="${root}docs/professional-cloud-developer.html">Cloud Developer</a>
          <a href="${root}docs/professional-cloud-devops-engineer.html">Cloud DevOps Engineer</a>
          <a href="${root}docs/professional-cloud-security-engineer.html">Cloud Security Engineer</a>
          <a href="${root}docs/professional-cloud-network-engineer.html">Cloud Network Engineer</a>
          <a href="${root}docs/professional-cloud-database-engineer.html">Cloud Database Engineer</a>
          <a href="${root}docs/professional-data-engineer.html">Data Engineer</a>
          <a href="${root}docs/professional-machine-learning-engineer.html">Machine Learning Engineer</a>
        </div>
      </div>
    </div>
    <div class="nav-dropdown">
      <button class="nav-dropdown-btn">Study Tools <span class="caret">&#9662;</span></button>
      <div class="nav-dropdown-menu">
        <a href="${root}docs/quiz.html">&#129513; Practice Quiz</a>
        <a href="${root}docs/flashcards.html">&#128218; Flashcards</a>
        <a href="${root}docs/planner.html">&#128197; Study Planner</a>
        <a href="${root}docs/cheatsheets.html">&#128221; Cheat Sheets</a>
        <a href="${root}docs/services.html">&#129513; Service Deep Dives</a>
        <a href="${root}docs/labs.html">&#128300; Labs &amp; Practice</a>
        <a href="${root}docs/dashboard.html">&#128202; My Progress</a>
      </div>
    </div>
    <a href="${root}docs/resources.html">Resources</a>
    <a href="${root}docs/news.html">News</a>
    <a href="https://github.com/motoraif/gcp-study-hub" target="_blank" rel="noopener">GitHub &#11088;</a>
    <button class="theme-toggle" id="search-toggle" aria-label="Search (press /)" title="Search (/)">&#128269;</button>
    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle light/dark theme" title="Toggle theme">&#127769;</button>
  </div>
</div></nav>`;

  const footer=`<footer><div class="container">
  <div class="footer-grid">
    <div>
      <div class="footer-brand">&#9729;&#65039; GCP Study Hub</div>
      <p class="footer-desc">Community-driven, open-source study platform for all Google Cloud certifications. Free forever.</p>
      <div class="flex-wrap mt-1">
        <a href="https://github.com/motoraif/gcp-study-hub" target="_blank" class="btn btn-outline" style="font-size:0.8rem;padding:0.4rem 0.9rem">&#11088; Star on GitHub</a>
        <a href="${root}CONTRIBUTING.md" target="_blank" class="btn btn-outline" style="font-size:0.8rem;padding:0.4rem 0.9rem">&#129309; Contribute</a>
      </div>
    </div>
    <div>
      <h5>Foundations</h5>
      <ul>
        <li><a href="${root}docs/foundations-linux.html">Linux Basics</a></li>
        <li><a href="${root}docs/foundations-networking.html">Networking Basics</a></li>
      </ul>
    </div>
    <div>
      <h5>Certifications</h5>
      <ul>
        <li><a href="${root}docs/cloud-digital-leader.html">Cloud Digital Leader</a></li>
        <li><a href="${root}docs/associate-cloud-engineer.html">Associate Cloud Engineer</a></li>
        <li><a href="${root}docs/associate-data-practitioner.html">Associate Data Practitioner &#127381;</a></li>
        <li><a href="${root}docs/associate-workspace-administrator.html">Workspace Administrator &#127381;</a></li>
        <li><a href="${root}docs/professional-cloud-architect.html">Cloud Architect</a></li>
        <li><a href="${root}docs/professional-cloud-developer.html">Cloud Developer</a></li>
        <li><a href="${root}docs/professional-cloud-devops-engineer.html">Cloud DevOps Engineer</a></li>
        <li><a href="${root}docs/professional-cloud-security-engineer.html">Cloud Security Engineer</a></li>
        <li><a href="${root}docs/professional-cloud-network-engineer.html">Cloud Network Engineer</a></li>
        <li><a href="${root}docs/professional-cloud-database-engineer.html">Cloud Database Engineer</a></li>
        <li><a href="${root}docs/professional-data-engineer.html">Data Engineer</a></li>
        <li><a href="${root}docs/professional-machine-learning-engineer.html">Machine Learning Engineer</a></li>
      </ul>
    </div>
    <div>
      <h5>Resources</h5>
      <ul>
        <li><a href="${root}docs/resources.html">All Resources</a></li>
        <li><a href="${root}docs/labs.html">Labs &amp; Practice</a></li>
        <li><a href="${root}docs/quiz.html">Practice Quiz</a></li>
        <li><a href="${root}docs/flashcards.html">Flashcards</a></li>
        <li><a href="${root}docs/planner.html">Study Planner</a></li>
        <li><a href="${root}docs/services.html">Service Deep Dives</a></li>
        <li><a href="${root}docs/cheatsheets.html">Cheat Sheets</a></li>
        <li><a href="${root}docs/dashboard.html">My Progress</a></li>
        <li><a href="${root}docs/news.html">Google Cloud News</a></li>
        <li><a href="https://www.cloudskillsboost.google/" target="_blank">Google Cloud Skills Boost</a></li>
        <li><a href="https://cloud.google.com/learn/certification" target="_blank">Official Certifications</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; 2026 GCP Study Hub - MIT License</span>
    <span><a href="${root}docs/affiliate-disclosure.html">Affiliate Disclosure</a></span>
    <span>Not affiliated with Google LLC.</span>
  </div>
</div></footer>
<button id="scroll-top" title="Back to top">&#8593;</button>`;

  document.addEventListener('DOMContentLoaded',()=>{
    document.body.insertAdjacentHTML('afterbegin',nav);
    document.body.insertAdjacentHTML('beforeend',footer);

    const themeBtn=document.getElementById('theme-toggle');
    function setThemeIcon(){
      if(!themeBtn) return;
      const dark=document.documentElement.getAttribute('data-theme')==='dark';
      themeBtn.innerHTML=dark?'&#9728;&#65039;':'&#127769;'; // sun when dark (to go light), moon when light
      themeBtn.setAttribute('title', dark?'Switch to light theme':'Switch to dark theme');
    }
    setThemeIcon();
    if(themeBtn){
      themeBtn.addEventListener('click',()=>{
        const dark=document.documentElement.getAttribute('data-theme')==='dark';
        if(dark){ document.documentElement.removeAttribute('data-theme'); try{localStorage.setItem('theme','light');}catch(e){} }
        else { document.documentElement.setAttribute('data-theme','dark'); try{localStorage.setItem('theme','dark');}catch(e){} }
        setThemeIcon();
      });
    }

    const toggle=document.getElementById('nav-toggle');
    const links=document.getElementById('nav-links');
    if(toggle&&links){
      toggle.addEventListener('click',()=>{
        const open=links.classList.toggle('open');
        toggle.classList.toggle('open',open);
        toggle.setAttribute('aria-expanded',open?'true':'false');
      });
    }

    const MOBILE_BP = 1024;
    document.querySelectorAll('.nav-dropdown-btn').forEach(btn=>{
      btn.addEventListener('click',e=>{
        if(window.innerWidth<=MOBILE_BP){
          e.preventDefault();
          const dd=btn.closest('.nav-dropdown');
          const wasOpen=dd.classList.contains('open');
          document.querySelectorAll('.nav-dropdown.open').forEach(x=>x.classList.remove('open'));
          if(!wasOpen)dd.classList.add('open');
        }
      });
    });

    links&&links.querySelectorAll('a').forEach(a=>{
      a.addEventListener('click',()=>{
        if(window.innerWidth<=MOBILE_BP){
          links.classList.remove('open');
          toggle&&toggle.classList.remove('open');
          toggle&&toggle.setAttribute('aria-expanded','false');
        }
      });
    });
  });
})();
