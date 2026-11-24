(function () {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let LESSONS = [], ALL = [], COURSES = [], CUR = null, MODULES = []; const BADGES = window.BADGES; // LESSONS/MODULES = current course only
  const API_BASE = window.API_BASE || 'http://localhost:8000/api/v1';
  const TOKEN_KEY = 'sqlacademy.token';
  let SQL = null, USER = null;
  let S = { xp: 0, level: 1, streak: 0, completed: {}, badges: [] }; // mirrors server progress

  /* ---------------- API client ---------------- */
  const getToken = () => { try { return localStorage.getItem(TOKEN_KEY); } catch { return null; } };
  const setToken = t => { try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY); } catch { /* ignore */ } };
  async function api(path, opts = {}) {
    let res;
    try {
      res = await fetch(API_BASE + path, {
        method: opts.method || 'GET',
        headers: { 'Content-Type': 'application/json', ...(getToken() ? { Authorization: 'Bearer ' + getToken() } : {}) },
        body: opts.body ? JSON.stringify(opts.body) : undefined
      });
    } catch { throw Object.assign(new Error('Cannot reach the server. Is the backend running on ' + API_BASE + '?'), { network: true }); }
    if (res.status === 401 && !opts.noAuthRedirect) { setToken(null); USER = null; showAuth(); throw Object.assign(new Error('Session expired'), { auth: true }); }
    if (res.status === 204) return null;
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const d = data.detail;
      throw new Error(typeof d === 'string' ? d : Array.isArray(d) ? d.map(x => x.msg).join('; ') : 'Request failed');
    }
    return data;
  }

  const RT = () => (CUR && CUR.runtime) || 'sql';
  const COURSE_KEY = 'sqlacademy.course';
  const SOON = [['🐍', 'Python', 'python'], ['🟨', 'JavaScript', 'javascript'], ['🎨', 'HTML & CSS', 'html-css'], ['🌿', 'Git', 'git']];
  function selectCourse(id) {
    CUR = COURSES.find(c => c.id === id) || COURSES[0] || null;
    MODULES = CUR ? CUR.modules : [];
    LESSONS = CUR ? ALL.filter(l => l.course_id === CUR.id) : [];
    try { if (CUR) localStorage.setItem(COURSE_KEY, CUR.id); } catch { /* ignore */ }
  }
  const courseProgress = c => { const ls = ALL.filter(l => l.course_id === c.id); return { total: ls.length, done: ls.filter(l => S.completed[l.id]).length }; };
  const unlocked = id => {
    if (USER && USER.role === 'admin') return true;
    const l = LESSONS.find(x => x.id === id); if (!l) return false;
    const pool = CUR && CUR.unlock_mode === 'by_module' ? LESSONS.filter(x => x.module_id === l.module_id) : LESSONS;
    const i = pool.indexOf(l);
    return i === 0 || (i > 0 && !!S.completed[pool[i - 1].id]);
  };

  function toast(msg) {
    const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg;
    $('#toasts').appendChild(t); setTimeout(() => t.remove(), 4200);
  }
  const badgeInfo = id => BADGES.find(b => b.id === id);

  /* ---------------- Local SQL engine (run/playground only; grading is server-side) ---------------- */
  function newDb() { const db = new SQL.Database(); db.run(window.SEED_SQL); return db; }

  function tableHtml(set, limit = 200) {
    if (!set || !set.columns.length) return '';
    const head = set.columns.map(c => `<th>${esc(c)}</th>`).join('');
    const body = set.values.slice(0, limit).map(r => '<tr>' + r.map(v => v === null ? '<td class="null">NULL</td>' : `<td>${esc(v)}</td>`).join('') + '</tr>').join('');
    const more = set.values.length > limit ? `<p class="empty">Showing first ${limit} of ${set.values.length} rows.</p>` : '';
    return `<div class="tbl"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>${more}`;
  }
  function schemaHtml(db) {
    const names = db.exec("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")[0]?.values.flat() || [];
    return names.map(n => {
      const cols = db.exec(`PRAGMA table_info(${n})`)[0].values.map(c => c[1]).join(', ');
      return `<div class="tb"><b>${esc(n)}</b><span>${esc(cols)}</span></div>`;
    }).join('');
  }

  function mountEditor(root, { starter, lesson, onPass, runtime = 'sql' }) {
    const py = runtime === 'python';
    let db = py ? null : newDb(), hintsShown = 0;
    const ta = $('textarea.code', root), out = $('.out-body', root), sch = $('.schema', root), stdin = $('.stdin', root);
    ta.value = starter;
    if (!py) sch.innerHTML = schemaHtml(db);
    const show = html => { out.innerHTML = html; };

    async function runPython() {
      const code = ta.value;
      if (!code.trim()) return show('<div class="msg warn">Write some code first.</div>');
      show('<p class="empty">Running on the server…</p>');
      try {
        const r = await api('/run', { method: 'POST', body: { runtime: 'python', code, stdin: stdin ? stdin.value : '' } });
        let html = '';
        if (r.timed_out) html += '<div class="msg err">Time limit reached – check for an infinite loop.</div>';
        else if (r.error) html += `<div class="msg err">${esc(r.error)}</div>`;
        html += r.stdout ? `<pre class="stdout">${esc(r.stdout)}</pre>` : (r.error || r.timed_out ? '' : '<p class="empty">The program finished without printing anything.</p>');
        show(html + `<p class="empty" style="margin-top:8px">${r.ms} ms</p>`);
      } catch (e) { if (!e.auth) show(`<div class="msg err">${esc(e.message)}</div>`); }
    }
    function run() {
      if (py) return runPython();
      const sql = ta.value.trim();
      if (!sql) return show('<div class="msg warn">Type a query first.</div>');
      const t0 = performance.now();
      try {
        const res = db.exec(sql);
        const ms = Math.round(performance.now() - t0);
        if (!res.length) show(`<div class="msg info">Statement executed (${db.getRowsModified()} row(s) changed) in ${ms} ms.</div>`);
        else show(`<div class="msg info">${res[res.length - 1].values.length} row(s) · ${ms} ms</div>` + tableHtml(res[res.length - 1]));
        sch.innerHTML = schemaHtml(db);
      } catch (e) { show(`<div class="msg err">${esc(e.message)}</div>`); }
    }
    $('[data-act=run]', root).onclick = run;
    $('[data-act=reset]', root).onclick = () => {
      ta.value = starter;
      if (py) { if (stdin) stdin.value = ''; show('<p class="empty">Editor reset.</p>'); return; }
      db.close(); db = newDb(); show('<p class="empty">Database and editor reset.</p>'); sch.innerHTML = schemaHtml(db);
    };
    ta.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); }
      if (e.key === 'Tab') { e.preventDefault(); ta.setRangeText('  ', ta.selectionStart, ta.selectionEnd, 'end'); }
    });

    if (lesson) {
      const hb = $('[data-act=hint]', root), hout = $('.hint-out', root), sb = $('[data-act=submit]', root);
      const hints = [];
      const paint = () => { hout.innerHTML = hints.map((h, i) => `<div class="hint reveal"><b>Hint ${i + 1}:</b> ${esc(h)}</div>`).join(''); };
      api(`/hints/${lesson.id}`).then(list => { hints.push(...list); paint(); }).catch(() => { });
      hb.onclick = async () => {
        hb.disabled = true;
        try {
          const h = await api(`/lessons/${lesson.id}/hint`, { method: 'POST' });
          hints[h.level - 1] = h.hint; hintsShown = h.level; paint();
          hb.disabled = h.level >= h.total;
          if (!hb.disabled) hb.textContent = '💡 Next hint';
          else hb.textContent = '💡 No more hints';
        } catch (e) { hb.disabled = false; toast(e.message); }
      };
      sb.onclick = async () => {
        sb.disabled = true; show('<p class="empty">Checking on the server…</p>');
        if (py && stdin) stdin.value = stdin.value; // stdin box is for Run only; graded tests bring their own input
        try {
          const r = await api('/submissions', { method: 'POST', body: { lesson_id: lesson.id, sql: ta.value } });
          S = r.progress;
          if (r.passed) { show(`<div class="msg ok reveal">✓ ${esc(r.message)}</div>`); onPass(r); }
          else show(`<div class="msg err reveal" style="white-space:pre-wrap">✗ ${esc(r.message)}</div><div class="msg warn">Try again – use <b>Hint</b> if you are stuck.</div>`);
        } catch (e) { if (!e.auth) show(`<div class="msg err">${esc(e.message)}</div>`); }
        finally { sb.disabled = false; }
      };
    }
    return { setSql: v => { ta.value = v; ta.focus(); }, run };
  }
  const editorHtml = (lesson, runtime = 'sql') => {
    const py = runtime === 'python';
    return `
    <div class="panel">
      <div class="editor-head"><b>${py ? 'Python editor' : 'SQL editor'}</b>
        <div class="actions">
          <button class="btn secondary sm" data-act="reset">↺ Reset</button>
          ${lesson ? '<button class="btn secondary sm" data-act="hint">💡 Hint</button>' : ''}
          <button class="btn sm" data-act="run">▶ Run</button>
          ${lesson ? '<button class="btn ok sm" data-act="submit">✓ Submit</button>' : ''}
        </div></div>
      <textarea class="code" spellcheck="false" aria-label="${py ? 'Python' : 'SQL'} code editor"></textarea>
      <div class="hint-bar"><kbd>Ctrl</kbd> + <kbd>Enter</kbd> to run · <kbd>Tab</kbd> indents${lesson ? ' · Submit is checked on the server' : ''}</div>
      <div class="out"><h5>Output</h5><div class="out-body"><p class="empty">${py ? 'Run your code to see the output here.' : 'Run a query to see results here.'}</p></div></div>
      ${lesson ? '<div class="hint-out" style="padding:0 16px 16px"></div>' : ''}
      ${py ? '<div class="schema"><label class="stdin-label">Input for <code>input()</code> when you press Run (one line per input)<textarea class="stdin" rows="2" spellcheck="false" aria-label="Program input"></textarea></label></div>'
           : '<div class="schema" aria-label="Database tables"></div>'}
    </div>`;
  };

  /* ---------------- Auth screen ---------------- */
  function showAuth(mode = 'login', notice = '') {
    $('.app').style.display = 'none';
    let el = $('#auth'); if (el) el.remove();
    el = document.createElement('div'); el.id = 'auth'; el.className = 'auth-wrap';
    const reg = mode === 'register';
    el.innerHTML = `<form class="auth-card reveal" novalidate>
      <a class="logo" href="index.html"><img class="logo-mark" src="assets/logo/rubitech-mark.svg" alt="" width="36" height="36"><span class="logo-text">Rubitech<small>ACADEMY</small></span></a>
      <h2>${reg ? 'Create your account' : 'Welcome back'}</h2>
      <p class="sub" style="font-size:15px;margin-bottom:18px">${reg ? 'Save your XP, streak and badges.' : 'Log in to continue learning.'}</p>
      <div id="auth-msg">${notice ? `<div class="msg info">${esc(notice)}</div>` : ''}</div>
      ${reg ? '<label>Username<input name="username" autocomplete="username" minlength="3" maxlength="30" required></label>' : ''}
      <label>Email<input name="email" type="email" autocomplete="email" required></label>
      <label>Password<input name="password" type="password" autocomplete="${reg ? 'new-password' : 'current-password'}" minlength="8" required></label>
      <button class="btn lg" style="width:100%;justify-content:center;margin-top:6px" type="submit">${reg ? 'Create account' : 'Log in'}</button>
      <p class="switch">${reg ? 'Already have an account? <a href="#" data-sw="login">Log in</a>' : 'New here? <a href="#" data-sw="register">Create an account</a>'}</p></form>`;
    document.body.appendChild(el);
    $('[data-sw]', el).onclick = e => { e.preventDefault(); showAuth(reg ? 'login' : 'register'); };
    $('form', el).onsubmit = async e => {
      e.preventDefault();
      const f = Object.fromEntries(new FormData(e.target));
      const btn = $('button[type=submit]', el); btn.disabled = true;
      try {
        const r = await api(reg ? '/auth/register' : '/auth/login', { method: 'POST', body: f, noAuthRedirect: true });
        setToken(r.access_token); el.remove(); await boot();
      } catch (err) { $('#auth-msg', el).innerHTML = `<div class="msg err">${esc(err.message)}</div>`; btn.disabled = false; }
    };
    $('input', el).focus();
  }

  /* ---------------- Views ---------------- */
  function renderSide(route) {
    const mods = MODULES.map(m => `<h6>${esc(m.title)}</h6>` + LESSONS.filter(l => l.module_id === m.id).map(l => {
      const done = S.completed[l.id], ok = unlocked(l.id), act = route === `/lesson/${l.id}`;
      return `<a class="lesson-link ${act ? 'active' : ''} ${ok ? '' : 'locked'}" href="#/lesson/${l.id}">
        <span class="dot ${done ? 'done' : act ? 'cur' : ''}">${done ? '✓' : ok ? '' : '🔒'}</span>${LESSONS.indexOf(l) + 1}. ${esc(l.title)}</a>`;
    }).join('')).join('');
    const sel = COURSES.length > 1 ? `<label class="course-sel">Course<select id="course-sel">${COURSES.map(c => `<option value="${c.id}" ${CUR && c.id === CUR.id ? 'selected' : ''}>${c.icon} ${esc(c.title)}</option>`).join('')}</select></label>` : '';
    $('#side').innerHTML = `<a class="logo" href="index.html"><img class="logo-mark" src="assets/logo/rubitech-mark.svg" alt="" width="36" height="36"><span class="logo-text">Rubitech<small>ACADEMY</small></span></a>${sel}
      <a class="nav-item ${route === '/dashboard' ? 'active' : ''}" href="#/dashboard">🏠 Dashboard</a>
      <a class="nav-item ${route === '/playground' ? 'active' : ''}" href="#/playground">🧪 Playground</a>
      <a class="nav-item ${route === '/leaderboard' ? 'active' : ''}" href="#/leaderboard">📈 Leaderboard</a>
      <a class="nav-item ${route === '/achievements' ? 'active' : ''}" href="#/achievements">🏅 Achievements</a>
      ${USER.role === 'admin' ? `<a class="nav-item ${route.startsWith('/admin') ? 'active' : ''}" href="#/admin">🛠 Admin</a>` : ''}${mods}
      <h6>Account</h6><div class="nav-item" style="cursor:default;color:var(--muted)">👤 ${esc(USER.username)}</div>
      <a class="nav-item" href="#" id="logout">↪ Log out</a>`;
    const cs = $('#course-sel'); if (cs) cs.onchange = () => { selectCourse(+cs.value); location.hash = '#/dashboard'; route(); };
    $('#logout').onclick = async e => { e.preventDefault(); try { await api('/auth/logout', { method: 'POST' }); } catch { /* ignore */ } setToken(null); USER = null; location.hash = ''; showAuth('login', 'You have been logged out.'); };
  }
  function renderChips() {
    $('#chips').innerHTML = `<span class="chip" title="Daily streak">🔥 ${S.streak}</span><span class="chip" title="Experience points">⚡ ${S.xp} XP</span><span class="chip" title="Level">Lv ${S.level}</span>`;
  }

  function dashboard() {
    const total = LESSONS.length, n = LESSONS.filter(l => S.completed[l.id]).length, pct = total ? Math.round(n / total * 100) : 0;
    const next = LESSONS.find(l => !S.completed[l.id]);
    const xpInLevel = S.xp % 100;
    $('#title').textContent = 'Dashboard';
    const cards = `<h3 style="margin:0 0 12px;font-size:18px">Courses</h3><div class="courses">${COURSES.map(c => { const p = courseProgress(c); return `
      <button class="course ${CUR && c.id === CUR.id ? 'sel' : ''}" data-course="${c.id}"><div class="ci">${esc(c.icon)}</div><h4>${esc(c.title)}</h4><p>${esc(c.description)}</p>
        <div class="bar"><i style="width:${p.total ? Math.round(p.done / p.total * 100) : 0}%"></i></div><div class="m"><span>${p.done}/${p.total} lessons</span><span>${CUR && c.id === CUR.id ? 'Selected' : 'Open'}</span></div></button>`; }).join('')}
      ${SOON.filter(x => !COURSES.some(c => c.slug === x[2])).map(x => `<div class="course soon"><div class="ci">${x[0]}</div><h4>${x[1]}</h4><p>Coming soon</p></div>`).join('')}</div>`;
    $('#view').innerHTML = `
      <div class="welcome reveal"><div><h2>${n ? 'Welcome back, ' : 'Welcome, '}${esc(USER.username)} 👋</h2>
        <p>${next ? `Next up: <b>${esc(next.title)}</b> · ${next.minutes} min · +${next.xp} XP` : 'You have completed every lesson. Brilliant!'}</p></div>
        ${next ? `<a class="btn" href="#/lesson/${next.id}">${n ? 'Continue learning' : 'Start lesson 1'} →</a>` : '<a class="btn" href="#/playground">Open playground</a>'}</div>
      <div class="stats">
        <div class="stat"><small>Course progress</small><b>${pct}%</b><div class="bar"><i style="width:${pct}%"></i></div></div>
        <div class="stat"><small>Lessons done</small><b>${n} / ${total}</b></div>
        <div class="stat"><small>Level ${S.level} · ${xpInLevel}/100 XP</small><b>${S.xp} XP</b><div class="bar"><i style="width:${xpInLevel}%"></i></div></div>
        <div class="stat"><small>Daily streak</small><b>🔥 ${S.streak} day${S.streak === 1 ? '' : 's'}</b></div>
      </div>` + cards + (CUR ? `<h3 style="margin:0 0 12px;font-size:18px">${esc(CUR.title)} roadmap</h3>` : '') + MODULES.map(m => `
      <section class="mod"><h3>${esc(m.title)}</h3><p class="b">${esc(m.blurb)}</p>
        <div class="lcards">${LESSONS.filter(l => l.module_id === m.id).map(l => `
          <a class="lcard ${S.completed[l.id] ? 'done' : ''} ${unlocked(l.id) ? '' : 'locked'}" href="#/lesson/${l.id}">
            <span class="n">LESSON ${LESSONS.indexOf(l) + 1}</span><h4 style="margin:2px 0 0;font-size:16px">${esc(l.title)}</h4>
            <div class="m"><span>${l.minutes} min</span><span>${S.completed[l.id] ? '✓ Done' : unlocked(l.id) ? '+' + l.xp + ' XP' : '🔒 Locked'}</span></div></a>`).join('')}
        </div></section>`).join('');
    document.querySelectorAll('[data-course]').forEach(b => b.onclick = () => { selectCourse(+b.dataset.course); route(); });
  }

  function lessonView(id) {
    const l = ALL.find(x => x.id === id);
    if (!l) return location.hash = '#/dashboard';
    if (!CUR || CUR.id !== l.course_id) selectCourse(l.course_id);
    if (!unlocked(id)) { toast('🔒 Finish the previous lesson to unlock this one.'); const pl = LESSONS[LESSONS.indexOf(l) - 1]; return location.hash = '#/lesson/' + (pl ? pl.id : LESSONS[0].id); }
    $('#title').textContent = `Lesson ${LESSONS.indexOf(l) + 1}`;
    const m = MODULES.find(x => x.id === l.module_id) || { title: '' };
    const idx = LESSONS.indexOf(l), prev = LESSONS[idx - 1], nextL = LESSONS[idx + 1];
    $('#view').innerHTML = `<div class="lesson reveal">
      <article class="panel pad lesson-col">
        <div class="meta"><span class="tag">${esc(m.title)}</span><span class="tag">⏱ ${l.minutes} min</span><span class="tag">⚡ ${l.xp} XP</span></div>
        <h2>${esc(l.title)}</h2>
        <div class="sec"><h4>1 · The concept</h4><p>${l.concept}</p></div>
        <div class="sec"><h4>2 · Why it matters</h4><p>${l.why}</p></div>
        <div class="sec"><h4>3 · Example</h4><pre class="example">${esc(l.example_sql)}</pre>
          <div class="example-note"><span>${esc(l.example_note)}</span><button class="btn secondary sm" id="try">Try it ▶</button></div></div>
        <div class="sec task"><h4>4 · Your task</h4><p>${l.prompt}</p>
          <p style="margin-top:8px;font-size:13px;color:var(--muted)">${RT() === 'python' ? 'Run tries your code. Submit checks it against hidden tests on the server.' : 'Column names do not need to match – the values do.' + (l.ordered ? ' Row order matters here.' : '')}</p></div>
        <div id="done"></div>
        <div class="pager">${prev ? `<a class="btn secondary sm" href="#/lesson/${prev.id}">← ${esc(prev.title)}</a>` : '<span></span>'}
          ${nextL ? `<a class="btn secondary sm" href="#/lesson/${nextL.id}">${esc(nextL.title)} →</a>` : '<span></span>'}</div>
      </article>
      <div id="ed">${editorHtml(l, RT())}</div></div>`;
    const ed = mountEditor($('#ed'), {
      starter: l.starter, lesson: l, runtime: RT(),
      onPass: r => {
        renderChips(); renderSide(`/lesson/${id}`);
        r.new_badges.forEach(b => { const i = badgeInfo(b); if (i) toast(`${i.icon} Badge unlocked: ${i.name}`); });
        if (r.xp_awarded) toast(`🎉 +${r.xp_awarded} XP`);
        $('#done').innerHTML = r.xp_awarded
          ? `<div class="msg ok reveal">Lesson complete! +${r.xp_awarded} XP ${nextL ? `· <a href="#/lesson/${nextL.id}">Next: ${esc(nextL.title)} →</a>` : '· You finished the course 🏆'}</div>`
          : '<div class="msg info">Already completed – XP is awarded only once per lesson.</div>';
      }
    });
    if (S.completed[id]) $('#done').innerHTML = '<div class="msg ok">✓ Completed. You can still practise below.</div>';
    $('#try').onclick = () => { ed.setSql(l.example_sql); ed.run(); };
  }

  function playground() {
    $('#title').textContent = 'Playground';
    const py = RT() === 'python';
    $('#view').innerHTML = `<div class="reveal" style="max-width:900px"><div class="msg info">${py
      ? 'Free practice: write any Python and press Run. It runs in a safe sandbox on the server (no network, 5 second limit). Playground code earns no XP.'
      : 'Free practice on the company database, running locally in your browser. Changes stay until you press <b>Reset</b>. Playground queries do not earn XP.'}</div>
      <div id="ed">${editorHtml(null, RT())}</div></div>`;
    mountEditor($('#ed'), { starter: py ? "print('Hello from the Rubitech playground!')\n" : 'SELECT * FROM employees;', lesson: null, runtime: RT() });
  }

  function achievements() {
    $('#title').textContent = 'Achievements';
    $('#view').innerHTML = `<p style="color:var(--muted);margin-top:0">${S.badges.length} of ${BADGES.length} unlocked</p><div class="badges reveal">${BADGES.map(b => `
      <div class="badge ${S.badges.includes(b.id) ? 'on' : ''}"><div class="i">${b.icon}</div><h4>${esc(b.name)}</h4><p>${esc(b.desc)}</p></div>`).join('')}</div>`;
  }

  async function leaderboard() {
    $('#title').textContent = 'Leaderboard';
    $('#view').innerHTML = '<p class="empty">Loading…</p>';
    try {
      const rows = await api('/leaderboard?limit=20');
      $('#view').innerHTML = `<div class="panel reveal" style="max-width:720px"><div class="tbl" style="max-height:none;border:0"><table>
        <thead><tr><th>#</th><th>Student</th><th>XP</th><th>Streak</th></tr></thead><tbody>${rows.map(r => `
        <tr ${r.username === USER.username ? 'style="background:var(--brand-50)"' : ''}><td>${r.rank}</td><td style="font-family:var(--font)">${esc(r.username)}</td><td>${r.xp}</td><td>🔥 ${r.streak}</td></tr>`).join('')}
        </tbody></table></div></div>`;
    } catch (e) { if (!e.auth) $('#view').innerHTML = `<div class="msg err">${esc(e.message)}</div>`; }
  }

  /* ---------------- Router & boot ---------------- */
  function route() {
    if (!USER) return;
    const r = (location.hash.slice(1) || '/dashboard');
    if (r.startsWith('/lesson/')) { const l = ALL.find(x => x.id === parseInt(r.split('/')[2], 10)); if (l && (!CUR || CUR.id !== l.course_id)) selectCourse(l.course_id); }
    renderSide(r); renderChips();
    $('#side').classList.remove('open');
    if (r.startsWith('/lesson/')) lessonView(parseInt(r.split('/')[2], 10));
    else if (r === '/playground') playground();
    else if (r === '/achievements') achievements();
    else if (r === '/leaderboard') leaderboard();
    else if (r.startsWith('/admin') && USER.role === 'admin') window.AdminUI.render(r, { api, esc, toast, $ });
    else dashboard();
    window.scrollTo(0, 0);
  }

  async function boot() {
    if (!getToken()) return showAuth();
    try {
      USER = await api('/auth/me');
      S = await api('/progress');
      COURSES = await api('/courses');
      ALL = await api('/lessons');
      let saved = null; try { saved = +localStorage.getItem(COURSE_KEY); } catch { /* ignore */ }
      selectCourse(saved);
    } catch (e) {
      if (e.auth) return;
      return showAuth('login', e.network ? e.message : '');
    }
    $('.app').style.display = '';
    route();
  }

  $('#menu').onclick = () => $('#side').classList.toggle('open');
  window.addEventListener('hashchange', route);

  if (typeof initSqlJs !== 'function') {
    document.body.innerHTML = '<p style="padding:24px;font-family:sans-serif">Could not load the SQL engine (sql.js). Check your internet connection and reload.</p>';
  } else {
    initSqlJs({ locateFile: f => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/${f}` })
      .then(m => { SQL = m; boot(); })
      .catch(e => { document.body.innerHTML = `<p style="padding:24px;font-family:sans-serif">Failed to start SQL engine: ${esc(e.message)}</p>`; });
  }
})();
