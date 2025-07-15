# Молодёжная молекулярная лаборатория ЮГУ - Веб-приложение для обработки данных секвенирования

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

Веб-приложение для обработки данных метабаркодинга с использованием удалённых вычислительных ресурсов университета.

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.10+
- Установленные системные зависимости (для Linux):
  ```bash
  sudo apt-get install python3-pip python3-venv
  ```

### Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-username/SUMMER_WEB.git
   cd SUMMER_WEB
   ```

2. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ИЛИ для Windows:
   venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустите приложение:
   ```bash
   uvicorn backend.main:app --reload
   ```

5. Откройте в браузере:
   ```
   http://localhost:8000
   ```

## 📂 Структура проекта
```
SUMMER_WEB/
├── backend/               # FastAPI приложение
│   ├── main.py           # Основной файл
│   ├── config.py         # Конфигурации
│   └── dependencies.py   # Зависимости
├── static/               # CSS/JS/Изображения
├── templates/            # HTML шаблоны (Jinja2)
└── requirements.txt      # Зависимости Python
```

## 🌟 Веб-интерфейс  
- 📤**Интерактивный интерфейс** для учёных (без командной строки).  
- ⚙️**Загрузка файлов и настройка параметров** через браузер.  
- 📨**Обработка задач** на сервере ЮГУ.  

## 🛠 Технологии
| Компонент       | Технологии                          |
|-----------------|-------------------------------------|
| **Бэкенд**      | FastAPI, Python 3.10+               |
| **Фронтенд**    | Jinja2, HTML5, CSS3, JavaScript     |
| **Сервер**      | Uvicorn (ASGI)                      |
| **Разработка**  | Visual Studio Code                  |

## 📝 Лицензия
Проект распространяется под лицензией [MIT](LICENSE).

## ✉️ Контакты
**Молодёжная молекулярная лаборатория ЮГУ**  
📧 Сайт: https://fungariumysu.org/moleculab/ 