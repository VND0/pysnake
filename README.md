# PySnake - змейка на pygame
## Описание
Игра, в которой персонаж, управляемый игроком, — змейка — стремится набрать максимальное количество очков,
поедая яблоки и вишни. Игра происходит на клетчатом поле и продолжается до победы (для этого нужно заполнить змейкой весь экран) или поражения 
(оно случается, когда змейка сталкивается с границей поля, препятствием или самой собой). В базе данных хранятся лучший
и последний результаты. Предусмотрены два уровня сложности. Управление осуществляется мышью.

## Техническое задание

### Игра

-[ ] Начальный экран:
    - [x] Информация об игре
    - [x] Лучший результат, последний результат
    - [ ] Выбор уровня сложности (карты)
    - [x] Кнопка начала игры
    - [x] Получение данных с БД
- [ ] Игра:
    - [ ] Два уровня
    - [ ] Счет
    - [x] Игровое поле
    - [x] Змейка
    - [x] Яблоки, ягоды
    - [x] Движение змейки
    - [ ] Управление мышью
    - [ ] Обработка окончания игры
    - [x] Кнопка закрытия игры
- [ ] Финальный экран
    - [ ] Результат последней игры
    - [ ] Обновление данных в БД
    - [ ] Кнопка возврата на начальный экран

### База данных

- [x] Таблица с колонками last_score, best_score