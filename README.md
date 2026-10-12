# Лабораторная работа № 1
## Индексирование и булев информационный поиск

**Вариант 1:** `random_state = 101`, `N = 500`, `min_len = 2`, оператор — `AND`.

## Цель

Освоить построение инвертированного индекса и выполнение булевых запросов `AND` и `OR` по текстовому корпусу.

## Краткая теория

Инвертированный индекс связывает термин со списком документов, в которых он встречается:

```text
magic -> {2, 8, 15}
world -> {2, 5, 8, 21}
```

Для булевого поиска используются операции над этими списками:

```text
magic AND world -> {2, 8}
magic OR world  -> {2, 5, 8, 15, 21}
```

`AND` вычисляет пересечение списков документов, `OR` — объединение.

В работе индекс строится по объединённому тексту:

```text
title + description + genre
```

Текст переводится в нижний регистр, разбивается на токены и фильтруется по минимальной длине `min_len`.

## Материалы

- Семинар: https://github.com/BosenkoTM/IIR/tree/main/seminars/03-indexing
- Исходное задание: https://github.com/BosenkoTM/IIR/tree/main/homeworks/hw1-boolean-retrieval

## Инструменты

Python 3. Внешние библиотеки для `solution.py` не требуются.

---

## 1. Подготовка корпуса

После выполнения семинара 02 в корне репозитория должен находиться файл:

```text
~/Downloads/IIR/result.jsonl
```

Перейдите в корень репозитория:

```bash
cd ~/Downloads/IIR
```

Проверьте файл:

```bash
ls -lh result.jsonl
wc -l result.jsonl
```

Для варианта 1 необходимо не менее `500` документов.

Если ранее собиралась только категория `Fantasy`, в:

```text
seminars/02-scraping/main.py
```

замените начальный адрес на:

```python
seed_urls = [
    'https://books.toscrape.com/index.html'
]
```

Удалите старый результат:

```bash
rm -f result.jsonl
```

и снова выполните:

```bash
python seminars/02-scraping/main.py
```

---

## 2. Создание каталога лабораторной работы

Находясь в:

```text
~/Downloads/IIR
```

создайте отдельный каталог:

```bash
mkdir -p lab/lab_01
```

Скопируйте туда полученный корпус:

```bash
cp result.jsonl lab/lab_01/
```

Проверьте:

```bash
ls -lh lab/lab_01/
```

На этом этапе должно быть:

```text
lab/lab_01/
└── result.jsonl
```

---

## 3. Копирование файлов лабораторной работы

Распакуйте архив с решением `lab_01_solution.zip`.

Например, если архив скачан в `~/Downloads`:

```bash
cd ~/Downloads
unzip lab_01_solution.zip
```

После распаковки появится каталог:

```text
~/Downloads/lab_01/
```

В нём находятся:

```text
README.md
solution.py
lab_01.ipynb
requirements.txt
```

Теперь скопируйте эти файлы в каталог лабораторной работы:

```bash
cp ~/Downloads/lab_01/README.md ~/Downloads/IIR/lab/lab_01/
cp ~/Downloads/lab_01/solution.py ~/Downloads/IIR/lab/lab_01/
cp ~/Downloads/lab_01/lab_01.ipynb ~/Downloads/IIR/lab/lab_01/
cp ~/Downloads/lab_01/requirements.txt ~/Downloads/IIR/lab/lab_01/
```

Или одной командой:

```bash
cp ~/Downloads/lab_01/{README.md,solution.py,lab_01.ipynb,requirements.txt} \
   ~/Downloads/IIR/lab/lab_01/
```

Проверьте итог:

```bash
ls -lh ~/Downloads/IIR/lab/lab_01/
```

Должны быть:

```text
README.md
solution.py
lab_01.ipynb
requirements.txt
result.jsonl
```

---

## 4. Переход в каталог лабораторной работы

Перейдите:

```bash
cd ~/Downloads/IIR/lab/lab_01
```

Проверьте:

```bash
pwd
```

Ожидаемый каталог:

```text
~/Downloads/IIR/lab/lab_01
```

Все дальнейшие команды выполняются отсюда.

> Если виртуальное окружение `(02-scraping)` уже активно, создавать новое окружение не требуется.

Проверить активный Python можно командой:

```bash
which python
python --version
```

---

## 5. Выполнение лабораторной работы

Запустите вариант 1:

```bash
python solution.py result.jsonl \
  --n 500 \
  --random-state 101 \
  --min-len 2 \
  --operator AND \
  --query "magic world"
```

Программа выполняет:

```text
result.jsonl
      ↓
подготовка текста
      ↓
токенизация
      ↓
выборка 500 документов
      ↓
построение инвертированного индекса
      ↓
AND-поиск
      ↓
измерение времени
```

После выполнения в текущем каталоге появятся:

```text
index.json
lab_01_results.json
```

---

## 6. Проверка результата

Посмотрите итоговый отчёт:

```bash
cat lab_01_results.json
```

Первые элементы индекса:

```bash
head -n 30 index.json
```

Для сравнения выполните запрос `OR`:

```bash
python solution.py result.jsonl \
  --n 500 \
  --random-state 101 \
  --min-len 2 \
  --operator OR \
  --query "magic world"
```

После выполнения сравните количество найденных документов.

## Результаты

| Показатель | Значение |
|---|---:|
| Число документов `N` | 500 |
| `random_state` | 101 |
| `min_len` | 2 |
| Размер словаря | |
| Время построения индекса, с | |
| Число результатов `AND` | |
| Время `AND`, с | |
| Число результатов `OR` | |
| Время `OR`, с | |

## Вывод

Инвертированный индекс позволяет выполнять поиск без последовательного просмотра всего корпуса. Оператор `AND` формирует более узкую выдачу, поскольку документ должен содержать все термины запроса. Оператор `OR` формирует более широкую выдачу, поскольку достаточно наличия хотя бы одного термина.

## Итоговая структура

После выполнения лабораторной:

```text
IIR/
└── lab/
    └── lab_01/
        ├── README.md
        ├── solution.py
        ├── lab_01.ipynb
        ├── requirements.txt
        ├── result.jsonl
        ├── index.json
        └── lab_01_results.json
```

Именно каталог:

```text
lab/lab_01/
```

размещается в GitHub.
