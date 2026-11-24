/* Admin screens: overview, courses & modules, lessons (create / edit / publish), students. */
window.AdminUI = (function () {
  'use strict';
  let c; // context from app.js: { api, esc, toast, $ }

  const tabs = r => `<div class="tabs">
    <a class="${r === '/admin' ? 'on' : ''}" href="#/admin">Overview</a>
    <a class="${r.startsWith('/admin/course') ? 'on' : ''}" href="#/admin/courses">Courses</a>
    <a class="${r.startsWith('/admin/lesson') ? 'on' : ''}" href="#/admin/lesson/new">+ New lesson</a>
    <a class="${r === '/admin/students' ? 'on' : ''}" href="#/admin/students">Students</a></div>`;

  async function render(route, ctx) {
    c = ctx;
    document.getElementById('title').textContent = 'Admin';
    const view = document.getElementById('view');
    view.innerHTML = tabs(route) + '<p class="empty">Loading…</p>';
    try {
      let html;
      if (route === '/admin/students') html = await students();
      else if (route === '/admin/courses') html = await courses();
      else if (route.startsWith('/admin/course/')) html = await courseEditor(route.split('/')[3]);
      else if (route.startsWith('/admin/lesson/')) html = await lessonEditor(route.split('/')[3]);
      else html = await overview();
      view.innerHTML = tabs(route) + `<div class="reveal">${html}</div>`;
      bind();
    } catch (e) { if (!e.auth) view.innerHTML = tabs(route) + `<div class="msg err">${c.esc(e.message)}</div>`; }
  }

  const tag = (ok, yes, no) => `<span class="tag" style="${ok ? '' : 'background:var(--warn-bg);color:var(--warn)'}">${ok ? yes : no}</span>`;

  async function overview() {
    const [st, lessons, courses, modules] = await Promise.all([c.api('/admin/stats'), c.api('/admin/lessons'), c.api('/admin/courses'), c.api('/admin/modules')]);
    const by = Object.fromEntries(st.lessons.map(l => [l.id, l]));
    const course = id => courses.find(x => x.id === id), mod = id => modules.find(x => x.id === id);
    return `<div class="stats" style="grid-template-columns:repeat(3,1fr)">
        <div class="stat"><small>Students</small><b>${st.students}</b></div>
        <div class="stat"><small>Submissions</small><b>${st.submissions}</b></div>
        <div class="stat"><small>Pass rate</small><b>${st.pass_rate === null ? '–' : Math.round(st.pass_rate * 100) + '%'}</b></div></div>
      <div class="panel"><div class="tbl" style="max-height:none;border:0"><table>
        <thead><tr><th>Lesson</th><th>Course</th><th>Module</th><th>XP</th><th>Done</th><th>Attempts</th><th>Status</th><th></th></tr></thead><tbody>
        ${lessons.map(l => `<tr>
          <td style="font-family:var(--font);font-weight:600">${c.esc(l.title)}</td>
          <td style="font-family:var(--font)">${c.esc((course(l.course_id) || {}).title || '')}</td><td style="font-family:var(--font)">${c.esc((mod(l.module_id) || {}).title || '')}</td>
          <td>${l.xp}</td><td>${by[l.id].completions}</td><td>${by[l.id].attempts}</td><td>${tag(l.published, 'Published', 'Draft')}</td>
          <td style="font-family:var(--font)"><a class="btn secondary sm" href="#/admin/lesson/${l.id}">Edit</a>
            <button class="btn ghost sm" data-pub="lessons/${l.id}" data-to="${!l.published}">${l.published ? 'Unpublish' : 'Publish'}</button></td></tr>`).join('')}
        </tbody></table></div></div>`;
  }

  async function courses() {
    const [list, rt] = await Promise.all([c.api('/admin/courses'), c.api('/admin/runtimes')]);
    return `<p style="display:flex;justify-content:space-between;align-items:center;margin-top:0"><span class="empty">Add Python, JavaScript and more as courses. A course can be published once its runtime exists.</span>
        <a class="btn sm" href="#/admin/course/new">+ New course</a></p>
      <div class="panel"><div class="tbl" style="max-height:none;border:0"><table>
        <thead><tr><th>Course</th><th>Slug</th><th>Runtime</th><th>Status</th><th></th></tr></thead><tbody>
        ${list.map(x => `<tr><td style="font-family:var(--font);font-weight:600">${c.esc(x.icon)} ${c.esc(x.title)}</td><td>${c.esc(x.slug)}</td>
          <td style="font-family:var(--font)">${c.esc(x.runtime)} ${x.runtime_available ? '' : '<span class="tag" style="background:var(--warn-bg);color:var(--warn)">not available yet</span>'}</td>
          <td>${tag(x.published, 'Published', 'Draft')}</td>
          <td style="font-family:var(--font)"><a class="btn secondary sm" href="#/admin/course/${x.id}">Edit</a>
            <button class="btn ghost sm" data-pub="courses/${x.id}" data-to="${!x.published}">${x.published ? 'Unpublish' : 'Publish'}</button></td></tr>`).join('')}
        </tbody></table></div></div>
      <p class="empty" style="margin-top:10px">Runtimes available: ${rt.available.map(r => c.esc(r.label)).join(', ')} · planned: ${rt.planned.map(c.esc).join(', ')}</p>`;
  }

  async function courseEditor(id) {
    const e = c.esc, rt = await c.api('/admin/runtimes');
    let x = { slug: '', title: '', description: '', icon: '📘', runtime: 'sql', published: false }, mods = [];
    if (id !== 'new') {
      x = (await c.api('/admin/courses')).find(y => String(y.id) === id);
      if (!x) throw new Error('Course not found');
      mods = await c.api(`/admin/modules?course_id=${x.id}`);
    }
    const opts = [...rt.available.map(r => [r.key, r.label]), ...rt.planned.map(k => [k, k + ' (not available yet – draft only)'])];
    return `<form class="panel pad editor-form" id="cf" data-id="${e(id)}"><div id="cf-msg"></div>
      <div class="row3"><label>Title<input name="title" required minlength="2" maxlength="80" value="${e(x.title)}"></label>
        <label>Slug<input name="slug" required pattern="[a-z0-9][a-z0-9-]*" maxlength="40" value="${e(x.slug)}"></label>
        <label>Icon<input name="icon" maxlength="8" value="${e(x.icon)}"></label>
        <label>Runtime<select name="runtime">${opts.map(([k, l]) => `<option value="${e(k)}" ${k === x.runtime ? 'selected' : ''}>${e(l)}</option>`).join('')}</select></label></div>
      <label>Description<input name="description" maxlength="300" value="${e(x.description)}"></label>
      <label>Lesson unlocking<select name="unlock_mode"><option value="sequential" ${x.unlock_mode !== 'by_module' ? 'selected' : ''}>One by one (finish a lesson to unlock the next)</option>
        <option value="by_module" ${x.unlock_mode === 'by_module' ? 'selected' : ''}>By module (every module open, lessons in order inside it)</option></select></label>
      <div class="checks"><label><input type="checkbox" name="published" ${x.published ? 'checked' : ''}> Published (visible to students)</label></div>
      <div class="actions" style="margin-top:14px"><button class="btn" type="submit">Save course</button><a class="btn secondary" href="#/admin/courses">Back</a></div></form>
      ${id === 'new' ? '' : `<div class="panel pad editor-form" style="margin-top:18px"><h3 style="margin:0 0 6px">Modules</h3>
        ${mods.map(m => `<div class="mini" data-mod="${m.id}"><input value="${e(m.title)}" aria-label="Module title"><input value="${e(m.blurb)}" aria-label="Module description">
          <button class="btn secondary sm" data-savemod="${m.id}">Save</button></div>`).join('') || '<p class="empty">No modules yet.</p>'}
        <div class="mini"><input id="nm-title" placeholder="New module title"><input id="nm-blurb" placeholder="Short description">
          <button class="btn sm" id="nm-add" data-course="${x.id}">Add module</button></div></div>`}`;
  }

  const blank = { module_id: null, title: '', minutes: 5, xp: 10, concept: '', why: '', example_sql: '', example_note: '', prompt: '',
    starter: '', solution: '', verify: '', ordered: false, hints: [], published: false };

  async function lessonEditor(id) {
    const e = c.esc;
    const [courses, modules] = await Promise.all([c.api('/admin/courses'), c.api('/admin/modules')]);
    let l = blank;
    if (id !== 'new') {
      l = (await c.api('/admin/lessons')).find(x => String(x.id) === id);
      if (!l) throw new Error('Lesson not found');
    }
    const curModule = modules.find(m => m.id === l.module_id) || modules[0];
    const curCourse = courses.find(x => x.id === (curModule && curModule.course_id)) || courses[0];
    const field = (label, name, val, rows, help = '') => `<label>${label}${help ? `<small>${help}</small>` : ''}
      <textarea name="${name}" rows="${rows}" spellcheck="false">${e(val ?? '')}</textarea></label>`;
    return `<form class="panel pad editor-form" id="lf" data-id="${e(id)}" data-modules='${e(JSON.stringify(modules))}'>
      <div id="lf-msg"></div>
      <div class="row3">
        <label>Title<input name="title" required minlength="3" maxlength="120" value="${e(l.title)}"></label>
        <label>Course<select name="course" ${id === 'new' ? '' : 'disabled'}>${courses.map(x => `<option value="${x.id}" ${x.id === curCourse.id ? 'selected' : ''}>${e(x.title)}</option>`).join('')}</select></label>
        <label>Module<select name="module_id"></select></label>
        <label>Minutes<input name="minutes" type="number" min="1" max="120" value="${l.minutes}"></label>
        <label>XP<input name="xp" type="number" min="1" max="500" value="${l.xp}"></label>
      </div>
      ${field('Concept', 'concept', l.concept, 4, 'Allowed HTML: b, i, em, strong, code, br, p, ul, ol, li')}
      ${field('Why it matters', 'why', l.why, 2)}
      ${field('Example code / query', 'example_sql', l.example_sql, 3)}
      <label>Example note<input name="example_note" maxlength="500" value="${e(l.example_note)}"></label>
      ${field('Task prompt (shown to students)', 'prompt', l.prompt, 2)}
      ${field('Starter code', 'starter', l.starter, 3)}
      ${field('Reference solution (private)', 'solution', l.solution, 3, 'Students never see this. It is run when you save to make sure it works.')}
      ${field('Verify query (optional, private)', 'verify', l.verify, 2, 'For INSERT / UPDATE / DELETE tasks: a SELECT run after the student statements and compared.')}
      ${field('Tests (JSON, Python lessons only)', 'tests', l.tests ? JSON.stringify(l.tests, null, 2) : '', 5, 'Example: {"cases":[{"expr":"add(2, 3)"},{"expr":"add(-1, 1)","visible":false}],"requires":[]}. Expected values come from the reference solution.')}
      ${field('Hints (one per line, private until requested)', 'hints', (l.hints || []).join('\n'), 3)}
      <div class="checks"><label><input type="checkbox" name="ordered" ${l.ordered ? 'checked' : ''}> Row order matters</label>
        <label><input type="checkbox" name="published" ${l.published ? 'checked' : ''}> Published (visible to students)</label></div>
      <div class="actions" style="margin-top:14px"><button class="btn" type="submit">Save lesson</button>
        <a class="btn secondary" href="#/admin">Cancel</a></div></form>`;
  }

  async function students() {
    const r = await c.api('/admin/students?per_page=100');
    const e = c.esc;
    return `<form class="panel pad editor-form" id="uf" style="margin-bottom:18px"><h3 style="margin:0 0 6px">Add a user</h3><div id="uf-msg"></div>
        <div class="mini"><input name="username" placeholder="Username" required minlength="3" maxlength="30" pattern="[A-Za-z0-9_]+">
          <input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Password (8+ chars)" required minlength="8" autocomplete="new-password">
          <select name="role" style="padding:8px;border:1px solid var(--line);border-radius:8px"><option value="student">Student</option><option value="admin">Admin</option></select>
          <button class="btn sm" type="submit">Add user</button></div></form>
      <div class="panel"><div class="tbl" style="max-height:none;border:0"><table>
      <thead><tr><th>User</th><th>Email</th><th>Role</th><th>XP</th><th>Lessons</th><th>Streak</th><th>Status</th><th>Actions</th></tr></thead><tbody>
      ${r.items.map(u => `<tr data-user="${e(u.id)}" data-name="${e(u.username)}">
        <td style="font-family:var(--font);font-weight:600">${e(u.username)}</td><td style="font-family:var(--font)">${e(u.email)}</td>
        <td><select data-role aria-label="Role for ${e(u.username)}" style="padding:5px;border:1px solid var(--line);border-radius:6px;font-family:var(--font)">
          <option value="student" ${u.role === 'student' ? 'selected' : ''}>student</option><option value="admin" ${u.role === 'admin' ? 'selected' : ''}>admin</option></select></td>
        <td>${u.xp}</td><td>${u.lessons_completed}</td><td>${u.streak}</td><td>${tag(u.is_active, 'Active', 'Disabled')}</td>
        <td style="font-family:var(--font);white-space:nowrap">
          <button class="btn ghost sm" data-act="active" data-to="${!u.is_active}">${u.is_active ? 'Disable' : 'Enable'}</button>
          <button class="btn ghost sm" data-act="pw">Reset password</button>
          <button class="btn ghost sm" data-act="progress">Reset progress</button>
          <button class="btn ghost sm" data-act="delete" style="color:var(--err)">Delete</button></td></tr>`).join('')}
      </tbody></table></div></div><p class="empty" style="margin-top:10px">${r.total} account(s). You cannot disable, demote or delete your own account.</p>`;
  }

  function bind() {
    const $ = s => document.querySelector(s);
    document.querySelectorAll('[data-pub]').forEach(b => b.onclick = async () => {
      try { await c.api(`/admin/${b.dataset.pub}/publish`, { method: 'POST', body: { published: b.dataset.to === 'true' } });
        c.toast(b.dataset.to === 'true' ? 'Published' : 'Unpublished (progress is kept)'); location.reload(); }
      catch (e) { c.toast(e.message); }
    });

    const uf = $('#uf');
    if (uf) uf.onsubmit = async ev => {
      ev.preventDefault();
      const f = Object.fromEntries(new FormData(uf));
      try { await c.api('/admin/users', { method: 'POST', body: f }); c.toast('User added'); location.reload(); }
      catch (e) { $('#uf-msg').innerHTML = `<div class="msg err">${c.esc(e.message)}</div>`; }
    };
    document.querySelectorAll('tr[data-user]').forEach(row => {
      const id = row.dataset.user, name = row.dataset.name, base = `/admin/users/${id}`;
      const act = async (fn, okMsg) => { try { await fn(); c.toast(okMsg); location.reload(); } catch (e) { c.toast(e.message); } };
      row.querySelector('[data-role]').onchange = ev => act(() => c.api(`${base}/role`, { method: 'POST', body: { role: ev.target.value } }), `Role updated for ${name}`);
      row.querySelector('[data-act=active]').onclick = ev => act(() => c.api(`${base}/active`, { method: 'POST', body: { active: ev.target.dataset.to === 'true' } }), `${name} updated`);
      row.querySelector('[data-act=pw]').onclick = () => {
        const pw = prompt(`New password for ${name} (min 8 characters):`);
        if (pw) act(() => c.api(`${base}/reset-password`, { method: 'POST', body: { password: pw } }), `Password reset for ${name}`);
      };
      row.querySelector('[data-act=progress]').onclick = () => {
        if (confirm(`Reset ALL XP, badges and lesson progress for ${name}? This cannot be undone.`)) act(() => c.api(`${base}/reset-progress`, { method: 'POST' }), `Progress reset for ${name}`);
      };
      row.querySelector('[data-act=delete]').onclick = () => {
        if (confirm(`Permanently delete ${name} and all their data? This cannot be undone.`)) act(() => c.api(base, { method: 'DELETE' }), `${name} deleted`);
      };
    });

    const cf = $('#cf');
    if (cf) cf.onsubmit = async ev => {
      ev.preventDefault();
      const f = new FormData(cf), id = cf.dataset.id;
      const body = { slug: f.get('slug'), title: f.get('title'), description: f.get('description'), icon: f.get('icon') || '📘', runtime: f.get('runtime'), unlock_mode: f.get('unlock_mode'), published: f.has('published') };
      try {
        const saved = await c.api(id === 'new' ? '/admin/courses' : `/admin/courses/${id}`, { method: id === 'new' ? 'POST' : 'PUT', body });
        c.toast('Course saved'); location.hash = id === 'new' ? `#/admin/course/${saved.id}` : '#/admin/courses';
      } catch (e) { $('#cf-msg').innerHTML = `<div class="msg err">${c.esc(e.message)}</div>`; }
    };
    document.querySelectorAll('[data-savemod]').forEach(b => b.onclick = async () => {
      const row = b.closest('[data-mod]'), [t, d] = row.querySelectorAll('input');
      try { await c.api(`/admin/modules/${b.dataset.savemod}`, { method: 'PUT', body: { course_id: +location.hash.split('/')[3], title: t.value, blurb: d.value } }); c.toast('Module saved'); }
      catch (e) { c.toast(e.message); }
    });
    const add = $('#nm-add');
    if (add) add.onclick = async () => {
      try { await c.api('/admin/modules', { method: 'POST', body: { course_id: +add.dataset.course, title: $('#nm-title').value, blurb: $('#nm-blurb').value } }); c.toast('Module added'); location.reload(); }
      catch (e) { c.toast(e.message); }
    };

    const lf = $('#lf');
    if (!lf) return;
    const modules = JSON.parse(lf.dataset.modules);
    const fill = () => {
      const cid = +lf.course.value, sel = lf.module_id;
      const keep = sel.dataset.keep || sel.value;
      sel.innerHTML = modules.filter(m => m.course_id === cid).map(m => `<option value="${m.id}">${c.esc(m.title)}</option>`).join('') || '<option value="">(create a module first)</option>';
      if (keep) sel.value = keep;
    };
    lf.course.onchange = () => { lf.module_id.dataset.keep = ''; fill(); };
    c.api('/admin/lessons').then(all => {
      const l = all.find(x => String(x.id) === lf.dataset.id);
      if (l) { lf.module_id.dataset.keep = String(l.module_id); }
      fill();
    });
    lf.onsubmit = async ev => {
      ev.preventDefault();
      const f = new FormData(lf), id = lf.dataset.id, msg = $('#lf-msg');
      const body = {
        module_id: +lf.module_id.value, title: f.get('title'), minutes: +f.get('minutes'), xp: +f.get('xp'),
        concept: f.get('concept'), why: f.get('why'), example_sql: f.get('example_sql'), example_note: f.get('example_note'),
        prompt: f.get('prompt'), starter: f.get('starter'), solution: f.get('solution'), verify: f.get('verify') || null,
        hints: String(f.get('hints')).split('\n').map(h => h.trim()).filter(Boolean),
        ordered: f.has('ordered'), published: f.has('published'), tests: null
      };
      const rawTests = String(f.get('tests') || '').trim();
      if (rawTests) {
        try { body.tests = JSON.parse(rawTests); }
        catch (err) { msg.innerHTML = '<div class="msg err">Tests must be valid JSON: ' + c.esc(err.message) + '</div>'; return; }
      }
      try {
        const saved = await c.api(id === 'new' ? '/admin/lessons' : `/admin/lessons/${id}`, { method: id === 'new' ? 'POST' : 'PUT', body });
        const chk = await c.api(`/admin/lessons/${saved.id}/check`, { method: 'POST' });
        c.toast(chk.ok ? '✓ Saved – solution verified' : 'Saved, but the solution does not grade as correct');
        location.hash = '#/admin';
      } catch (e) { msg.innerHTML = `<div class="msg err">${c.esc(e.message)}</div>`; window.scrollTo(0, 0); }
    };
  }

  return { render };
})();
