/* GCP Study Hub - Progress Dashboard
   Aggregates locally-stored progress: quiz best/last scores per cert
   (quiz_history_v1) and overall study-checklist completion (chk_* keys).
   All data is read-only from localStorage; nothing leaves the browser. */
(function () {
  var root = document.getElementById('dashboard-app');
  if (!root) return;

  var QUIZ_KEY = 'quiz_history_v1';

  var CERT_NAMES = {
    'CDL': 'Cloud Digital Leader',
    'ACE': 'Associate Cloud Engineer',
    'ADP': 'Associate Data Practitioner',
    'GWA': 'Associate Google Workspace Administrator',
    'PCA': 'Professional Cloud Architect',
    'PCD': 'Professional Cloud Developer',
    'PCDOE': 'Professional Cloud DevOps Engineer',
    'PCSE': 'Professional Cloud Security Engineer',
    'PCNE': 'Professional Cloud Network Engineer',
    'PCDE': 'Professional Cloud Database Engineer',
    'PDE': 'Professional Data Engineer',
    'PMLE': 'Professional Machine Learning Engineer',
    'ALL': 'All certifications'
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function loadQuiz() {
    try { return JSON.parse(localStorage.getItem(QUIZ_KEY)) || {}; } catch (e) { return {}; }
  }

  function checklistStats() {
    var done = 0, total = 0;
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.indexOf('chk_') === 0) { total++; if (localStorage.getItem(k) === '1') done++; }
    }
    return { done: done, total: total };
  }

  function bar(pct, cls) {
    return '<div class="progress-bar"><div class="progress-fill ' + (cls || '') + '" style="width:' + pct + '%"></div></div>';
  }

  function render() {
    var quiz = loadQuiz();
    var certs = Object.keys(quiz).filter(function (c) { return c !== 'ALL'; }).sort();
    var chk = checklistStats();

    var quizRows = certs.map(function (c) {
      var r = quiz[c];
      var pass = r.best >= 70;
      return '<tr>' +
        '<td><strong>' + esc(c) + '</strong><br><span style="color:var(--text-muted);font-size:0.85rem">' + esc(CERT_NAMES[c] || '') + '</span></td>' +
        '<td>' + r.attempts + '</td>' +
        '<td>' + r.last + '%</td>' +
        '<td><span style="color:' + (pass ? '#33cc66' : 'var(--text)') + ';font-weight:700">' + r.best + '%</span></td>' +
        '<td>' + (pass ? '<span class="badge badge-green">Exam-ready</span>' : '<span class="badge badge-orange">Keep going</span>') + '</td>' +
        '</tr>';
    }).join('');

    var overallBest = certs.length ? Math.round(certs.reduce(function (a, c) { return a + quiz[c].best; }, 0) / certs.length) : 0;
    var totalAttempts = certs.reduce(function (a, c) { return a + quiz[c].attempts; }, 0);
    var chkPct = chk.total ? Math.round(chk.done / chk.total * 100) : 0;

    var html =
      '<div class="grid-3" style="margin-bottom:1.5rem">' +
        '<div class="card"><div class="card-icon">&#129513;</div><h3>' + certs.length + '</h3><p style="color:var(--text-muted);margin:0">certs practiced</p></div>' +
        '<div class="card"><div class="card-icon">&#127919;</div><h3>' + overallBest + '%</h3><p style="color:var(--text-muted);margin:0">avg best score</p></div>' +
        '<div class="card"><div class="card-icon">&#9989;</div><h3>' + chk.done + '</h3><p style="color:var(--text-muted);margin:0">checklist items done</p></div>' +
      '</div>';

    if (certs.length) {
      html += '<div class="card quiz-panel"><h2 style="margin-top:0">&#129513; Quiz readiness by certification</h2>' +
        '<div class="table-wrap"><table><thead><tr><th>Certification</th><th>Attempts</th><th>Last</th><th>Best</th><th>Status</th></tr></thead><tbody>' +
        quizRows + '</tbody></table></div>' +
        '<p style="color:var(--text-muted);font-size:0.85rem;margin-top:0.75rem">Total quiz attempts: ' + totalAttempts + '. "Exam-ready" means a best score of 70%+ (aim higher for the real exam).</p>' +
        '</div>';
    } else {
      html += '<div class="card quiz-panel"><h2 style="margin-top:0">&#129513; Quiz readiness</h2>' +
        '<p style="color:var(--text-muted)">You have not taken any quizzes yet. <a href="quiz.html">Take a practice quiz</a> and your scores will appear here.</p></div>';
    }

    html += '<div class="card quiz-panel" style="margin-top:1.5rem"><h2 style="margin-top:0">&#9989; Study checklist progress</h2>';
    if (chk.total) {
      html += '<div class="progress-label" style="display:flex;justify-content:space-between"><span>' + chk.done + ' of ' + chk.total + ' items across all pages</span><span>' + chkPct + '%</span></div>' +
        bar(chkPct) +
        '<p style="color:var(--text-muted);font-size:0.85rem;margin-top:0.75rem">Tick items on the cert and foundations pages to track your study progress. This counts every checklist item you have marked complete.</p>';
    } else {
      html += '<p style="color:var(--text-muted)">No checklist items marked yet. Visit a <a href="cloud-digital-leader.html">certification guide</a> or the <a href="foundations-linux.html">foundations pages</a> and tick items as you learn.</p>';
    }
    html += '</div>';

    html += '<div class="quiz-nav" style="margin-top:1.5rem"><a class="btn btn-primary" href="quiz.html">Take a Quiz</a>' +
      (certs.length ? '<button class="btn btn-outline" id="dash-reset">Reset quiz history</button>' : '<span></span>') + '</div>';

    root.innerHTML = html;

    var reset = document.getElementById('dash-reset');
    if (reset) reset.addEventListener('click', function () {
      if (confirm('Clear all saved quiz history? (Checklist progress is kept.)')) { localStorage.removeItem(QUIZ_KEY); render(); }
    });
  }

  render();
})();
