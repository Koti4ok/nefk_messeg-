"""
Management command: python manage.py seed_data
Створює: директора, замдиректора, 100+ юзерів, групи (рілси/тікток стайл),
         пости, коментарі, дружбу, підписки, аватарки.
"""
import os
import random
import urllib.request
import urllib.error
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

# ─── Імена ────────────────────────────────────────────────────────────────────
FIRST_NAMES_M = [
    'Олексій','Дмитро','Іван','Максим','Андрій','Сергій','Михайло','Олег',
    'Тарас','Богдан','Владислав','Артем','Євген','Ярослав','Роман','Назар',
    'Денис','Павло','Ігор','Юрій','Кирило','Антон','Микола','Василь',
    'Руслан','Данило','Арсен','Захар','Лука','Олексій','Віктор','Олександр',
    'Едуард','Ростислав','Геннадій','Степан','Остап','Мар\'ян','Вадим','Станіслав',
]
FIRST_NAMES_F = [
    'Анна','Марія','Олена','Юлія','Катерина','Наталія','Ірина','Вікторія',
    'Діана','Аліна','Софія','Поліна','Дарина','Тетяна','Оксана','Людмила',
    'Ганна','Христина','Валентина','Надія','Лілія','Яна','Карина','Тамара',
    'Зоя','Ніна','Лариса','Інна','Жанна','Регіна',
]
LAST_NAMES = [
    'Іваненко','Коваленко','Бондаренко','Кравченко','Мельник','Шевченко',
    'Ткаченко','Поліщук','Савченко','Лисенко','Гриценко','Марченко',
    'Клименко','Василенко','Петренко','Олійник','Мороз','Романенко',
    'Кириленко','Литвиненко','Данченко','Гончаренко','Хоменко','Науменко',
    'Яременко','Семенченко','Сидоренко','Кучеренко','Тимошенко','Пономаренко',
    'Зінченко','Бабенко','Мусієнко','Приходько','Левченко','Власенко',
    'Лазаренко','Юрченко','Карпенко','Нечипоренко',
]

SPECIALTIES = [
    'Комп\'ютерна інженерія',
    'Електромеханіка',
    'Автоматизація виробничих процесів',
    'Програмна інженерія',
    'Монтаж і обслуговування',
]

HOBBIES = [
    'Знімаю рілси та монтую відео','Захоплююсь музикою та стримінгом',
    'Люблю фотографію та тревел-контент','Пишу вірші та читаю книги',
    'Займаюся спортом та фітнесом','Граю в ігри та стримлю на Twitch',
    'Малюю та займаюся дизайном','Займаюся програмуванням у вільний час',
    'Люблю готувати та ділитися рецептами','Цікавлюсь психологією та саморозвитком',
    'Веду тікток про студентське життя','Займаюся скейтом та BMX',
    'Захоплююся аніме та манґою','Вчу іноземні мови та подорожую',
    'Знімаю влоги про навчання та лайфхаки',
]

# ─── Навчальні та соцмережеві групи ─────────────────────────────────────────
# (name, description, emoji, тематика для аватарки)
STUDY_GROUPS = [
    ('КІ-31', 'Комп\'ютерна інженерія — 3 курс 💻', 'КІ'),
    ('КІ-21', 'Комп\'ютерна інженерія — 2 курс 💻', 'КІ'),
    ('ЕМ-31', 'Електромеханіка — 3 курс ⚡', 'ЕМ'),
    ('ЕМ-21', 'Електромеханіка — 2 курс ⚡', 'ЕМ'),
    ('ПІ-31', 'Програмна інженерія — 3 курс 🖥️', 'ПІ'),
    ('ПІ-21', 'Програмна інженерія — 2 курс 🖥️', 'ПІ'),
    ('АВТ-31', 'Автоматизація — 3 курс 🤖', 'АВТ'),
]

# TikTok/Reels тематичні групи — (name, description, seed_color)
TIKTOK_GROUPS = [
    (
        'НЕМК Рілси 🎬',
        'Публікуємо найкращі рілси, відосіки та смішні моменти з коледжу. Знімаєш — ділись! Переглядів не рахуємо, тут головне настрій 😂🔥',
        'ff0050',
    ),
    (
        'Studyvlog НЕМК 📚',
        'Влоги про навчання, сесійні будні та лайфхаки для студентів. "Вчишся — знімай, спиш на парі — не знімай" 😴📹',
        '6441a5',
    ),
    (
        'НЕМК Trendy 🕺',
        'Танцюємо тренди, робимо челенджі і не соромимось! Найгарячіші кліпи від студентів коледжу. Duet welcome 💃🔊',
        'fe2d55',
    ),
    (
        'Мемасики НЕМК 😂',
        'Збірна мемів про студентське життя, пари, сесії та всі ті ситуації які ти знаєш занадто добре. Без мемів не виживемо 🙏',
        'ffcc00',
    ),
    (
        'НЕМК Фіт & Спорт 💪',
        'Тренування, зарядки, спортивні відосіки та мотивація. Показуємо прогрес, ділимося порадами. До зали — разом! 🏋️‍♂️🏃',
        '00c170',
    ),
    (
        'Їжа & Рецепти 🍕',
        'Що готуємо на загурт, що їмо в їдальні і що приносимо на пари. Рецепти, огляди та "що приготувати за 5 хвилин" 🧑‍🍳😋',
        'ff6b35',
    ),
    (
        'Gaming Squad НЕМК 🎮',
        'Геймери коледжу об\'єднуйтесь! Стриміть, кліпайте, ділиться топ моментами з ігор. CS2, Valorant, FIFA — все тут 🕹️',
        '7b2ff7',
    ),
    (
        'Музика & Каверки 🎵',
        'Граєш, співаєш або просто любиш музику? Ось твоє місце. Каверки, реміксики, рекомендації плейлистів і living concerts 🎸🎤',
        'e91e8c',
    ),
    (
        'Подорожі & Тревел 🌍',
        'Поділись де побував цього літа, покажи красиві місця Ніжина та Чернігівщини. Travel reels та фоточки welcome ✈️📸',
        '1da1f2',
    ),
    (
        'DIY & Лайфхаки ⚡',
        'Корисні фішки, саморобки, ліфхаки для навчання і побуту. Зробив щось крутим — покажи нам! Натхнення тут 🔧💡',
        'ff9500',
    ),
    (
        'Аніме & Манґа 🌸',
        'Для тих хто знає що таке "Ще один епізод і сплю". Обговорення, фанарт, рекомендації та weebs unite 🗡️👺',
        'e83e8c',
    ),
    (
        'IT Talk 👨‍💻',
        'Розбираємо технології, ділимося проєктами, обговорюємо новини зі світу IT. Від Arduino до Web3 — всім цікаво 🔥💻',
        '0d6efd',
    ),
    (
        'НЕМК Загальна 🏫',
        'Офіційна спільнота Ніжинського електромеханічного коледжу. Новини, оголошення, події — все тут 📋',
        '2c3e50',
    ),
    (
        'Спорт НЕМК 🏆',
        'Спортивне життя коледжу — змагання, перемоги, тренування. Пишаємося нашими спортсменами! 💪',
        '27ae60',
    ),
    (
        'Культура та події 🎭',
        'Концерти, вистави, виставки та культурне життя НЕМК. Не пропусти найцікавіше! 🎉',
        '8e44ad',
    ),
]

# ─── Пости ───────────────────────────────────────────────────────────────────
POSTS = [
    ('director', 'Вітаю всіх студентів та викладачів НЕМК! Новий навчальний рік обіцяє бути насиченим подіями, новими знаннями та досягненнями. Бажаю кожному натхнення та успіхів! 🎓'),
    ('director', 'Оголошення: 15 жовтня відбудеться День відкритих дверей у НЕМК. Запрошуємо абітурієнтів та їхніх батьків! Реєстрація на сайті немк.com.ua 📋'),
    ('vice_director', 'Нагадую студентам 3-го курсу — здача залікових книжок до 20 числа. Будь ласка, не затягуйте! 📚'),
    ('vice_director', 'Вітаємо команду НЕМК з перемогою на обласній олімпіаді з інформатики! Ви нас дуже порадували! 🏆'),
    ('student', 'Хлопці з КІ-31, хто хоче разом готуватись до іспитів? Збираємось в читальному залі завтра о 15:00 👨‍💻'),
    ('student', 'Нарешті здав курсову! Тиждень не спав, але воно того варте 😅 Спасибі викладачу за терпіння!'),
    ('student', 'Зняв рілс про нашу лабораторію — вже 2к переглядів за ніч 🔥 не очікував взагалі'),
    ('student', 'Хто бере участь у конкурсі молодих програмістів? Давайте об\'єднаємося в команду! 💪'),
    ('student', 'Щойно дізнався що наш коледж отримав нове обладнання для лабораторії електроніки. Будемо практикуватись по-справжньому! ⚡'),
    ('student', 'Поради першокурсникам: не пропускайте лекції, вони дуже важливі. Кажу з власного досвіду 😊'),
    ('student', 'Відзначаємо день народження нашої групи ЕМ-31 у п\'ятницю в їдальні! Всі запрошені 🎉'),
    ('student', 'Зробили челендж в коридорі між парами — дивіться в рілсах 😂😂 тег немкрілси'),
    ('student', 'Ранкова пробіжка перед парами — найкращий початок дня! Хто зі мною завтра о 7:00? 🏃'),
    ('student', 'Знайшов класний відеокурс з Arduino — якщо комусь треба, кидайте реакцію 📩'),
    ('student', 'Наша команда зайняла 2 місце на регіональному чемпіонаті з робототехніки! 🤖 Дякуємо всім хто підтримував!'),
    ('student', 'Сьогодні була екскурсія на завод — побачили реальне виробництво. Дуже мотивує навчатись! 🏭'),
    ('student', 'Новий розклад занять вивісили на сайті НЕМК — перевіряйте! Є зміни на середу.'),
    ('student', 'Після практики на підприємстві зрозумів — обрав правильну спеціальність! Дуже цікаво 💡'),
    ('student', 'Щодо завтрашньої пари з математики — перенесена на 14:00, аудиторія 205. Передайте всім!'),
    ('student', 'ПОВ: ти вивчаєш всю ніч а на іспиті питання яких не було на парах 💀💀💀'),
    ('student', 'Тренд зробили разом з групою — вийшло топчик 🕺🔥 дивіться в нашому тіктоці @nemk_ki31'),
    ('student', 'Зранку кава, потім алгоритми. Такий він — студентський ритм ☕👨‍💻'),
    ('student', 'Хто грає у CS2? Збираємось на рейтинг увечері, потрібні два гравці 🎮'),
    ('student', 'Зняли влог "24 години в НЕМК" — монтую, скоро буде 📹✨'),
    ('student', 'Коли дедлайн завтра але ти дізнався про нього сьогодні 😭😭 класика'),
    ('student', 'Знайшли найкрасивіше місце для фото в коледжі — підйомова сходи з вікном. Рекомендую 📸'),
    ('student', 'Зробив саморобний контролер на Arduino для дипломної — горджуся собою нічого не скажу 🤩⚡'),
    ('student', 'Кав\'ярня біля коледжу запустила студентську знижку 20% — поспішайте ☕💸'),
    ('student', 'Вчора сесійна ніч, сьогодні іспит, завтра — свобода! 🎊 Тримаємось хлопці'),
    ('student', 'Пишу диплом і слухаю lo-fi — єдиний спосіб не здатися 🎵📝'),
]

COMMENTS = [
    'Дякую, дуже корисно! 🙏',
    'Підтримую! 👍',
    'Цікаво, не знав про це',
    'Теж беру участь!',
    'Молодці, так тримати!',
    'Дякую за інформацію 🙏',
    'Супер новина! 🔥',
    'Уже записався!',
    'Це дуже важливо знати',
    'Збираємось!',
    'Круто! Хочу теж спробувати',
    'Дякую за нагадування',
    'Завтра буду точно!',
    'Поділився з групою',
    'Відмінна ідея! 💡',
    'Вже чекаю не дочекаюсь 🎊',
    'Так, давно пора!',
    'Ура! 🏆',
    'Топчик контент 🔥🔥',
    'Лайк залишив 👌',
    'OMG це я 😂',
    'Дякую за роботу!',
    'Той самий вайб 🤌',
    'Це занадто реально 💀',
    'Підписався щоб не пропустити наступне!',
]

CHAT_MSGS = [
    ('director', 'Доброго дня! Нагадую про завтрашні збори о 10:00 в актовому залі.'),
    ('vice', 'Дякую за нагадування! Всі будуть присутні.'),
    ('student', 'Добрий день! Хто знає де взяти методичку з курсової?'),
    ('student', 'В бібліотеці є, але треба замовляти заздалегідь.'),
    ('director', 'Поздоровляю нашу команду з перемогою! Ви – гордість коледжу 🏆'),
    ('student', 'Хто завтра здає залік з електроніки?'),
    ('student', 'Я, і ще кілька хлопців з групи'),
    ('vice', 'Розклад екзаменів оновлено. Перевіряйте на сайті!'),
    ('student', 'Коли буде наступна практика на підприємстві?'),
    ('director', 'Практика запланована на 15-25 листопада. Деталі в деканаті.'),
    ('student', 'Хто з КІ йде на хакатон у Чернігів?'),
    ('student', 'Я та ще двоє з нашої групи точно йдемо 💪'),
    ('student', 'Кинули новий рілс в групу НЕМК Рілси — гляньте 🔥'),
    ('student', 'Вже подивився, вогонь! Підписався'),
    ('vice', 'Нагадую про здачу рефератів до кінця тижня 📋'),
]


def download_avatar(url, filename, folder):
    """Завантажує зображення з URL і повертає ContentFile або None."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
        return ContentFile(data, name=filename)
    except Exception:
        return None


class Command(BaseCommand):
    help = 'Заповнює БД тестовими даними: юзери, пости, коментарі, групи (TikTok стайл)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-avatars',
            action='store_true',
            default=False,
            help='Пропустити завантаження аватарок (швидший запуск)',
        )

    def handle(self, *args, **options):
        from accounts.models import User
        from posts.models import Post, Comment, Like
        from groups.models import Group, GroupMembership
        from friends.models import Friendship, FriendRequest, Follow
        from notifications.models import NotificationSettings

        load_avatars = not options['no_avatars']

        self.stdout.write(self.style.MIGRATE_HEADING('🚀 Починаємо seed_data...'))

        created_users = []

        def make_user(username, first, last, role='user', is_staff=False, is_super=False,
                      bio='', avatar_seed=None):
            # Ідемпотентно: якщо вже існує — повертаємо, не оновлюємо
            try:
                u = User.objects.get(username=username)
                created_users.append(u)
                return u
            except User.DoesNotExist:
                pass
            u = User.objects.create_user(
                username=username,
                password='nemk1234',
                first_name=first,
                last_name=last,
                email=f'{username}@nemk.edu.ua',
                role=role,
                is_staff=is_staff,
                is_superuser=is_super,
                bio=bio,
                location='Ніжин, Чернігівська обл.',
                created_at=timezone.now() - timedelta(days=random.randint(30, 365)),
            )
            NotificationSettings.objects.get_or_create(user=u)

            # Аватарка через DiceBear API (безкоштовний SVG сервіс)
            if load_avatars and not u.avatar:
                seed = avatar_seed or username
                # Використовуємо різні стилі для різноманітності
                styles = ['adventurer', 'avataaars', 'big-smile', 'fun-emoji',
                          'lorelei', 'micah', 'miniavs', 'notionists-neutral',
                          'open-peeps', 'personas']
                style = random.choice(styles)
                avatar_url = f'https://api.dicebear.com/8.x/{style}/svg?seed={seed}&size=200'
                img_file = download_avatar(avatar_url, f'{username}_avatar.svg', 'avatars/')
                if img_file:
                    u.avatar.save(f'{username}_avatar.svg', img_file, save=True)

            created_users.append(u)
            self.stdout.write(f'  ✅ {u.get_full_name()} (@{username})')
            return u

        # ── Директор ─────────────────────────────────────────────
        director = make_user(
            'director', 'Василь', 'Петренко',
            role='admin', is_staff=True, is_super=True,
            bio='Директор Ніжинського електромеханічного коледжу. Педагог вищої категорії, відмінник освіти України.',
            avatar_seed='director-vasyl',
        )

        # ── Заступник директора ───────────────────────────────────
        vice = make_user(
            'vice_director', 'Олена', 'Коваленко',
            role='admin', is_staff=True, is_super=False,
            bio='Заступник директора з навчальної роботи. Кандидат педагогічних наук.',
            avatar_seed='vice-olena',
        )

        # ── 100 студентів ─────────────────────────────────────────
        all_names = []
        for n in FIRST_NAMES_M:
            all_names.append((n, random.choice(LAST_NAMES), 'M'))
        for n in FIRST_NAMES_F:
            all_names.append((n, random.choice(LAST_NAMES), 'F'))

        # Дублюємо щоб отримати 100 осіб
        extended_names = all_names.copy()
        random.shuffle(all_names)
        random.shuffle(extended_names)
        full_pool = (all_names + extended_names)[:100]

        students = []
        for i, (fname, lname, gender) in enumerate(full_pool):
            uname = f'student_{i+1}'
            spec = random.choice(SPECIALTIES)
            hobby = random.choice(HOBBIES)
            course = random.choice(['1', '2', '3'])
            bio = f'Студент {course} курсу · {spec} · {hobby}.'
            s = make_user(uname, fname, lname, bio=bio, avatar_seed=f'{fname}-{lname}-{i}')
            students.append(s)

        all_users = [director, vice] + students
        self.stdout.write(self.style.SUCCESS(f'\n👥 Всього юзерів: {len(all_users)}'))

        # ── Групи ─────────────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING('\n📁 Створюємо групи...'))
        group_objs = []

        # Навчальні групи
        study_group_objs = []
        for gname, gdesc, short in STUDY_GROUPS:
            g, created = Group.objects.get_or_create(
                name=gname,
                defaults={
                    'description': gdesc,
                    'creator': director,
                    'is_private': False,
                }
            )
            if created:
                GroupMembership.objects.get_or_create(
                    group=g, user=director, defaults={'role': 'admin'}
                )
                # Аватарка для навчальної групи — кольоровий плейсхолдер
                if load_avatars and not g.avatar:
                    colors = ['2c3e50', '16213e', '0f3460', '533483', '2d6a4f']
                    color = random.choice(colors)
                    avatar_url = (
                        f'https://ui-avatars.com/api/?name={urllib.parse.quote(short)}'
                        f'&background={color}&color=fff&size=200&bold=true&font-size=0.4'
                    )
                    img_file = download_avatar(avatar_url, f'group_{gname}_avatar.png', 'groups/avatars/')
                    if img_file:
                        g.avatar.save(f'group_{gname.replace("/","_")}_avatar.png', img_file, save=True)
                self.stdout.write(f'  📚 {gname}')
            group_objs.append(g)
            study_group_objs.append(g)

        # TikTok/Reels тематичні групи
        tiktok_group_objs = []
        for gname, gdesc, color in TIKTOK_GROUPS:
            g, created = Group.objects.get_or_create(
                name=gname,
                defaults={
                    'description': gdesc,
                    'creator': director,
                    'is_private': False,
                }
            )
            if created:
                GroupMembership.objects.get_or_create(
                    group=g, user=director, defaults={'role': 'admin'}
                )
                # Аватарка — DiceBear shapes або initials через ui-avatars
                if load_avatars and not g.avatar:
                    # Беремо перші слова назви для initials
                    initials = ''.join(w[0] for w in gname.split()[:2] if w[0].isalpha())[:2]
                    if not initials:
                        initials = 'НМ'
                    avatar_url = (
                        f'https://ui-avatars.com/api/?name={urllib.parse.quote(initials)}'
                        f'&background={color}&color=fff&size=200&bold=true&rounded=true&font-size=0.5'
                    )
                    safe_name = gname.replace('/', '_').replace(' ', '_').replace(':', '')
                    img_file = download_avatar(
                        avatar_url, f'group_{safe_name}_avatar.png', 'groups/avatars/'
                    )
                    if img_file:
                        g.avatar.save(f'group_{safe_name}_avatar.png', img_file, save=True)
                self.stdout.write(f'  🎬 {gname}')
            group_objs.append(g)
            tiktok_group_objs.append(g)

        self.stdout.write(self.style.SUCCESS(f'📁 Груп створено: {len(group_objs)}'))

        # ── Розподіл учасників ────────────────────────────────────
        # Навчальні групи — рівномірно по студентах
        for i, student in enumerate(students):
            sg = study_group_objs[i % len(study_group_objs)]
            GroupMembership.objects.get_or_create(
                group=sg, user=student, defaults={'role': 'member'}
            )

        # Знаходимо тематичні групи за назвою
        def find_tg(name_part):
            return next((g for g in tiktok_group_objs if name_part in g.name), None)

        nemk_zagalna  = find_tg('НЕМК Загальна')
        nemk_rilsy    = find_tg('Рілси')
        studyvlog     = find_tg('Studyvlog')
        trendy        = find_tg('Trendy')
        memy          = find_tg('Мемасики')
        fit           = find_tg('Фіт')
        yizha         = find_tg('Їжа')
        gaming        = find_tg('Gaming')
        muzyka        = find_tg('Музика')
        travel        = find_tg('Подорожі')
        diy           = find_tg('DIY')
        anime         = find_tg('Аніме')
        it_talk       = find_tg('IT Talk')
        sport_nemk    = find_tg('Спорт НЕМК')
        kultura       = find_tg('Культура')

        for i, student in enumerate(students):
            # Всі — в загальну
            if nemk_zagalna:
                GroupMembership.objects.get_or_create(
                    group=nemk_zagalna, user=student, defaults={'role': 'member'}
                )
            # ~80% — в рілси (це ж ТТ стайл!)
            if nemk_rilsy and random.random() < 0.8:
                GroupMembership.objects.get_or_create(
                    group=nemk_rilsy, user=student, defaults={'role': 'member'}
                )
            # ~60% — в мемасики
            if memy and random.random() < 0.6:
                GroupMembership.objects.get_or_create(
                    group=memy, user=student, defaults={'role': 'member'}
                )
            # ~50% — стадивлог
            if studyvlog and random.random() < 0.5:
                GroupMembership.objects.get_or_create(
                    group=studyvlog, user=student, defaults={'role': 'member'}
                )
            # ~40% — trendy
            if trendy and random.random() < 0.4:
                GroupMembership.objects.get_or_create(
                    group=trendy, user=student, defaults={'role': 'member'}
                )
            # Решта — рандомно по тематиках
            optional_groups = [g for g in [fit, yizha, gaming, muzyka, travel, diy, anime, it_talk, sport_nemk, kultura] if g]
            chosen = random.sample(optional_groups, random.randint(1, min(4, len(optional_groups))))
            for og in chosen:
                GroupMembership.objects.get_or_create(
                    group=og, user=student, defaults={'role': 'member'}
                )

        # Додаємо vice до всіх груп як модератора
        for g in group_objs:
            GroupMembership.objects.get_or_create(
                group=g, user=vice, defaults={'role': 'moderator'}
            )

        self.stdout.write(self.style.SUCCESS('👥 Учасників розподілено по групах'))

        # ── Дружба між студентами ─────────────────────────────────
        pairs_done = set()
        for s1 in students:
            pool = random.sample(students, min(15, len(students)))
            count = 0
            for s2 in pool:
                if s1 == s2:
                    continue
                pair = tuple(sorted([s1.id, s2.id]))
                if pair in pairs_done:
                    continue
                pairs_done.add(pair)
                u1 = min(s1, s2, key=lambda u: u.id)
                u2 = max(s1, s2, key=lambda u: u.id)
                Friendship.objects.get_or_create(user1=u1, user2=u2)
                count += 1
                if count >= 8:
                    break

        # Підписки на директора і замдира
        for student in students:
            Follow.objects.get_or_create(follower=student, following=director)
            if random.random() > 0.35:
                Follow.objects.get_or_create(follower=student, following=vice)
            # Студенти підписуються один на одного (~30%)
            targets = random.sample(students, min(10, len(students)))
            for t in targets:
                if t != student and random.random() < 0.3:
                    Follow.objects.get_or_create(follower=student, following=t)

        self.stdout.write(self.style.SUCCESS('🤝 Дружба та підписки встановлені'))

        # ── Пости ─────────────────────────────────────────────────
        post_objs = []
        days_ago = len(POSTS)
        for i, (role_key, content) in enumerate(POSTS):
            if role_key == 'student':
                author = random.choice(students)
            elif role_key == 'director':
                author = director
            else:
                author = vice

            # Кожен 3-й пост іде в одну з тематичних груп
            group = None
            if i % 3 == 0 and tiktok_group_objs:
                group = random.choice(tiktok_group_objs[:5])

            if not Post.objects.filter(author=author, content=content[:40]).exists():
                p = Post.objects.create(
                    author=author,
                    content=content,
                    post_type='status',
                    group=group,
                    created_at=timezone.now() - timedelta(days=days_ago - i, hours=random.randint(0, 12)),
                )
                post_objs.append(p)

        self.stdout.write(self.style.SUCCESS(f'📝 Постів: {len(post_objs)}'))

        # ── Лайки та коментарі ────────────────────────────────────
        for post in post_objs:
            likers = random.sample(all_users, random.randint(3, min(25, len(all_users))))
            for liker in likers:
                Like.objects.get_or_create(post=post, user=liker)

            commenters = random.sample(all_users, random.randint(1, min(7, len(all_users))))
            for commenter in commenters:
                Comment.objects.create(
                    post=post,
                    author=commenter,
                    content=random.choice(COMMENTS),
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48)),
                )

        self.stdout.write(self.style.SUCCESS('❤️  Лайки та коментарі додано'))

        # ── Повідомлення в чатах ──────────────────────────────────
        from chat.models import Conversation, Message

        if not Conversation.objects.filter(name='НЕМК Загальний чат').exists():
            gc = Conversation.objects.create(name='НЕМК Загальний чат', is_group=True)
            for u in all_users[:30]:
                gc.participants.add(u)

            for j, (role, text) in enumerate(CHAT_MSGS):
                if role == 'director':
                    sender = director
                elif role == 'vice':
                    sender = vice
                else:
                    sender = random.choice(students)
                Message.objects.create(
                    conversation=gc, sender=sender, content=text,
                    created_at=timezone.now() - timedelta(hours=len(CHAT_MSGS) - j),
                )

        self.stdout.write(self.style.SUCCESS('💬 Груповий чат створено'))

        # ── Підсумок ──────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS('\n✨ seed_data завершено успішно!'))
        self.stdout.write(self.style.WARNING('\n📋 Логіни для тесту:'))
        self.stdout.write('  директор:  director   | пароль: nemk1234')
        self.stdout.write('  замдир:    vice_director | пароль: nemk1234')
        self.stdout.write('  студент:   student_1  | пароль: nemk1234')
        self.stdout.write(f'\n  👥 Юзерів: {len(all_users)}')
        self.stdout.write(f'  📁 Груп:   {len(group_objs)}')
        self.stdout.write(f'  📝 Постів: {len(post_objs)}')


# urllib.parse потрібен для quote — імпортуємо тут щоб не ламати top-level
import urllib.parse
