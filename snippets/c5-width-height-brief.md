# C5 — width/height (и aspect-ratio) у изображений

Дата: 11.08.2026  
Цель: зафиксировать место под картинки, чтобы CLS оставался ~0 при правках баннеров/карточек.

## Аудит после B3

CLS уже **отличный (0 в lab 11.08; было 0.001)** — срочности нет, но страховка нужна.

На Aspro Allcorp3 большинство «картинок» — это **не `<img>`**, а:

| Тип | Как выводится | Что помогает CLS |
|-----|---------------|------------------|
| Hero «Большие баннеры» | `background-image` на `.main-slider__item` | CSS **`aspect-ratio`** на контейнере |
| Карточки услуг / проектов / новостей | `span` + `data-bg` + lazyload | CSS **aspect-ratio** / min-height |
| Логотип | `<img>` без width/height | атрибуты **width/height** |
| Логотипы клиентов | `<img class="brands-list__image">` lazy | width/height **186×90** (уже resize) |

Hero после B3: **1920×822** (и др. ~1920×718) — WebP ≤120 KB ✅

Логотип: `/upload/iblock/87e/...png` → **401×80** px, без атрибутов width/height на всех страницах.

## Почему нельзя «просто в админке галочку»

В Битрикс/Aspro нет одной кнопки «проставить width/height всем». Нужны правки **шаблона** и/или **custom CSS**.

## План (2 уровня)

### C5.1 — быстро (логотип) ~5 мин

Файл шаблона (или include логотипа), тег `<img>` логотипа добавить:

```html
width="401" height="80"
```

Где искать:
- https://a2c.by/bitrix/admin/fileman_file_edit.php?lang=ru&site=s1&path=%2Fbitrix%2Ftemplates%2Faspro-allcorp3%2Fpage_blocks%2Fheader_1.php  
  или блок логотипа в `header_*` / настройки Aspro «Логотип».

Проверка: view-source главной — у логотипа есть `width="401" height="80"`.

### C5.2 — hero + карточки через CSS (рекомендуется)

Если в Aspro есть поле **«Пользовательские стили» / custom.css**:

Путь часто:  
`/bitrix/templates/aspro-allcorp3/css/custom.css`  
или Aspro → Настройки решения → доп. CSS.

Вставить (подогнать под факт высоты баннера на десктопе):

```css
/* C5: резерв места под hero (фоны, не img) */
.banners-big .main-slider__item,
.banners-big__item {
  aspect-ratio: 1920 / 822;
}

/* карточки услуг / проектов — типовой квадрат/горизонталь Aspro; уточнить по макету */
.services-list__item-image,
.project-list__item-image {
  aspect-ratio: 16 / 10;
  display: block;
}

/* бренды клиентов */
.brands-list__image {
  width: 186px;
  height: 90px;
  object-fit: contain;
}
```

**Важно:** не ломать мобильную высоту баннера Aspro (`banners-big--adaptive-*`). Если на мобиле съедет — обернуть в `@media (min-width: 992px) { ... }` только десктоп.

### C5.3 — полноценно (разработчик)

В шаблонах компонентов (`news.list`, `banners`, header) при выводе `CFile::ResizeImageGet(..., true)` проставлять `width`/`height` в HTML.  
Это закрывает PageSpeed «Image elements do not have explicit width and height» для всех `<img>`.

## Чек-лист

- [x] C5.1/C5.2: custom.css на проде (logo + brands + hero desktop)  
- [x] Live-проверка 11.08.2026: custom.css содержит C5-блоки, файл подключён  
- [ ] C5.3 PHP width/height в компонентах — опционально (разработчик)  
- [ ] Мобильный вид баннера глазами (если aspect-ratio странный — оставить только desktop media)

## Не делаем

- Не откатываем WebP B3.  
- Не ставим width/height на `background-image` (атрибуты только у `<img>`).  
- Не трогаем демо-баннеры с «Нет».
