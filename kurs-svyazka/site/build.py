"""Сборка сайта курса «Связка: сайт + Яндекс Директ» (вторая версия).

    python build.py          → собирает сайт в папку public/

Исходники:
  src/pages/*.body.html   — содержимое страниц (без шапки и подвала)
  src/articles/*.html     — статьи; первая строка — комментарий <!--META {...} --> с данными статьи
  static/                 — CSS, JS, картинки (копируются как есть)

ВСЁ, ЧТО НАДО ПОДСТАВИТЬ ПЕРЕД ПУБЛИКАЦИЕЙ, лежит в блоках SITE / COURSE / TARIFFS ниже.
Значения-заглушки помечены функцией ph() — при сборке они выводятся списком в конце.
"""
import html
import json
import re
import shutil
import time as _t
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC, STATIC, OUT = ROOT / 'src', ROOT / 'static', ROOT / 'public'
TODAY = date.today().isoformat()
ASSET_V = _t.strftime('%Y%m%d%H%M')   # сброс кеша CSS/JS при каждой сборке

# ------------------------------------------------------------------ заглушки
TODO = []


def ph(label, value):
    """Помечает значение-заглушку: попадёт в список «заполнить» в конце сборки."""
    TODO.append(f'{label} → сейчас «{value}»')
    return value


# ------------------------------------------------------------------ сайт
SITE = {
    'url': ph('Адрес сайта (SITE[url]): поддомен или папка курса', 'https://svyazka.directzavod.ru'),
    'name': 'Связка',
    'full_name': 'Связка: сайт + Яндекс Директ',
    'legal_desc': 'Практикум по связке сайта и Яндекс Директа: настраиваем сайт, аналитику и рекламные кампании на проектах участников',
    'author': 'Александр Евстигнеев',
    'author_short': 'Александр',
    'phone': ph('Телефон на сайте (SITE[phone])', '+7 995 904-45-45'),
    'phone_raw': '+79959044545',
    'email': ph('E-mail для заявок (SITE[email])', 'info@directzavod.ru'),
    'hours': 'Пн–Пт: 10:00–19:00',
    'city': 'Москва',
    'founded': '2017',
    'ip': ph('Реквизиты для подвала (SITE[ip]/inn/ogrnip)', 'ИП Евстигнеев Александр Валерьевич'),
    'inn': '772143966858',
    'ogrnip': '320774600097090',
    'telegram': ph('Личный Telegram для заявок (SITE[telegram])', 'https://t.me/avedirect'),
    'telegram_name': '@avedirect',
    'max': ph('Ссылка MAX (SITE[max]); если не нужна — удалите', 'https://max.ru/u/'),
    'blog_main': ph('Ссылка на основной сайт/блог автора', 'https://directzavod.ru'),
    'metrika': ph('Номер счётчика Яндекс Метрики (SITE[metrika])', ''),
    'same_as': [],
}
SITE['same_as'] = [SITE['telegram'], SITE['blog_main']]

COURSE = {
    'version': 'Вторая версия',
    'start': ph('Дата старта потока (COURSE[start])', '00 месяца 2026'),
    'weeks': ph('Длительность потока в неделях (COURSE[weeks])', '6'),
    'seats': ph('Сколько мест в группе (COURSE[seats])', '00'),
    'calls': ph('Сколько живых созвонов (COURSE[calls])', '00'),
    'format': 'Групповой практикум + личный разбор каждого проекта',
    'where': 'Онлайн, созвоны в записи остаются участникам',
    # цифры ниже взяты из описания в блоге автора — подтвердите или поправьте
    'streams': ph('Сколько потоков было у первой версии (COURSE[streams])', '8'),
    'students': ph('Сколько человек прошло обучение (COURSE[students])', '367'),
}

# тарифы: цены — заглушки, правятся здесь в одном месте
TARIFFS = [
    {
        'slug': 'sam',
        'name': 'Сам',
        'tag': 'Для тех, кто хочет разобраться',
        'price': ph('Цена тарифа «Сам» (TARIFFS)', '00 000 ₽'),
        'old': '',
        'lead': 'Вся программа и живые созвоны. Домашние задания проверяются в общем чате.',
        'rows': [('Доступ к программе', 'все 8 модулей'), ('Живые созвоны', 'да'), ('Разбор вашего проекта', '—'),
                 ('Проверка домашних заданий', 'в чате группы'), ('Аудит кампании перед стартом', '—'), ('Доступ к записям', 'бессрочно')],
        'cta': 'Выбрать тариф «Сам»',
        'accent': False,
    },
    {
        'slug': 'vmeste',
        'name': 'Вместе',
        'tag': 'Основной формат второй версии',
        'price': ph('Цена тарифа «Вместе» (TARIFFS)', '00 000 ₽'),
        'old': ph('Цена до окончания раннего набора, тариф «Вместе»', '00 000 ₽'),
        'lead': 'Личная работа: смотрим ваш сайт и ваш кабинет Директа, настраиваем связку вместе на созвонах.',
        'rows': [('Доступ к программе', 'все 8 модулей'), ('Живые созвоны', 'да'), ('Разбор вашего проекта', f'да, {ph("Сколько личных разборов в тарифе «Вместе»", "0")} на потоке'),
                 ('Проверка домашних заданий', 'лично, с правками'), ('Аудит кампании перед стартом', 'да'), ('Доступ к записям', 'бессрочно')],
        'cta': 'Забронировать место',
        'accent': True,
    },
    {
        'slug': 'pod-kluch',
        'name': 'Под ключ',
        'tag': 'Собираем связку вашими руками, но под моим контролем',
        'price': ph('Цена тарифа «Под ключ» (TARIFFS)', '00 000 ₽'),
        'old': '',
        'lead': 'Программа, личные разборы и сопровождение после потока: держим кампании до стабильной стоимости заявки.',
        'rows': [('Доступ к программе', 'все 8 модулей'), ('Живые созвоны', 'да'), ('Разбор вашего проекта', 'без ограничений в рамках потока'),
                 ('Проверка домашних заданий', 'лично, с правками'), ('Аудит кампании перед стартом', 'да'),
                 ('Сопровождение после потока', ph('Срок сопровождения в тарифе «Под ключ»', '0 недель'))],
        'cta': 'Обсудить тариф «Под ключ»',
        'accent': False,
    },
]

# ------------------------------------------------------------------ программа
MODULES = [
    {
        'n': 1, 'icon': 'ruble', 'title': 'Деньги до рекламы: за сколько вам выгодно покупать заявку',
        'short': 'Считаем юнит-экономику проекта и получаем целевой CPL, CPA и ДРР — цифры, по которым дальше судим о каждой кампании.',
        'points': [
            'Воронка в цифрах: клик → заявка → продажа → повторная продажа',
            'Целевая стоимость заявки (CPL) и клиента (CPA) из маржи, а не «по ощущениям»',
            'ДРР и доля рекламы в выручке: когда реклама работает, а когда просто крутится',
            'Сколько денег нужно на тест кампании, чтобы вывод был достоверным',
            'Почему «дешёвые заявки» часто дороже дорогих',
        ],
        'hands': 'Посчитаете свою экономику в таблице и зафиксируете целевой CPL — с ним сверяем все решения на потоке.',
    },
    {
        'n': 2, 'icon': 'site', 'title': 'Сайт, который принимает трафик из Директа',
        'short': 'Разбираем страницу, на которую вы льёте: оффер, первый экран, формы, скорость и мобильная версия.',
        'points': [
            'Оффер на первом экране: что человек должен понять за 5 секунд',
            'Структура страницы под платный трафик: оффер → доказательства → цена → действие',
            'Формы и квизы: сколько полей, что спрашивать, где ставить',
            'Релевантность «запрос → объявление → страница» и почему от неё зависит цена клика',
            'Скорость загрузки и мобильная версия: что чинить в первую очередь',
            'Отдельные страницы под разные группы запросов вместо одной «универсальной»',
        ],
        'hands': 'Переделаете первый экран и форму на своём сайте — на созвоне смотрим до и после.',
    },
    {
        'n': 3, 'icon': 'target', 'title': 'Аналитика раньше рекламы: Метрика, цели, UTM',
        'short': 'Без настроенных целей автостратегии учиться не на чем. Ставим счётчик, цели, разметку и передачу конверсий.',
        'points': [
            'Счётчик Метрики: вебвизор, карта кликов, точный показатель отказов',
            'Цели: JavaScript-событие против «посещения страницы» — что надёжнее и почему',
            'Какие цели нужны всегда: заявка, звонок, клик в мессенджер, отправка квиза',
            'UTM-разметка и yclid: как потом понять, какая кампания принесла деньги',
            'Сегменты и составные условия в Метрике — основа ретаргетинга',
            'Передача офлайн-конверсий и связка с CRM: учим Директ оптимизироваться на продажи, а не на формы',
            'Коллтрекинг: когда он нужен, а когда достаточно отдельного номера',
        ],
        'hands': 'Настроите цели в своей Метрике и проверите их отладкой — на созвоне проверяем, что они действительно срабатывают.',
    },
    {
        'n': 4, 'icon': 'layers', 'title': 'Структура аккаунта в Директе: как устроен кабинет в 2026 году',
        'short': 'Единая перфоманс-кампания, Мастер кампаний, товарная кампания — что выбрать под вашу задачу и как не смешать всё в одну.',
        'points': [
            'Мастер кампаний: где он правда помогает, а где просто расходует бюджет',
            'Единая перфоманс-кампания: поиск и сети в одной кампании, плюсы и ловушки',
            'Когда поиск и РСЯ стоит разделить и как тогда считать результат',
            'Товарная кампания и фид: для магазинов и каталогов',
            'Автотаргетинг: как ограничить его так, чтобы он не тянул нецелевые запросы',
            'Логика групп: сколько кампаний, сколько групп, что в них складывать',
            'Геотаргетинг и расписание показов под реальный график работы',
        ],
        'hands': 'Соберёте структуру своего аккаунта на схеме и согласуете её до запуска — переделывать потом дороже.',
    },
    {
        'n': 5, 'icon': 'search', 'title': 'Запросы и объявления: что человек ищет и что он увидит',
        'short': 'Собираем семантику, чистим мусор и пишем объявления, которые совпадают с запросом и с вашей страницей.',
        'points': [
            'Сбор запросов: Вордстат, подсказки, запросы конкурентов, внутренний поиск сайта',
            'Группировка по смыслу и по этапу спроса: «купить», «цена», «как выбрать»',
            'Минус-фразы: базовый список и регулярная чистка по отчёту поисковых запросов',
            'Заголовки и тексты: что писать в первом и втором заголовке, как использовать подстановку',
            'Быстрые ссылки, уточнения, цена, визитка — что реально влияет на клик',
            'Креативы для РСЯ: изображения, видео, какие форматы заполнять',
            'Модерация: типовые причины отказа и как их обойти законно',
        ],
        'hands': 'Соберёте семантику и объявления под свой проект; разбираем их построчно на созвоне.',
    },
    {
        'n': 6, 'icon': 'brain', 'title': 'Стратегии и ставки: как Директ учится и как ему не мешать',
        'short': 'Оплата за конверсии, максимум конверсий, ДРР, ручное управление — когда что включать и сколько ждать.',
        'points': [
            'Как работает обучение автостратегии и сколько конверсий в неделю ей нужно',
            'Оплата за конверсии: когда это защита бюджета, а когда тормоз показов',
            'Максимум конверсий с ограничением CPA и с недельным бюджетом: разница на практике',
            'Стратегия по ДРР: для магазинов с передачей ценности заказа',
            'Где ещё осмысленно ручное управление ставками',
            'Корректировки: устройства, пол и возраст, аудитории, платёжеспособность',
            'Главная ошибка: менять настройки каждый день и сбрасывать обучение',
            'Что делать, если стратегия не обучается: по шагам',
        ],
        'hands': 'Выберете стратегию под свою экономику и запустите кампанию с обоснованными лимитами.',
    },
    {
        'n': 7, 'icon': 'funnel', 'title': 'Ретаргетинг и аудитории: добираем тех, кто уже был',
        'short': 'Самый дешёвый трафик — тот, кто уже знает вас. Собираем сегменты и догоняем их по уму.',
        'points': [
            'Сегменты Метрики под ретаргетинг: был на странице цены, начал форму, не отправил',
            'Условия ретаргетинга: наборы правил и их комбинации',
            'Look-alike и Яндекс Аудитории: загрузка своей базы, похожие пользователи',
            'Исключение тех, кто уже купил — чтобы не платить за своих клиентов',
            'Ограничение частоты показов, чтобы не выжигать аудиторию',
            'Отдельные офферы для «тёплых»: что показывать тому, кто уже сравнивает',
        ],
        'hands': 'Запустите ретаргетинг на свои сегменты и сравните его стоимость заявки с холодным трафиком.',
    },
    {
        'n': 8, 'icon': 'rocket', 'title': 'Управление и рост: что смотреть каждую неделю',
        'short': 'Регламент работы с кабинетом, отчёты, рост бюджета без потери стоимости заявки.',
        'points': [
            'Ежедневный минимум и еженедельный разбор: какие цифры открывать',
            'Мастер отчётов: срезы, по которым видно, где теряются деньги',
            'Отчёт по поисковым запросам и чистка площадок РСЯ',
            'A/B офферов и страниц: как проверять идеи, а не спорить о них',
            'Масштабирование: как поднимать бюджет, чтобы стоимость заявки не улетела',
            'Сезонность и паузы: что делать, когда спрос падает',
            'Реклама и закон: что обязан делать рекламодатель, как это устроено в Директе',
        ],
        'hands': 'Заберёте регламент ведения своего кабинета и план на 4 недели после потока.',
    },
]

PAINS = [
    {'icon': 'trend-down', 'label': 'Бюджет', 'title': 'Мастер кампаний крутится — заявок нет',
     'text': 'Кампания запущена «по подсказкам», автотаргетинг тянет всё подряд, отчёт показывает клики, а в телефоне тишина.',
     'viz': 'budget'},
    {'icon': 'funnel', 'label': 'Продажи', 'title': 'Заявки есть, а продаж нет',
     'text': 'Директ оптимизируется на то, что ему передали. Передали «отправку формы» — он и приносит формы, а не покупателей.',
     'viz': 'funnel'},
    {'icon': 'site', 'label': 'Сайт', 'title': 'Сайт не держит трафик',
     'text': 'Первый экран без оффера, форма в подвале, на телефоне всё разъезжается. Трафик приходит и уходит — платно.',
     'viz': 'site'},
    {'icon': 'target', 'label': 'Данные', 'title': 'Решения принимаются наугад',
     'text': 'Цели не настроены или считают не то. Непонятно, какая кампания приносит деньги, поэтому выключают всё подряд.',
     'viz': 'data'},
]

LAB = [
    {'icon': 'eye', 'title': 'Смотрим ваш сайт', 'text': 'Разбираем первый экран, оффер, формы и мобильную версию. Решаем, что переделать до запуска рекламы, а что можно оставить.'},
    {'icon': 'target', 'title': 'Настраиваем аналитику', 'text': 'Счётчик, цели на все способы связи, UTM-разметка, проверка отладкой. Пока цели не работают, рекламу не запускаем.'},
    {'icon': 'layers', 'title': 'Собираем кабинет', 'text': 'Структура кампаний под вашу задачу, семантика, объявления, креативы. Открываем ваш Директ и делаем это вместе.'},
    {'icon': 'brain', 'title': 'Выбираем стратегию', 'text': 'Считаем, сколько вы можете платить за заявку, и подбираем стратегию и лимиты под эту цифру, а не «как у всех».'},
    {'icon': 'chart', 'title': 'Ведём и растим', 'text': 'Еженедельно смотрим отчёты, чистим запросы и площадки, поднимаем бюджет там, где экономика позволяет.'},
]

STEPS = [
    ('calendar', 'Знакомство и аудит', 'До старта смотрю ваш проект: сайт, кабинет, если реклама уже шла — её отчёты. На первом созвоне у каждого есть точка «откуда идём».'),
    ('ruble', 'Экономика и цели', 'Считаем, за сколько вам выгодно покупать заявку. Настраиваем Метрику и цели — фундамент, без которого дальше нет смысла.'),
    ('site', 'Сайт под трафик', 'Переделываем первый экран, оффер и формы. Готовим страницу так, чтобы платный трафик не уходил впустую.'),
    ('layers', 'Сборка кампаний', 'Структура аккаунта, семантика, объявления, креативы. Запускаем первые кампании с обоснованными лимитами.'),
    ('brain', 'Обучение стратегий', 'Даём кампаниям обучиться, не дёргая настройки. Разбираем первые данные и правим то, что действительно мешает.'),
    ('rocket', 'Рост и регламент', 'Снижаем стоимость заявки, добавляем ретаргетинг, поднимаем бюджет. Забираете регламент ведения кабинета.'),
]

COMPARE_BAD = [
    'Запустили Мастер кампаний «на всё» и ждём',
    'Цели в Метрике не настроены или дублируют друг друга',
    'Трафик льётся на главную страницу сайта',
    'Стратегию меняют каждые два дня',
    'Отчёт смотрят по клику и показам',
]
COMPARE_GOOD = [
    'Структура кампаний собрана под конкретную задачу',
    'Цели настроены и проверены отладкой до запуска',
    'Под группы запросов — свои страницы и свои офферы',
    'Стратегии дают обучиться и меняют по данным',
    'Решения принимаются по стоимости заявки и продажи',
]

# ------------------------------------------------------------------ страницы
NAV_MAIN = [('/programma/', 'Программа'), ('/tarify/', 'Тарифы'), ('/avtor/', 'Автор'), ('/blog/', 'Блог'), ('/faq/', 'Вопросы'), ('/kontakty/', 'Контакты')]
NAV_EXTRA = [('/politika/', 'Политика конфиденциальности'), ('/soglasie/', 'Согласие на обработку данных')]

PAGES = [
    {'path': '/', 'body': 'home', 'nav': None, 'crumb': 'Главная',
     'title': f'{SITE["full_name"]} — практикум {SITE["author"]}, вторая версия',
     'description': 'Вторая версия практикума: собираем связку сайта и Яндекс Директа на вашем проекте. Личный разбор сайта и кабинета, настройка целей, кампаний и стратегий.'},
    {'path': '/programma/', 'body': 'programma', 'nav': '/programma/', 'crumb': 'Программа',
     'title': 'Программа практикума «Связка»: 8 модулей по сайту и Яндекс Директу',
     'description': 'Что внутри: экономика заявки, сайт под трафик, Метрика и цели, структура кампаний, семантика и объявления, стратегии, ретаргетинг, управление и рост.'},
    {'path': '/tarify/', 'body': 'tarify', 'nav': '/tarify/', 'crumb': 'Тарифы',
     'title': 'Тарифы и участие в практикуме «Связка: сайт + Яндекс Директ»',
     'description': 'Три формата участия: самостоятельно, с личным разбором проекта и с сопровождением после потока. Что входит в каждый тариф и как забронировать место.'},
    {'path': '/avtor/', 'body': 'avtor', 'nav': '/avtor/', 'crumb': 'Автор',
     'title': f'{SITE["author"]} — автор практикума по связке сайта и Яндекс Директа',
     'description': f'{SITE["author"]}: практик по трафику и лидогенерации. Кто ведёт практикум, как устроена личная работа с проектами участников и чем вторая версия отличается от первой.'},
    {'path': '/kontakty/', 'body': 'kontakty', 'nav': '/kontakty/', 'crumb': 'Контакты',
     'title': 'Контакты практикума «Связка» — записаться и задать вопрос',
     'description': 'Напишите в Telegram или оставьте телефон — расскажу про формат, тарифы и ближайший поток практикума по связке сайта и Яндекс Директа.'},
]

# ------------------------------------------------------------------ утилиты
TR = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'f', 'h', 'ts', 'ch', 'sh', 'sch', '', 'y', '', 'e', 'yu', 'ya']))


def slugify(text):
    text = re.sub(r'<[^>]+>', '', text).lower()
    text = ''.join(TR.get(c, c) for c in text)
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-')[:60]


def esc(s):
    return html.escape(str(s), quote=True)


def strip_tags(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'</(p|li|h2|h3|tr|div|figcaption)>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\n\s*\n+', '\n\n', re.sub(r'[ \t]+', ' ', s)).strip()


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '</script>'


def ru_date(iso):
    y, m, d = iso.split('-')
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    return f'{int(d)} {months[int(m) - 1]} {y}'


def ico(name, cls=''):
    return f'<svg class="ico {cls}"><use href="#i-{name}"/></svg>'


# ------------------------------------------------------------------ разметка для поиска и нейросетей
ORG_ID = SITE['url'] + '/#org'
PERSON_ID = SITE['url'] + '/#author'
PERSON = {
    '@type': 'Person', '@id': PERSON_ID, 'name': SITE['author'],
    'description': 'Практик по трафику и лидогенерации, автор практикума по связке сайта и Яндекс Директа',
    'url': SITE['url'] + '/avtor/', 'sameAs': SITE['same_as'], 'knowsAbout': ['Яндекс Директ', 'Яндекс Метрика', 'контекстная реклама', 'лидогенерация', 'посадочные страницы'],
}
ORG = {
    '@type': 'Organization', '@id': ORG_ID, 'name': SITE['full_name'], 'description': SITE['legal_desc'],
    'url': SITE['url'] + '/', 'email': SITE['email'], 'telephone': SITE['phone_raw'],
    'legalName': SITE['ip'], 'taxID': SITE['inn'], 'founder': {'@id': PERSON_ID}, 'sameAs': SITE['same_as'],
    'identifier': {'@type': 'PropertyValue', 'propertyID': 'ОГРНИП', 'value': SITE['ogrnip']},
}
COURSE_LD = {
    '@type': 'Course', '@id': SITE['url'] + '/#course', 'name': SITE['full_name'],
    'description': 'Практикум: участники собирают связку сайта, Яндекс Метрики и Яндекс Директа на своих проектах под разбором автора.',
    'url': SITE['url'] + '/', 'inLanguage': 'ru-RU', 'provider': {'@id': ORG_ID}, 'author': {'@id': PERSON_ID},
    'teaches': [m['title'] for m in MODULES],
    'hasCourseInstance': {
        '@type': 'CourseInstance', 'courseMode': ['online', 'blended'],
        'courseWorkload': f'P{COURSE["weeks"]}W', 'inLanguage': 'ru-RU',
        'instructor': {'@id': PERSON_ID},
    },
}


def crumbs_ld(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE['url'] + u} for i, (u, n) in enumerate(items)]}


def faq_ld(faq):
    return {'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}} for q, a in faq]}


def faq_html(faq, title='Частые вопросы', eyebrow='Вопросы и ответы', lead=''):
    items = '\n'.join(f'<details class="reveal"><summary>{esc(q)}</summary><div>{a}</div></details>' for q, a in faq)
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    return f'''<section class="faq-sec" id="faq">
  <div class="wrap">
    <div class="sec-head faq-head reveal"><div><div class="eyebrow">{eyebrow}</div><h2>{title}</h2></div>{lead_html}</div>
    <div class="faq{' faq-2' if len(faq) >= 6 else ''}">{items}</div>
  </div>
</section>'''


# ------------------------------------------------------------------ шапка, подвал, окна
SPRITE = (SRC / 'sprite.svg').read_text(encoding='utf-8')
LOGO = ('<svg class="logo-mark" viewBox="0 0 44 40" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="7" width="16" height="12" rx="3"/><rect x="25" y="21" width="16" height="12" rx="3"/>'
        '<path d="M19 13h7a5 5 0 0 1 5 5v3"/><path d="M27 17l4 4 4-4" stroke-width="2.6"/></svg>')


def header(active):
    def links(items):
        cur = ' aria-current="page"'
        return ''.join(f'<a href="{u}"{cur if u == active else ""}>{n}</a>' for u, n in items)
    logo = f'<a href="/" class="logo" aria-label="{esc(SITE["full_name"])} — на главную">{LOGO}<span class="logo-text">Связка<br>сайт + директ</span></a>'
    burger = f'<button class="burger" type="button" data-burger aria-label="Меню">{ico("menu")}</button>'
    return f'''<header class="header" id="header">
  <div class="wrap">
    <div class="hd">
      <div class="hd-top">
        {logo}
        <p class="hd-desc"><b>Практикум {esc(SITE['author'])}</b>: сайт, аналитика и Яндекс Директ в одной системе</p>
        <a class="btn hd-calc" href="/#quiz"><span class="hd-calc-ico">{ico("target")}</span>Подобрать формат</a>
        <div class="hd-msg">
          <span class="hd-label"><i class="dot"></i>Вопрос по курсу? Пишите</span>
          <div class="hd-msg-btns">
            <a class="msg tg" href="{SITE['telegram']}" target="_blank" rel="noopener" aria-label="Написать в Telegram">{ico("tg")}</a>
            <a class="msg mx" href="{SITE['max']}" target="_blank" rel="noopener" aria-label="Написать в MAX">{ico("max")}</a>
          </div>
        </div>
        <div class="hd-phone">
          <span class="hd-label"><i class="dot"></i>Звоните {SITE['hours']}</span>
          <a class="hd-tel" href="tel:{SITE['phone_raw']}">{SITE['phone']}</a>
          <button class="hd-zamer" type="button" data-open-modal>Забронировать место в группе</button>
        </div>
        <a class="hd-call" href="tel:{SITE['phone_raw']}" aria-label="Позвонить {SITE['phone']}">{ico("phone")}</a>
        {burger}
      </div>
      <nav class="hd-nav" aria-label="Разделы">{links(NAV_MAIN)}</nav>
    </div>
  </div>
</header>
<div class="hd-sticky" id="hdSticky" aria-hidden="true">
  <div class="wrap">
    {logo}
    <nav class="hd-sticky-nav" aria-label="Разделы">{links(NAV_MAIN)}</nav>
    <a class="hd-sticky-tel" href="tel:{SITE['phone_raw']}">{ico("phone")}{SITE['phone']}</a>
    <button class="btn btn-sm" type="button" data-open-modal>Забронировать место</button>
    <a class="hd-call" href="tel:{SITE['phone_raw']}" aria-label="Позвонить">{ico("phone")}</a>
    {burger}
  </div>
</div>
<nav class="mobile-nav" id="mobileNav" aria-label="Мобильное меню"><a href="/">Главная</a>{links(NAV_MAIN)}
  <div class="mn-contacts"><a href="tel:{SITE['phone_raw']}"><b>{SITE['phone']}</b></a><span>{SITE['hours']}</span>
  <div class="hd-msg-btns"><a class="msg tg" href="{SITE['telegram']}" aria-label="Telegram">{ico("tg")}</a><a class="msg mx" href="{SITE['max']}" aria-label="MAX">{ico("max")}</a></div></div>
</nav>'''


def footer(articles):
    arts = ''.join(f'<li><a href="{a["url"]}">{esc(a["short"])}</a></li>' for a in articles[:5])
    pages = ''.join(f'<li><a href="{u}">{n}</a></li>' for u, n in NAV_MAIN)
    mods = ''.join(f'<li><a href="/programma/#modul-{m["n"]}">Модуль {m["n"]}. {esc(m["title"].split(":")[0])}</a></li>' for m in MODULES[:5])
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="sf-grid">
      <div class="sf-brand">
        <a href="/" class="logo">{LOGO}<span class="logo-text">Связка<br>сайт + директ</span></a>
        <p>{esc(SITE['legal_desc'])}. Автор — {esc(SITE['author'])}.</p>
      </div>
      <div><b>Разделы</b><ul>{pages}</ul></div>
      <div><b>Программа</b><ul>{mods}<li><a href="/programma/">Вся программа →</a></li></ul></div>
      <div><b>Связаться</b><ul>
        <li><a href="tel:{SITE['phone_raw']}">{SITE['phone']}</a></li>
        <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
        <li>{SITE['hours']}</li>
        <li class="sf-msg"><a class="msg tg" href="{SITE['telegram']}" target="_blank" rel="noopener" aria-label="Telegram">{ico("tg")}</a><a class="msg mx" href="{SITE['max']}" target="_blank" rel="noopener" aria-label="MAX">{ico("max")}</a></li>
        <li>{SITE['city']} и онлайн</li>
      </ul></div>
    </div>
    <div class="sf-bottom">
      <span>© {TODAY[:4]} {esc(SITE['full_name'])} · {esc(SITE['ip'])}, ИНН {SITE['inn']}, ОГРНИП {SITE['ogrnip']}</span>
      <span class="sf-legal"><a href="/politika/">Политика конфиденциальности</a><a href="/soglasie/">Согласие на обработку данных</a><a href="https://avedirect.ru" target="_blank" rel="noopener">Создание сайтов в AVEDIRECT.RU</a></span>
    </div>
  </div>
</footer>'''


CONSENTS = ('<div class="consents">'
            '<label class="consent"><input type="checkbox" name="consent"> <span>Я даю согласие на <a href="/soglasie/" target="_blank">обработку персональных данных</a> на условиях <a href="/politika/" target="_blank">политики конфиденциальности</a></span></label>'
            '<label class="consent"><input type="checkbox" name="ads"> <span>Я согласен получать сообщения о старте потоков и материалы по рекламе</span></label>'
            '</div>')
CONSENT_SHORT = ('<div class="consents"><label class="consent"><input type="checkbox" name="consent" checked> <span>Согласен с условиями '
                 '<a href="/politika/" target="_blank">политики конфиденциальности</a> и даю <a href="/soglasie/" target="_blank">согласие на обработку данных</a></span></label></div>')

MODAL = f'''<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal-bg" data-close></div>
  <div class="modal-box">
    <button class="modal-close" type="button" data-close aria-label="Закрыть">{ico("x")}</button>
    <div data-modal-form>
      <h3 id="modalTitle">Забронировать место в группе</h3>
      <p>Оставьте телефон — свяжусь, расскажу про формат и тарифы, отвечу на вопросы по вашему проекту.</p>
      <form class="form" data-form="measure" novalidate><input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
        <div class="field">{ico("user")}<input type="text" name="name" placeholder="Ваше имя" autocomplete="name" aria-label="Ваше имя"></div>
        <div class="field">{ico("phone")}<input type="tel" name="phone" placeholder="+7 (___) ___-__-__" autocomplete="tel" inputmode="tel" aria-label="Телефон"></div>
        <label class="field-label" for="modalMsg">Куда удобнее ответить:</label>
        <div class="field field-select">{ico("send")}<select name="messenger" id="modalMsg"><option>Telegram</option><option>MAX</option><option>Звонок</option></select></div>
        {CONSENTS}
        <button class="btn btn-block" type="submit">Забронировать место {ico("arrow", "arrow")}</button>
        <p class="form-note">{ico("lock")}Без обязательств. Данные не передаются третьим лицам</p>
      </form>
    </div>
    <div class="success" data-modal-success hidden>
      <span class="icon-box y">{ico("check")}</span>
      <h3>Заявка принята</h3>
      <p>Свяжусь в рабочее время ({SITE['hours']}).</p>
    </div>
  </div>
</div>
<div class="modal" id="modalCalc" role="dialog" aria-modal="true" aria-labelledby="calcTitle">
  <div class="modal-bg" data-close></div>
  <div class="modal-box">
    <button class="modal-close" type="button" data-close aria-label="Закрыть">{ico("x")}</button>
    <div data-modal-form>
      <h3 id="calcTitle">Задать вопрос по курсу</h3>
      <p>Только телефон — и я на связи. Отвечу в рабочее время.</p>
      <form class="form" data-form="calc" novalidate><input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
        <label class="field-label" for="calcTariff">Что вас интересует:</label>
        <div class="field field-select">{ico("list")}<select name="service" id="calcTariff">
          <option>Ближайший поток и тарифы</option><option>Тариф «Сам»</option><option>Тариф «Вместе»</option>
          <option>Тариф «Под ключ»</option><option>Разбор моего текущего Директа</option><option>Другое</option></select></div>
        <div class="field">{ico("phone")}<input type="tel" name="phone" placeholder="Ваш номер телефона" autocomplete="tel" inputmode="tel" aria-label="Телефон"></div>
        {CONSENT_SHORT}
        <button class="btn btn-block" type="submit">Отправить вопрос {ico("arrow", "arrow")}</button>
      </form>
    </div>
  </div>
</div>
<div class="fdock" id="fdock">
  <button class="fdock-x" type="button" data-dock-toggle aria-label="Свернуть меню">{ico("x")}</button>
  <button class="fdock-i" type="button" data-open-calc data-goal="dock_zayavka">{ico("phone")}<span>Задать вопрос</span></button>
  <a class="fdock-i" href="/programma/" data-goal="dock_programma">{ico("list")}<span>Программа курса</span></a>
  <a class="fdock-i" href="{SITE['telegram']}" target="_blank" rel="noopener" data-goal="dock_telegram">{ico("tg")}<span>Написать в Telegram</span></a>
  <a class="fdock-i" href="/#quiz" data-goal="dock_quiz">{ico("target")}<span>Подобрать формат</span></a>
</div>
<button class="fdock-open" type="button" data-dock-toggle aria-label="Открыть меню">{ico("chat")}</button>'''


def metrika_head():
    if not SITE['metrika']:
        return ('<!-- Яндекс Метрика: номер счётчика не указан. Впишите его в build.py → SITE[\'metrika\'] '
                'и пересоберите сайт — код счётчика и цели подключатся автоматически. -->')
    n = SITE['metrika']
    return f'''<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){{
        m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js', 'ym');
    ym({n}, 'init', {{webvisor:true, clickmap:true, referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/{n}" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->'''


def page(path, title, description, body, active=None, schema=(), og_type='website', articles=(), noindex=False):
    url = SITE['url'] + path
    graph = {'@context': 'https://schema.org', '@graph': [
        ORG, PERSON,
        {'@type': 'WebSite', '@id': SITE['url'] + '/#site', 'url': SITE['url'] + '/', 'name': SITE['full_name'], 'inLanguage': 'ru-RU', 'publisher': {'@id': ORG_ID}},
        *schema]}
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{"noindex, follow" if noindex else "index, follow, max-image-preview:large"}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(SITE['full_name'])}">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE['url']}/og.svg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_V}">
<link rel="stylesheet" href="/assets/css/pages.css?v={ASSET_V}">
<link rel="stylesheet" href="/assets/css/course.css?v={ASSET_V}">
{ld(graph)}
{metrika_head()}
</head>
<body>
{SPRITE}
{header(active)}
<main id="top">
{body}
</main>
{footer(articles)}
{MODAL}
<div class="cookie" id="cookie" role="region" aria-label="Уведомление о cookie" hidden>
  <p>Мы используем файлы cookie, чтобы улучшить работу сайта. Продолжая пользоваться сайтом, вы соглашаетесь с использованием cookie и <a href="/politika/">Политикой в отношении обработки персональных данных</a>.</p>
  <button class="btn btn-sm" type="button" id="cookieOk">Хорошо</button>
</div>
<script>window.YM_ID = {SITE['metrika'] or 'null'};</script>
<script src="/assets/js/site.js?v={ASSET_V}" defer></script>
</body>
</html>
'''


def page_hero(crumbs, h1, lead, extra=''):
    items = ''.join(f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>' for i, (u, n) in enumerate(crumbs))
    return f'''<section class="page-hero on-dark">
  <div class="wrap">
    <nav aria-label="Хлебные крошки"><ol class="crumbs">{items}</ol></nav>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>{extra}
  </div>
</section>'''


# ------------------------------------------------------------------ блоки-конструкторы
def art_cards(arts):
    out = []
    for a in arts:
        out.append(f'''
  <a class="art-card reveal" href="{a['url']}" data-cat="{slugify(a['tag'])}">
    <span class="art-cover art-cover-{a.get('cover', 1)}" aria-hidden="true"><span>{esc(a['tag'])}</span></span>
    <span class="art-card-body"><span class="art-card-tag">{esc(a['tag'])}</span><h3>{esc(a['h1'])}</h3><p>{esc(a['description'])}</p><span class="art-card-more">Читать статью {ico("arrow")}</span></span>
  </a>''')
    return '<div class="art-grid">' + ''.join(out) + '\n</div>'


def module_cards(full=False):
    out = []
    for m in MODULES:
        points = ''
        if full:
            points = '<ul class="list-check mod-points">' + ''.join(f'<li>{esc(p)}</li>' for p in m['points']) + '</ul>' \
                     f'<p class="mod-hands"><b>Сделаете руками:</b> {esc(m["hands"])}</p>'
        out.append(f'''<article class="mod reveal{' mod-full' if full else ''}" id="modul-{m['n']}">
      <div class="mod-top"><span class="mod-n">{m['n']:02d}</span><span class="icon-box y">{ico(m['icon'])}</span></div>
      <h3>{esc(m['title'])}</h3>
      <p>{esc(m['short'])}</p>
      {points}
    </article>''')
    return '<div class="mod-grid' + (' mod-grid-full' if full else '') + '">' + ''.join(out) + '</div>'


def tariff_cards():
    out = []
    for t in TARIFFS:
        rows = ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in t['rows'])
        old = f'<s>{esc(t["old"])}</s>' if t['old'] else ''
        return_btn = ('<button class="btn btn-block" type="button" data-open-modal>' if t['accent'] else '<button class="btn btn-ghost btn-block" type="button" data-open-calc>')
        out.append(f'''<article class="price-card tr-card reveal{' tr-accent' if t['accent'] else ''}">
      <div class="price-card-body">
        <div class="tr-head"><div class="eyebrow">{esc(t['tag'])}</div><h3>{esc(t['name'])}</h3></div>
        <div class="price">{esc(t['price'])} {old}</div>
        <p class="tr-lead">{esc(t['lead'])}</p>
        <dl>{rows}</dl>
        {return_btn}{esc(t['cta'])}</button>
      </div>
    </article>''')
    return '<div class="price-grid">' + ''.join(out) + '</div>'


def scheme_svg():
    """Схема связки: сайт → Метрика → Директ → CRM → обратно в Директ."""
    nodes = [
        (40, 'site', 'Сайт', 'оффер, формы, скорость'),
        (240, 'target', 'Метрика', 'цели и сегменты'),
        (440, 'layers', 'Директ', 'кампании и стратегия'),
        (640, 'db', 'CRM', 'продажи и офлайн-конверсии'),
    ]
    cards, arrows = [], []
    for i, (x, _icon, title, sub) in enumerate(nodes):
        cards.append(f'''<g transform="translate({x},60)">
      <rect width="170" height="104" rx="18" fill="#171B20" stroke="rgba(255,255,255,.16)"/>
      <text x="20" y="40" fill="#fff" font-size="19" font-weight="800">{esc(title)}</text>
      <text x="20" y="68" fill="rgba(255,255,255,.66)" font-size="13">{esc(sub[:26])}</text>
      <text x="20" y="86" fill="rgba(255,255,255,.66)" font-size="13">{esc(sub[26:])}</text>
    </g>''')
        if i < len(nodes) - 1:
            cards.append(f'<path d="M{x + 174} 112h22" stroke="#FFC61A" stroke-width="2.4" marker-end="url(#ah)"/>')
    arrows.append('<path d="M725 164v44H125v-44" stroke="#FFC61A" stroke-width="2.4" stroke-dasharray="7 6" fill="none" marker-end="url(#ah)"/>')
    arrows.append('<text x="425" y="232" text-anchor="middle" fill="#FFC61A" font-size="14" font-weight="700">конверсии возвращаются в Директ — стратегия учится на деньгах</text>')
    return f'''<svg class="scheme" viewBox="0 0 850 250" role="img" aria-label="Схема связки: сайт передаёт цели в Яндекс Метрику, Метрика — в Яндекс Директ, продажи из CRM возвращаются в Директ как офлайн-конверсии">
  <defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0l10 5-10 5z" fill="#FFC61A"/></marker></defs>
  {''.join(cards)}
  {''.join(arrows)}
</svg>'''


PAIN_VIZ = {
    'budget': '<svg viewBox="0 0 220 120" aria-hidden="true"><rect width="220" height="120" rx="14" fill="#fff"/><path d="M20 90h180" stroke="#E6E8EB" stroke-width="2"/><path d="M24 34l34 18 34 10 34 14 34 8 34 4" fill="none" stroke="#E5484D" stroke-width="3"/><g fill="#111418" font-size="11" font-weight="700"><text x="20" y="24">бюджет −</text><text x="150" y="24" fill="#E5484D">заявки 0</text></g><g fill="#FFC61A">{}</g></svg>',
    'funnel': '<svg viewBox="0 0 220 120" aria-hidden="true"><rect width="220" height="120" rx="14" fill="#fff"/><path d="M30 28h160l-52 40v30l-56 14V68z" fill="#FFF6D6" stroke="#FFC61A" stroke-width="2.4"/><text x="110" y="52" text-anchor="middle" font-size="12" font-weight="800" fill="#8A6200">100 заявок</text><text x="110" y="100" text-anchor="middle" font-size="12" font-weight="800" fill="#E5484D">2 продажи</text></svg>',
    'site': '<svg viewBox="0 0 220 120" aria-hidden="true"><rect width="220" height="120" rx="14" fill="#fff"/><rect x="24" y="20" width="172" height="80" rx="10" fill="#F3F4F6"/><rect x="36" y="32" width="86" height="12" rx="6" fill="#D6D9DD"/><rect x="36" y="52" width="120" height="8" rx="4" fill="#E6E8EB"/><rect x="36" y="68" width="60" height="8" rx="4" fill="#E6E8EB"/><rect x="140" y="80" width="48" height="14" rx="7" fill="#E5484D" opacity=".25"/><text x="164" y="91" text-anchor="middle" font-size="9" font-weight="800" fill="#E5484D">форма</text></svg>',
    'data': '<svg viewBox="0 0 220 120" aria-hidden="true"><rect width="220" height="120" rx="14" fill="#fff"/><g stroke="#E6E8EB" stroke-width="2"><path d="M30 92h160M30 92V28"/></g><g fill="#D6D9DD"><rect x="46" y="66" width="22" height="26" rx="4"/><rect x="86" y="56" width="22" height="36" rx="4"/><rect x="126" y="74" width="22" height="18" rx="4"/><rect x="166" y="62" width="22" height="30" rx="4"/></g><text x="110" y="46" text-anchor="middle" font-size="12" font-weight="800" fill="#6B7178">цели не настроены</text></svg>',
}


def pain_cards():
    out = []
    for p in PAINS:
        viz = PAIN_VIZ[p['viz']].replace('{}', '')
        out.append(f'''<article class="pain reveal">
      <div class="pain-media pain-viz">{viz}<span class="x">{ico("x")}</span></div>
      <div class="pain-body">
        <div class="pain-weather">{ico(p['icon'])}{esc(p['label'])}</div>
        <h3>{esc(p['title'])}</h3>
        <p>{esc(p['text'])}</p>
      </div>
    </article>''')
    return '<div class="problem-grid">' + ''.join(out) + '</div>'


def lab_block():
    tabs = ''.join(f'''<button class="lab-tab{' on' if i == 0 else ''}" type="button" data-tab="{i}" data-goal="lab_step_view">
        <span class="icon-box y">{ico(x['icon'])}</span><b>{esc(x['title'])}</b></button>''' for i, x in enumerate(LAB))
    panes = ''.join(f'''<div class="lab-pane{' on' if i == 0 else ''}" data-pane="{i}">
        <div class="eyebrow">Шаг {i + 1} из {len(LAB)}</div>
        <h3>{esc(x['title'])}</h3>
        <p>{esc(x['text'])}</p>
      </div>''' for i, x in enumerate(LAB))
    return f'''<div class="lab reveal" data-tabs>
    <div class="lab-tabs">{tabs}</div>
    <div class="lab-panes">{panes}
      <div class="lab-actions">
        <button class="btn" type="button" data-open-modal>Забронировать место {ico("arrow", "arrow")}</button>
        <a class="btn btn-ghost" href="/programma/">Смотреть программу</a>
      </div>
    </div>
  </div>'''


def steps_block():
    weeks = COURSE['weeks']
    items = ''.join(f'''<li class="reveal{' accent' if i == len(STEPS) - 1 else ''}">{ico(ic)}<b>{esc(t)}</b><p>{esc(d)}</p></li>''' for i, (ic, t, d) in enumerate(STEPS))
    return f'''<section id="etapy">
  <div class="wrap">
    <div class="sec-head reveal"><div><div class="eyebrow">Как идёт поток</div><h2>{weeks} недель: от экономики до рабочих кампаний</h2></div>
      <p class="lead">Каждый шаг — созвон, домашнее задание и разбор. Домашние задания делаются на вашем проекте, а не на учебном примере.</p></div>
    <ol class="steps">{items}</ol>
  </div>
</section>'''


def compare_block():
    bad = ''.join(f'<div class="sc-row bad"><i>{ico("x")}</i><s>{esc(x)}</s></div>' for x in COMPARE_BAD)
    good = ''.join(f'<div class="sc-row good"><i>{ico("check")}</i>{esc(x)}</div>' for x in COMPARE_GOOD)
    return f'''<div class="fix">
    <div class="reveal">
      <div class="eyebrow">Как обычно запускают</div>
      <div class="scenario">{bad}</div>
    </div>
    <div class="reveal">
      <div class="eyebrow">Как делаем на практикуме</div>
      <div class="scenario">{good}</div>
    </div>
  </div>'''


def quiz_block():
    """Квиз «Подберите формат участия» — 4 вопроса + контакты."""
    q = [
        ('state', 'Что у вас сейчас?', 'Отвечайте как есть — от этого зависит, с чего начнём.', [
            ('Ни сайта, ни рекламы', 'собираем всё с нуля'),
            ('Сайт есть, рекламы нет', 'готовим сайт и запускаем'),
            ('Реклама идёт, заявки дорогие', 'разбираем кабинет и чиним'),
            ('Есть подрядчик или команда', 'хочу понимать и контролировать'),
        ]),
        ('niche', 'Что продаёте?', 'Под разные типы спроса — разные кампании.', [
            ('Услуги', 'ремонт, строительство, b2c-услуги'),
            ('Товары, магазин', 'каталог, фид, товарная кампания'),
            ('B2B, опт', 'длинный цикл сделки'),
            ('Своё производство', 'и товары, и услуги'),
        ]),
        ('budget', 'Бюджет на Директ в месяц', 'От него зависит, какая стратегия вообще обучится.', [
            ('До 30 000 ₽', ''), ('30–100 тыс ₽', ''), ('100–300 тыс ₽', ''), ('Больше 300 тыс ₽', ''),
        ]),
        ('goal', 'Что важнее на потоке?', 'Это главный ориентир для личных разборов.', [
            ('Собрать связку с нуля', ''), ('Снизить стоимость заявки', ''),
            ('Масштабировать то, что работает', ''), ('Разобраться самому', 'чтобы контролировать подрядчика'),
        ]),
    ]
    steps = []
    for i, (key, title, hint, opts) in enumerate(q, start=1):
        o = ''.join(f'''<button class="opt text" type="button" data-value="{esc(v)}">
          <span class="opt-label"><span class="opt-txt">{esc(v)}{f'<small>{esc(s)}</small>' if s else ''}</span></span></button>''' for v, s in opts)
        steps.append(f'''<div class="step{' active' if i == 1 else ''}" data-step="{i}" data-key="{key}" data-title="{esc(title)}">
        <h3>{esc(title)}</h3><p class="hint">{esc(hint)}</p>
        <div class="opts four">{o}</div>
      </div>''')
    form = f'''<div class="step" data-step="5">
        <div class="result-top">{ico("check")}Готово</div>
        <h3>Куда прислать подходящий формат участия?</h3>
        <p class="hint">Пришлю программу, тариф под вашу задачу и дату старта. Без звонков-«дожимов».</p>
        <div class="summary" id="summary"></div>
        <form class="form" data-form="quiz" novalidate><input type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
          <div class="form-row">
            <div class="field">{ico("user")}<input type="text" name="name" placeholder="Ваше имя" autocomplete="name" aria-label="Ваше имя"></div>
            <div class="field">{ico("phone")}<input type="tel" name="phone" placeholder="+7 (___) ___-__-__" autocomplete="tel" inputmode="tel" aria-label="Телефон"></div>
          </div>
          <div class="messengers"><span>Куда ответить:</span>
            <label><input type="radio" name="messenger" value="Telegram" checked><span>Telegram</span></label>
            <label><input type="radio" name="messenger" value="MAX"><span>MAX</span></label>
            <label><input type="radio" name="messenger" value="Звонок"><span>Звонок</span></label>
          </div>
          {CONSENTS}
          <button class="btn btn-block" type="submit">Получить формат и программу {ico("arrow", "arrow")}</button>
          <p class="form-note">{ico("lock")}Данные не передаются третьим лицам</p>
        </form>
        <button class="q-edit" type="button" data-goto="1">← Изменить ответы</button>
      </div>
      <div class="step" data-step="6">
        <div class="success"><span class="icon-box y">{ico("check")}</span><h3>Заявка принята</h3><p>Свяжусь в рабочее время и пришлю программу.</p></div>
      </div>'''
    return f'''<section class="quiz-sec" id="quiz">
  <div class="wrap">
    <div class="quiz-grid">
      <div class="quiz-left on-dark reveal">
        <div class="eyebrow">Подбор формата</div>
        <h2>4 вопроса — и я скажу, что делать с вашей связкой</h2>
        <div class="perk-list">
          <div class="perk"><span class="icon-box y">{ico("target")}</span>Скажу, с чего начинать именно в вашем случае</div>
          <div class="perk"><span class="icon-box y">{ico("ruble")}</span>Назову реальную вилку стоимости заявки в вашей нише</div>
          <div class="perk"><span class="icon-box y">{ico("list")}</span>Пришлю программу и подходящий тариф</div>
          <div class="perk"><span class="icon-box y">{ico("lock")}</span>Без спама и звонков с незнакомых номеров</div>
        </div>
      </div>
      <div class="quiz" id="quizBox">
        <div class="q-progress"><span id="qCounter">Вопрос 1 из 4</span><div class="q-bar"><i id="qBar" style="width:25%"></i></div><em id="qPercent">25%</em></div>
        {''.join(steps)}
        {form}
        <div class="q-nav" id="qNav">
          <button class="q-back" type="button" id="qBack" disabled>{ico("back")}Назад</button>
          <button class="btn q-next" type="button" id="qNext" disabled>Далее {ico("arrow", "arrow")}</button>
        </div>
      </div>
      <div class="quiz-get reveal">
        <div class="quiz-get-head quiz-get-plain">
          <div>{ico("gift")}Бонус участникам второй версии</div>
        </div>
        <ul class="get-list">
          <li><span class="icon-box y">{ico("eye")}</span><div><b>Аудит текущей рекламы</b><span>до старта потока, с письменным разбором</span></div></li>
          <li><span class="icon-box y">{ico("target")}</span><div><b>Чек-лист целей Метрики</b><span>что настроить, чтобы стратегия обучилась</span></div></li>
          <li><span class="icon-box y">{ico("site")}</span><div><b>Разбор первого экрана</b><span>что менять на вашей странице</span></div></li>
          <li><span class="icon-box y">{ico("doc")}</span><div><b>Шаблон расчёта экономики</b><span>целевой CPL и ДРР по вашим цифрам</span></div></li>
        </ul>
      </div>
    </div>
    <div class="quiz-bottom">
      <div>{ico("calendar")}<span><b>Старт {esc(COURSE['start'])}</b><span>{esc(COURSE['version'])}</span></span></div>
      <div>{ico("team")}<span><b>{esc(COURSE['seats'])} мест</b><span>маленькая группа — каждому разбор</span></span></div>
      <div>{ico("clock")}<span><b>{esc(COURSE['weeks'])} недель</b><span>{esc(COURSE['calls'])} живых созвонов</span></span></div>
      <div>{ico("shield")}<span><b>Записи остаются</b><span>доступ бессрочно</span></span></div>
    </div>
  </div>
</section>'''


CTA = {
    'book': f'<aside class="icta icta-dark"><span class="icon-box y">{ico("calendar")}</span>'
            f'<div><b>Вторая версия практикума</b><p>Старт {COURSE["start"]}, группа на {COURSE["seats"]} мест. Личный разбор сайта и кабинета Директа каждого участника.</p></div>'
            '<button class="btn" type="button" data-open-modal>Забронировать место</button></aside>',
    'quiz': f'<aside class="icta icta-y"><span class="icon-box dark">{ico("target")}</span>'
            '<div><b>Не знаете, с чего начать?</b><p>Ответьте на 4 вопроса — пришлю разбор вашей ситуации и подходящий формат участия.</p></div>'
            '<a class="btn" href="/#quiz">Подобрать формат</a></aside>',
    'programma': f'<aside class="icta icta-light"><span class="icon-box y">{ico("list")}</span>'
                 '<div><b>Посмотрите программу целиком</b><p>8 модулей: экономика, сайт, аналитика, структура кампаний, объявления, стратегии, ретаргетинг, рост.</p></div>'
                 '<a class="btn btn-ghost" href="/programma/">Открыть программу</a></aside>',
    'telegram': f'<aside class="icta icta-light"><span class="icon-box" style="background:#229ED9;color:#fff">{ico("tg")}</span>'
                f'<div><b>Спросите напрямую в Telegram</b><p>Пришлите ссылку на сайт и скриншот кабинета — скажу, что в вашем случае чинить первым. Отвечаю {SITE["hours"]}.</p></div>'
                f'<span class="icta-btns"><a class="btn btn-ghost" href="{SITE["telegram"]}" target="_blank" rel="noopener">{ico("tg")}Telegram</a>'
                f'<a class="btn btn-ghost" href="{SITE["max"]}" target="_blank" rel="noopener">{ico("max")}MAX</a></span></aside>',
}


def apply_cta(body):
    return re.sub(r'<!--CTA:(\w+)-->', lambda m: CTA[m.group(1)], body)


# ------------------------------------------------------------------ статьи
DRAFTS = []


def load_articles():
    arts = []
    for f in sorted((SRC / 'articles').glob('*.html')):
        raw = f.read_text(encoding='utf-8')
        m = re.match(r'\s*<!--META\s*(\{.*?\})\s*-->\s*', raw, re.S)
        if not m:
            continue
        meta = json.loads(m.group(1))
        meta['slug'] = f.stem.split('_', 1)[-1]
        meta['url'] = f'/blog/{meta["slug"]}/'
        meta['body'] = raw[m.end():]
        meta.setdefault('updated', meta['published'])
        meta.setdefault('cover', 1)
        arts.append(meta)
    return arts


def render_article(a, arts):
    toc = []

    def add_id(m):
        text = m.group(1)
        sid = slugify(text)
        toc.append((sid, re.sub(r'<[^>]+>', '', text)))
        return f'<h2 id="{sid}">{text}</h2>'
    body = apply_cta(re.sub(r'<h2>(.*?)</h2>', add_id, a['body']))
    words = len(strip_tags(body).split())
    minutes = max(3, round(words / 180))
    toc_html = ''.join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
    related = [x for x in arts if x['slug'] in a.get('related', [])] or [x for x in arts if x is not a][:3]
    crumbs = [('/', 'Главная'), ('/blog/', 'Блог'), (a['url'], a['short'])]
    meta = f'''<div class="art-meta">
      <span>{ico("calendar")}Обновлено <time datetime="{a['updated']}">{ru_date(a['updated'])}</time></span>
      <span>{ico("clock")}{minutes} мин чтения</span>
      <span>{ico("user")}{esc(SITE['author'])}</span>
    </div>'''
    body_html = f'''{page_hero(crumbs, esc(a['h1']), esc(a['description']), meta)}
<section>
  <div class="wrap art-layout">
    <article class="prose-wrap">
      <div class="tldr"><b>Коротко</b><p>{a['tldr']}</p></div>
      <div class="prose">
{body}
      </div>
      <div class="art-cta">
        <div><b>Разберём вашу связку лично</b><p>На практикуме смотрим ваш сайт и ваш кабинет Директа: настраиваем цели, собираем кампании, считаем стоимость заявки.</p></div>
        <button class="btn" type="button" data-open-modal>Забронировать место {ico("arrow", "arrow")}</button>
      </div>
      <div class="author"><span class="icon-box y">{ico("user")}</span><div><b>{esc(SITE['author'])}</b><span>Автор практикума «{esc(SITE['full_name'])}». Материал написан по практике настройки и ведения рекламных кампаний. Опубликовано {ru_date(a['published'])}.</span></div></div>
    </article>
    <aside class="art-aside">
      <nav class="toc" aria-label="Содержание"><b>Содержание</b><ol>{toc_html}</ol></nav>
      <div class="aside-cta"><b>Вторая версия, старт {esc(COURSE['start'])}</b><p>Группа на {esc(COURSE['seats'])} мест: сайт, аналитика и Директ на вашем проекте.</p><button class="btn" type="button" data-open-modal>Забронировать</button></div>
    </aside>
  </div>
</section>
{faq_html(a['faq'], title='Вопросы по теме', eyebrow='Коротко о главном')}
<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head reveal"><div><div class="eyebrow">Читайте также</div><h2>Другие разборы</h2></div><a class="sec-link" href="/blog/">Все статьи {ico("arrow")}</a></div>
    {art_cards(related[:3])}
  </div>
</section>'''
    schema = [
        {'@type': 'BlogPosting', '@id': SITE['url'] + a['url'] + '#article', 'headline': a['h1'], 'description': a['description'],
         'datePublished': a['published'], 'dateModified': a['updated'], 'inLanguage': 'ru-RU',
         'author': {'@id': PERSON_ID}, 'publisher': {'@id': ORG_ID},
         'mainEntityOfPage': SITE['url'] + a['url'], 'articleSection': a['tag'], 'wordCount': words,
         'keywords': ', '.join(a.get('keywords', []))},
        crumbs_ld(crumbs), faq_ld(a['faq'])]
    return page(a['url'], a['title'], a['description'], body_html, active='/blog/', schema=schema, og_type='article', articles=arts), body


# ------------------------------------------------------------------ юридические страницы
LEGAL = {
    'politika': ('Политика в отношении обработки персональных данных',
                 'Политика обработки персональных данных сайта практикума: какие данные собираются из форм, зачем, сколько хранятся и как их удалить.',
                 [('Кто обрабатывает данные',
                   f'<p>Оператор персональных данных — {SITE["ip"]}, ИНН {SITE["inn"]}, ОГРНИП {SITE["ogrnip"]} (далее — Оператор). '
                   f'Связаться можно по адресу <a href="mailto:{SITE["email"]}">{SITE["email"]}</a> или по телефону <a href="tel:{SITE["phone_raw"]}">{SITE["phone"]}</a>.</p>'),
                  ('Какие данные собираются',
                   '<p>Через формы на сайте Оператор получает: имя, номер телефона, выбранный способ связи, ответы на вопросы подбора формата участия, '
                   'а также технические данные — адрес страницы, параметры перехода (UTM-метки, идентификатор клика), дату и время отправки.</p>'
                   '<p>Оператор не собирает специальные категории персональных данных и не запрашивает паспортные или платёжные данные через формы сайта.</p>'),
                  ('Зачем они нужны',
                   '<p>Данные используются, чтобы связаться с вами по вашему обращению, рассказать о программе, тарифах и дате старта потока, '
                   'а при вашем отдельном согласии — присылать материалы и сообщения о новых потоках. Отказаться от рассылки можно в любой момент одним сообщением.</p>'),
                  ('Передача третьим лицам',
                   '<p>Данные не продаются и не передаются третьим лицам, кроме случаев, предусмотренных законом, и кроме сервисов, '
                   'которые технически обеспечивают работу сайта: хостинг, сервис отправки писем, мессенджер для ответа на обращение, Яндекс Метрика (обезличенная статистика).</p>'),
                  ('Сроки и удаление',
                   '<p>Данные хранятся столько, сколько нужно для обработки обращения и исполнения договорённостей, но не дольше срока, установленного законом. '
                   f'Чтобы отозвать согласие и удалить данные, напишите на <a href="mailto:{SITE["email"]}">{SITE["email"]}</a> — Оператор удалит их и подтвердит это ответным письмом.</p>'),
                  ('Cookie и статистика',
                   '<p>Сайт использует cookie и Яндекс Метрику, чтобы понимать, какие страницы полезны посетителям. '
                   'Cookie можно отключить в настройках браузера — основные функции сайта продолжат работать.</p>'),
                  ('Изменения политики',
                   f'<p>Актуальная редакция всегда опубликована на этой странице. Дата последнего обновления — {ru_date(TODAY)}.</p>'),
                  ]),
    'soglasie': ('Согласие на обработку персональных данных',
                 'Текст согласия на обработку персональных данных, которое даётся при отправке формы на сайте практикума.',
                 [('Текст согласия',
                   f'<p>Отправляя форму на сайте, я даю {SITE["ip"]} (ИНН {SITE["inn"]}) согласие на обработку указанных мной персональных данных: '
                   'имени, номера телефона, выбранного способа связи и ответов на вопросы формы.</p>'
                   '<p>Обработка включает сбор, запись, систематизацию, хранение, уточнение, использование, передачу сервисам, обеспечивающим работу сайта и связь со мной, '
                   'блокирование, удаление и уничтожение данных — в объёме, необходимом для ответа на моё обращение и организации моего участия в практикуме.</p>'),
                  ('Срок и отзыв',
                   f'<p>Согласие действует до его отзыва. Отозвать согласие можно письмом на <a href="mailto:{SITE["email"]}">{SITE["email"]}</a> '
                   'или сообщением в тот мессенджер, через который шла переписка. После отзыва обработка прекращается, а данные удаляются, '
                   'если закон не требует их хранить дольше.</p>'),
                  ('Отдельное согласие на рассылку',
                   '<p>Согласие на получение сообщений о старте потоков и материалов по рекламе даётся отдельной галочкой и не является условием '
                   'для ответа на обращение. Отписаться можно в любой момент.</p>'),
                  ]),
}


def render_legal(slug, arts):
    title, desc, blocks = LEGAL[slug]
    crumbs = [('/', 'Главная'), (f'/{slug}/', title)]
    sections = ''.join(f'<h2 id="{slugify(h)}">{esc(h)}</h2>{t}' for h, t in blocks)
    body = page_hero(crumbs, esc(title), esc(desc)) + f'''
<section>
  <div class="wrap art-layout">
    <article class="prose-wrap"><div class="prose">{sections}</div>
      <p class="note" style="margin-top:28px">{ico("clock")}Редакция от {ru_date(TODAY)}. Шаблон документа: перед публикацией проверьте его у юриста и подставьте свои реквизиты.</p>
    </article>
    <aside class="art-aside"><div class="aside-cta"><b>Остались вопросы?</b><p>Напишите — отвечу, какие данные и зачем собираются.</p><button class="btn" type="button" data-open-calc>Задать вопрос</button></div></aside>
  </div>
</section>'''
    return page(f'/{slug}/', f'{title} | {SITE["full_name"]}', desc, body, schema=[crumbs_ld(crumbs)], articles=arts)


# ------------------------------------------------------------------ сборка
def build():
    OUT.mkdir(exist_ok=True)
    for x in OUT.iterdir():
        shutil.rmtree(x) if x.is_dir() else x.unlink()
    shutil.copytree(STATIC, OUT, dirs_exist_ok=True)

    arts = load_articles()
    arts.sort(key=lambda a: (a['published'], -a.get('order', 99)), reverse=True)
    full_texts = []
    home_faq = json.loads((SRC / 'pages' / 'home.faq.json').read_text(encoding='utf-8'))

    # ---------- статьи
    for a in arts:
        out, body = render_article(a, arts)
        d = OUT / a['url'].strip('/')
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(out, encoding='utf-8')
        faq_txt = '\n'.join(f'В: {q}\nО: {strip_tags(ans)}' for q, ans in a['faq'])
        full_texts.append(f'## {a["h1"]}\nURL: {SITE["url"]}{a["url"]}\nОбновлено: {a["updated"]}\n\nКоротко: {strip_tags(a["tldr"])}\n\n{strip_tags(body)}\n\nВопросы и ответы:\n{faq_txt}')

    # ---------- блог: страницы по 9 статей и рубрики
    PER_PAGE = 9
    cats = []
    for a in arts:
        if a['tag'] not in cats:
            cats.append(a['tag'])
    blog_urls = []

    def chips_html(active):
        out = f'<a class="chip{" active" if active is None else ""}" href="/blog/">Все <span>{len(arts)}</span></a>'
        for c in cats:
            out += f'<a class="chip{" active" if active == c else ""}" href="/blog/tema/{slugify(c)}/">{esc(c)} <span>{sum(1 for a in arts if a["tag"] == c)}</span></a>'
        return f'<nav class="chips" aria-label="Рубрики блога">{out}</nav>'

    def pager(n, total):
        if total < 2:
            return ''
        url = lambda k: '/blog/' if k == 1 else f'/blog/page/{k}/'
        cur = ' aria-current="page"'
        items = ''.join(f'<a class="pg{" active" if k == n else ""}" href="{url(k)}"{cur if k == n else ""}>{k}</a>' for k in range(1, total + 1))
        prev = f'<a class="pg" href="{url(n - 1)}" rel="prev" aria-label="Предыдущая страница">←</a>' if n > 1 else ''
        nxt = f'<a class="pg" href="{url(n + 1)}" rel="next" aria-label="Следующая страница">→</a>' if n < total else ''
        return f'<nav class="pager" aria-label="Страницы блога">{prev}{items}{nxt}</nav>'

    pages_total = max(1, -(-len(arts) // PER_PAGE))
    lead = 'Разборы по Яндекс Директу и сайтам под платный трафик: стратегии, цели в Метрике, структура кампаний, стоимость заявки. Без «секретных фишек» — только то, что проверяется цифрами.'
    for n in range(1, pages_total + 1):
        chunk = arts[(n - 1) * PER_PAGE:n * PER_PAGE]
        path = '/blog/' if n == 1 else f'/blog/page/{n}/'
        crumbs = [('/', 'Главная'), ('/blog/', 'Блог')] + ([] if n == 1 else [(path, f'Страница {n}')])
        h1 = 'Блог о Яндекс Директе и сайтах' + ('' if n == 1 else f' — страница {n}')
        body = page_hero(crumbs, h1, lead) + f'''
<section><div class="wrap">{chips_html(None)}{art_cards(chunk)}{pager(n, pages_total)}</div></section>
<section style="padding-top:0"><div class="wrap">{CTA['book']}</div></section>'''
        blog_ld = {'@type': 'Blog', 'name': f'Блог «{SITE["full_name"]}»', 'url': SITE['url'] + path, 'inLanguage': 'ru-RU', 'publisher': {'@id': ORG_ID},
                   'blogPost': [{'@type': 'BlogPosting', 'headline': a['h1'], 'url': SITE['url'] + a['url'], 'datePublished': a['published']} for a in chunk]}
        d = OUT / path.strip('/')
        d.mkdir(parents=True, exist_ok=True)
        title = 'Блог о Яндекс Директе: стратегии, цели, стоимость заявки' + ('' if n == 1 else f' — страница {n}') + f' | {SITE["name"]}'
        (d / 'index.html').write_text(page(path, title, lead[:155], body, active='/blog/', schema=[blog_ld, crumbs_ld(crumbs)], articles=arts), encoding='utf-8')
        blog_urls.append(path)

    for c in cats:
        items_c = [a for a in arts if a['tag'] == c]
        path = f'/blog/tema/{slugify(c)}/'
        crumbs = [('/', 'Главная'), ('/blog/', 'Блог'), (path, c)]
        body = page_hero(crumbs, f'{c}: разборы и инструкции', f'{len(items_c)} материалов в рубрике «{c}».') + f'''
<section><div class="wrap">{chips_html(c)}{art_cards(items_c)}</div></section>
<section style="padding-top:0"><div class="wrap">{CTA['quiz']}</div></section>'''
        ld_c = {'@type': 'CollectionPage', 'name': f'{c} — блог «{SITE["full_name"]}»', 'url': SITE['url'] + path,
                'hasPart': [{'@type': 'BlogPosting', 'headline': a['h1'], 'url': SITE['url'] + a['url']} for a in items_c]}
        d = OUT / path.strip('/')
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(page(path, f'{c} — Яндекс Директ и сайты | {SITE["name"]}',
            f'Материалы рубрики «{c}»: ' + '; '.join(a['short'] for a in items_c)[:140] + '.', body, active='/blog/', schema=[ld_c, crumbs_ld(crumbs)], articles=arts), encoding='utf-8')
        blog_urls.append(path)

    # ---------- обычные страницы
    for p in PAGES:
        body = (SRC / 'pages' / f'{p["body"]}.body.html').read_text(encoding='utf-8')
        schema = []
        body = (body
                .replace('<!--QUIZ-->', quiz_block())
                .replace('<!--MODULES-->', module_cards(full=False))
                .replace('<!--MODULES-FULL-->', module_cards(full=True))
                .replace('<!--TARIFFS-->', tariff_cards())
                .replace('<!--SCHEME-->', scheme_svg())
                .replace('<!--PAINS-->', pain_cards())
                .replace('<!--LAB-->', lab_block())
                .replace('<!--STEPS-->', steps_block())
                .replace('<!--COMPARE-->', compare_block())
                .replace('<!--ARTICLES-->', art_cards(arts[:3])))
        body = apply_cta(body)
        # {{icon-name}} → иконка из спрайта; {{icon-arrow-btn}} → стрелка в кнопке
        body = body.replace('{{icon-arrow-btn}}', ico('arrow', 'arrow'))
        body = re.sub(r'\{\{icon-([a-z-]+)\}\}', lambda m: ico(m.group(1)), body)
        for k, v in [('{{start}}', COURSE['start']), ('{{weeks}}', COURSE['weeks']), ('{{seats}}', COURSE['seats']),
                     ('{{calls}}', COURSE['calls']), ('{{version}}', COURSE['version']), ('{{author}}', SITE['author']),
                     ('{{phone}}', SITE['phone']), ('{{phone_raw}}', SITE['phone_raw']), ('{{email}}', SITE['email']),
                     ('{{telegram}}', SITE['telegram']), ('{{telegram_name}}', SITE['telegram_name']), ('{{max}}', SITE['max']),
                     ('{{hours}}', SITE['hours']), ('{{blog_main}}', SITE['blog_main']),
                     ('{{author_ip}}', SITE['ip']), ('{{inn}}', SITE['inn']), ('{{ogrnip}}', SITE['ogrnip']),
                     ('{{city}}', SITE['city']), ('{{founded}}', SITE['founded']),
                     ('{{streams}}', COURSE['streams']), ('{{students}}', COURSE['students'])]:
            body = body.replace(k, v)
        if p['path'] == '/':
            body = body.replace('<!--FAQ-->', faq_html(home_faq, lead='Короткие ответы на то, что спрашивают чаще всего. Полный список — на странице «Вопросы».'))
            schema = [faq_ld(home_faq), COURSE_LD]
        else:
            crumbs = [('/', 'Главная'), (p['path'], p['crumb'])]
            body = body.replace('<!--CRUMBS-->', ''.join(
                f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>' for i, (u, n) in enumerate(crumbs)))
            schema = [crumbs_ld(crumbs)]
            faq_file = SRC / 'pages' / f'{p["body"]}.faq.json'
            if faq_file.exists():
                f = json.loads(faq_file.read_text(encoding='utf-8'))
                body = body.replace('<!--FAQ-->', faq_html(f))
                schema.append(faq_ld(f))
            if p['path'] == '/programma/':
                schema.append(COURSE_LD)
        dest = OUT / p['path'].strip('/') if p['path'] != '/' else OUT
        dest.mkdir(parents=True, exist_ok=True)
        (dest / 'index.html').write_text(page(p['path'], p['title'], p['description'], body, active=p['nav'], schema=schema, articles=arts), encoding='utf-8')

    # ---------- все вопросы одной страницей
    all_faq = list(home_faq)
    for f in sorted((SRC / 'pages').glob('*.faq.json')):
        if f.name != 'home.faq.json':
            all_faq += json.loads(f.read_text(encoding='utf-8'))
    for a in arts:
        all_faq += a['faq']
    seen_q, uniq = set(), []
    for q, a_ in all_faq:
        if q not in seen_q:
            seen_q.add(q)
            uniq.append([q, a_])
    crumbs = [('/', 'Главная'), ('/faq/', 'Вопросы и ответы')]
    body = page_hero(crumbs, 'Вопросы о практикуме и о Яндекс Директе', f'{len(uniq)} ответов: формат и тарифы, что нужно иметь до старта, бюджеты, стратегии, цели в Метрике и стоимость заявки.') + \
        faq_html(uniq, title='Все вопросы', eyebrow='FAQ') + f'<section style="padding-top:0"><div class="wrap">{CTA["telegram"]}</div></section>'
    (OUT / 'faq').mkdir(exist_ok=True)
    (OUT / 'faq' / 'index.html').write_text(page('/faq/', f'Вопросы и ответы о практикуме и Яндекс Директе | {SITE["name"]}',
        'Ответы на частые вопросы: как проходит практикум, что нужно до старта, какой бюджет нужен Директу, какие цели настраивать, когда ждать первых заявок.',
        body, active='/faq/', schema=[crumbs_ld(crumbs), faq_ld(uniq)], articles=arts), encoding='utf-8')

    # ---------- юридические страницы
    for slug in LEGAL:
        d = OUT / slug
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(render_legal(slug, arts), encoding='utf-8')

    # ---------- страницы «Спасибо»
    tnx = [
        ('tnx1', 'Спасибо! Подбираю формат под ваш проект', 'Я получил ответы на вопросы подбора — посмотрю ваш случай и вернусь с рекомендацией.',
         ['Посмотрю ваши ответы и, если прислали ссылку, ваш сайт', 'Напишу, с чего начинать именно вам и какой тариф подходит', 'Пришлю программу и дату старта потока']),
        ('tnx2', 'Спасибо! Место за вами забронировано', 'Свяжусь в рабочее время, отвечу на вопросы и расскажу, как проходит оплата и старт.',
         ['Свяжусь по указанному номеру или в мессенджере', 'Обсудим ваш проект и подходящий тариф', 'Закрепим место в группе и пришлю материалы к старту']),
        ('tnx3', 'Спасибо, вопрос получен', 'Отвечу в рабочее время. Если вопрос срочный — напишите в Telegram, там отвечаю быстрее.',
         ['Прочитаю вопрос и, если нужно, посмотрю ваш сайт', 'Отвечу подробно, без общих слов', 'Если задача шире вопроса — предложу формат участия']),
    ]
    for slug_t, h1, lead_t, steps in tnx:
        body = f'''<section class="tnx"><div class="wrap tnx-grid">
  <div class="tnx-text reveal">
    <span class="tnx-ok">{ico("check")}Заявка отправлена</span>
    <h1>{h1}</h1>
    <p class="lead">{lead_t}</p>
    <ol class="tnx-steps">{''.join(f'<li>{s}</li>' for s in steps)}</ol>
    <p class="tnx-wait">А пока ждёте ответа — посмотрите программу практикума или разборы в блоге: там разложено, почему кампании сливают бюджет и что с этим делать.</p>
    <div class="tnx-actions">
      <a class="btn" href="/programma/">{ico("list")}Смотреть программу {ico("arrow", "arrow")}</a>
      <a class="btn btn-ghost" href="/blog/">{ico("doc")}Читать блог</a>
    </div>
    <p class="tnx-call">Срочный вопрос — пишите в Telegram: <a href="{SITE['telegram']}" target="_blank" rel="noopener"><b>{SITE['telegram_name']}</b></a> или звоните <a href="tel:{SITE['phone_raw']}"><b>{SITE['phone']}</b></a></p>
  </div>
  <div class="tnx-side reveal">
    <div class="tnx-card-mini">
      <div class="eyebrow">{esc(COURSE['version'])}</div>
      <h2>{esc(SITE['full_name'])}</h2>
      <ul class="list-check">
        <li>Старт {esc(COURSE['start'])}, группа на {esc(COURSE['seats'])} мест</li>
        <li>{esc(COURSE['weeks'])} недель, {esc(COURSE['calls'])} живых созвонов</li>
        <li>Личный разбор сайта и кабинета Директа</li>
        <li>Записи остаются бессрочно</li>
      </ul>
    </div>
  </div>
</div></section>
<section style="padding-top:0"><div class="wrap">{CTA['programma']}</div></section>'''
        (OUT / f'{slug_t}.html').write_text(page(f'/{slug_t}.html', h1 + f' | {SITE["name"]}', lead_t, body, noindex=True, articles=arts), encoding='utf-8')

    # ---------- 404
    (OUT / '404.html').write_text(page('/404.html', f'Страница не найдена | {SITE["name"]}', 'Страница не найдена.',
        page_hero([('/', 'Главная'), ('/404.html', 'Страница не найдена')], 'Страница не найдена',
                  'Возможно, её переместили. Откройте программу практикума или блог — там всё главное.',
                  f'<div class="hero-ctas" style="margin-top:28px"><a class="btn" href="/">На главную</a><a class="btn btn-ghost" href="/programma/">Программа</a></div>'),
        noindex=True, articles=arts), encoding='utf-8')

    # ---------- og-картинка (генерируется, чтобы ссылка в мессенджерах выглядела прилично)
    (OUT / 'og.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#0E1114"/>
<circle cx="1060" cy="90" r="320" fill="#FFC61A" opacity=".10"/>
<text x="80" y="150" fill="#FFC61A" font-family="Manrope,Arial" font-size="26" font-weight="800" letter-spacing="4">{esc(COURSE['version'].upper())}</text>
<text x="80" y="268" fill="#fff" font-family="Manrope,Arial" font-size="86" font-weight="800">Связка:</text>
<text x="80" y="366" fill="#fff" font-family="Manrope,Arial" font-size="86" font-weight="800">сайт + Яндекс Директ</text>
<text x="80" y="446" fill="rgba(255,255,255,.78)" font-family="Manrope,Arial" font-size="30">Практикум {esc(SITE['author'])}: настраиваем на вашем проекте</text>
<rect x="80" y="500" width="420" height="72" rx="18" fill="#FFC61A"/>
<text x="290" y="546" fill="#111418" text-anchor="middle" font-family="Manrope,Arial" font-size="26" font-weight="800">Старт {esc(COURSE['start'])}</text>
</svg>
''', encoding='utf-8')

    # ---------- sitemap
    urls = ([(p['path'], TODAY, '1.0' if p['path'] == '/' else '0.9') for p in PAGES]
            + [('/faq/', TODAY, '0.8')]
            + [(u, TODAY, '0.7') for u in blog_urls]
            + [(a['url'], a['updated'], '0.7') for a in arts]
            + [(f'/{s}/', TODAY, '0.2') for s in LEGAL])
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{SITE["url"]}{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n' for u, d, pr in urls) + '</urlset>\n', encoding='utf-8')

    # ---------- robots
    bots = ['Yandex', 'YandexAdditional', 'YandexAdditionalBot', 'Googlebot', 'Google-Extended', 'Bingbot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
            'PerplexityBot', 'Perplexity-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'Applebot-Extended', 'DeepSeekBot', 'GigaChat']
    (OUT / 'robots.txt').write_text('\n'.join(f'User-agent: {b}\nAllow: /\n' for b in bots) +
        f'\nUser-agent: *\nAllow: /\nDisallow: /404.html\nDisallow: /tnx1.html\nDisallow: /tnx2.html\nDisallow: /tnx3.html\nDisallow: /send.php\n\nSitemap: {SITE["url"]}/sitemap.xml\n', encoding='utf-8')

    # ---------- llms.txt / llms-full.txt (чтобы нейросети отвечали о курсе фактами)
    facts = f'''- Продукт: «{SITE['full_name']}» — {COURSE['version'].lower()} практикума по связке сайта, Яндекс Метрики и Яндекс Директа.
- Автор и ведущий: {SITE['author']}.
- Формат: {COURSE['format']}. {COURSE['where']}.
- Длительность: {COURSE['weeks']} недель, {COURSE['calls']} живых созвонов, группа на {COURSE['seats']} мест. Старт — {COURSE['start']}.
- Для кого: предприниматели и специалисты, которые ведут или собираются вести рекламу в Яндекс Директе на свой сайт.
- Главная идея: сайт, аналитика и реклама настраиваются как одна система; решения принимаются по стоимости заявки и продажи, а не по кликам.
- Программа: ''' + '; '.join(f'модуль {m["n"]} — {m["title"]}' for m in MODULES) + f'''
- Тарифы: ''' + '; '.join(f'{t["name"]} — {t["price"]}' for t in TARIFFS) + f'''
- Контакты: {SITE['phone']} ({SITE['hours']}), {SITE['email']}, Telegram {SITE['telegram']}.'''
    llms = f'''# {SITE['full_name']}

> Практикум {SITE['author']}: участники собирают связку сайта, Яндекс Метрики и Яндекс Директа на своих проектах, под личным разбором автора.

## Факты
{facts}

## Основные страницы
''' + ''.join(f'- [{p["crumb"]}]({SITE["url"]}{p["path"]}): {p["description"]}\n' for p in PAGES) + f'''- [Вопросы и ответы]({SITE['url']}/faq/): формат, бюджеты, стратегии, цели в Метрике

## Блог
''' + ''.join(f'- [{a["h1"]}]({SITE["url"]}{a["url"]}): {a["description"]}\n' for a in arts) + f'''
## Полные тексты
- [llms-full.txt]({SITE['url']}/llms-full.txt): все статьи и программа одним текстовым файлом
'''
    (OUT / 'llms.txt').write_text(llms, encoding='utf-8')
    prog_txt = '\n\n'.join(f'### Модуль {m["n"]}. {m["title"]}\n{m["short"]}\n' + '\n'.join(f'- {p}' for p in m['points']) + f'\nСделаете руками: {m["hands"]}' for m in MODULES)
    (OUT / 'llms-full.txt').write_text(f'# {SITE["full_name"]} — программа и статьи\n\n## Факты\n{facts}\n\n## Программа\n{prog_txt}\n\n' +
        '\n\n---\n\n'.join(full_texts) + '\n', encoding='utf-8')

    print(f'Готово: {len(PAGES)} основных страниц, {len(arts)} статей, {len(TARIFFS)} тарифов → {OUT}')
    if TODO:
        print('\nНадо подставить реальные данные (в build.py):')
        for t in TODO:
            print('  •', t)


if __name__ == '__main__':
    build()
