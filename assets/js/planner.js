/* GCP Study Hub - Exam Study Planner
   Pick a certification and an exam date; get a week-by-week study plan
   derived from that cert's milestones. Plan + checkbox progress are saved
   privately in localStorage. No backend. */
(function () {
  var root = document.getElementById('planner-app');
  if (!root) return;

  var LS_KEY = 'planner_v1';

  // Cert metadata: code, name, guide page, and ordered study milestones.
  var CERTS = {
    'CDL': { name: 'Cloud Digital Leader', page: 'cloud-digital-leader.html', milestones: [
      'Cloud concepts: IaaS/PaaS/SaaS, CapEx vs OpEx, digital transformation',
      'Data & AI: BigQuery, databases, Pub/Sub, Vertex AI, pretrained APIs',
      'Infrastructure & modernization: compute options, migration paths',
      'Security & operations: shared responsibility, IAM, SCC, billing',
      'Review product mappings + take a full practice quiz' ] },
    'ACE': { name: 'Associate Cloud Engineer', page: 'associate-cloud-engineer.html', milestones: [
      'Resource hierarchy, projects, billing; set up gcloud & Cloud Shell',
      'IAM: members, roles, service accounts, best practices',
      'Compute: Compute Engine, MIGs, GKE, Cloud Run, App Engine',
      'VPC networking: subnets, firewall, Cloud NAT, load balancing',
      'Storage & databases: Cloud Storage classes, Cloud SQL, Spanner, etc.',
      'Operations: Cloud Monitoring, Logging, budgets',
      'Hands-on labs on Skills Boost; drill gcloud commands',
      'Full practice quiz + review weak domains' ] },
    'PCA': { name: 'Professional Cloud Architect', page: 'professional-cloud-architect.html', milestones: [
      'Read all four official case studies and map requirements to services',
      'Solution design patterns: compute, data, global web apps',
      'Security & compliance: IAM, org policies, VPC Service Controls, KMS',
      'Reliability & SRE: SLIs/SLOs/SLAs, error budgets, HA/DR (RPO/RTO)',
      'Migration (5 Rs) and the right transfer tools',
      'Cost optimization: CUDs, Spot, sustained use, right-sizing',
      'Re-read case studies; take a timed full quiz' ] },
    'PCD': { name: 'Professional Cloud Developer', page: 'professional-cloud-developer.html', milestones: [
      'Compute targets: Cloud Run, GKE, App Engine, Functions',
      'Data & caching: Firestore, Cloud SQL/Spanner, Memorystore',
      'APIs & messaging: API Gateway/Apigee, Pub/Sub, Cloud Tasks',
      'Build & deploy: Cloud Build, Artifact Registry, canary/blue-green',
      'Observability: Logging, Trace, Profiler, Error Reporting',
      'Full practice quiz + review' ] },
    'PCDOE': { name: 'Professional Cloud DevOps Engineer', page: 'professional-cloud-devops-engineer.html', milestones: [
      'SRE principles: SLIs/SLOs/SLAs, error budgets, toil',
      'CI/CD: Cloud Build, Artifact Registry, Cloud Deploy, Terraform',
      'Monitoring: Cloud Monitoring SLOs, log-based metrics, burn-rate alerts',
      'Incident management: on-call, postmortems',
      'Performance optimization: Profiler, Trace',
      'Full practice quiz + review' ] },
    'PCSE': { name: 'Professional Cloud Security Engineer', page: 'professional-cloud-security-engineer.html', milestones: [
      'Identity & access: Cloud Identity, IAM, Workload Identity Federation',
      'Network security: firewall policies, VPC Service Controls, Cloud Armor, IAP',
      'Data protection: CMEK/CSEK, Cloud KMS, DLP, Secret Manager',
      'Security operations: Security Command Center, audit logging',
      'Compliance mapping (PCI, HIPAA, ISO)',
      'Full practice quiz + review' ] },
    'PCNE': { name: 'Professional Cloud Network Engineer', page: 'professional-cloud-network-engineer.html', milestones: [
      'VPC design: global VPC, subnets, Shared VPC, peering, IP planning',
      'Load balancing: pick the right LB per scenario',
      'Hybrid connectivity: HA VPN, Interconnect, Cloud Router (BGP)',
      'Network services: Cloud DNS, NAT, CDN, Private Service Connect',
      'Operations: VPC Flow Logs, Network Intelligence Center',
      'Full practice quiz + review' ] },
    'PCDE': { name: 'Professional Cloud Database Engineer', page: 'professional-cloud-database-engineer.html', milestones: [
      'Choose the right database for OLTP/NoSQL/global/analytics',
      'HA & scaling: Cloud SQL HA, replicas, Spanner, Bigtable replication',
      'Migration: Database Migration Service, Datastream (CDC)',
      'Security: IAM, CMEK, private IP, Auth Proxy',
      'Backups, PITR, maintenance windows, monitoring',
      'Full practice quiz + review' ] },
    'PDE': { name: 'Professional Data Engineer', page: 'professional-data-engineer.html', milestones: [
      'Storage choices: BigQuery, Bigtable, Cloud SQL/Spanner, Cloud Storage',
      'Pipelines: Pub/Sub, Dataflow (windowing/watermarks), Dataproc',
      'BigQuery: partitioning, clustering, pricing, security',
      'ML & analytics: BigQuery ML, Vertex AI',
      'Orchestration & governance: Composer, Dataplex, DLP',
      'Full practice quiz + review' ] },
    'PMLE': { name: 'Professional Machine Learning Engineer', page: 'professional-machine-learning-engineer.html', milestones: [
      'Vertex AI platform; AutoML vs custom vs pretrained APIs',
      'Data & features: Feature Store, skew/leakage',
      'Training & tuning: distributed training, GPUs/TPUs, Vizier',
      'Serving: online vs batch; model versioning',
      'MLOps: Vertex AI Pipelines, Model Monitoring',
      'Full practice quiz + review' ] },
    'ADP': { name: 'Associate Data Practitioner', page: 'associate-data-practitioner.html', milestones: [
      'Ingestion & storage: Pub/Sub, Cloud Storage, transfer services, BigQuery',
      'Transformation: Dataflow, Dataproc, Data Fusion',
      'Analysis & BI: BigQuery SQL, Looker Studio, BigQuery ML',
      'Governance: Dataplex, dataset IAM, column/row security',
      'Full practice quiz + review' ] },
    'GWA': { name: 'Associate Google Workspace Administrator', page: 'associate-workspace-administrator.html', milestones: [
      'Users, groups & OUs; provisioning (GCDS, Admin SDK)',
      'Services: Gmail, Drive, Calendar, Meet policies per OU',
      'Security: 2SV, Context-Aware Access, DLP, Vault',
      'Monitoring & troubleshooting: audit logs, SPF/DKIM/DMARC',
      'Full practice quiz + review' ] }
  };

  function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];}); }

  function load(){ try { return JSON.parse(localStorage.getItem(LS_KEY)) || {}; } catch(e){ return {}; } }
  function save(o){ try { localStorage.setItem(LS_KEY, JSON.stringify(o)); } catch(e){} }

  function daysBetween(a,b){ return Math.round((b-a)/(1000*60*60*24)); }
  function fmtDate(d){ return d.toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'}); }

  // Build week buckets from today to the exam date, distributing milestones evenly.
  function buildPlan(cert, examISO){
    var c = CERTS[cert];
    var today = new Date(); today.setHours(0,0,0,0);
    var exam = new Date(examISO + 'T00:00:00');
    var totalDays = daysBetween(today, exam);
    if (totalDays < 1) return { error: 'Pick an exam date in the future.' };
    var weeks = Math.max(1, Math.ceil(totalDays / 7));
    var ms = c.milestones.slice();
    // Distribute milestones across available weeks (reserve the last week for review).
    var buckets = [];
    var perWeek = Math.ceil(ms.length / weeks);
    for (var w = 0; w < weeks; w++){
      var start = new Date(today); start.setDate(start.getDate() + w*7);
      var end = new Date(start); end.setDate(end.getDate() + 6);
      if (end > exam) end = exam;
      buckets.push({ start: start, end: end, items: ms.splice(0, perWeek) });
      if (!ms.length) break;
    }
    return { cert: cert, name: c.name, page: c.page, exam: exam, totalDays: totalDays, weeks: buckets };
  }

  function renderSetup(prefCert){
    var opts = Object.keys(CERTS).map(function(k){
      return '<option value="'+k+'"'+(k===prefCert?' selected':'')+'>'+esc(CERTS[k].name)+'</option>';
    }).join('');
    var saved = load();
    var minDate = new Date(); minDate.setDate(minDate.getDate()+1);
    var minISO = minDate.toISOString().slice(0,10);
    root.innerHTML =
      '<div class="card quiz-panel">' +
        '<h2 style="margin-top:0">Plan your exam</h2>' +
        '<p style="color:var(--text-muted)">Choose a certification and your target exam date. We will generate a week-by-week study plan and track your progress - saved privately in your browser.</p>' +
        '<div class="quiz-controls">' +
          '<label>Certification<br><select id="pl-cert">'+opts+'</select></label>' +
          '<label>Exam date<br><input type="date" id="pl-date" min="'+minISO+'" style="margin-top:0.35rem;background:var(--bg-hover);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:0.55rem 0.75rem;font-size:0.95rem"></label>' +
        '</div>' +
        '<button class="btn btn-primary" id="pl-make">Generate my plan &rarr;</button>' +
        (saved.cert ? ' <button class="btn btn-outline" id="pl-resume">Resume saved plan</button>' : '') +
      '</div>';
    document.getElementById('pl-make').addEventListener('click', function(){
      var cert = document.getElementById('pl-cert').value;
      var date = document.getElementById('pl-date').value;
      if(!date){ alert('Please choose your exam date.'); return; }
      var plan = buildPlan(cert, date);
      if (plan.error){ alert(plan.error); return; }
      save({ cert: cert, date: date, done: {} });
      renderPlan(plan);
    });
    var resume = document.getElementById('pl-resume');
    if (resume) resume.addEventListener('click', function(){
      var s = load();
      var plan = buildPlan(s.cert, s.date);
      if (plan.error){ renderSetup(s.cert); return; }
      renderPlan(plan);
    });
  }

  function renderPlan(plan){
    var s = load();
    var done = s.done || {};
    var totalItems = plan.weeks.reduce(function(a,w){ return a + w.items.length; }, 0);
    var doneCount = Object.keys(done).filter(function(k){ return done[k]; }).length;
    var pct = totalItems ? Math.round(doneCount/totalItems*100) : 0;

    var weeksHtml = plan.weeks.map(function(w, wi){
      var items = w.items.map(function(it, ii){
        var id = 'w'+wi+'i'+ii;
        var checked = done[id] ? ' checked' : '';
        var cls = done[id] ? ' class="done"' : '';
        return '<li'+cls+'><label style="display:flex;gap:0.6rem;align-items:flex-start;cursor:pointer"><input type="checkbox" data-id="'+id+'"'+checked+' style="margin-top:0.2rem;accent-color:var(--accent)"><span>'+esc(it)+'</span></label></li>';
      }).join('');
      return '<div class="card" style="margin-bottom:1rem">' +
        '<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;align-items:center">' +
          '<h3 style="margin:0">Week '+(wi+1)+'</h3>' +
          '<span class="badge badge-blue">'+fmtDate(w.start)+' - '+fmtDate(w.end)+'</span>' +
        '</div>' +
        '<ul class="checklist" style="margin-top:0.75rem">'+items+'</ul>' +
      '</div>';
    }).join('');

    var daysLeft = Math.max(0, Math.ceil((plan.exam - new Date())/(1000*60*60*24)));

    root.innerHTML =
      '<div class="card quiz-panel" style="margin-bottom:1.5rem">' +
        '<div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:1rem;align-items:center">' +
          '<div><h2 style="margin:0">'+esc(plan.name)+'</h2>' +
          '<p style="color:var(--text-muted);margin:0.25rem 0 0">Exam on <strong>'+fmtDate(plan.exam)+'</strong> &middot; <strong>'+daysLeft+'</strong> day'+(daysLeft===1?'':'s')+' to go</p></div>' +
          '<div style="text-align:center"><div style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,var(--gcp-blue),var(--gcp-green));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">'+pct+'%</div><div style="font-size:0.8rem;color:var(--text-muted)">complete</div></div>' +
        '</div>' +
        '<div class="progress-bar" style="margin-top:1rem"><div class="progress-fill" style="width:'+pct+'%"></div></div>' +
        '<div class="flex-wrap" style="margin-top:1rem">' +
          '<a class="btn btn-primary" href="'+esc(plan.page)+'">Open the '+esc(plan.cert)+' guide &rarr;</a>' +
          '<a class="btn btn-outline" href="quiz.html?cert='+esc(plan.cert)+'">Quiz yourself</a>' +
          '<button class="btn btn-outline" id="pl-reset">Start a new plan</button>' +
        '</div>' +
      '</div>' +
      weeksHtml;

    root.querySelectorAll('input[type="checkbox"][data-id]').forEach(function(cb){
      cb.addEventListener('change', function(){
        var st = load(); st.done = st.done || {};
        st.done[cb.dataset.id] = cb.checked; save(st);
        renderPlan(plan); // re-render to update progress + strike-through
      });
    });
    document.getElementById('pl-reset').addEventListener('click', function(){
      if (confirm('Start a new plan? Your current plan progress will be cleared.')){
        localStorage.removeItem(LS_KEY); renderSetup(plan.cert);
      }
    });
  }

  // Boot: deep-link ?cert=PCA preselects; resume saved plan if present.
  var params = new URLSearchParams(location.search);
  var wanted = (params.get('cert') || '').toUpperCase();
  var saved = load();
  if (saved.cert && saved.date && !wanted){
    var plan = buildPlan(saved.cert, saved.date);
    if (!plan.error){ renderPlan(plan); } else { renderSetup(saved.cert); }
  } else {
    renderSetup(CERTS[wanted] ? wanted : 'ACE');
  }
})();
