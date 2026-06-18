// Год в подвале
document.getElementById('year').textContent = new Date().getFullYear();

// Мобильное меню
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');
burger.addEventListener('click', () => nav.classList.toggle('open'));
nav.addEventListener('click', (e) => {
  if (e.target.tagName === 'A') nav.classList.remove('open');
});

// Маска телефона (простая)
const phone = document.getElementById('phone');
phone.addEventListener('input', () => {
  let d = phone.value.replace(/\D/g, '').slice(0, 11);
  if (d.startsWith('8')) d = '7' + d.slice(1);
  let out = '';
  if (d.length) out = '+7';
  if (d.length > 1) out += ' (' + d.slice(1, 4);
  if (d.length >= 4) out += ') ' + d.slice(4, 7);
  if (d.length >= 7) out += '-' + d.slice(7, 9);
  if (d.length >= 9) out += '-' + d.slice(9, 11);
  phone.value = out;
});

// Отправка формы (демо — без бэкенда)
const form = document.getElementById('leadForm');
const success = document.getElementById('formSuccess');
form.addEventListener('submit', (e) => {
  e.preventDefault();
  const name = form.name.value.trim();
  const tel = form.phone.value.trim();
  if (!name || tel.length < 18) {
    alert('Пожалуйста, заполните имя и корректный телефон.');
    return;
  }
  // Здесь подключается реальная отправка (fetch на бэкенд / Telegram / CRM)
  console.log('Заявка:', {
    name,
    phone: tel,
    service: form.service.value,
    comment: form.comment.value.trim(),
  });
  form.reset();
  success.hidden = false;
  setTimeout(() => { success.hidden = true; }, 6000);
});
