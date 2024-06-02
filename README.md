# HackVladivostokBack
## 🚂Запуск решения по кейсу РЖД🚂
---
#### Запуск сервера

1. Клонируем репозиторий⬇️:  
```bash
git clone <(https://github.com/MrApple100/HackVladivostokBack.git)>
```
2. По данной [ссылке](https://disk.yandex.ru/d/Dyl0HzUJcWzqbw) на Яндекс.Диск'е лежит обученная модель нейронной сети. Ее необходимо скачать и положить в папку `static` проекта🎞️.
3. Необходимо создать виртуальное окружение💻: 
```bash
python -m venv venv
```
4.  Теперь его нужно активировать✨
```bash
.\venv\Scripts\activate
```
5. Осталось только запустить сервер и все готово🎉!
```python
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```


