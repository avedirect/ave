<?php
/**
 * Приём заявок с сайта практикума «Связка: сайт + Яндекс Директ» → почта + Telegram + файл-резерв.
 *
 * НАСТРОЙКА (один раз, перед публикацией):
 * 1. MAIL_TO   — ваш рабочий e-mail, куда приходят заявки.
 * 2. MAIL_FROM — адрес на домене хостинга (иначе письма уходят в спам).
 * 3. Telegram: @BotFather → /newbot → токен вставьте в TG_TOKEN.
 * 4. Напишите своему боту любое сообщение (бот не может написать первым),
 *    откройте https://ВАШ-ДОМЕН/send.php?tg_chat_id — скрипт покажет chat_id, вставьте его в TG_CHAT_ID.
 * 5. После публикации токен лучше сменить: @BotFather → /revoke (он уже побывал в переписке).
 */

const MAIL_TO     = 'avedirectru@gmail.com';   // куда присылать заявки
const MAIL_FROM   = 'noreply@example.beget.tech';   // адрес на домене хостинга
const TG_TOKEN    = '';   // токен бота от @BotFather
const TG_CHAT_ID  = '';   // ваш chat_id (см. п. 4)
const SITE_NAME   = 'Связка: сайт + Яндекс Директ';

header('Content-Type: application/json; charset=utf-8');

// помощник для получения chat_id
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['tg_chat_id'])) {
    if (!TG_TOKEN) { echo json_encode(['error' => 'Сначала вставьте TG_TOKEN']); exit; }
    $u = @file_get_contents('https://api.telegram.org/bot' . TG_TOKEN . '/getUpdates');
    $d = json_decode($u, true);
    $ids = [];
    foreach (($d['result'] ?? []) as $upd) {
        $c = $upd['message']['chat'] ?? null;
        if ($c) $ids[$c['id']] = ($c['username'] ?? '') . ' ' . ($c['first_name'] ?? '');
    }
    echo json_encode(['chats' => $ids], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }

$in = json_decode(file_get_contents('php://input'), true);
if (!is_array($in)) { http_response_code(400); echo '{"ok":false,"error":"bad json"}'; exit; }

// защита от ботов: скрытое поле должно быть пустым
if (!empty($in['website'])) { echo '{"ok":true}'; exit; }

$clean = fn($s, $n = 300) => mb_substr(trim(strip_tags((string)$s)), 0, $n);
$phone = preg_replace('/[^\d+]/', '', (string)($in['phone'] ?? ''));
if (strlen(preg_replace('/\D/', '', $phone)) !== 11) { http_response_code(422); echo '{"ok":false,"error":"phone"}'; exit; }
if (empty($in['consent'])) { http_response_code(422); echo '{"ok":false,"error":"consent"}'; exit; }

// простое ограничение частоты: не больше 5 заявок в 10 минут с одного IP
$ip = $_SERVER['REMOTE_ADDR'] ?? '';
$rl = sys_get_temp_dir() . '/svyazka_rl_' . md5($ip);
$hits = array_filter(explode(',', @file_get_contents($rl) ?: ''), fn($t) => $t && $t > time() - 600);
if (count($hits) >= 5) { http_response_code(429); echo '{"ok":false,"error":"rate"}'; exit; }
$hits[] = time();
@file_put_contents($rl, implode(',', $hits));

$forms = [
    'quiz'    => 'Квиз «Подбор формата участия»',
    'measure' => 'Бронь места в группе',
    'calc'    => 'Вопрос по курсу (плавающее меню)',
    'contact' => 'Форма на странице «Контакты»',
];
$form = $forms[$in['form'] ?? ''] ?? $clean($in['form'] ?? 'Заявка', 60);

$lines = [
    '🟡 Новая заявка — ' . SITE_NAME,
    'Форма: ' . $form,
    'Имя: ' . ($clean($in['name'] ?? '') ?: '—'),
    'Телефон: ' . $phone,
];
if (!empty($in['service']))   $lines[] = 'Интересует: ' . $clean($in['service'], 80);
if (!empty($in['messenger'])) $lines[] = 'Куда ответить: ' . $clean($in['messenger'], 40);
if (!empty($in['answers']) && is_array($in['answers'])) {
    $labels = ['state' => 'Что сейчас', 'niche' => 'Что продаёт', 'budget' => 'Бюджет на Директ', 'goal' => 'Главная задача'];
    foreach ($in['answers'] as $k => $v) $lines[] = ($labels[$k] ?? $clean($k, 30)) . ': ' . $clean($v, 100);
}
$lines[] = 'Согласие на материалы и анонсы: ' . (!empty($in['ads_consent']) ? 'да' : 'нет');
$lines[] = 'Страница: ' . $clean($in['page'] ?? '', 300);
if (!empty($in['utm']) && is_array($in['utm'])) {
    foreach ($in['utm'] as $k => $v) $lines[] = $clean($k, 20) . ': ' . $clean($v, 150);
}
$lines[] = 'Время: ' . date('d.m.Y H:i');
$text = implode("\n", $lines);

// почта
$subject = '=?UTF-8?B?' . base64_encode('Заявка с сайта курса: ' . $form . ' — ' . $phone) . '?=';
$headers = "From: " . MAIL_FROM . "\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit";
$mailOk = @mail(MAIL_TO, $subject, $text, $headers, '-f' . MAIL_FROM);

// Telegram
$tgOk = false;
if (TG_TOKEN && TG_CHAT_ID) {
    $ctx = stream_context_create(['http' => [
        'method' => 'POST', 'timeout' => 8,
        'header' => "Content-Type: application/json\r\n",
        'content' => json_encode(['chat_id' => TG_CHAT_ID, 'text' => $text, 'disable_web_page_preview' => true], JSON_UNESCAPED_UNICODE),
    ]]);
    $r = @file_get_contents('https://api.telegram.org/bot' . TG_TOKEN . '/sendMessage', false, $ctx);
    $tgOk = $r && (json_decode($r, true)['ok'] ?? false);
}

// резервная копия заявки на сервере (на уровень выше public_html — снаружи не читается)
$logOk = (bool)@file_put_contents(__DIR__ . '/../leads.log', $text . "\n---\n", FILE_APPEND | LOCK_EX);

echo json_encode(['ok' => $mailOk || $tgOk || $logOk, 'mail' => $mailOk, 'telegram' => $tgOk]);
