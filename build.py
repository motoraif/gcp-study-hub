#!/usr/bin/env python3
"""Build all GCP Study Hub HTML pages.

A static-site generator for Google Cloud certification study material.
Run `python3 build.py` from the project root; it emits index.html plus all
pages under docs/, and regenerates data/search-index.json and sitemap.xml.
"""
import os, json as _json_stats
BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = f"{BASE}/docs"
os.makedirs(DOCS, exist_ok=True)

# ── Dynamic site stats ──────────────────────────────────────
def _compute_stats():
    stats = {"questions": 0, "quiz_certs": 0, "cert_pages": 0}
    try:
        with open(f"{BASE}/data/quiz-questions.json", encoding="utf-8") as f:
            qdata = _json_stats.load(f)
        qs = qdata.get("questions", [])
        stats["questions"] = len(qs)
        stats["quiz_certs"] = len({q.get("cert") for q in qs if q.get("cert")})
    except Exception:
        pass
    return stats

STATS = _compute_stats()
# Total certifications covered (hand-maintained to match CERT_INDEX below).
CERT_COUNT = 12

def _stat_str(n, step=10):
    if n <= 0:
        return "0"
    if n < step:
        return str(n)
    return f"{(n // step) * step}+"

# Canonical site URL (custom domain). Used for SEO tags and sitemap.
SITE_URL = "https://toraif.com/gcp-study-hub"
OG_IMAGE = f"{SITE_URL}/assets/og-image.svg"
SITE_NAME = "GCP Study Hub"
GITHUB_URL = "https://github.com/motoraif/gcp-study-hub"

def _full_title(title):
    t = title.strip()
    if t == SITE_NAME or t.endswith(f" - {SITE_NAME}") or SITE_NAME in t:
        return t
    return f"{t} - {SITE_NAME}"

def seo_tags(title, desc, root):
    full_title = _full_title(title)
    return f"""  <meta name="robots" content="index,follow">
  <meta name="author" content="GCP Study Hub">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="GCP Study Hub">
  <meta property="og:title" content="{full_title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{OG_IMAGE}">
  <meta property="og:url" content="{SITE_URL}/">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{full_title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{OG_IMAGE}">
  <script type="application/ld+json">{{"@context":"https://schema.org","@graph":[{{"@type":"WebSite","@id":"{SITE_URL}/#website","name":"GCP Study Hub","url":"{SITE_URL}/","description":"Free, open-source study platform for every Google Cloud certification.","inLanguage":"en","publisher":{{"@id":"{SITE_URL}/#org"}}}},{{"@type":"EducationalOrganization","@id":"{SITE_URL}/#org","name":"GCP Study Hub","url":"{SITE_URL}/","description":"Free, community-driven study resources for Google Cloud certifications."}}]}}</script>"""

HEAD = lambda t,d: f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{_full_title(t)}</title>
  <meta name="description" content="{d}">
{seo_tags(t, d, "../")}
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'><circle cx='14' cy='20' r='6' fill='%234285F4'/><circle cx='26' cy='14' r='6' fill='%23EA4335'/><circle cx='34' cy='24' r='6' fill='%23FBBC04'/><circle cx='22' cy='30' r='6' fill='%2334A853'/></svg>">
  <link rel="manifest" href="../manifest.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/css/style.css">
  <script src="../assets/js/components.js"></script>
  <script src="../assets/js/search.js" defer></script>
</head><body>"""

HEAD_ROOT = lambda t,d: f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{_full_title(t)}</title>
  <meta name="description" content="{d}">
{seo_tags(t, d, "")}
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'><circle cx='14' cy='20' r='6' fill='%234285F4'/><circle cx='26' cy='14' r='6' fill='%23EA4335'/><circle cx='34' cy='24' r='6' fill='%23FBBC04'/><circle cx='22' cy='30' r='6' fill='%2334A853'/></svg>">
  <link rel="manifest" href="manifest.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
  <script src="assets/js/components.js"></script>
  <script src="assets/js/search.js" defer></script>
</head><body>"""

FOOT      = '<script src="../assets/js/main.js"></script></body></html>'
FOOT_ROOT = '<script src="assets/js/main.js"></script></body></html>'

def crumb(cert):
    return f'<div class="container" style="padding-top:2rem;"><div class="breadcrumb"><a href="../index.html">Home</a> / <span>Certifications</span> / <span>{cert}</span></div></div>'

def phdr(bcls,btxt,icon,title,desc,badges="",extra_badge=""):
    eb = f' {extra_badge}' if extra_badge else ''
    return f'<div class="page-header"><div class="container"><span class="badge {bcls}">{btxt}</span>{eb}<h1 style="margin-top:0.75rem;">{icon} {title}</h1><p>{desc}</p><div class="flex-wrap mt-1">{badges}</div></div></div>'

def quiz_cta(code):
    return (f'<div class="container" style="padding-top:1.25rem"><div class="quiz-cta">'
            f'<span>&#129513; Ready to test yourself on {code}?</span>'
            f'<span class="quiz-cta-actions">'
            f'<a class="btn btn-primary" href="quiz.html?cert={code}">Quiz yourself &rarr;</a>'
            f'</span></div></div>')

def wrap(toc,body):
    links="".join(f'<a href="#{a}">{b}</a>\n' for a,b in toc)
    return f'<div class="container" style="padding-bottom:4rem;"><div class="doc-layout"><aside class="sidebar"><h4>Contents</h4>{links}</aside><main>{body}</main></div></div>'

def chk(items,nf,nl):
    rows="".join(f'<li><input type="checkbox"><span>{i}</span></li>' for i in items)
    nxt = f'<div class="mt-2"><a href="{nf}" class="btn btn-primary">Next: {nl} &rarr;</a></div>' if nf else ''
    return f'<section id="checklist" class="progress-section"><h2>&#128203; Study Checklist</h2><div class="progress-wrap"><div class="progress-label"><span>Progress</span><span class="progress-pct">0%</span></div><div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div></div><ul class="checklist">{rows}</ul>{nxt}</section>'

def exam(cn, cu, egu, dur, q, domains, cost="$125 USD", validity="2-3 years"):
    """Exam overview block. domains is a list of (name, weight%) tuples (weight optional)."""
    if domains and isinstance(domains[0], (list, tuple)) and len(domains[0]) == 2 and domains[0][1]:
        head = "<tr><th>Section</th><th>Weight</th></tr>"
        dr = "".join(f"<tr><td>{d}</td><td>{p}</td></tr>" for d, p in domains)
    else:
        head = "<tr><th>Section</th></tr>"
        dr = "".join(f"<tr><td>{(d[0] if isinstance(d,(list,tuple)) else d)}</td></tr>" for d in domains)
    return f"""<section id="overview"><h2>Exam Overview</h2>
<div class="grid-2">
  <div class="card"><h3>Exam Details</h3><ul>
    <li><strong>Duration:</strong> {dur}</li><li><strong>Questions:</strong> {q}</li>
    <li><strong>Format:</strong> Multiple choice &amp; multiple select</li>
    <li><strong>Delivery:</strong> Online-proctored or onsite test center</li>
    <li><strong>Cost:</strong> {cost}</li><li><strong>Validity:</strong> {validity}</li>
  </ul></div>
  <div class="card"><h3>&#127891; Official Resources</h3><ul>
    <li><a href="{cu}" target="_blank" rel="noopener">Skills Boost Learning Path: {cn}</a></li>
    <li><a href="{egu}" target="_blank" rel="noopener">Official Exam Guide</a></li>
    <li><a href="https://cloud.google.com/learn/certification" target="_blank" rel="noopener">Register / Schedule Your Exam</a></li>
    <li><a href="https://www.cloudskillsboost.google/" target="_blank" rel="noopener">Google Cloud Skills Boost</a></li>
    <li><a href="https://cloud.google.com/docs" target="_blank" rel="noopener">Google Cloud Documentation</a></li>
  </ul></div>
</div>
<h3>Exam Sections</h3>
<div class="table-wrap"><table><thead>{head}</thead><tbody>{dr}</tbody></table></div>
</section>"""

# ── Mermaid diagram support ─────────────────────────────────
def mermaid_block(diagram_src, caption=""):
    cap = f'<figcaption class="diagram-caption">{caption}</figcaption>' if caption else ''
    return f'<figure class="diagram"><pre class="mermaid">{diagram_src}</pre>{cap}</figure>'

MERMAID_LOADER = """
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  var light = document.documentElement.getAttribute('data-theme') === 'light';
  mermaid.initialize({ startOnLoad: true, theme: light ? 'default' : 'dark', securityLevel: 'strict' });
</script>"""

# ── Canonical URL + breadcrumb injection ────────────────────
def _canonical_rel(rel):
    return "" if rel == "index.html" else rel

def _page_url(path):
    rel = os.path.relpath(path, BASE).replace(os.sep, "/")
    return f"{SITE_URL}/{_canonical_rel(rel)}"

def _breadcrumb_jsonld(path, content):
    import json as _j, re as _re, html as _h
    rel = os.path.relpath(path, BASE).replace(os.sep, "/")
    url = f"{SITE_URL}/{_canonical_rel(rel)}"
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"}]
    if rel != "index.html":
        m = _re.search(r"<title>(.*?)</title>", content, _re.S)
        name = _h.unescape(m.group(1)).replace(" - GCP Study Hub", "").strip() if m else rel
        items.append({"@type": "ListItem", "position": 2, "name": name, "item": url})
    return ('<script type="application/ld+json">'
            + _j.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}, ensure_ascii=False)
            + '</script>')

# Collect written pages for search-index + sitemap generation.
WRITTEN_PAGES = []

def write(path, content):
    if path.endswith(".html"):
        url = _page_url(path)
        if '<link rel="canonical"' not in content:
            content = content.replace('  <link rel="manifest"',
                                      f'  <link rel="canonical" href="{url}">\n  <link rel="manifest"', 1)
        content = content.replace(f'<meta property="og:url" content="{SITE_URL}/">',
                                  f'<meta property="og:url" content="{url}">', 1)
        if 'BreadcrumbList' not in content:
            content = content.replace('</head>', '  ' + _breadcrumb_jsonld(path, content) + '\n</head>', 1)
        WRITTEN_PAGES.append((path, content))
    with open(path, 'w') as f:
        f.write(content)
    print(f"  Written: {path.split('/')[-1]}")

print("Building GCP Study Hub pages...")


# ── index.html ──────────────────────────────────────────────
index_html = HEAD_ROOT("GCP Study Hub - Ultimate Google Cloud Certification Study Platform","Free, community-driven study hub for all Google Cloud (GCP) certifications - guides, labs, practice questions, and foundations.") + f"""
<section class="hero"><div class="container">
  <div class="hero-eyebrow">&#128640; Open Source &middot; Community Driven &middot; Always Free</div>
  <h1>The Ultimate <span class="accent-blue">G</span><span class="accent-red">o</span><span class="accent-yellow">o</span><span class="accent-blue">g</span><span class="accent-green">l</span><span class="accent-red">e</span> Cloud<br>Certification Study Hub</h1>
  <p class="subtitle">Everything you need to pass every Google Cloud certification - official Skills Boost paths, hands-on labs, practice questions, and Linux &amp; networking foundations. All free, all in one place.</p>
  <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
    <a href="docs/cloud-digital-leader.html" class="btn btn-primary">&#127891; Start Learning</a>
    <a href="docs/quiz.html" class="btn btn-outline">&#129513; Take a Quiz</a>
    <a href="docs/resources.html" class="btn btn-outline">&#128218; Browse Resources</a>
    <a href="{GITHUB_URL}" target="_blank" class="btn btn-outline">&#11088; Star on GitHub</a>
  </div>
  <div class="hero-stats">
    <div class="stat-item"><div class="stat-number">{CERT_COUNT}+</div><div class="stat-label">GCP Certifications</div></div>
    <div class="stat-item"><div class="stat-number">200+</div><div class="stat-label">Study Topics</div></div>
    <div class="stat-item"><div class="stat-number">{_stat_str(STATS["questions"])}</div><div class="stat-label">Practice Questions</div></div>
    <div class="stat-item"><div class="stat-number">100%</div><div class="stat-label">Free Forever</div></div>
  </div>
</div></section>

<section class="path-strip" style="padding:1.5rem 0">
<div class="container"><div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;justify-content:center">
  <span style="color:var(--text-muted);font-size:0.88rem;font-weight:600">RECOMMENDED PATH:</span>
  <a href="docs/foundations-linux.html" class="badge badge-teal" style="text-decoration:none">1. Linux</a><span style="color:var(--text-muted)">&rarr;</span>
  <a href="docs/foundations-networking.html" class="badge badge-blue" style="text-decoration:none">2. Networking</a><span style="color:var(--text-muted)">&rarr;</span>
  <a href="docs/cloud-digital-leader.html" class="badge badge-green" style="text-decoration:none">3. Cloud Digital Leader</a><span style="color:var(--text-muted)">&rarr;</span>
  <a href="docs/associate-cloud-engineer.html" class="badge badge-blue" style="text-decoration:none">4. Associate Cloud Engineer</a><span style="color:var(--text-muted)">&rarr;</span>
  <span class="badge badge-purple">Professional</span>
</div></div></section>

<section class="section" style="background:var(--bg-card);border-top:1px solid var(--border);border-bottom:1px solid var(--border)"><div class="container">
  <div class="text-center mb-2"><h2>&#128640; Interactive Study Tools</h2><p style="color:var(--text-muted);max-width:620px;margin:0 auto">Go beyond reading. Test yourself, drill with spaced-repetition flashcards, review the tricky comparisons, and track your readiness - all free and saved privately in your browser.</p></div>
  <div class="grid-4">
    <a href="docs/quiz.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#129513;</div><h3>Practice Quiz</h3><p style="color:var(--text-muted);font-size:0.92rem">Timed, randomized questions per certification with instant scoring, a domain breakdown, and explanations for every answer.</p><div class="flex-wrap mt-1"><span class="badge badge-blue">{_stat_str(STATS["questions"])} questions</span><span class="badge badge-green">Instant scoring</span></div></a>
    <a href="docs/flashcards.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128218;</div><h3>Flashcards</h3><p style="color:var(--text-muted);font-size:0.92rem">Spaced-repetition flashcards that resurface each concept at the optimal time. Rate your recall and let the SM-2 scheduler do the rest.</p><div class="flex-wrap mt-1"><span class="badge badge-purple">Spaced repetition</span><span class="badge badge-green">Adaptive</span></div></a>
    <a href="docs/cheatsheets.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128221;</div><h3>Confusing Pairs Cheat Sheet</h3><p style="color:var(--text-muted);font-size:0.92rem">Side-by-side comparisons of the look-alike services that trip people up: Firewall vs Firewall Policy, Pub/Sub vs Tasks, Dataflow vs Dataproc, and more.</p><div class="flex-wrap mt-1"><span class="badge badge-teal">Quick reference</span><span class="badge badge-orange">Exam gold</span></div></a>
    <a href="docs/dashboard.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128202;</div><h3>My Progress</h3><p style="color:var(--text-muted);font-size:0.92rem">Your quiz readiness per certification and study-checklist completion in one dashboard. Private and local - no account needed.</p><div class="flex-wrap mt-1"><span class="badge badge-green">Track readiness</span><span class="badge badge-blue">Saved locally</span></div></a>
  </div>
  <div class="text-center mt-2"><p style="color:var(--text-muted);font-size:0.9rem">Tip: press <kbd style="background:var(--bg-hover);border:1px solid var(--border);border-radius:4px;padding:0.05em 0.4em">/</kbd> anywhere to search the whole site.</p></div>
</div></section>

<section class="section"><div class="container">
  <div class="text-center mb-2"><h2>&#129139; Foundations First</h2><p style="color:var(--text-muted);max-width:600px;margin:0 auto">Build solid Linux and networking fundamentals before diving into Google Cloud. These skills make every cert exam significantly easier.</p></div>
  <div class="grid-2">
    <a href="docs/foundations-linux.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128039;</div><h3>Linux Fundamentals</h3><p style="color:var(--text-muted);font-size:0.92rem">File system, permissions, processes, networking, shell scripting, systemd.</p><div class="flex-wrap mt-1"><span class="badge badge-teal">Beginner Friendly</span><span class="badge badge-green">20 Topics</span></div></a>
    <a href="docs/foundations-networking.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#127760;</div><h3>Networking Fundamentals</h3><p style="color:var(--text-muted);font-size:0.92rem">OSI model, TCP/IP, DNS, CIDR, subnetting, routing, load balancers, firewalls.</p><div class="flex-wrap mt-1"><span class="badge badge-blue">Essential</span><span class="badge badge-green">25 Topics</span></div></a>
  </div>
</div></section>

<section class="section" style="background:var(--bg-card);border-top:1px solid var(--border);border-bottom:1px solid var(--border)">
<div class="container">
  <div class="text-center mb-2"><h2>&#9729;&#65039; Google Cloud Certifications</h2><p style="color:var(--text-muted);max-width:600px;margin:0 auto">From beginner to expert. Each page includes official Skills Boost links, key topics, cheat sheets, and practice questions.</p></div>
  <h3 style="color:var(--accent);margin-bottom:1rem">Foundational</h3>
  <div class="grid-2" style="margin-bottom:2rem">
    <a href="docs/cloud-digital-leader.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#127885;</div><div><div class="cert-path-title">Cloud Digital Leader</div><div class="cert-path-meta">The perfect entry point. Cloud concepts, Google Cloud products, and digital transformation. No technical background needed.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-green">Foundational</span></div></div></a>
  </div>
  <h3 style="color:var(--accent);margin:2rem 0 1rem">Associate</h3>
  <div class="grid-3" style="margin-bottom:2rem">
    <a href="docs/associate-cloud-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#9881;</div><div><div class="cert-path-title">Associate Cloud Engineer</div><div class="cert-path-meta">Deploy, monitor, and manage GCP solutions</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-blue">Associate</span></div></div></a>
    <a href="docs/associate-data-practitioner.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128202;</div><div><div class="cert-path-title">Associate Data Practitioner</div><div class="cert-path-meta">Data ingestion, analysis, and pipelines</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-blue">Associate</span><span class="badge badge-green">New &#127381;</span></div></div></a>
    <a href="docs/associate-workspace-administrator.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128188;</div><div><div class="cert-path-title">Workspace Administrator</div><div class="cert-path-meta">Manage Google Workspace at scale</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-blue">Associate</span><span class="badge badge-green">New &#127381;</span></div></div></a>
  </div>
  <h3 style="color:var(--accent);margin-bottom:1rem">Professional</h3>
  <div class="grid-3">
    <a href="docs/professional-cloud-architect.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#127959;</div><div><div class="cert-path-title">Cloud Architect</div><div class="cert-path-meta">Design robust, secure, scalable cloud architecture. Google's #1 pro cert.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-cloud-developer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128187;</div><div><div class="cert-path-title">Cloud Developer</div><div class="cert-path-meta">Build scalable, reliable cloud-native apps.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-cloud-devops-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128260;</div><div><div class="cert-path-title">Cloud DevOps Engineer</div><div class="cert-path-meta">CI/CD, SRE practices, monitoring, SLOs.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-cloud-security-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128274;</div><div><div class="cert-path-title">Cloud Security Engineer</div><div class="cert-path-meta">IAM, network security, data protection.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-cloud-network-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#127760;</div><div><div class="cert-path-title">Cloud Network Engineer</div><div class="cert-path-meta">VPC design, hybrid connectivity, load balancing.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-cloud-database-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128451;</div><div><div class="cert-path-title">Cloud Database Engineer</div><div class="cert-path-meta">Design and manage GCP database solutions.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-data-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#128200;</div><div><div class="cert-path-title">Data Engineer</div><div class="cert-path-meta">Build data pipelines; BigQuery, Dataflow, Dataproc.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
    <a href="docs/professional-machine-learning-engineer.html" class="cert-path" style="text-decoration:none;color:var(--text)"><div class="cert-path-icon">&#129302;</div><div><div class="cert-path-title">Machine Learning Engineer</div><div class="cert-path-meta">Design, build, and productionize ML on Vertex AI.</div><div class="flex-wrap" style="margin-top:0.4rem"><span class="badge badge-purple">Professional</span></div></div></a>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="text-center mb-2"><h2>&#10024; Why GCP Study Hub?</h2></div>
  <div class="grid-3">
    <div class="card"><div class="card-icon">&#127358;</div><h3>100% Free</h3><p style="color:var(--text-muted);font-size:0.9rem">Every resource is free or points to the best-value options. Official Google Cloud content first.</p></div>
    <div class="card"><div class="card-icon">&#127963;</div><h3>Official First</h3><p style="color:var(--text-muted);font-size:0.9rem">All content links back to Google Cloud Skills Boost, official docs, and exam guides.</p></div>
    <div class="card"><div class="card-icon">&#129309;</div><h3>Community Driven</h3><p style="color:var(--text-muted);font-size:0.9rem">Open source on GitHub. Anyone can contribute. PRs and issues welcome!</p></div>
    <div class="card"><div class="card-icon">&#9989;</div><h3>Progress Tracking</h3><p style="color:var(--text-muted);font-size:0.9rem">Interactive checklists saved in your browser. No account needed.</p></div>
    <a href="docs/news.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128260;</div><h3>Auto-Updated</h3><p style="color:var(--text-muted);font-size:0.9rem">GitHub Actions pulls the latest Google Cloud release notes weekly so content stays fresh. <span style="color:var(--accent)">View news &rarr;</span></p></a>
    <div class="card"><div class="card-icon">&#129139;</div><h3>Full-Stack Learning</h3><p style="color:var(--text-muted);font-size:0.9rem">Linux basics &rarr; Networking &rarr; Associate &rarr; Professional.</p></div>
  </div>
</div></section>

<section class="section"><div class="container">
  <div class="text-center mb-2"><h2>&#128240; Latest Google Cloud News</h2><p style="color:var(--text-muted);max-width:600px;margin:0 auto">Fresh from the official Google Cloud release notes, updated automatically every week.</p></div>
  <div id="home-news" class="grid-3">
    <div class="card"><p style="color:var(--text-muted)">Loading latest Google Cloud news&hellip;</p></div>
  </div>
  <div class="text-center mt-2"><a href="docs/news.html" class="btn btn-outline">View All Google Cloud News &rarr;</a></div>
</div></section>
<script>
(function(){{
  var el = document.getElementById("home-news");
  if(!el) return;
  function esc(s){{ return String(s==null?"":s).replace(/[&<>"']/g,function(c){{
    return {{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}}[c]; }}); }}
  fetch("data/gcp-news.json",{{cache:"no-cache"}})
    .then(function(r){{ if(!r.ok) throw new Error("HTTP "+r.status); return r.json(); }})
    .then(function(data){{
      var items=((data&&data.items)||[]).slice(0,3);
      if(!items.length){{ el.innerHTML='<div class="card"><p style="color:var(--text-muted)">No news items yet.</p></div>'; return; }}
      el.innerHTML=items.map(function(it){{
        return '<a href="'+esc(it.link||"#")+'" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text);display:block">'+
               '<div class="flex-wrap" style="margin-bottom:0.5rem"><span class="badge badge-blue">'+esc(it.date||"")+'</span></div>'+
               '<h3 style="font-size:1rem;margin:0 0 0.4rem">'+esc(it.title||"")+'</h3>'+
               '<p style="color:var(--text-muted);font-size:0.85rem;margin:0">'+esc((it.summary||"").slice(0,140))+'</p></a>';
      }}).join("");
    }})
    .catch(function(){{ el.innerHTML='<div class="card"><p style="color:var(--text-muted)">Could not load news. <a href="docs/news.html">Open the News page &rarr;</a></p></div>'; }});
}})();
</script>

<section class="section" style="background:var(--bg-card);border-top:1px solid var(--border);border-bottom:1px solid var(--border)">
<div class="container">
  <div class="text-center mb-2"><h2>&#128279; Top Study Resources</h2></div>
  <div class="grid-4">
    <a href="https://www.cloudskillsboost.google/" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text);text-align:center"><div style="font-size:2.5rem;margin-bottom:0.75rem">&#127891;</div><h3 style="font-size:1rem">Google Cloud Skills Boost</h3><p style="font-size:0.85rem;color:var(--text-muted)">Official learning paths, labs, and quests.</p><span class="badge badge-green">FREE+PAID</span></a>
    <a href="https://cloud.google.com/docs" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text);text-align:center"><div style="font-size:2.5rem;margin-bottom:0.75rem">&#128218;</div><h3 style="font-size:1rem">Google Cloud Docs</h3><p style="font-size:0.85rem;color:var(--text-muted)">The authoritative product documentation.</p><span class="badge badge-green">FREE</span></a>
    <a href="https://www.coursera.org/googlecloud" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text);text-align:center"><div style="font-size:2.5rem;margin-bottom:0.75rem">&#11088;</div><h3 style="font-size:1rem">Coursera (Google Cloud)</h3><p style="font-size:0.85rem;color:var(--text-muted)">Official specializations and prep courses.</p><span class="badge badge-orange">PAID</span></a>
    <a href="https://cloud.google.com/free" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text);text-align:center"><div style="font-size:2.5rem;margin-bottom:0.75rem">&#127919;</div><h3 style="font-size:1rem">Free Tier &amp; $300 Credit</h3><p style="font-size:0.85rem;color:var(--text-muted)">Hands-on practice in a real GCP account.</p><span class="badge badge-green">FREE</span></a>
  </div>
  <div class="text-center mt-2"><a href="docs/resources.html" class="btn btn-outline">View All Resources &rarr;</a></div>
</div></section>

<section class="section"><div class="container">
  <div class="card" style="text-align:center;max-width:700px;margin:0 auto;padding:3rem">
    <div style="font-size:3rem;margin-bottom:1rem">&#129309;</div>
    <h2 style="margin-top:0">Help Make This the #1 Google Cloud Study Resource</h2>
    <p style="color:var(--text-muted)">Passed an exam? Share your tips. Found a great resource? Add it. Found a bug? Fix it. Every contribution helps thousands of learners.</p>
    <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem">
      <a href="{GITHUB_URL}/blob/main/CONTRIBUTING.md" target="_blank" class="btn btn-primary">Read Contributing Guide</a>
      <a href="{GITHUB_URL}/issues/new/choose" target="_blank" class="btn btn-outline">Open an Issue</a>
    </div>
  </div>
</div></section>
""" + FOOT_ROOT
write(f"{BASE}/index.html", index_html)


# ── Reusable certification page builder ─────────────────────
def cert_page(slug, level_cls, level_txt, icon, title, desc, badges,
              exam_args, toc, body_html, checklist_items, next_file, next_label,
              extra_badge=""):
    """Assemble a full certification guide page and write it to docs/<slug>.html."""
    header = phdr(level_cls, level_txt, icon, title, desc, badges, extra_badge)
    html = (HEAD(title, desc) + crumb(title.split(" - ")[0]) + header
            + quiz_cta(exam_args["code"])
            + wrap(toc, exam(exam_args["cn"], exam_args["cu"], exam_args["egu"],
                             exam_args["dur"], exam_args["q"], exam_args["domains"],
                             exam_args.get("cost", "$125 USD"),
                             exam_args.get("validity", "3 years"))
                   + body_html
                   + chk(checklist_items, next_file, next_label))
            + FOOT)
    write(f"{DOCS}/{slug}.html", html)


# ── Cloud Digital Leader (CDL) ──────────────────────────────
cert_page(
    "cloud-digital-leader", "badge-green", "Foundational", "&#127885;",
    "Cloud Digital Leader",
    "The entry-level Google Cloud certification. Cloud concepts, Google Cloud products and services, digital transformation, and modernizing infrastructure, data, and operations. No technical background required.",
    '<span class="badge badge-green">90 min | ~50-60 questions</span><span class="badge badge-blue">No prerequisites</span><span class="badge badge-teal">Business + tech</span>',
    {"code": "CDL",
     "cn": "Cloud Digital Leader Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/9",
     "egu": "https://cloud.google.com/learn/certification/cloud-digital-leader",
     "dur": "90 minutes", "q": "~50-60",
     "cost": "$99 USD", "validity": "3 years",
     "domains": [("Introduction to digital transformation with Google Cloud", "~10%"),
                 ("Innovating with data and Google Cloud", "~30%"),
                 ("Infrastructure and application modernization", "~30%"),
                 ("Google Cloud security and operations", "~30%")]},
    [("overview","Exam Overview"),("digital-transformation","Digital Transformation"),
     ("data","Data &amp; AI/ML"),("infra","Infrastructure &amp; Modernization"),
     ("security","Security &amp; Operations"),("products","Key Products"),("checklist","Checklist")],
    """
<section id="digital-transformation"><h2>Digital Transformation</h2>
<p>Digital transformation is using new digital technologies to create or modify business processes, culture, and customer experiences. Google Cloud enables this through three transformation clouds: <strong>data</strong>, <strong>open</strong>, and <strong>collaboration</strong>.</p>
<div class="grid-3">
  <div class="card"><h4>Infrastructure as a Service (IaaS)</h4><p>You manage OS and apps; Google manages hardware. Example: Compute Engine.</p></div>
  <div class="card"><h4>Platform as a Service (PaaS)</h4><p>You deploy code; Google manages the runtime. Example: App Engine, Cloud Run.</p></div>
  <div class="card"><h4>Software as a Service (SaaS)</h4><p>Fully managed app you just use. Example: Google Workspace.</p></div>
</div>
<div class="callout info"><div class="callout-title">&#128161; Total Cost of Ownership (TCO)</div><p>Moving to cloud shifts spending from capital expenditure (CapEx, buying hardware upfront) to operational expenditure (OpEx, paying for what you use). Know this distinction.</p></div>
</section>

<section id="data"><h2>Data &amp; AI/ML</h2>
<div class="table-wrap"><table><thead><tr><th>Need</th><th>Google Cloud Product</th></tr></thead><tbody>
  <tr><td>Data warehouse / analytics</td><td>BigQuery</td></tr>
  <tr><td>Relational database (managed)</td><td>Cloud SQL, AlloyDB, Spanner</td></tr>
  <tr><td>NoSQL document database</td><td>Firestore</td></tr>
  <tr><td>Wide-column NoSQL at scale</td><td>Bigtable</td></tr>
  <tr><td>Streaming / messaging</td><td>Pub/Sub</td></tr>
  <tr><td>Batch &amp; stream data pipelines</td><td>Dataflow</td></tr>
  <tr><td>Managed Spark / Hadoop</td><td>Dataproc</td></tr>
  <tr><td>Build &amp; deploy ML models</td><td>Vertex AI</td></tr>
  <tr><td>Pre-trained AI APIs</td><td>Vision, Speech-to-Text, Translation, Natural Language</td></tr>
</tbody></table></div>
</section>

<section id="infra"><h2>Infrastructure &amp; Modernization</h2>
<div class="grid-2">
  <div class="card"><h4>Compute options</h4><ul>
    <li><strong>Compute Engine</strong> - VMs (IaaS)</li>
    <li><strong>Google Kubernetes Engine (GKE)</strong> - managed containers</li>
    <li><strong>Cloud Run</strong> - serverless containers</li>
    <li><strong>App Engine</strong> - serverless apps (PaaS)</li>
    <li><strong>Cloud Functions</strong> - event-driven functions</li>
  </ul></div>
  <div class="card"><h4>Modernization paths</h4><ul>
    <li><strong>Rehost</strong> ("lift and shift") - move as-is to VMs</li>
    <li><strong>Replatform</strong> - minor tweaks, e.g. managed DB</li>
    <li><strong>Refactor</strong> - re-architect to cloud-native</li>
    <li><strong>Hybrid / multicloud</strong> - Anthos / GKE Enterprise</li>
  </ul></div>
</div>
</section>

<section id="security"><h2>Security &amp; Operations</h2>
<div class="callout tip"><div class="callout-title">&#128272; Shared Responsibility</div><p>Google secures the infrastructure (<em>security OF the cloud</em>); you secure your data, identities, and configuration (<em>security IN the cloud</em>). Google also promotes <strong>shared fate</strong> - actively helping customers be secure.</p></div>
<div class="table-wrap"><table><thead><tr><th>Area</th><th>Product</th></tr></thead><tbody>
  <tr><td>Identity &amp; access</td><td>Cloud IAM</td></tr>
  <tr><td>Secrets</td><td>Secret Manager</td></tr>
  <tr><td>Encryption keys</td><td>Cloud KMS</td></tr>
  <tr><td>Threat detection / posture</td><td>Security Command Center</td></tr>
  <tr><td>Monitoring, logging, tracing</td><td>Google Cloud Observability (Cloud Monitoring + Logging)</td></tr>
  <tr><td>Cost management</td><td>Billing reports, budgets &amp; alerts, committed use discounts</td></tr>
</tbody></table></div>
</section>

<section id="products"><h2>Products You Must Recognize</h2>
<p>CDL is scenario-based: given a business need, pick the right product. Memorize the "need &rarr; product" mappings in the tables above. Focus on <strong>BigQuery, Vertex AI, GKE, Cloud Run, Cloud SQL, Spanner, Pub/Sub, and IAM</strong>.</p>
</section>
""",
    ["Explain IaaS vs PaaS vs SaaS with Google Cloud examples",
     "Describe digital transformation and the three transformation clouds",
     "Explain CapEx vs OpEx and Total Cost of Ownership",
     "Map data needs to products (BigQuery, Cloud SQL, Spanner, Bigtable, Firestore)",
     "Explain Pub/Sub, Dataflow, and Dataproc at a high level",
     "Describe Vertex AI and the pre-trained AI APIs",
     "Compare Compute Engine, GKE, Cloud Run, App Engine, Cloud Functions",
     "Explain the modernization paths (rehost, replatform, refactor)",
     "Describe the shared responsibility and shared fate models",
     "Explain Cloud IAM, Security Command Center, and Cloud KMS at a high level",
     "Describe Google Cloud billing, budgets, and committed use discounts",
     "Understand hybrid and multicloud with GKE Enterprise / Anthos"],
    "associate-cloud-engineer.html", "Associate Cloud Engineer")


# ── Associate Cloud Engineer (ACE) ──────────────────────────
cert_page(
    "associate-cloud-engineer", "badge-blue", "Associate", "&#9881;",
    "Associate Cloud Engineer",
    "Deploy applications, monitor operations, and manage enterprise solutions on Google Cloud. The most popular hands-on GCP cert. Heavy on gcloud, the Console, IAM, networking, and compute.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-blue">Hands-on focus</span>',
    {"code": "ACE",
     "cn": "Associate Cloud Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/11",
     "egu": "https://cloud.google.com/learn/certification/cloud-engineer",
     "dur": "120 minutes", "q": "~50-60",
     "cost": "$125 USD", "validity": "3 years",
     "domains": [("Setting up a cloud solution environment", "~17.5%"),
                 ("Planning and configuring a cloud solution", "~17.5%"),
                 ("Deploying and implementing a cloud solution", "~25%"),
                 ("Ensuring successful operation of a cloud solution", "~20%"),
                 ("Configuring access and security", "~20%")]},
    [("overview","Exam Overview"),("resource-hierarchy","Resource Hierarchy"),
     ("iam","IAM"),("compute","Compute"),("networking","VPC Networking"),
     ("storage","Storage &amp; Databases"),("gcloud","gcloud &amp; Tooling"),("checklist","Checklist")],
    """
<section id="resource-hierarchy"><h2>Resource Hierarchy</h2>
<p>Google Cloud resources are organized top-down. Policies set higher up are inherited downward.</p>
<div class="table-wrap"><table><thead><tr><th>Level</th><th>Purpose</th></tr></thead><tbody>
  <tr><td><strong>Organization</strong></td><td>Root node; tied to a Cloud Identity / Workspace domain</td></tr>
  <tr><td><strong>Folders</strong></td><td>Group projects by department / environment; optional</td></tr>
  <tr><td><strong>Projects</strong></td><td>The core trust and billing boundary; all resources live in a project</td></tr>
  <tr><td><strong>Resources</strong></td><td>VMs, buckets, databases, etc.</td></tr>
</tbody></table></div>
<div class="callout warn"><div class="callout-title">&#9888; Exam Tip</div><p>IAM policies are <strong>inherited</strong> and the effective policy is the <strong>union</strong> of policies at every level. A less restrictive parent policy cannot be overridden by a child. Billing is linked at the project level.</p></div>
</section>

<section id="iam"><h2>Identity &amp; Access Management (IAM)</h2>
<div class="grid-2">
  <div class="card"><h4>Member types</h4><ul>
    <li>Google account (user)</li><li>Service account (for workloads)</li>
    <li>Google group</li><li>Cloud Identity / Workspace domain</li>
    <li>allAuthenticatedUsers / allUsers (public)</li>
  </ul></div>
  <div class="card"><h4>Role types</h4><ul>
    <li><strong>Basic</strong> - Owner, Editor, Viewer (avoid in prod)</li>
    <li><strong>Predefined</strong> - granular, per-service (preferred)</li>
    <li><strong>Custom</strong> - you pick exact permissions</li>
  </ul></div>
</div>
<div class="callout tip"><div class="callout-title">&#128161; Service Accounts</div><p>Use service accounts for VM/app identity. Prefer attaching a service account to a resource over downloading JSON keys. Grant the <em>Service Account User</em> role to let a principal act as a service account.</p></div>
</section>

<section id="compute"><h2>Compute</h2>
<div class="table-wrap"><table><thead><tr><th>Service</th><th>Best for</th><th>Key facts</th></tr></thead><tbody>
  <tr><td>Compute Engine</td><td>VMs, full OS control</td><td>Machine families (E2, N2, C3); preemptible/Spot VMs for ~60-91% savings; MIGs for autoscaling</td></tr>
  <tr><td>GKE</td><td>Containerized microservices</td><td>Autopilot (managed nodes) vs Standard; workload identity for IAM</td></tr>
  <tr><td>Cloud Run</td><td>Stateless containers, serverless</td><td>Scales to zero; pay per request</td></tr>
  <tr><td>App Engine</td><td>Web apps, PaaS</td><td>Standard (sandbox) vs Flexible (containers)</td></tr>
  <tr><td>Cloud Functions</td><td>Event-driven glue code</td><td>Triggered by HTTP, Pub/Sub, Storage events</td></tr>
</tbody></table></div>
<div class="callout info"><div class="callout-title">&#128161; Managed Instance Groups (MIGs)</div><p>Provide autoscaling, autohealing, rolling updates, and multi-zone deployment. Pair with a load balancer for HA. Know the difference between <strong>managed</strong> (identical, template-based) and <strong>unmanaged</strong> instance groups.</p></div>
</section>

<section id="networking"><h2>VPC Networking</h2>
<div class="table-wrap"><table><thead><tr><th>Concept</th><th>Details</th></tr></thead><tbody>
  <tr><td>VPC</td><td><strong>Global</strong> resource; subnets are <strong>regional</strong></td></tr>
  <tr><td>Subnet</td><td>Regional IP range; spans all zones in the region</td></tr>
  <tr><td>Firewall rules</td><td>Stateful; applied by network tags or service accounts; implied deny ingress / allow egress</td></tr>
  <tr><td>Routes</td><td>Direct traffic; default route to internet gateway</td></tr>
  <tr><td>Cloud NAT</td><td>Outbound internet for private VMs without external IPs</td></tr>
  <tr><td>Cloud Load Balancing</td><td>Global (HTTP(S), SSL/TCP proxy) vs Regional (Network, Internal)</td></tr>
  <tr><td>Shared VPC</td><td>Share one VPC across projects (host + service projects)</td></tr>
  <tr><td>VPC Peering</td><td>Private connectivity between two VPCs; non-transitive</td></tr>
</tbody></table></div>
</section>

<section id="storage"><h2>Storage &amp; Databases</h2>
<div class="table-wrap"><table><thead><tr><th>Need</th><th>Service</th><th>Notes</th></tr></thead><tbody>
  <tr><td>Object storage</td><td>Cloud Storage</td><td>Classes: Standard, Nearline (30d), Coldline (90d), Archive (365d)</td></tr>
  <tr><td>Managed SQL</td><td>Cloud SQL</td><td>MySQL, PostgreSQL, SQL Server; regional HA</td></tr>
  <tr><td>Global SQL at scale</td><td>Spanner</td><td>Horizontally scalable, strongly consistent</td></tr>
  <tr><td>Document NoSQL</td><td>Firestore</td><td>Serverless, mobile/web SDKs</td></tr>
  <tr><td>Wide-column NoSQL</td><td>Bigtable</td><td>Low-latency, high-throughput, time-series/IoT</td></tr>
  <tr><td>Analytics warehouse</td><td>BigQuery</td><td>Serverless, SQL, separates storage &amp; compute</td></tr>
  <tr><td>Block storage</td><td>Persistent Disk / Hyperdisk</td><td>Attached to VMs; snapshots for backup</td></tr>
</tbody></table></div>
</section>

<section id="gcloud"><h2>gcloud &amp; Tooling</h2>
<p>Expect to read and complete <code>gcloud</code> commands. Core patterns:</p>
<pre><code># Set the active project
gcloud config set project my-project-id

# Create a VM
gcloud compute instances create web-1 --zone=us-central1-a --machine-type=e2-medium

# Grant an IAM role
gcloud projects add-iam-policy-binding my-project-id \\
  --member="user:alice@example.com" --role="roles/compute.viewer"

# Deploy to Cloud Run
gcloud run deploy my-svc --image=gcr.io/my-project/img --region=us-central1

# Interact with a GKE cluster
gcloud container clusters get-credentials my-cluster --region=us-central1
kubectl get pods</code></pre>
<div class="callout tip"><div class="callout-title">&#128161; Know the tools</div><p><strong>gcloud</strong> (platform), <strong>gsutil</strong>/<strong>gcloud storage</strong> (Cloud Storage), <strong>bq</strong> (BigQuery), <strong>kubectl</strong> (Kubernetes), and <strong>Cloud Shell</strong> (browser terminal with tools preinstalled).</p></div>
</section>
""",
    ["Explain the resource hierarchy (Org, Folders, Projects, Resources)",
     "Understand IAM policy inheritance and the union rule",
     "Compare basic, predefined, and custom IAM roles",
     "Create and use service accounts correctly (attach vs keys)",
     "Create VMs with gcloud; understand machine types and Spot VMs",
     "Configure Managed Instance Groups with autoscaling and health checks",
     "Compare Compute Engine, GKE, Cloud Run, App Engine, Cloud Functions",
     "Understand VPC (global) vs subnets (regional) and firewall rules",
     "Configure Cloud NAT, load balancers, Shared VPC, and VPC peering",
     "Choose the right storage/database for a scenario",
     "Set Cloud Storage lifecycle rules and storage classes",
     "Use gcloud, gsutil/gcloud storage, bq, and kubectl confidently",
     "Set up billing, budgets, and billing export to BigQuery",
     "Use Cloud Monitoring, Logging, and alerting policies"],
    "professional-cloud-architect.html", "Professional Cloud Architect")


# ── Professional Cloud Architect (PCA) ──────────────────────
cert_page(
    "professional-cloud-architect", "badge-purple", "Professional", "&#127959;",
    "Professional Cloud Architect",
    "Design, develop, and manage robust, secure, scalable, and dynamic solutions on Google Cloud. The most valued GCP certification. Features case studies and solution-design scenarios.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">Case studies</span>',
    {"code": "PCA",
     "cn": "Cloud Architect Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/12",
     "egu": "https://cloud.google.com/learn/certification/cloud-architect",
     "dur": "120 minutes", "q": "~50-60",
     "cost": "$200 USD", "validity": "2 years",
     "domains": [("Designing and planning a cloud solution architecture", "~24%"),
                 ("Managing and provisioning a solution infrastructure", "~15%"),
                 ("Designing for security and compliance", "~18%"),
                 ("Analyzing and optimizing technical and business processes", "~18%"),
                 ("Managing implementation", "~11%"),
                 ("Ensuring solution and operations reliability", "~14%")]},
    [("overview","Exam Overview"),("case-studies","Case Studies"),
     ("design","Solution Design"),("security","Security &amp; Compliance"),
     ("reliability","Reliability &amp; SRE"),("migration","Migration"),
     ("cost","Cost Optimization"),("checklist","Checklist")],
    """
<section id="case-studies"><h2>Case Studies</h2>
<div class="callout warn"><div class="callout-title">&#9888; Study the Official Case Studies</div><p>A significant share of PCA questions reference four official case studies. Read them before the exam and map each company's requirements to GCP services.</p></div>
<div class="grid-2">
  <div class="card"><h4>EHR Healthcare</h4><p>Healthcare SaaS. Themes: hybrid connectivity, compliance (HIPAA), containerization (GKE), observability, 99.9% availability.</p></div>
  <div class="card"><h4>Helicopter Racing League</h4><p>Live streaming + ML predictions. Themes: global reach, CDN, AI/ML (Vertex AI), real-time analytics, edge.</p></div>
  <div class="card"><h4>Mountkirk Games</h4><p>Multiplayer mobile game. Themes: GKE, global load balancing, Spanner, autoscaling, low latency, analytics.</p></div>
  <div class="card"><h4>TerramEarth</h4><p>Connected vehicles / IoT. Themes: Pub/Sub ingestion, Dataflow, BigQuery, API management (Apigee), partner connectivity.</p></div>
</div>
</section>

<section id="design"><h2>Solution Design</h2>
<p>Translate business &amp; technical requirements into architecture. Key patterns:</p>
<div class="table-wrap"><table><thead><tr><th>Requirement</th><th>Design choice</th></tr></thead><tbody>
  <tr><td>Global, strongly consistent SQL</td><td>Spanner (multi-region)</td></tr>
  <tr><td>Serverless microservices</td><td>Cloud Run + Pub/Sub + Firestore</td></tr>
  <tr><td>High-throughput ingestion</td><td>Pub/Sub &rarr; Dataflow &rarr; BigQuery/Bigtable</td></tr>
  <tr><td>Container orchestration at scale</td><td>GKE (regional cluster, multi-zone node pools)</td></tr>
  <tr><td>Global web app with low latency</td><td>Global external HTTP(S) LB + Cloud CDN</td></tr>
  <tr><td>Decoupling / async</td><td>Pub/Sub, Cloud Tasks</td></tr>
</tbody></table></div>
</section>

<section id="security"><h2>Security &amp; Compliance</h2>
<ul>
  <li><strong>Least privilege</strong> with predefined/custom IAM roles; avoid basic roles in production.</li>
  <li><strong>Org policies</strong> to enforce guardrails (e.g., restrict resource locations, disable SA key creation).</li>
  <li><strong>VPC Service Controls</strong> to prevent data exfiltration from managed services.</li>
  <li><strong>CMEK/CSEK</strong> with Cloud KMS for customer-managed encryption keys.</li>
  <li><strong>Security Command Center</strong> for posture, vulnerabilities, and threat detection.</li>
  <li><strong>Shielded VMs</strong>, Binary Authorization (GKE), and Workload Identity.</li>
</ul>
</section>

<section id="reliability"><h2>Reliability &amp; SRE</h2>
<div class="grid-2">
  <div class="card"><h4>SRE concepts</h4><ul>
    <li><strong>SLI</strong> - a measured indicator (e.g. latency, error rate)</li>
    <li><strong>SLO</strong> - target for an SLI (e.g. 99.9%)</li>
    <li><strong>SLA</strong> - contractual promise with consequences</li>
    <li><strong>Error budget</strong> - allowed unreliability (1 - SLO)</li>
  </ul></div>
  <div class="card"><h4>HA/DR patterns</h4><ul>
    <li>Multi-zone and multi-region deployments</li>
    <li>RPO (data loss tolerance) vs RTO (recovery time)</li>
    <li>Backup/restore, warm standby, hot (active-active)</li>
    <li>Health checks + autohealing + autoscaling</li>
  </ul></div>
</div>
</section>

<section id="migration"><h2>Migration</h2>
<p>Know the "5 Rs": <strong>Rehost</strong> (lift-and-shift with Migrate to Virtual Machines), <strong>Replatform</strong>, <strong>Refactor</strong>, <strong>Repurchase</strong>, and <strong>Retire</strong>. For data: <strong>Storage Transfer Service</strong> (online), <strong>Transfer Appliance</strong> (offline, large), <strong>Database Migration Service</strong> (DBs), and <strong>BigQuery Data Transfer Service</strong>.</p>
</section>

<section id="cost"><h2>Cost Optimization</h2>
<ul>
  <li><strong>Committed use discounts</strong> (1 or 3 year) for steady workloads.</li>
  <li><strong>Spot VMs</strong> for fault-tolerant batch.</li>
  <li><strong>Sustained use discounts</strong> applied automatically on Compute Engine.</li>
  <li>Right-size with recommendations (Active Assist / Recommender).</li>
  <li>Cloud Storage lifecycle policies to move cold data to cheaper classes.</li>
  <li>BigQuery: partitioning, clustering, and slot reservations.</li>
</ul>
</section>
""",
    ["Read and map all four official case studies to GCP services",
     "Translate business/technical requirements into architecture",
     "Choose compute (GKE, Cloud Run, GCE, App Engine) per scenario",
     "Design global data layers (Spanner, BigQuery, Bigtable, Firestore)",
     "Apply least-privilege IAM, org policies, and VPC Service Controls",
     "Use Cloud KMS with CMEK/CSEK and Secret Manager",
     "Define SLIs, SLOs, SLAs, and error budgets",
     "Design multi-zone/multi-region HA and DR (RPO/RTO)",
     "Plan migrations using the 5 Rs and the right transfer tools",
     "Optimize cost (CUDs, Spot, sustained use, right-sizing)",
     "Design hybrid/multicloud connectivity (Interconnect, VPN, GKE Enterprise)",
     "Apply the Google Cloud Architecture Framework pillars"],
    "professional-cloud-developer.html", "Professional Cloud Developer")


# ── Associate Data Practitioner (ADP) ───────────────────────
cert_page(
    "associate-data-practitioner", "badge-blue", "Associate", "&#128202;",
    "Associate Data Practitioner",
    "Demonstrate foundational data skills on Google Cloud: data ingestion, storage, transformation, analysis, and visualization using managed services like BigQuery, Dataflow, and Looker.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-blue">Data focus</span><span class="badge badge-green">New &#127381;</span>',
    {"code": "ADP",
     "cn": "Data Analyst / Data Practitioner Learning Path",
     "cu": "https://www.cloudskillsboost.google/",
     "egu": "https://cloud.google.com/learn/certification/data-practitioner",
     "dur": "120 minutes", "q": "~50-60",
     "cost": "$125 USD", "validity": "3 years",
     "domains": [("Data preparation and ingestion", "~30%"),
                 ("Data analysis and presentation", "~26%"),
                 ("Data pipeline orchestration", "~22%"),
                 ("Data management", "~22%")]},
    [("overview","Exam Overview"),("ingestion","Ingestion &amp; Storage"),
     ("transform","Transformation"),("analysis","Analysis &amp; BI"),
     ("governance","Governance"),("checklist","Checklist")],
    """
<section id="ingestion"><h2>Ingestion &amp; Storage</h2>
<div class="table-wrap"><table><thead><tr><th>Pattern</th><th>Service</th></tr></thead><tbody>
  <tr><td>Streaming ingestion</td><td>Pub/Sub</td></tr>
  <tr><td>Batch file landing</td><td>Cloud Storage</td></tr>
  <tr><td>Managed transfers</td><td>Storage Transfer Service, BigQuery Data Transfer Service</td></tr>
  <tr><td>Analytics storage</td><td>BigQuery</td></tr>
  <tr><td>Operational NoSQL</td><td>Bigtable, Firestore</td></tr>
</tbody></table></div>
</section>
<section id="transform"><h2>Transformation</h2>
<ul>
  <li><strong>Dataflow</strong> - unified batch + stream (Apache Beam).</li>
  <li><strong>Dataproc</strong> - managed Spark/Hadoop for lift-and-shift big data.</li>
  <li><strong>Dataprep / Cloud Data Fusion</strong> - visual, low-code ETL.</li>
  <li><strong>BigQuery SQL + scheduled queries</strong> - in-warehouse ELT.</li>
</ul>
</section>
<section id="analysis"><h2>Analysis &amp; BI</h2>
<ul>
  <li><strong>BigQuery</strong> - serverless SQL analytics; partitioning &amp; clustering for cost/perf.</li>
  <li><strong>Looker / Looker Studio</strong> - dashboards and self-serve BI.</li>
  <li><strong>BigQuery ML</strong> - train models with SQL.</li>
</ul>
</section>
<section id="governance"><h2>Governance</h2>
<p>Understand <strong>Dataplex</strong> (data governance/catalog), IAM for datasets, column/row-level security in BigQuery, and data retention/lifecycle policies.</p>
</section>
""",
    ["Choose ingestion services (Pub/Sub, Cloud Storage, transfer services)",
     "Select the right storage/warehouse for a data workload",
     "Build transformations with Dataflow, Dataproc, and Data Fusion",
     "Write efficient BigQuery SQL; use partitioning and clustering",
     "Create dashboards with Looker Studio",
     "Train models with BigQuery ML at a basic level",
     "Apply dataset IAM and column/row-level security",
     "Use Dataplex for cataloging and governance",
     "Orchestrate pipelines (Cloud Composer / scheduled queries)",
     "Manage data lifecycle, retention, and cost"],
    "associate-workspace-administrator.html", "Workspace Administrator")


# ── Associate Google Workspace Administrator (GWA) ──────────
cert_page(
    "associate-workspace-administrator", "badge-blue", "Associate", "&#128188;",
    "Associate Google Workspace Administrator",
    "Manage Google Workspace for an organization: provisioning users and groups, configuring services, securing data, and troubleshooting from the Admin console.",
    '<span class="badge badge-green">~90 min | ~50-60 questions</span><span class="badge badge-blue">Admin console</span><span class="badge badge-green">New &#127381;</span>',
    {"code": "GWA",
     "cn": "Google Workspace Administration Learning Path",
     "cu": "https://www.cloudskillsboost.google/",
     "egu": "https://cloud.google.com/learn/certification/google-workspace-administrator",
     "dur": "~90 minutes", "q": "~50-60",
     "cost": "$125 USD", "validity": "3 years",
     "domains": [("Managing user accounts, domains, and directory", "~25%"),
                 ("Managing and configuring Workspace services", "~25%"),
                 ("Securing Workspace", "~25%"),
                 ("Monitoring, reporting, and troubleshooting", "~25%")]},
    [("overview","Exam Overview"),("users","Users &amp; OUs"),
     ("services","Services"),("security","Security"),("ops","Monitoring"),("checklist","Checklist")],
    """
<section id="users"><h2>Users, Groups &amp; Organizational Units</h2>
<ul>
  <li><strong>Organizational Units (OUs)</strong> - apply settings/policies hierarchically.</li>
  <li><strong>Groups</strong> - for mailing lists and access control.</li>
  <li>Provisioning via Admin console, GCDS (directory sync), or the Admin SDK / API.</li>
  <li>SSO and SAML; integration with Cloud Identity.</li>
</ul>
</section>
<section id="services"><h2>Services</h2>
<p>Configure Gmail (routing, compliance), Drive (sharing policies), Calendar, Meet, and Chat. Control service availability per OU.</p>
</section>
<section id="security"><h2>Security</h2>
<ul>
  <li><strong>2-Step Verification</strong> and security keys enforcement.</li>
  <li><strong>Context-Aware Access</strong> and access levels.</li>
  <li>DLP for Drive and Gmail; data regions; retention with Google Vault.</li>
  <li>Alert Center and the security investigation tool.</li>
</ul>
</section>
<section id="ops"><h2>Monitoring, Reporting &amp; Troubleshooting</h2>
<p>Use audit logs, reports, and the security dashboard. Troubleshoot mail delivery (headers, SPF/DKIM/DMARC) and access issues.</p>
</section>
""",
    ["Design an OU structure and apply policies by OU",
     "Provision users/groups via console, GCDS, and the Admin SDK",
     "Configure SSO/SAML and Cloud Identity integration",
     "Manage Gmail routing and compliance settings",
     "Set Drive sharing and external access policies",
     "Enforce 2-Step Verification and security keys",
     "Configure Context-Aware Access and DLP",
     "Use Google Vault for retention and eDiscovery",
     "Investigate incidents with the security tool and Alert Center",
     "Troubleshoot mail delivery (SPF, DKIM, DMARC)"],
    "professional-cloud-developer.html", "Professional Cloud Developer")


# ── Professional Cloud Developer (PCD) ──────────────────────
cert_page(
    "professional-cloud-developer", "badge-purple", "Professional", "&#128187;",
    "Professional Cloud Developer",
    "Build scalable and highly available applications using Google-recommended practices and tools. Focus on serverless, containers, APIs, data, and application observability.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">Code-centric</span>',
    {"code": "PCD",
     "cn": "Cloud Developer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/17",
     "egu": "https://cloud.google.com/learn/certification/cloud-developer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Designing highly scalable, available, reliable apps", "~25%"),
                 ("Building and testing applications", "~20%"),
                 ("Deploying applications", "~20%"),
                 ("Integrating Google Cloud services", "~20%"),
                 ("Managing deployed applications", "~15%")]},
    [("overview","Exam Overview"),("compute","Compute Targets"),
     ("data","Data &amp; Caching"),("apis","APIs &amp; Messaging"),
     ("cicd","Build &amp; Deploy"),("observe","Observability"),("checklist","Checklist")],
    """
<section id="compute"><h2>Compute Targets</h2>
<p>Pick the right runtime: <strong>Cloud Run</strong> (stateless containers, scale-to-zero), <strong>GKE</strong> (complex microservices), <strong>App Engine</strong> (PaaS), <strong>Cloud Functions</strong> (event glue). Know cold starts, concurrency, min instances, and request timeouts.</p>
</section>
<section id="data"><h2>Data &amp; Caching</h2>
<ul>
  <li><strong>Firestore</strong> for app data; understand transactions and indexes.</li>
  <li><strong>Cloud SQL / Spanner</strong> for relational.</li>
  <li><strong>Memorystore</strong> (Redis/Memcached) for caching.</li>
  <li><strong>Cloud Storage</strong> for assets; signed URLs for direct access.</li>
</ul>
</section>
<section id="apis"><h2>APIs &amp; Messaging</h2>
<p>Design REST/gRPC APIs; use <strong>API Gateway</strong>/<strong>Apigee</strong>. Decouple with <strong>Pub/Sub</strong> (at-least-once, ordering keys, dead-letter topics) and <strong>Cloud Tasks</strong> (rate-limited task queues).</p>
</section>
<section id="cicd"><h2>Build &amp; Deploy</h2>
<ul>
  <li><strong>Cloud Build</strong> for CI; store images in <strong>Artifact Registry</strong>.</li>
  <li>Deployment strategies: rolling, blue/green, canary (traffic splitting on Cloud Run / GKE).</li>
  <li>Manage config/secrets with <strong>Secret Manager</strong> and env vars.</li>
</ul>
</section>
<section id="observe"><h2>Observability</h2>
<p>Instrument with <strong>Cloud Logging</strong>, <strong>Cloud Trace</strong>, <strong>Cloud Profiler</strong>, and <strong>Error Reporting</strong>. Use structured logs and correlation IDs.</p>
</section>
""",
    ["Choose Cloud Run, GKE, App Engine, or Functions per use case",
     "Handle cold starts, concurrency, and timeouts",
     "Model data in Firestore; use transactions and indexes",
     "Add caching with Memorystore",
     "Design REST/gRPC APIs and use API Gateway/Apigee",
     "Decouple with Pub/Sub (ordering, dead-letter) and Cloud Tasks",
     "Build CI/CD with Cloud Build and Artifact Registry",
     "Implement canary/blue-green deployments with traffic splitting",
     "Manage secrets with Secret Manager",
     "Instrument apps with Logging, Trace, Profiler, Error Reporting"],
    "professional-cloud-devops-engineer.html", "Professional Cloud DevOps Engineer")


# ── Professional Cloud DevOps Engineer (PCDOE) ──────────────
cert_page(
    "professional-cloud-devops-engineer", "badge-purple", "Professional", "&#128260;",
    "Professional Cloud DevOps Engineer",
    "Implement SRE practices and CI/CD on Google Cloud: build pipelines, define SLOs and error budgets, manage services, and optimize for reliability and velocity.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">SRE + CI/CD</span>',
    {"code": "PCDOE",
     "cn": "Cloud DevOps Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/18",
     "egu": "https://cloud.google.com/learn/certification/cloud-devops-engineer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Applying SRE principles to a service", "~=20%"),
                 ("Building and implementing CI/CD pipelines", "~=20%"),
                 ("Implementing service monitoring strategies", "~=20%"),
                 ("Optimizing service performance", "~=20%"),
                 ("Managing service incidents", "~=20%")]},
    [("overview","Exam Overview"),("sre","SRE Principles"),
     ("cicd","CI/CD Pipelines"),("monitoring","Monitoring"),
     ("incidents","Incident Management"),("checklist","Checklist")],
    """
<section id="sre"><h2>SRE Principles</h2>
<ul>
  <li><strong>SLI / SLO / SLA</strong> and <strong>error budgets</strong> drive release decisions.</li>
  <li>Toil reduction through automation.</li>
  <li>Blameless postmortems and a culture of learning.</li>
</ul>
</section>
<section id="cicd"><h2>CI/CD Pipelines</h2>
<p><strong>Cloud Build</strong> (triggers, build config), <strong>Artifact Registry</strong>, <strong>Cloud Deploy</strong> (managed progressive delivery to GKE/Cloud Run), and GitOps patterns. Infrastructure as code with <strong>Terraform</strong> and Config Controller.</p>
</section>
<section id="monitoring"><h2>Monitoring</h2>
<p>Google Cloud Observability: <strong>Cloud Monitoring</strong> (metrics, dashboards, SLO monitoring, alerting), <strong>Cloud Logging</strong> (log-based metrics, sinks), <strong>Cloud Trace/Profiler</strong>. Define alerting policies tied to SLOs, not raw symptoms.</p>
</section>
<section id="incidents"><h2>Incident Management</h2>
<p>On-call, incident response roles, escalation, and postmortems. Use error budget burn-rate alerts to catch fast and slow failures.</p>
</section>
""",
    ["Define SLIs, SLOs, SLAs, and manage error budgets",
     "Reduce toil through automation",
     "Build CI with Cloud Build triggers and Artifact Registry",
     "Use Cloud Deploy for progressive delivery",
     "Apply Terraform / IaC for repeatable infrastructure",
     "Create SLO-based alerting policies in Cloud Monitoring",
     "Use log-based metrics and logging sinks",
     "Implement burn-rate alerts for error budgets",
     "Run blameless postmortems and incident response",
     "Optimize service performance with Profiler and Trace"],
    "professional-cloud-security-engineer.html", "Professional Cloud Security Engineer")


# ── Professional Cloud Security Engineer (PCSE) ─────────────
cert_page(
    "professional-cloud-security-engineer", "badge-purple", "Professional", "&#128274;",
    "Professional Cloud Security Engineer",
    "Design and implement secure workloads and infrastructure on Google Cloud: identity and access, network security, data protection, and compliance.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">Security</span>',
    {"code": "PCSE",
     "cn": "Cloud Security Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/19",
     "egu": "https://cloud.google.com/learn/certification/cloud-security-engineer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Configuring access", "~27%"),
                 ("Securing communications and boundary protection", "~21%"),
                 ("Ensuring data protection", "~20%"),
                 ("Managing operations", "~22%"),
                 ("Supporting compliance requirements", "~10%")]},
    [("overview","Exam Overview"),("iam","Identity &amp; Access"),
     ("network","Network Security"),("data","Data Protection"),
     ("ops","Security Operations"),("checklist","Checklist")],
    """
<section id="iam"><h2>Identity &amp; Access</h2>
<ul>
  <li>Cloud Identity, SSO/SAML, 2SV, and super-admin protection.</li>
  <li>Least-privilege IAM; conditions; <strong>Workload Identity Federation</strong> (no SA keys).</li>
  <li><strong>Organization policies</strong> and the policy hierarchy.</li>
</ul>
</section>
<section id="network"><h2>Network Security</h2>
<ul>
  <li>Firewall rules/policies, hierarchical firewall policies.</li>
  <li><strong>VPC Service Controls</strong> perimeters to stop exfiltration.</li>
  <li><strong>Cloud Armor</strong> (WAF, DDoS), Identity-Aware Proxy (IAP), Private Google Access.</li>
</ul>
</section>
<section id="data"><h2>Data Protection</h2>
<ul>
  <li>Default encryption at rest/in transit; <strong>CMEK/CSEK</strong> with Cloud KMS; Cloud HSM / External Key Manager.</li>
  <li><strong>Sensitive Data Protection (DLP)</strong> for discovery, de-identification, tokenization.</li>
  <li>Secret Manager; Confidential Computing.</li>
</ul>
</section>
<section id="ops"><h2>Security Operations</h2>
<p><strong>Security Command Center</strong> (posture, findings), audit logs, log sinks to BigQuery/SIEM, and Chronicle. Map controls to compliance frameworks (PCI DSS, HIPAA, ISO).</p>
</section>
""",
    ["Configure Cloud Identity, SSO, and 2-Step Verification",
     "Apply least-privilege IAM with conditions",
     "Use Workload Identity Federation instead of SA keys",
     "Enforce organization policies across the hierarchy",
     "Design firewall policies and VPC Service Controls perimeters",
     "Protect apps with Cloud Armor and Identity-Aware Proxy",
     "Implement CMEK/CSEK and Cloud HSM with Cloud KMS",
     "Use Sensitive Data Protection (DLP) for de-identification",
     "Operate Security Command Center and audit logging",
     "Map controls to compliance frameworks"],
    "professional-cloud-network-engineer.html", "Professional Cloud Network Engineer")


# ── Professional Cloud Network Engineer (PCNE) ──────────────
cert_page(
    "professional-cloud-network-engineer", "badge-purple", "Professional", "&#127760;",
    "Professional Cloud Network Engineer",
    "Design, implement, and manage Google Cloud network architectures: VPC design, hybrid connectivity, network services, and security.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">Networking</span>',
    {"code": "PCNE",
     "cn": "Cloud Network Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/20",
     "egu": "https://cloud.google.com/learn/certification/cloud-network-engineer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Designing, planning, and prototyping a network", "~26%"),
                 ("Implementing Virtual Private Cloud (VPC) instances", "~21%"),
                 ("Configuring network services", "~23%"),
                 ("Implementing hybrid interconnectivity", "~14%"),
                 ("Managing, monitoring, and optimizing network operations", "~16%")]},
    [("overview","Exam Overview"),("vpc","VPC Design"),
     ("lb","Load Balancing"),("hybrid","Hybrid Connectivity"),
     ("services","Network Services"),("checklist","Checklist")],
    """
<section id="vpc"><h2>VPC Design</h2>
<ul>
  <li>VPC is <strong>global</strong>; subnets are <strong>regional</strong>. Auto vs custom mode.</li>
  <li><strong>Shared VPC</strong> (host/service projects) vs <strong>VPC Peering</strong> (non-transitive).</li>
  <li>Routes, firewall rules/policies, network tags, and service accounts.</li>
  <li>IP addressing: primary/secondary ranges (alias IPs for GKE), RFC 1918 planning.</li>
</ul>
</section>
<section id="lb"><h2>Load Balancing</h2>
<div class="table-wrap"><table><thead><tr><th>Type</th><th>Scope</th><th>Use</th></tr></thead><tbody>
  <tr><td>Global external Application LB</td><td>Global, L7</td><td>HTTP(S), CDN, global web apps</td></tr>
  <tr><td>Global external proxy Network LB</td><td>Global, L4</td><td>TCP/SSL proxy</td></tr>
  <tr><td>Regional external Network LB</td><td>Regional, L4</td><td>Pass-through TCP/UDP</td></tr>
  <tr><td>Internal Application/Network LB</td><td>Regional</td><td>Internal services</td></tr>
</tbody></table></div>
</section>
<section id="hybrid"><h2>Hybrid Connectivity</h2>
<ul>
  <li><strong>Cloud VPN</strong> (HA VPN, 99.99%) over the internet.</li>
  <li><strong>Dedicated Interconnect</strong> (10/100 Gbps) and <strong>Partner Interconnect</strong>.</li>
  <li><strong>Cloud Router</strong> for dynamic (BGP) route exchange.</li>
  <li><strong>Network Connectivity Center</strong> for hub-and-spoke topologies.</li>
</ul>
</section>
<section id="services"><h2>Network Services</h2>
<p><strong>Cloud DNS</strong> (public/private zones, DNS peering), <strong>Cloud NAT</strong>, <strong>Cloud CDN</strong>, <strong>Cloud Armor</strong>, Private Service Connect, and VPC Flow Logs / Network Intelligence Center for troubleshooting.</p>
</section>
""",
    ["Design VPCs (global) with regional subnets; auto vs custom mode",
     "Choose Shared VPC vs VPC Peering",
     "Plan IP addressing including alias IP ranges for GKE",
     "Select the correct load balancer for a scenario",
     "Configure HA VPN and Cloud Router with BGP",
     "Design Dedicated vs Partner Interconnect",
     "Use Network Connectivity Center for hub-and-spoke",
     "Configure Cloud DNS public/private zones and peering",
     "Set up Cloud NAT, Cloud CDN, and Private Service Connect",
     "Troubleshoot with VPC Flow Logs and Network Intelligence Center"],
    "professional-cloud-database-engineer.html", "Professional Cloud Database Engineer")


# ── Professional Cloud Database Engineer (PCDE) ─────────────
cert_page(
    "professional-cloud-database-engineer", "badge-purple", "Professional", "&#128451;",
    "Professional Cloud Database Engineer",
    "Design, manage, and migrate scalable database solutions on Google Cloud. Covers Cloud SQL, AlloyDB, Spanner, Bigtable, Firestore, and migrations.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">Databases</span>',
    {"code": "PCDE",
     "cn": "Cloud Database Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/",
     "egu": "https://cloud.google.com/learn/certification/cloud-database-engineer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Designing scalable and highly available databases", "~=25%"),
                 ("Managing a solution for the enterprise", "~=25%"),
                 ("Migrating data solutions", "~=25%"),
                 ("Deploying scalable and secure databases", "~=25%")]},
    [("overview","Exam Overview"),("choose","Choosing a Database"),
     ("ha","HA &amp; Scaling"),("migrate","Migration"),("secure","Security"),("checklist","Checklist")],
    """
<section id="choose"><h2>Choosing a Database</h2>
<div class="table-wrap"><table><thead><tr><th>Service</th><th>Model</th><th>Best for</th></tr></thead><tbody>
  <tr><td>Cloud SQL</td><td>Relational (MySQL/PostgreSQL/SQL Server)</td><td>Lift-and-shift OLTP, regional</td></tr>
  <tr><td>AlloyDB</td><td>PostgreSQL-compatible</td><td>High-performance OLTP + analytics</td></tr>
  <tr><td>Spanner</td><td>Relational, globally distributed</td><td>Global scale, strong consistency, 99.999%</td></tr>
  <tr><td>Bigtable</td><td>Wide-column NoSQL</td><td>High-throughput, low-latency, time-series/IoT</td></tr>
  <tr><td>Firestore</td><td>Document NoSQL</td><td>Mobile/web apps, serverless</td></tr>
  <tr><td>Memorystore</td><td>In-memory (Redis/Memcached)</td><td>Caching, sessions</td></tr>
  <tr><td>BigQuery</td><td>Analytics warehouse</td><td>OLAP, not OLTP</td></tr>
</tbody></table></div>
</section>
<section id="ha"><h2>HA &amp; Scaling</h2>
<p>Cloud SQL regional HA (failover replica), read replicas (incl. cross-region), and maintenance windows. Spanner nodes/processing units and multi-region configs. Bigtable replication and cluster routing.</p>
</section>
<section id="migrate"><h2>Migration</h2>
<p><strong>Database Migration Service (DMS)</strong> for homogeneous/heterogeneous migrations with minimal downtime. Understand continuous replication, cutover, and Datastream for CDC.</p>
</section>
<section id="secure"><h2>Security</h2>
<p>IAM database roles, CMEK, private IP + Private Service Connect, Cloud SQL Auth Proxy, and audit logging.</p>
</section>
""",
    ["Choose the right database for OLTP, NoSQL, global, or analytics needs",
     "Design Cloud SQL regional HA and read replicas",
     "Scale Spanner with nodes/processing units and multi-region",
     "Model Bigtable schemas and configure replication",
     "Use Database Migration Service and Datastream (CDC)",
     "Plan minimal-downtime cutovers",
     "Secure databases with IAM, CMEK, and private IP",
     "Use the Cloud SQL Auth Proxy",
     "Set backups, PITR, and maintenance windows",
     "Monitor database performance and query insights"],
    "professional-data-engineer.html", "Professional Data Engineer")


# ── Professional Data Engineer (PDE) ────────────────────────
cert_page(
    "professional-data-engineer", "badge-purple", "Professional", "&#128200;",
    "Professional Data Engineer",
    "Design and build data processing systems and operationalize ML models on Google Cloud. Heavy on BigQuery, Dataflow, Dataproc, Pub/Sub, and data governance.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">Data pipelines</span>',
    {"code": "PDE",
     "cn": "Data Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/16",
     "egu": "https://cloud.google.com/learn/certification/data-engineer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Designing data processing systems", "~=22%"),
                 ("Ingesting and processing the data", "~=25%"),
                 ("Storing the data", "~=20%"),
                 ("Preparing and using data for analysis", "~=15%"),
                 ("Maintaining and automating data workloads", "~=18%")]},
    [("overview","Exam Overview"),("storage","Storage Choices"),
     ("pipelines","Pipelines"),("bigquery","BigQuery"),
     ("ml","ML &amp; Analytics"),("ops","Orchestration &amp; Governance"),("checklist","Checklist")],
    """
<section id="storage"><h2>Storage Choices</h2>
<div class="table-wrap"><table><thead><tr><th>Need</th><th>Service</th></tr></thead><tbody>
  <tr><td>Analytics warehouse</td><td>BigQuery</td></tr>
  <tr><td>Wide-column, high throughput</td><td>Bigtable</td></tr>
  <tr><td>Relational OLTP</td><td>Cloud SQL / AlloyDB / Spanner</td></tr>
  <tr><td>Object/data lake</td><td>Cloud Storage</td></tr>
  <tr><td>Document NoSQL</td><td>Firestore</td></tr>
</tbody></table></div>
</section>
<section id="pipelines"><h2>Pipelines</h2>
<ul>
  <li><strong>Pub/Sub</strong> - ingest streams; ordering keys, dead-letter topics, exactly-once.</li>
  <li><strong>Dataflow</strong> - Apache Beam, unified batch/stream, windowing, watermarks.</li>
  <li><strong>Dataproc</strong> - managed Spark/Hadoop; ephemeral clusters, autoscaling.</li>
  <li><strong>Data Fusion</strong> - visual ETL; <strong>Datastream</strong> - CDC.</li>
</ul>
</section>
<section id="bigquery"><h2>BigQuery</h2>
<ul>
  <li>Partitioning (time/ingestion/integer) and clustering for cost/performance.</li>
  <li>On-demand vs capacity (slots/editions) pricing; reservations.</li>
  <li>Materialized views, authorized views, and row/column-level security.</li>
  <li>Streaming inserts vs the Storage Write API; external/BigLake tables.</li>
</ul>
</section>
<section id="ml"><h2>ML &amp; Analytics</h2>
<p><strong>BigQuery ML</strong> for SQL-based models; <strong>Vertex AI</strong> for custom training/serving. Know feature engineering, batch vs online prediction, and when to use pretrained APIs.</p>
</section>
<section id="ops"><h2>Orchestration &amp; Governance</h2>
<p><strong>Cloud Composer</strong> (managed Airflow) and Dataflow templates for automation. <strong>Dataplex</strong> for governance, <strong>Data Catalog</strong> for metadata, and DLP for sensitive data.</p>
</section>
""",
    ["Choose storage for warehouse, NoSQL, OLTP, and lake needs",
     "Design streaming pipelines with Pub/Sub and Dataflow",
     "Apply windowing, watermarks, and handle late data",
     "Run Dataproc with ephemeral, autoscaling clusters",
     "Optimize BigQuery with partitioning and clustering",
     "Choose BigQuery pricing models and reservations",
     "Secure BigQuery with authorized views and row/column security",
     "Use BigQuery ML and Vertex AI appropriately",
     "Orchestrate with Cloud Composer (Airflow)",
     "Govern data with Dataplex, Data Catalog, and DLP"],
    "professional-machine-learning-engineer.html", "Professional Machine Learning Engineer")


# ── Professional Machine Learning Engineer (PMLE) ───────────
cert_page(
    "professional-machine-learning-engineer", "badge-purple", "Professional", "&#129302;",
    "Professional Machine Learning Engineer",
    "Design, build, and productionize ML models on Google Cloud using Vertex AI and Google-recommended MLOps practices.",
    '<span class="badge badge-green">120 min | ~50-60 questions</span><span class="badge badge-purple">MLOps + Vertex AI</span>',
    {"code": "PMLE",
     "cn": "Machine Learning Engineer Learning Path",
     "cu": "https://www.cloudskillsboost.google/paths/17",
     "egu": "https://cloud.google.com/learn/certification/machine-learning-engineer",
     "dur": "120 minutes", "q": "~50-60", "cost": "$200 USD", "validity": "2 years",
     "domains": [("Architecting low-code AI solutions", "~=13%"),
                 ("Collaborating to manage data and models", "~=14%"),
                 ("Scaling prototypes into ML models", "~=18%"),
                 ("Serving and scaling models", "~=20%"),
                 ("Automating and orchestrating ML pipelines", "~=22%"),
                 ("Monitoring AI solutions", "~=13%")]},
    [("overview","Exam Overview"),("vertex","Vertex AI"),
     ("data","Data &amp; Features"),("train","Training &amp; Tuning"),
     ("serve","Serving"),("mlops","MLOps"),("checklist","Checklist")],
    """
<section id="vertex"><h2>Vertex AI</h2>
<p>The unified ML platform: AutoML (low-code), custom training, Model Registry, Endpoints, Pipelines, Feature Store, and the Model Garden / Gemini for generative AI. Know when to use AutoML vs custom vs pretrained APIs.</p>
</section>
<section id="data"><h2>Data &amp; Features</h2>
<ul>
  <li>Feature engineering; <strong>Vertex AI Feature Store</strong> for reuse/consistency.</li>
  <li>Data in BigQuery / Cloud Storage; TFRecord, managed datasets.</li>
  <li>Handle imbalance, leakage, and train/serve skew.</li>
</ul>
</section>
<section id="train"><h2>Training &amp; Tuning</h2>
<ul>
  <li>Custom training with containers; distributed training; GPUs/TPUs.</li>
  <li><strong>Hyperparameter tuning</strong> (Vertex AI Vizier).</li>
  <li>Transfer learning and foundation-model fine-tuning.</li>
</ul>
</section>
<section id="serve"><h2>Serving</h2>
<p>Online (low-latency endpoints, autoscaling) vs batch prediction. Optimize cost/latency; use private endpoints; model versioning and traffic splitting.</p>
</section>
<section id="mlops"><h2>MLOps</h2>
<p><strong>Vertex AI Pipelines</strong> (Kubeflow/TFX) for automation, <strong>Model Monitoring</strong> for drift/skew, CI/CD for models, and the Model Registry for governance and lineage.</p>
</section>
""",
    ["Choose AutoML, custom training, or pretrained APIs per use case",
     "Use Vertex AI Model Registry, Endpoints, and Pipelines",
     "Engineer and serve features with Feature Store",
     "Prevent training/serving skew and data leakage",
     "Run distributed custom training on GPUs/TPUs",
     "Tune hyperparameters with Vertex AI Vizier",
     "Fine-tune foundation models (Gemini / Model Garden)",
     "Choose online vs batch prediction and optimize cost/latency",
     "Automate ML with Vertex AI Pipelines (Kubeflow/TFX)",
     "Monitor models for drift and skew in production"],
    "", "")

print("All certification pages written.")


# ── Service deep-dive pages ─────────────────────────────────
def service_page(slug, name, icon, tagline, meta_desc, sections, exam_tips, related):
    """sections: list of (heading, html_body). related: list of (href, label)."""
    toc = [(f"s{i}", h) for i, (h, _) in enumerate(sections)]
    toc.append(("exam-tips", "Exam Tips"))
    body = ""
    for i, (h, b) in enumerate(sections):
        body += f'<section id="s{i}"><h2>{h}</h2>{b}</section>\n'
    tips = "".join(f"<li>{t}</li>" for t in exam_tips)
    body += f'<section id="exam-tips"><h2>&#127919; Exam Tips</h2><div class="callout tip"><div class="callout-title">&#128161; Remember</div><ul>{tips}</ul></div></section>'
    rel = "".join(f'<a href="{href}" class="badge badge-blue" style="text-decoration:none;margin-right:0.4rem">{label}</a>' for href, label in related)
    header = phdr("badge-blue", "Service Deep Dive", icon, name, tagline)
    html = (HEAD(f"{name} - Service Deep Dive", meta_desc) + crumb(name) + header
            + f'<div class="container" style="padding-top:1rem">{rel}</div>'
            + wrap(toc, body) + FOOT)
    write(f"{DOCS}/service-{slug}.html", html)


service_page(
    "compute-engine", "Compute Engine", "&#128421;",
    "Scalable, high-performance virtual machines on Google's infrastructure.",
    "Compute Engine deep dive: machine types, Spot VMs, MIGs, images, disks, and networking.",
    [("What it is", "<p>Infrastructure-as-a-Service VMs. Full control of the OS. Billed per second with sustained and committed use discounts.</p>"),
     ("Machine families", "<div class='table-wrap'><table><thead><tr><th>Family</th><th>Use</th></tr></thead><tbody><tr><td>E2</td><td>Cost-optimized general purpose</td></tr><tr><td>N2/N2D/N4</td><td>Balanced general purpose</td></tr><tr><td>C3/C4</td><td>Compute-optimized</td></tr><tr><td>M3/M4</td><td>Memory-optimized (SAP, in-memory DB)</td></tr><tr><td>A3/G2</td><td>GPU/accelerator for ML</td></tr></tbody></table></div>"),
     ("Cost savers", "<ul><li><strong>Spot VMs</strong> - up to 60-91% off, preemptible.</li><li><strong>Committed use discounts</strong> - 1 or 3 year.</li><li><strong>Sustained use discounts</strong> - automatic.</li></ul>"),
     ("Scaling &amp; HA", "<p><strong>Managed Instance Groups (MIGs)</strong> provide autoscaling, autohealing, rolling updates, and multi-zone spread. Pair with a load balancer.</p>")],
    ["Spot VMs can be reclaimed with 30s notice - only for fault-tolerant work.",
     "MIGs (not unmanaged groups) give autoscaling and autohealing.",
     "Sustained use discounts apply automatically; CUDs require commitment.",
     "Use instance templates to define MIG VM configuration."],
    [("associate-cloud-engineer.html", "ACE"), ("professional-cloud-architect.html", "PCA")])

service_page(
    "cloud-storage", "Cloud Storage", "&#128230;",
    "Unified object storage for any amount of data, any access pattern.",
    "Cloud Storage deep dive: storage classes, lifecycle, security, and signed URLs.",
    [("What it is", "<p>Durable, highly available object storage. Buckets hold objects; names are globally unique. Location types: region, dual-region, multi-region.</p>"),
     ("Storage classes", "<div class='table-wrap'><table><thead><tr><th>Class</th><th>Min storage</th><th>Use</th></tr></thead><tbody><tr><td>Standard</td><td>none</td><td>Hot, frequently accessed</td></tr><tr><td>Nearline</td><td>30 days</td><td>&lt; once/month</td></tr><tr><td>Coldline</td><td>90 days</td><td>&lt; once/quarter</td></tr><tr><td>Archive</td><td>365 days</td><td>Backup/compliance</td></tr></tbody></table></div>"),
     ("Lifecycle &amp; security", "<ul><li>Lifecycle rules auto-transition or delete objects by age.</li><li>Uniform bucket-level access (IAM) vs fine-grained ACLs.</li><li>Signed URLs for time-limited, keyless access.</li><li>CMEK with Cloud KMS; object versioning; retention policies.</li></ul>")],
    ["All classes have the same availability SLA tier but differ in min storage duration and retrieval cost.",
     "Prefer uniform bucket-level access over ACLs for simpler IAM.",
     "Signed URLs grant temporary access without IAM changes.",
     "Lifecycle rules are the standard answer for cost optimization on cold data."],
    [("associate-cloud-engineer.html", "ACE"), ("professional-data-engineer.html", "PDE")])

service_page(
    "bigquery", "BigQuery", "&#128202;",
    "Serverless, highly scalable data warehouse with built-in ML.",
    "BigQuery deep dive: architecture, partitioning, clustering, pricing, and security.",
    [("What it is", "<p>Serverless analytics warehouse. Separates storage from compute. Standard SQL. Scales to petabytes with no infrastructure to manage.</p>"),
     ("Performance", "<ul><li><strong>Partitioning</strong> (by time/ingestion/integer) prunes scanned data.</li><li><strong>Clustering</strong> sorts data within partitions for faster filters.</li><li>Materialized views precompute results.</li></ul>"),
     ("Pricing", "<ul><li><strong>Storage</strong> - active vs long-term (auto-discounted).</li><li><strong>Compute</strong> - on-demand (per TB scanned) or capacity (slots/editions).</li></ul>"),
     ("Security", "<p>Dataset-level IAM, authorized views, row-level and column-level security, and VPC Service Controls.</p>")],
    ["Partition + cluster large tables to cut on-demand query cost.",
     "On-demand is priced per TB scanned - SELECT only needed columns.",
     "Use authorized views to share results without exposing source tables.",
     "BigQuery is OLAP (analytics), not OLTP - don't use it for transactional apps."],
    [("professional-data-engineer.html", "PDE"), ("associate-data-practitioner.html", "ADP")])

service_page(
    "gke", "Google Kubernetes Engine", "&#9881;",
    "Managed Kubernetes for containerized applications at scale.",
    "GKE deep dive: Autopilot vs Standard, node pools, networking, and security.",
    [("What it is", "<p>Managed Kubernetes. Google runs the control plane. <strong>Autopilot</strong> manages nodes for you (pay per pod); <strong>Standard</strong> gives node control.</p>"),
     ("Key concepts", "<ul><li>Clusters, node pools, pods, services, deployments.</li><li>Regional clusters for HA control plane.</li><li>Cluster autoscaler + horizontal pod autoscaler.</li></ul>"),
     ("Security &amp; networking", "<ul><li><strong>Workload Identity</strong> maps K8s SAs to Google SAs (no keys).</li><li>Binary Authorization enforces trusted images.</li><li>VPC-native (alias IP) clusters; private clusters.</li></ul>")],
    ["Autopilot = less ops, pay-per-pod; Standard = node control.",
     "Use Workload Identity instead of exporting service account keys.",
     "Regional clusters give a highly available control plane.",
     "VPC-native clusters use alias IP ranges for pods/services."],
    [("professional-cloud-architect.html", "PCA"), ("professional-cloud-developer.html", "PCD")])

service_page(
    "iam", "Cloud IAM", "&#128273;",
    "Fine-grained identity and access management across Google Cloud.",
    "Cloud IAM deep dive: members, roles, policies, service accounts, and best practices.",
    [("Core model", "<p>An IAM policy binds <strong>members</strong> (who) to <strong>roles</strong> (what) on a <strong>resource</strong> (where). Policies are inherited down the hierarchy; the effective policy is the union.</p>"),
     ("Roles", "<ul><li><strong>Basic</strong> - Owner/Editor/Viewer (avoid in prod).</li><li><strong>Predefined</strong> - granular per service.</li><li><strong>Custom</strong> - exact permissions you choose.</li></ul>"),
     ("Service accounts", "<p>Identities for workloads. Prefer attaching SAs to resources and using Workload Identity Federation over downloading JSON keys.</p>")],
    ["Effective permissions are the UNION of all inherited policies.",
     "Grant least privilege with predefined/custom roles, not basic roles.",
     "Service Account User role lets a principal impersonate an SA.",
     "Prefer Workload Identity Federation over long-lived SA keys."],
    [("professional-cloud-security-engineer.html", "PCSE"), ("associate-cloud-engineer.html", "ACE")])

# ── Services index ──────────────────────────────────────────
services_index = (HEAD("Service Deep Dives", "In-depth guides to the core Google Cloud services that appear across every certification exam.")
    + crumb("Service Deep Dives")
    + phdr("badge-blue", "Reference", "&#129513;", "Service Deep Dives", "Focused, exam-oriented guides to the Google Cloud services that show up again and again across certifications.")
    + """<div class="container section"><div class="grid-3">
    <a href="service-compute-engine.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128421;</div><h3>Compute Engine</h3><p style="color:var(--text-muted);font-size:0.9rem">VMs, machine types, Spot, MIGs.</p></a>
    <a href="service-gke.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#9881;</div><h3>Google Kubernetes Engine</h3><p style="color:var(--text-muted);font-size:0.9rem">Autopilot vs Standard, Workload Identity.</p></a>
    <a href="service-cloud-storage.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128230;</div><h3>Cloud Storage</h3><p style="color:var(--text-muted);font-size:0.9rem">Classes, lifecycle, signed URLs.</p></a>
    <a href="service-bigquery.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128202;</div><h3>BigQuery</h3><p style="color:var(--text-muted);font-size:0.9rem">Partitioning, clustering, pricing.</p></a>
    <a href="service-iam.html" class="card" style="text-decoration:none;color:var(--text)"><div class="card-icon">&#128273;</div><h3>Cloud IAM</h3><p style="color:var(--text-muted);font-size:0.9rem">Members, roles, service accounts.</p></a>
    </div></div>""" + FOOT)
write(f"{DOCS}/services.html", services_index)


# ── Foundations: Linux ──────────────────────────────────────
linux = (HEAD("Linux Fundamentals", "Linux fundamentals for cloud engineers: filesystem, permissions, processes, networking, and shell scripting.")
    + crumb("Linux Fundamentals")
    + phdr("badge-teal", "Foundations", "&#128039;", "Linux Fundamentals",
           "Most Google Cloud VMs and containers run Linux. These fundamentals make every certification and hands-on task easier.",
           '<span class="badge badge-green">Beginner friendly</span>')
    + wrap([("filesystem","Filesystem"),("permissions","Permissions"),("processes","Processes"),
            ("networking","Networking"),("scripting","Shell Scripting"),("checklist","Checklist")],
    """
<section id="filesystem"><h2>Filesystem &amp; Navigation</h2>
<div class="table-wrap"><table><thead><tr><th>Command</th><th>Does</th></tr></thead><tbody>
<tr><td><code>pwd</code></td><td>Print working directory</td></tr>
<tr><td><code>ls -la</code></td><td>List all files with details</td></tr>
<tr><td><code>cd /path</code></td><td>Change directory</td></tr>
<tr><td><code>cp / mv / rm</code></td><td>Copy / move / remove</td></tr>
<tr><td><code>find / grep</code></td><td>Search files / text</td></tr>
<tr><td><code>cat / less / tail -f</code></td><td>View / page / follow a file</td></tr>
</tbody></table></div>
<p>Key directories: <code>/etc</code> (config), <code>/var/log</code> (logs), <code>/home</code> (users), <code>/tmp</code> (temp), <code>/usr/bin</code> (programs).</p>
</section>
<section id="permissions"><h2>Permissions</h2>
<p>Files have owner/group/other permissions: read (4), write (2), execute (1).</p>
<pre><code>chmod 644 file.txt   # rw-r--r--
chmod 755 script.sh  # rwxr-xr-x
chown user:group f   # change ownership
sudo command         # run as root</code></pre>
</section>
<section id="processes"><h2>Processes &amp; Services</h2>
<pre><code>ps aux | grep nginx    # find a process
top / htop             # live resource usage
kill -9 PID            # force-kill
systemctl status sshd  # service status
journalctl -u sshd     # service logs</code></pre>
</section>
<section id="networking"><h2>Networking</h2>
<pre><code>ip a                 # interfaces/addresses
ss -tulpn            # listening ports
curl -I https://x    # HTTP headers
ping / traceroute    # connectivity
ssh user@host        # remote shell</code></pre>
<div class="callout tip"><div class="callout-title">&#128161; On GCP</div><p>Connect to Compute Engine VMs with <code>gcloud compute ssh VM_NAME</code>, which handles keys for you.</p></div>
</section>
<section id="scripting"><h2>Shell Scripting</h2>
<pre><code>#!/bin/bash
set -euo pipefail
for f in *.log; do
  echo "Processing $f"
  gzip "$f"
done</code></pre>
</section>
""" + chk([
    "Navigate the filesystem and use ls, cd, cp, mv, rm",
    "Search with find and grep",
    "Read logs with cat, less, and tail -f",
    "Understand chmod numeric permissions (644, 755)",
    "Change ownership with chown and use sudo",
    "Inspect processes with ps, top, and kill",
    "Manage services with systemctl and journalctl",
    "Check networking with ip, ss, curl, and ping",
    "SSH to a host and to a GCE VM with gcloud",
    "Write a basic bash script with a loop"],
    "foundations-networking.html", "Networking Fundamentals"))
    + FOOT)
write(f"{DOCS}/foundations-linux.html", linux)


# ── Foundations: Networking ─────────────────────────────────
net = (HEAD("Networking Fundamentals", "Networking fundamentals for cloud: OSI model, TCP/IP, DNS, CIDR, subnetting, routing, and firewalls.")
    + crumb("Networking Fundamentals")
    + phdr("badge-blue", "Foundations", "&#127760;", "Networking Fundamentals",
           "Networking is the backbone of every cloud architecture. Master these before the Network Engineer and Architect exams.",
           '<span class="badge badge-green">Essential</span>')
    + wrap([("osi","OSI &amp; TCP/IP"),("ip","IP &amp; CIDR"),("dns","DNS"),
            ("routing","Routing &amp; NAT"),("firewalls","Firewalls &amp; LB"),("checklist","Checklist")],
    """
<section id="osi"><h2>OSI &amp; TCP/IP</h2>
<div class="table-wrap"><table><thead><tr><th>Layer</th><th>Example</th></tr></thead><tbody>
<tr><td>7 Application</td><td>HTTP, DNS, gRPC</td></tr>
<tr><td>4 Transport</td><td>TCP, UDP</td></tr>
<tr><td>3 Network</td><td>IP, routing</td></tr>
<tr><td>2 Data link</td><td>Ethernet, MAC</td></tr>
</tbody></table></div>
<p>Google Cloud load balancers map to layers: Application LB (L7), Network LB (L4).</p>
</section>
<section id="ip"><h2>IP Addressing &amp; CIDR</h2>
<ul>
<li>Private ranges (RFC 1918): <code>10.0.0.0/8</code>, <code>172.16.0.0/12</code>, <code>192.168.0.0/16</code>.</li>
<li>CIDR: <code>/24</code> = 256 addresses, <code>/16</code> = 65,536. Smaller number = larger network.</li>
<li>Plan non-overlapping ranges for VPCs, subnets, and hybrid connectivity.</li>
</ul>
</section>
<section id="dns"><h2>DNS</h2>
<p>Resolves names to IPs. Record types: A/AAAA, CNAME, MX, TXT, NS. On GCP use <strong>Cloud DNS</strong> with public and private zones, plus DNS peering/forwarding.</p>
</section>
<section id="routing"><h2>Routing &amp; NAT</h2>
<p>Routes direct traffic between networks. <strong>Cloud NAT</strong> gives private VMs outbound internet without external IPs. <strong>Cloud Router</strong> exchanges BGP routes for hybrid connectivity.</p>
</section>
<section id="firewalls"><h2>Firewalls &amp; Load Balancing</h2>
<ul>
<li>GCP firewall rules are <strong>stateful</strong>; implied deny ingress, allow egress.</li>
<li>Target by network tags or service accounts.</li>
<li>Load balancers distribute traffic; health checks remove unhealthy backends.</li>
</ul>
</section>
""" + chk([
    "Explain the OSI layers and map LBs to L4/L7",
    "Know TCP vs UDP",
    "Recognize RFC 1918 private ranges",
    "Calculate hosts for /24, /16, /28 CIDR blocks",
    "Plan non-overlapping VPC/subnet ranges",
    "Explain DNS record types (A, CNAME, MX, TXT)",
    "Use Cloud DNS public and private zones",
    "Explain Cloud NAT and Cloud Router (BGP)",
    "Understand stateful firewall rules and target tags",
    "Explain load balancing and health checks"],
    "cloud-digital-leader.html", "Cloud Digital Leader"))
    + FOOT)
write(f"{DOCS}/foundations-networking.html", net)


# ── Quiz page ───────────────────────────────────────────────
quiz = (HEAD("Practice Quiz", "Free Google Cloud certification practice quiz with instant scoring, domain breakdowns, and explanations.")
    + crumb("Practice Quiz")
    + phdr("badge-blue", "Study Tool", "&#129513;", "Practice Quiz",
           "Test yourself with randomized, timed questions per certification. Instant scoring, a domain breakdown, and an explanation for every answer. Your best scores are saved privately in your browser.")
    + '<div class="container section"><div id="quiz-app"></div></div>'
    + '<script src="../assets/js/quiz.js" defer></script>' + FOOT)
write(f"{DOCS}/quiz.html", quiz)

# ── Flashcards page (with inline .fc-* styles) ──────────────
FC_STYLES = """<style>
.fc-topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;flex-wrap:wrap;gap:0.5rem}
.fc-meta{display:flex;gap:0.5rem;flex-wrap:wrap}
.fc-remaining{color:var(--text-muted);font-size:0.85rem;font-weight:600}
.fc-progress{height:6px;background:var(--border);border-radius:999px;overflow:hidden;margin-bottom:1rem}
.fc-progress-fill{height:100%;background:linear-gradient(90deg,var(--gcp-blue),var(--gcp-green));transition:width 0.4s}
.flashcard{perspective:1200px;cursor:pointer;outline:none;margin-bottom:1.25rem}
.flashcard-inner{position:relative;transform-style:preserve-3d;transition:transform 0.5s cubic-bezier(0.22,1,0.36,1);min-height:260px}
.flashcard.flipped .flashcard-inner{transform:rotateY(180deg)}
.flashcard-face{position:absolute;inset:0;backface-visibility:hidden;background:var(--bg-card);border:1px solid var(--border);border-radius:14px;padding:2rem;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.flashcard-back{transform:rotateY(180deg)}
.fc-face-label{font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.75rem}
.fc-q{font-size:1.15rem;font-weight:600;line-height:1.5}
.fc-a{font-size:1.1rem;font-weight:700;color:var(--gcp-green);margin-bottom:0.75rem}
.fc-exp{color:var(--text-muted);font-size:0.9rem}
.fc-hint{color:var(--text-muted);font-size:0.78rem;margin-top:1rem}
.fc-controls{min-height:60px}
.fc-flip-row{display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap}
.fc-rate-prompt{text-align:center;color:var(--text-muted);font-size:0.9rem;margin:0 0 0.6rem}
.fc-rate-btns{display:flex;gap:0.6rem;justify-content:center;flex-wrap:wrap}
.fc-rate-btns .btn{position:relative;min-width:90px;justify-content:center;border:1px solid var(--border);background:var(--bg-hover);color:var(--text)}
.fc-rate-key{display:inline-block;font-size:0.7rem;background:var(--border);border-radius:4px;padding:0 0.35em;margin-right:0.4em}
.fc-again{border-color:#ff6b6b!important}.fc-hard{border-color:var(--gcp-yellow)!important}
.fc-good{border-color:var(--gcp-blue)!important}.fc-easy{border-color:var(--gcp-green)!important}
.fc-stats{display:flex;gap:1.5rem;margin:1rem 0 1.25rem}
.fc-stat{text-align:center}.fc-stat-num{font-size:1.6rem;font-weight:800;color:var(--accent)}
.fc-stat-lbl{font-size:0.78rem;color:var(--text-muted)}
.fc-done{text-align:center}
</style>"""
flash = (HEAD("Flashcards", "Spaced-repetition flashcards for Google Cloud certifications, powered by the SM-2 algorithm. Free and private.")
    + crumb("Flashcards")
    + phdr("badge-blue", "Study Tool", "&#128218;", "Flashcards",
           "Study with spaced repetition. Flip each card, rate your recall, and the SM-2 scheduler brings it back at the right time. All progress stays in your browser.")
    + FC_STYLES
    + '<div class="container section"><div id="flashcards-app"></div></div>'
    + '<script src="../assets/js/flashcards.js" defer></script>' + FOOT)
write(f"{DOCS}/flashcards.html", flash)

# ── Dashboard page ──────────────────────────────────────────
dash = (HEAD("My Progress", "Track your Google Cloud certification study progress: quiz readiness and checklist completion, saved privately in your browser.")
    + crumb("My Progress")
    + phdr("badge-blue", "Study Tool", "&#128202;", "My Progress Dashboard",
           "Your quiz readiness per certification and overall study-checklist completion in one place. Everything is private and stored locally - no account needed.")
    + '<div class="container section"><div id="dashboard-app"></div></div>'
    + '<script src="../assets/js/dashboard.js" defer></script>' + FOOT)
write(f"{DOCS}/dashboard.html", dash)


# ── Cheat Sheets: confusing pairs ───────────────────────────
def pair(a, b, rows):
    body = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>" for r in rows)
    return f'<div class="card" style="margin-bottom:1.5rem"><h3>{a} vs {b}</h3><div class="table-wrap"><table><thead><tr><th>{a}</th><th>{b}</th></tr></thead><tbody>{body}</tbody></table></div></div>'

cheat_body = (
    pair("Cloud SQL", "Spanner", [
        ("Regional managed MySQL/PostgreSQL/SQL Server", "Globally distributed relational"),
        ("Vertical scaling, read replicas", "Horizontal scaling, 99.999% multi-region"),
        ("Lift-and-shift OLTP", "Global scale + strong consistency")]) +
    pair("Bigtable", "BigQuery", [
        ("Wide-column NoSQL (operational)", "Analytics data warehouse (OLAP)"),
        ("Low-latency, high-throughput reads/writes", "Serverless SQL over huge datasets"),
        ("Time-series, IoT, fraud detection", "Reporting, BI, ad-hoc analytics")]) +
    pair("Pub/Sub", "Cloud Tasks", [
        ("Many-to-many event streaming", "Explicit task dispatch to a worker"),
        ("Fan-out, decoupling, analytics ingestion", "Rate-limited, scheduled task execution"),
        ("At-least-once (and exactly-once option)", "Per-task control and deduplication")]) +
    pair("Dataflow", "Dataproc", [
        ("Serverless Apache Beam (batch + stream)", "Managed Spark/Hadoop clusters"),
        ("No cluster to manage, autoscaling", "Lift-and-shift existing Spark/Hadoop"),
        ("Unified pipelines", "Ephemeral clusters for jobs")]) +
    pair("Firewall Rules", "Hierarchical Firewall Policies", [
        ("Applied at the VPC level", "Applied at org/folder level, inherited"),
        ("Target by tags or service accounts", "Enforce org-wide guardrails"),
        ("Project-scoped", "Centralized governance")]) +
    pair("Cloud Run", "GKE", [
        ("Serverless containers, scale-to-zero", "Full Kubernetes control"),
        ("Simple stateless services", "Complex microservices, operators, DaemonSets"),
        ("Pay per request", "Pay for nodes (Standard) or pods (Autopilot)")]) +
    pair("Basic Roles", "Predefined/Custom Roles", [
        ("Owner/Editor/Viewer, broad", "Granular per-service permissions"),
        ("Convenient but over-privileged", "Least-privilege, recommended for prod"),
        ("Avoid in production", "Preferred everywhere")]) +
    pair("Committed Use Discounts", "Spot VMs", [
        ("Commit 1 or 3 years for steady workloads", "Up to ~91% off spare capacity"),
        ("Guaranteed capacity + discount", "Can be preempted with ~30s notice"),
        ("Predictable baseline", "Fault-tolerant batch only")]))

cheat = (HEAD("Confusing Pairs Cheat Sheet", "Side-by-side comparisons of look-alike Google Cloud services that commonly appear on certification exams.")
    + crumb("Cheat Sheets")
    + phdr("badge-blue", "Quick Reference", "&#128221;", "Confusing Pairs Cheat Sheet",
           "The look-alike Google Cloud services that trip people up on exams, compared side by side. Memorize the right-hand distinctions.")
    + f'<div class="container section">{cheat_body}</div>' + FOOT)
write(f"{DOCS}/cheatsheets.html", cheat)


# ── Labs & Practice ─────────────────────────────────────────
labs = (HEAD("Labs &amp; Practice", "Free and low-cost hands-on labs and practice resources for Google Cloud certifications.")
    + crumb("Labs & Practice")
    + phdr("badge-blue", "Hands-On", "&#128300;", "Labs &amp; Practice",
           "Nothing beats hands-on practice. These platforms let you build real Google Cloud solutions - most have free tiers or credits.")
    + """<div class="container section">
    <div class="grid-2">
      <a href="https://www.cloudskillsboost.google/" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>&#127891; Google Cloud Skills Boost</h3><p style="color:var(--text-muted)">Guided labs, quests, and skill badges in temporary provisioned GCP environments. The official hands-on platform.</p><span class="badge badge-green">FREE+PAID</span></a>
      <a href="https://cloud.google.com/free" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>&#127381; GCP Free Tier + $300 Credit</h3><p style="color:var(--text-muted)">A real GCP account with a 90-day $300 credit and always-free products. Best for building end-to-end.</p><span class="badge badge-green">FREE</span></a>
      <a href="https://www.qwiklabs.com/" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>&#129514; Qwiklabs</h3><p style="color:var(--text-muted)">Short, scenario-based labs (now part of Skills Boost).</p><span class="badge badge-blue">FREE+PAID</span></a>
      <a href="https://codelabs.developers.google.com/" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>&#128187; Google Codelabs</h3><p style="color:var(--text-muted)">Free step-by-step tutorials across Google Cloud products.</p><span class="badge badge-green">FREE</span></a>
    </div>
    <h2 style="margin-top:2.5rem">Suggested Practice Projects</h2>
    <div class="grid-3">
      <div class="card"><h4>Static site on Cloud Storage + CDN</h4><p style="color:var(--text-muted);font-size:0.9rem">Host a site, front it with the global LB and Cloud CDN. (ACE/PCA)</p></div>
      <div class="card"><h4>Serverless API</h4><p style="color:var(--text-muted);font-size:0.9rem">Cloud Run + Firestore + Pub/Sub. (PCD)</p></div>
      <div class="card"><h4>Data pipeline</h4><p style="color:var(--text-muted);font-size:0.9rem">Pub/Sub &rarr; Dataflow &rarr; BigQuery, dashboard in Looker Studio. (PDE/ADP)</p></div>
      <div class="card"><h4>GKE microservices</h4><p style="color:var(--text-muted);font-size:0.9rem">Deploy to Autopilot with Workload Identity. (PCA/PCDOE)</p></div>
      <div class="card"><h4>Secure VPC</h4><p style="color:var(--text-muted);font-size:0.9rem">Custom VPC, Cloud NAT, firewall policies, IAP. (PCNE/PCSE)</p></div>
      <div class="card"><h4>ML on Vertex AI</h4><p style="color:var(--text-muted);font-size:0.9rem">Train, deploy an endpoint, monitor drift. (PMLE)</p></div>
    </div>
    </div>""" + FOOT)
write(f"{DOCS}/labs.html", labs)


# ── Resources ───────────────────────────────────────────────
resources = (HEAD("Resources", "Curated free and paid study resources for Google Cloud certifications: official learning, courses, and practice.")
    + crumb("Resources")
    + phdr("badge-blue", "Curated", "&#128218;", "Study Resources",
           "The best places to learn Google Cloud, official content first. Everything here is either free or clearly marked as paid.")
    + """<div class="container section">
    <h2>Official</h2>
    <div class="grid-2">
      <a href="https://www.cloudskillsboost.google/" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Google Cloud Skills Boost</h3><p style="color:var(--text-muted)">Official learning paths, labs, and skill badges.</p><span class="badge badge-green">FREE+PAID</span></a>
      <a href="https://cloud.google.com/docs" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Google Cloud Documentation</h3><p style="color:var(--text-muted)">Authoritative product docs and how-to guides.</p><span class="badge badge-green">FREE</span></a>
      <a href="https://cloud.google.com/architecture" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Architecture Center</h3><p style="color:var(--text-muted)">Reference architectures and best practices (incl. the Architecture Framework).</p><span class="badge badge-green">FREE</span></a>
      <a href="https://cloud.google.com/learn/certification" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Certification Hub + Exam Guides</h3><p style="color:var(--text-muted)">Official exam guides, sample questions, and registration.</p><span class="badge badge-green">FREE</span></a>
    </div>
    <h2 style="margin-top:2rem">Courses &amp; Practice</h2>
    <div class="grid-2">
      <a href="https://www.coursera.org/googlecloud" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Coursera - Google Cloud</h3><p style="color:var(--text-muted)">Official specializations and professional certificates.</p><span class="badge badge-orange">PAID</span></a>
      <a href="https://www.pluralsight.com/partners/google-cloud" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Pluralsight / A Cloud Guru</h3><p style="color:var(--text-muted)">Video courses and hands-on labs.</p><span class="badge badge-orange">PAID</span></a>
      <a href="https://www.udemy.com/" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Udemy Practice Exams</h3><p style="color:var(--text-muted)">Many well-rated GCP practice-exam courses.</p><span class="badge badge-orange">PAID</span></a>
      <a href="https://cloud.google.com/blog" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text)"><h3>Google Cloud Blog</h3><p style="color:var(--text-muted)">Product announcements and deep dives.</p><span class="badge badge-green">FREE</span></a>
    </div>
    <h2 style="margin-top:2rem">Recommended Path</h2>
    <div class="card"><p style="margin:0">Linux &rarr; Networking &rarr; Cloud Digital Leader &rarr; Associate Cloud Engineer &rarr; a Professional cert aligned to your role (Architect, Developer, DevOps, Security, Network, Database, Data Engineer, or ML Engineer).</p></div>
    </div>""" + FOOT)
write(f"{DOCS}/resources.html", resources)


# ── News ────────────────────────────────────────────────────
news = (HEAD("Google Cloud News", "The latest Google Cloud release notes and announcements, updated automatically every week.")
    + crumb("News")
    + phdr("badge-blue", "Auto-Updated", "&#128240;", "Latest Google Cloud News",
           "Fresh from the official Google Cloud release notes feed. This page is refreshed automatically every week by GitHub Actions.")
    + """<div class="container section">
    <div id="news-list" class="grid-2"><div class="card"><p style="color:var(--text-muted)">Loading Google Cloud news&hellip;</p></div></div>
    <p id="news-updated" style="color:var(--text-muted);font-size:0.85rem;margin-top:1.5rem"></p>
    </div>
    <script>
    (function(){
      var el=document.getElementById("news-list"),up=document.getElementById("news-updated");
      function esc(s){return String(s==null?"":s).replace(/[&<>\\"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}[c];});}
      fetch("../data/gcp-news.json",{cache:"no-cache"})
        .then(function(r){if(!r.ok)throw 0;return r.json();})
        .then(function(data){
          var items=(data&&data.items)||[];
          if(!items.length){el.innerHTML='<div class="card"><p style="color:var(--text-muted)">No news items yet.</p></div>';return;}
          el.innerHTML=items.slice(0,60).map(function(it){
            return '<a href="'+esc(it.link||"#")+'" target="_blank" rel="noopener" class="card" style="text-decoration:none;color:var(--text);display:block">'+
              '<div class="flex-wrap" style="margin-bottom:0.5rem"><span class="badge badge-blue">'+esc(it.date||"")+'</span></div>'+
              '<h3 style="font-size:1rem;margin:0 0 0.4rem">'+esc(it.title||"")+'</h3>'+
              '<p style="color:var(--text-muted);font-size:0.85rem;margin:0">'+esc((it.summary||"").slice(0,180))+'</p></a>';
          }).join("");
          if(up&&data.updated)up.textContent="Last updated: "+data.updated;
        })
        .catch(function(){el.innerHTML='<div class="card"><p style="color:var(--text-muted)">Could not load news right now. Please try again later.</p></div>';});
    })();
    </script>""" + FOOT)
write(f"{DOCS}/news.html", news)


# ── Affiliate disclosure ────────────────────────────────────
aff = (HEAD("Affiliate Disclosure", "Affiliate and transparency disclosure for GCP Study Hub.")
    + crumb("Affiliate Disclosure")
    + phdr("badge-blue", "Transparency", "&#128196;", "Affiliate Disclosure", "How this free, open-source project is funded and our commitment to unbiased recommendations.")
    + """<div class="container section" style="max-width:760px">
    <p>GCP Study Hub is a free, community-driven, open-source project. Some outbound links to third-party courses or platforms may be affiliate links, meaning we could earn a small commission at no additional cost to you if you make a purchase.</p>
    <h2>Our commitment</h2>
    <ul>
      <li>We always point to official, free Google Cloud resources first.</li>
      <li>Recommendations are based on quality and learner value, not commission.</li>
      <li>Paid resources are clearly labeled with a <span class="badge badge-orange">PAID</span> badge.</li>
      <li>You are never required to use any paid resource to study with this site.</li>
    </ul>
    <p style="color:var(--text-muted)">This site is not affiliated with, endorsed by, or sponsored by Google LLC. All Google Cloud and Google trademarks belong to Google LLC.</p>
    </div>""" + FOOT)
write(f"{DOCS}/affiliate-disclosure.html", aff)


# ── Generate search-index.json and sitemap.xml ──────────────
def _generate_index_and_sitemap():
    import re, html, json
    docs_out = []
    for path, content in WRITTEN_PAGES:
        rel = os.path.relpath(path, BASE).replace(os.sep, "/")
        m = re.search(r"<title>(.*?)</title>", content, re.S)
        title = html.unescape(m.group(1)).replace(" - GCP Study Hub", "").strip() if m else rel
        dm = re.search(r'<meta name="description" content="(.*?)"', content, re.S)
        desc = html.unescape(dm.group(1)).strip() if dm else ""
        headings = [html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
                    for h in re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.S)]
        headings = [h for h in headings if h][:12]
        docs_out.append({"url": _canonical_rel(rel) or "index.html",
                         "title": title, "desc": desc, "headings": headings})
    with open(f"{BASE}/data/search-index.json", "w") as f:
        json.dump({"generated": True, "count": len(docs_out), "docs": docs_out}, f, indent=1)
    print(f"  Written: search-index.json ({len(docs_out)} pages)")

    # Priority ordering for sitemap
    def _priority(rel):
        if rel == "index.html":
            return "1.0"
        if "foundations" in rel or rel.startswith("docs/cloud-digital-leader") or rel.startswith("docs/associate-") or rel.startswith("docs/professional-"):
            return "0.8"
        return "0.6"
    urls = []
    for path, _ in WRITTEN_PAGES:
        rel = os.path.relpath(path, BASE).replace(os.sep, "/")
        loc = f"{SITE_URL}/{_canonical_rel(rel)}"
        urls.append(f"  <url><loc>{loc}</loc><priority>{_priority(rel)}</priority></url>")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "\n".join(urls) + "\n</urlset>\n")
    with open(f"{BASE}/sitemap.xml", "w") as f:
        f.write(sitemap)
    print(f"  Written: sitemap.xml ({len(urls)} urls)")

_generate_index_and_sitemap()
print("Done. Build complete.")
