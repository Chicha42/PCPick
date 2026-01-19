# PCPick

Веб-сервис, разработанный для автоматизированного подбора ключевых комплектующих персонального компьютера под заданный бюджет пользователя. Система решает проблему технической совместимости компонентов и помогает найти наиболее производительное решение, основываясь на реальных рыночных ценах и мировых рейтингах мощности. Сервис также позволяет отслеживать динамику цен с помощью интерактивных графиков и сохранять удачные конфигурации в личном профиле

**Ссылка на рабочий проект:** [https://pcpick.jgroup.top](https://pcpick.jgroup.top)

## Стек технологий
*   **Backend:** Python 3.13, Django 6.0
*   **Data Science / Parsing:** BeautifulSoup4, Requests, LXML, Plotly
*   **Frontend:** Bootstrap 5, CSS3, Montserrat Fonts, HTML5
*   **DevOps / Deploy:** Docker, Docker-compose, Cron

## Архитектура проекта
Проект разделен на два основных модуля для обеспечения чистоты кода и разделения ответственности:
*   **Components (`components/`):** Отвечает за хранение данных о комплектующих, историю цен и логику парсинга. Включает в себя кастомные Management-команды для ежедневного обновления БД
*   **Configurator (`configurator/`):** Содержит бизнес-логику подбора сборки (алгоритм совместимости), систему визуализации графиков Plotly и управление профилем пользователя
*   **Static (`static/`):** Глобальные стили и ресурсы оформления в едином дизайн-коде

## Интерфейс сервиса

![Главная страница](https://raw.githubusercontent.com/Chicha42/PCPick/main/static/images/readme/home.png)
*Главная страница: ввод бюджета и работающее меню*

![Результат подбора](https://raw.githubusercontent.com/Chicha42/PCPick/main/static/images/readme/build.png)
*Карточки комплектующих сборки с описанием и интерактивными графиками цен*

![Сохранённые сборки](https://raw.githubusercontent.com/Chicha42/PCPick/main/static/images/readme/builds.png)
*Карточки сохранённых сборок с возможностью посмотреть детали и удалить их*

## Как запустить проект локально
1. **Клонируйте репозиторий:**
   ```bash
   git clone [https://github.com/Chicha42/PCPick](https://github.com/Chicha42/PCPick)
   ```
2. **Создайте и активируйте виртуальное окружение:**
   ```bash
   cd PCPick
   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   .\venv\Scripts\activate   # для Windows
   ```
3. **Установка зависимостей и настройка:**
   ```bash
   pip install -r requirements.txt
   # Создайте файл .env в корне проекта и добавьте:
   # SECRET_KEY=ваш_ключ
   ```
4. **Выполните миграции:**
   ```bash
   python manage.py migrate
   ```
5. **Создайте администратора:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Наполните базу данных актуальными данными через парсер:**
   ```bash
   python manage.py parse_hardware
   ```
7. **Запустите сервер:**
   ```bash
   python manage.py runserver
   ```
8. **Откройте проект в браузере:**
   Перейдите по ссылке: http://127.0.0.1:8000/
