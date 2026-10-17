"""
Management command: python manage.py seed_data
Створює: директора, замдиректора, 50 студентів, групи, пости, коментарі, дружбу, підписки
"""
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

FIRST_NAMES_M = [
    'Олексій','Дмитро','Іван','Максим','Андрій','Сергій','Михайло','Олег',
    'Тарас','Богдан','Владислав','Артем','Євген','Ярослав','Роман','Назар',
    'Денис','Павло','Ігор','Юрій','Кирило','Антон','Микола','Василь',
    'Руслан','Олексій','Данило','Арсен','Захар','Лука',
]
FIRST_NAMES_F = [
    'Анна','Марія','Олена','Юлія','Катерина','Наталія','Ірина','Вікторія',
    'Діана','Аліна','Софія','Поліна','Дарина','Тетяна','Оксана','Людмила',
    'Ганна','Христина','Валентина','Надія',
]
LAST_NAMES = [
    'Іваненко','Коваленко','Бондаренко','Кравченко','Мельник','Шевченко',
    'Ткаченко','Поліщук','Савченко','Лисенко','Гриценко','Марченко',
    'Клименко','Василенко','Петренко','Олійник','Мороз','Романенко',
    'Кириленко','Литвиненко','Данченко','Гончаренко','Хоменко','Науменко',
    'Яременко','Семенченко','Сидоренко','Кучеренко','Тимошенко','Пономаренко',
]

SPECIALTIES = [
    'Комп\'ютерна інженерія',
    'Електромеханіка',
    'Автоматизація виробничих процесів',
    'Програмна інженерія',
    'Монтаж і обслуговування',
]

GROUPS = [
    ('КІ-31','Комп\'ютерна інженерія 3 курс'),
    ('КІ-21','Комп\'ютерна інженерія 2 курс'),
    ('ЕМ-31','Електромеханіка 3 курс'),
    ('ЕМ-21','Електромеханіка 2 курс'),
    ('ПІ-31','Програмна інженерія 3 курс'),
    ('ПІ-21','Програмна інженерія 2 курс'),
    ('АВТ-31','Автоматизація 3 курс'),
    ('НЕМК Загальна','Офіційна спільнота коледжу'),
    ('Спорт НЕМК','Спортивне життя коледжу'),
    ('Культура та події','Культурне життя та заходи'),
]

POSTS = [
    # (автор_роль, текст)
    ('director', 'Вітаю всіх студентів та викладачів НЕМК! Новий навчальний рік обіцяє бути насиченим подіями, новими знаннями та досягненнями. Бажаю кожному натхнення та успіхів! 🎓'),
    ('director', 'Оголошення: 15 жовтня відбудеться День відкритих дверей у НЕМК. Запрошуємо абітурієнтів та їхніх батьків! Реєстрація на сайті nemk.com.ua 📋'),
    ('vice_director', 'Нагадую студентам 3-го курсу — здача залікових книжок до 20 числа. Будь ласка, не затягуйте! 📚'),
    ('vice_director', 'Вітаємо команду НЕМК з перемогою на обласній олімпіаді з інформатики! Ви нас дуже порадували! 🏆 Пишаємося кожним із вас!'),
    ('student', 'Хлопці з КІ-31, хто хоче разом готуватись до іспитів? Збираємось в читальному залі завтра о 15:00 👨‍💻'),
    ('student', 'Нарешті здав курсову! Тиждень не спав, але воно того варте 😅 Спасибі викладачу за терпіння!'),
    ('student', 'Хто бере участь у конкурсі молодих програмістів? Давайте об\'єднаємося в команду! 💪'),
    ('student', 'Щойно дізнався що наш коледж отримав нове обладнання для лабораторії електроніки. Будемо практикуватись по-справжньому! ⚡'),
    ('student', 'Поради першокурсникам: не пропускайте лекції, вони дуже важливі. Кажу з власного досвіду 😊'),
    ('student', 'Відзначаємо день народження нашої групи ЕМ-31 у п\'ятницю в їдальні! Всі запрошені 🎉'),
    ('student', 'Хто знає де взяти підручник "Основи програмування на Python"? В бібліотеці вже немає...'),
    ('student', 'Щойно вийшов з пари з фізики — голова кругом 😵 Але розібрався з формулами завдяки гарному поясненню!'),
    ('student', 'Ранкова пробіжка перед парами — найкращий початок дня! Хто зі мною завтра о 7:00? 🏃'),
    ('student', 'Знайшов класний відеокурс з Arduino — якщо комусь треба, скиньте в коменти своїй email 📩'),
    ('student', 'Наша команда зайняла 2 місце на регіональному чемпіонаті з робототехніки! 🤖 Дякуємо всім хто підтримував!'),
    ('student', 'Сьогодні була екскурсія на завод — побачили реальне виробництво. Дуже мотивує навчатись! 🏭'),
    ('student', 'Хто пише дипломну роботу на тему IoT? Давайте обміняємось матеріалами 🔌'),
    ('student', 'Новий розклад занять вивісили на сайті НЕМК — перевіряйте! Є зміни на середу.'),
    ('student', 'Після практики на підприємстві зрозумів — обрав правильну спеціальність! Дуже цікаво 💡'),
    ('student', 'Щодо завтрашньої пари з математики — перенесена на 14:00, аудиторія 205. Передайте всім!'),
]

COMMENTS = [
    'Дякую, дуже корисно!',
    'Підтримую! 👍',
    'Цікаво, не знав про це',
    'Теж беру участь!',
    'Молодці, так тримати!',
    'Дякую за інформацію 🙏',
    'Супер новина!',
    'Уже записався!',
    'Це дуже важливо знати',
    'Збираємось!',
    'Круто! Хочу теж спробувати',
    'Дякую за нагадування',
    'Завтра буду точно!',
    'Поділився з групою',
    'Відмінна ідея!',
    'Вже чекаю не дочекаюсь 🎊',
    'Так, давно пора!',
    'Ура! 🏆',
    'Надсилаю вам матеріали',
    'Дякую за роботу!',
]


class Command(BaseCommand):
    help = 'Заповнює БД тестовими даними: юзери, пости, коментарі, групи'

    def handle(self, *args, **options):
        from accounts.models import User
        from posts.models import Post, Comment, Like
        from groups.models import Group, GroupMembership
        from friends.models import Friendship, FriendRequest, Follow
        from notifications.models import NotificationSettings

        self.stdout.write(self.style.MIGRATE_HEADING('🚀 Починаємо seed_data...'))

        created_users = []

        def make_user(username, first, last, role='user', is_staff=False, is_super=False, bio=''):
            if User.objects.filter(username=username).exists():
                u = User.objects.get(username=username)
                created_users.append(u)
                return u
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
            created_users.append(u)
            self.stdout.write(f'  ✅ Юзер: {u.get_full_name()} (@{username})')
            return u

        # ── Директор ─────────────────────────────────────────────
        director = make_user(
            'director', 'Василь', 'Петренко',
            role='admin', is_staff=True, is_super=True,
            bio='Директор Ніжинського електромеханічного коледжу. Педагог вищої категорії, відмінник освіти України.',
        )

        # ── Заступник директора ───────────────────────────────────
        vice = make_user(
            'vice_director', 'Олена', 'Коваленко',
            role='admin', is_staff=True, is_super=False,
            bio='Заступник директора з навчальної роботи. Кандидат педагогічних наук.',
        )

        # ── 50 студентів ──────────────────────────────────────────
        all_names = []
        for n in FIRST_NAMES_M:
            all_names.append((n, random.choice(LAST_NAMES), 'M'))
        for n in FIRST_NAMES_F:
            all_names.append((n, random.choice(LAST_NAMES), 'F'))
        random.shuffle(all_names)

        students = []
        for i, (fname, lname, gender) in enumerate(all_names[:50]):
            uname = f'student_{i+1}'
            spec = random.choice(SPECIALTIES)
            bio = f'Студент {random.choice(["1","2","3"])} курсу. Спеціальність: {spec}. Захоплюся технологіями та спортом.'
            s = make_user(uname, fname, lname, bio=bio)
            students.append(s)

        all_users = [director, vice] + students
        self.stdout.write(self.style.SUCCESS(f'\n👥 Створено {len(all_users)} юзерів'))

        # ── Групи ─────────────────────────────────────────────────
        group_objs = []
        for gname, gdesc in GROUPS:
            g, created = Group.objects.get_or_create(
                name=gname,
                defaults={
                    'description': gdesc,
                    'creator': director,
                    'is_private': False,
                }
            )
            if created:
                GroupMembership.objects.get_or_create(group=g, user=director, defaults={'role': 'admin'})
                self.stdout.write(f'  📁 Група: {gname}')
            group_objs.append(g)

        # Розподіляємо студентів по групах
        study_groups = group_objs[:7]
        for i, student in enumerate(students):
            g = study_groups[i % len(study_groups)]
            GroupMembership.objects.get_or_create(group=g, user=student, defaults={'role': 'member'})
            # Кожен входить в загальну групу
            GroupMembership.objects.get_or_create(group=group_objs[7], user=student, defaults={'role': 'member'})
            # Частина в спортивну і культурну
            if i % 3 == 0:
                GroupMembership.objects.get_or_create(group=group_objs[8], user=student, defaults={'role': 'member'})
            if i % 4 == 0:
                GroupMembership.objects.get_or_create(group=group_objs[9], user=student, defaults={'role': 'member'})

        self.stdout.write(self.style.SUCCESS(f'📁 Груп: {len(group_objs)}'))

        # ── Дружба між студентами ─────────────────────────────────
        pairs_done = set()
        for i, s1 in enumerate(students):
            friends_count = 0
            for s2 in random.sample(students, min(8, len(students))):
                if s1 == s2:
                    continue
                pair = tuple(sorted([s1.id, s2.id]))
                if pair in pairs_done:
                    continue
                pairs_done.add(pair)
                u1 = min(s1, s2, key=lambda u: u.id)
                u2 = max(s1, s2, key=lambda u: u.id)
                Friendship.objects.get_or_create(user1=u1, user2=u2)
                friends_count += 1
                if friends_count >= 5:
                    break

        # Підписки на директора і замдира
        for student in students:
            Follow.objects.get_or_create(follower=student, following=director)
            if random.random() > 0.4:
                Follow.objects.get_or_create(follower=student, following=vice)

        self.stdout.write(self.style.SUCCESS(f'🤝 Дружба та підписки встановлені'))

        # ── Пости ─────────────────────────────────────────────────
        post_authors = {
            'director': director,
            'vice_director': vice,
            'student': None,
        }
        post_objs = []
        days_ago = len(POSTS)
        for i, (role_key, content) in enumerate(POSTS):
            if role_key == 'student':
                author = random.choice(students)
            else:
                author = post_authors[role_key]

            # Деякі пости — в групи
            group = None
            if i % 3 == 0 and group_objs:
                group = random.choice(group_objs[:5])

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
            likers = random.sample(all_users, random.randint(2, min(15, len(all_users))))
            for liker in likers:
                Like.objects.get_or_create(post=post, user=liker)

            commenters = random.sample(all_users, random.randint(1, min(5, len(all_users))))
            for commenter in commenters:
                Comment.objects.create(
                    post=post,
                    author=commenter,
                    content=random.choice(COMMENTS),
                    created_at=post.created_at + timedelta(hours=random.randint(1, 24)),
                )

        self.stdout.write(self.style.SUCCESS(f'❤️  Лайки та коментарі додано'))

        # ── Повідомлення в чатах ──────────────────────────────────
        from chat.models import Conversation, Message

        CHAT_MSGS = [
            ('director', 'Доброго дня! Нагадую про завтрашні збори о 10:00 в актовому залі.'),
            ('vice', 'Дякую за нагадування! Всі будуть присутні.'),
            ('student', 'Добрий день! Хто знає де взяти методичку з курсової?'),
            ('student', 'В бібліотеці є, але треба замовляти заздалегідь.'),
            ('director', 'Поздравляю нашу команду з перемогою! Ви – гордість коледжу 🏆'),
            ('student', 'Хто завтра здає залік з електроніки?'),
            ('student', 'Я, і ще кілька хлопців з групи'),
            ('vice', 'Розклад екзаменів оновлено. Перевіряйте на сайті!'),
            ('student', 'Коли буде наступна практика на підприємстві?'),
            ('director', 'Практика заплановна на 15-25 листопада. Деталі в деканаті.'),
        ]

        # Головна групова розмова
        if not Conversation.objects.filter(name='НЕМК Загальний чат').exists():
            gc = Conversation.objects.create(name='НЕМК Загальний чат', is_group=True)
            for u in all_users[:20]:
                gc.participants.add(u)

            msg_authors = [director, vice] + random.sample(students, 8)
            for j, (role, text) in enumerate(CHAT_MSGS):
                if role == 'director':
                    sender = director
                elif role == 'vice':
                    sender = vice
                else:
                    sender = random.choice(students)
                Message.objects.create(
                    conversation=gc, sender=sender, content=text,
                    created_at=timezone.now() - timedelta(hours=len(CHAT_MSGS)-j),
                )

        self.stdout.write(self.style.SUCCESS('💬 Груповий чат створено'))

        self.stdout.write(self.style.SUCCESS('\n✨ seed_data завершено успішно!'))
        self.stdout.write(self.style.WARNING('\n📋 Логіни для тесту:'))
        self.stdout.write('  директор:  director / nemk1234')
        self.stdout.write('  замдир:    vice_director / nemk1234')
        self.stdout.write('  студент:   student_1 / nemk1234')
        self.stdout.write('  адмін:     admin / admin1234')
