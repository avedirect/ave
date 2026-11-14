/* ================= ЗАЯВКИ И ИНТЕРФЕЙС САЙТА КУРСА =================
   LEAD_ENDPOINT — обработчик send.php в корне сайта: шлёт заявку на почту, в Telegram и в leads.log.
   После успешной отправки открывается своя страница «Спасибо» (THANKS) — на ней стоит цель Метрики.
   Заявка уходит POST-запросом JSON: { form, name, phone, messenger?, service?, answers?, page, utm }

   Номер счётчика Метрики подставляется сборкой в window.YM_ID (build.py → SITE['metrika']).
   Пока он не указан, цели просто не отправляются, остальное работает. */
const LEAD_ENDPOINT = '/send.php';
const THANKS = { quiz: '/tnx1.html', measure: '/tnx2.html', calc: '/tnx3.html', contact: '/tnx3.html' };
const PHONE_FALLBACK = '+7 995 904-45-45';

function goal(name) { try { if (window.YM_ID && window.ym) ym(window.YM_ID, 'reachGoal', name); } catch (e) {} }

(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* ---------- появление при скролле ---------- */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -60px 0px' });
  $$('.reveal').forEach(el => {
    const sib = Array.from(el.parentElement.children).filter(c => c.classList.contains('reveal'));
    el.style.transitionDelay = (sib.indexOf(el) % 6) * 60 + 'ms';
    io.observe(el);
  });

  /* ---------- меню: мобильное и компактное при скролле ---------- */
  const mnav = $('#mobileNav');
  if (mnav) {
    $$('[data-burger]').forEach(b => b.addEventListener('click', () => mnav.classList.toggle('open')));
    $$('a', mnav).forEach(a => a.addEventListener('click', () => mnav.classList.remove('open')));
  }
  const hdSticky = $('#hdSticky'), hd = $('#header');
  if (hdSticky && hd) {
    const onHd = () => {
      const show = window.scrollY > hd.offsetHeight + 60;
      hdSticky.classList.toggle('show', show);
      hdSticky.setAttribute('aria-hidden', String(!show));
      if (mnav) mnav.style.top = show ? '76px' : '';
    };
    window.addEventListener('scroll', onHd, { passive: true }); onHd();
  }

  /* ---------- вкладки «как идёт личная работа» ---------- */
  $$('[data-tabs]').forEach(box => {
    const tabs = $$('.lab-tab', box), panes = $$('.lab-pane', box);
    tabs.forEach(t => t.addEventListener('click', () => {
      tabs.forEach(x => x.classList.toggle('on', x === t));
      panes.forEach(p => p.classList.toggle('on', p.dataset.pane === t.dataset.tab));
    }));
  });

  /* ---------- квиз подбора формата (главная) ---------- */
  const box = $('#quizBox');
  const answers = {};
  let go = () => {};
  if (box) {
    const steps = $$('.step', box);
    const bar = $('#qBar'), counter = $('#qCounter'), percent = $('#qPercent');
    const back = $('#qBack'), next = $('#qNext'), nav = $('#qNav');
    let cur = 1;
    go = (n, scroll) => {
      cur = n;
      steps.forEach(s => s.classList.toggle('active', +s.dataset.step === n));
      const p = n >= 5 ? 100 : n * 25;
      bar.style.width = p + '%'; percent.textContent = p + '%';
      counter.textContent = n >= 5 ? 'Готово' : `Вопрос ${n} из 4`;
      nav.style.display = n >= 5 ? 'none' : '';
      back.disabled = n === 1;
      const st = steps.find(s => +s.dataset.step === n);
      next.disabled = !(st && st.dataset.key && answers[st.dataset.key]);
      if (n === 5) $('#summary').innerHTML = steps.filter(s => s.dataset.key && answers[s.dataset.key]).map(s => `<span>${s.dataset.title.replace(/[?]/g, '')}: ${answers[s.dataset.key]}</span>`).join('');
      if (scroll) {
        const top = box.getBoundingClientRect().top;
        if (top < 80 || top > window.innerHeight * 0.5) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    };
    const choose = (step, value) => {
      $$('.opt', step).forEach(o => o.classList.toggle('selected', o.dataset.value === value));
      answers[step.dataset.key] = value;
    };
    steps.forEach(step => $$('.opt', step).forEach(opt => opt.addEventListener('click', () => {
      choose(step, opt.dataset.value);
      next.disabled = false;
      setTimeout(() => go(+step.dataset.step + 1, window.innerWidth < 900), 280);
    })));
    back.addEventListener('click', () => go(Math.max(1, cur - 1)));
    next.addEventListener('click', () => go(cur + 1));
    $$('[data-goto]', box).forEach(b => b.addEventListener('click', () => go(+b.dataset.goto)));
    /* быстрый старт квиза с первого экрана */
    $$('.hq-opt').forEach(b => b.addEventListener('click', () => {
      choose(steps[0], b.dataset.hq);
      go(2);
      box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }));
  }

  /* ---------- маска телефона ---------- */
  $$('input[type=tel]').forEach(input => {
    input.addEventListener('input', () => {
      let d = input.value.replace(/\D/g, '');
      if (d.startsWith('8')) d = '7' + d.slice(1);
      if (!d.startsWith('7')) d = '7' + d;
      d = d.slice(0, 11);
      let o = '+7';
      if (d.length > 1) o += ' (' + d.slice(1, 4);
      if (d.length >= 4) o += ')';
      if (d.length > 4) o += ' ' + d.slice(4, 7);
      if (d.length > 7) o += '-' + d.slice(7, 9);
      if (d.length > 9) o += '-' + d.slice(9, 11);
      input.value = o;
      input.closest('.field').classList.remove('error');
    });
    input.addEventListener('focus', () => { if (!input.value) input.value = '+7 ('; });
    input.addEventListener('blur', () => { if (input.value.replace(/\D/g, '').length <= 1) input.value = ''; });
  });

  /* ---------- отправка заявок ---------- */
  const utm = () => { const p = new URLSearchParams(location.search), o = {}; ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid'].forEach(k => p.get(k) && (o[k] = p.get(k))); return o; };
  async function sendLead(payload) {
    if (!LEAD_ENDPOINT) { console.log('Lead:', payload); return true; }
    try {
      const r = await fetch(LEAD_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const j = await r.json().catch(() => ({}));
      return r.ok && j.ok !== false;
    } catch (e) { return false; }
  }
  $$('form[data-form]').forEach(form => {
    const pd = $('input[name=consent]', form), submitBtn = $('button[type=submit]', form);
    const syncBtn = () => { submitBtn.disabled = !pd.checked; };
    pd.addEventListener('change', syncBtn); syncBtn();
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const phone = $('input[type=tel]', form), consent = $('input[name=consent]', form);
      let ok = true;
      if (phone.value.replace(/\D/g, '').length !== 11) { phone.closest('.field').classList.add('error'); ok = false; }
      consent.closest('.consent').classList.toggle('error', !consent.checked);
      if (!consent.checked) ok = false;
      if (!ok) return;
      const btn = submitBtn, html = btn.innerHTML;
      btn.disabled = true; btn.textContent = 'Отправляем…';
      const fd = new FormData(form);
      const sent = await sendLead({
        form: form.dataset.form,
        name: fd.get('name') || '',
        phone: fd.get('phone'),
        service: fd.get('service') || undefined,
        messenger: fd.get('messenger') || undefined,
        consent: true,
        ads_consent: !!fd.get('ads'),
        website: fd.get('website') || '',
        answers: form.dataset.form === 'quiz' ? { ...answers } : undefined,
        page: location.href,
        utm: utm(),
      });
      btn.innerHTML = html; syncBtn();
      if (!sent) { alert('Не удалось отправить заявку. Напишите в Telegram или позвоните: ' + PHONE_FALLBACK); return; }
      goal('lead'); goal('lead_' + form.dataset.form);
      if (THANKS[form.dataset.form]) { setTimeout(() => { location.href = THANKS[form.dataset.form]; }, 300); return; }
      if (form.dataset.form === 'quiz') { go(6); return; }
      if (form.closest('#modal')) { $('[data-modal-form]', $('#modal')).hidden = true; $('[data-modal-success]').hidden = false; return; }
      form.hidden = true;
      const done = form.parentElement.querySelector('[data-form-success]');
      if (done) done.hidden = false;
    });
    $$('input[name=consent]', form).forEach(c => c.addEventListener('change', () => c.closest('.consent').classList.remove('error')));
  });

  /* ---------- уведомление о cookie ---------- */
  const cookie = $('#cookie');
  if (cookie) {
    let seen = false;
    try { seen = localStorage.getItem('cookieOk') === '1'; } catch (e) {}
    if (!seen) cookie.hidden = false;
    $('#cookieOk').addEventListener('click', () => { cookie.hidden = true; try { localStorage.setItem('cookieOk', '1'); } catch (e) {} });
  }

  /* ---------- окна: бронь места и вопрос по курсу ---------- */
  const openModal = m => { m.classList.add('open'); document.body.style.overflow = 'hidden'; setTimeout(() => { const i = m.querySelector('input[type=tel]'); i && i.focus(); }, 100); };
  const closeModal = m => { m.classList.remove('open'); document.body.style.overflow = ''; };
  const modal = $('#modal'), calc = $('#modalCalc');
  if (modal) {
    $$('[data-open-modal]').forEach(b => b.addEventListener('click', () => openModal(modal)));
    $$('[data-close]', modal).forEach(b => b.addEventListener('click', () => closeModal(modal)));
  }
  if (calc) {
    $$('[data-open-calc]').forEach(b => b.addEventListener('click', () => openModal(calc)));
    $$('[data-close]', calc).forEach(b => b.addEventListener('click', () => closeModal(calc)));
  }
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    [modal, calc].forEach(m => m && closeModal(m));
    if (mnav) mnav.classList.remove('open');
  });

  /* ---------- плавающее меню справа ---------- */
  const KEY = 'fdockHidden';
  const setDock = h => { document.documentElement.classList.toggle('dock-hidden', h); try { h ? localStorage.setItem(KEY, '1') : localStorage.removeItem(KEY); } catch (e) {} };
  try { if (localStorage.getItem(KEY) === '1') setDock(true); } catch (e) {}
  $$('[data-dock-toggle]').forEach(b => b.addEventListener('click', () => setDock(!document.documentElement.classList.contains('dock-hidden'))));
})();

/* ---------- цели Яндекс Метрики ----------
   Цели создаются в Метрике как «JavaScript-событие» с этими идентификаторами:
   lead, lead_quiz, lead_measure, lead_calc, click_phone, click_telegram, click_max, click_email,
   open_book_form, open_quiz, quiz_answer, open_programma, open_tarify, lab_step_view,
   dock_zayavka, dock_programma, dock_telegram, dock_quiz, click_cta_blog
   Элементу можно задать data-goal="..." — он главнее автоопределения. */
document.addEventListener('click', e => {
  const el = e.target.closest('a, button');
  if (!el) return;
  const href = el.getAttribute('href') || '', txt = (el.textContent || '').toLowerCase();
  let g = el.dataset.goal;
  if (!g) {
    if (href.startsWith('tel:')) g = 'click_phone';
    else if (/t\.me|telegram/i.test(href)) g = 'click_telegram';
    else if (/max\.ru/i.test(href)) g = 'click_max';
    else if (href.startsWith('mailto:')) g = 'click_email';
    else if (el.hasAttribute('data-open-modal')) g = 'open_book_form';
    else if (href.includes('#quiz') || /подобрать формат/.test(txt)) g = 'open_quiz';
    else if (el.hasAttribute('data-value') && el.closest('#quizBox')) g = 'quiz_answer';
    else if (href.startsWith('/programma')) g = 'open_programma';
    else if (href.startsWith('/tarify')) g = 'open_tarify';
    else if (el.closest('[class*="icta"]')) g = 'click_cta_blog';
  }
  if (g) goal(g);
}, true);
