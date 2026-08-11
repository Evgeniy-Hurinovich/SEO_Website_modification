# E4 — перелинковка кейсы ↔ услуги

Дата: 11.08.2026  
Цель: контекстные ссылки с коммерческими анкорами между P1-кластерами (DWH, BI, AI) и релевантными проектами.

## Аудит (до правок)

| Направление | Сейчас |
|-------------|--------|
| Услуги → кейсы | В тексте E1–E3 **нет** блока «Примеры проектов»; в HTML только меню/футер на разделы `/projects/{отрасль}/` |
| Кейсы → услуги | В теле кейса **нет** явных ссылок на `/services/dwh/`, `/services/bi/`, `/services/ai-rpa-ml/`; внизу Aspro показывает карточку дочерней услуги |

## План (2 шага)

### Шаг A — услуги (3 правки)

Вставить HTML-блок **перед** `<h2>Смежные услуги>` в поле «Описание» раздела:

| Кластер | IB 42, ID | Файл вставки |
|---------|-----------|--------------|
| DWH | 94 | `snippets/e4-dwh-projects-insert.html` |
| BI | 95 | `snippets/e4-bi-projects-insert.html` |
| AI/RPA/ML | 97 | `snippets/e4-ai-projects-insert.html` |

Админка (пример DWH):  
https://a2c.by/bitrix/admin/iblock_section_edit.php?IBLOCK_ID=42&type=aspro_allcorp3_content&lang=ru&ID=94

### Шаг B — проекты (9 правок)

**Важно:** проекты — это **элементы** инфоблока (не разделы, как услуги).  
Нужный список: **не** `iblock_admin.php`, а:

**https://a2c.by/bitrix/admin/iblock_list_admin.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru**

Меню: **Контент → Проекты** (IB 41) → список элементов.

Как редактировать:
1. В списке найти проект по названию (фильтр **«Название»** сверху) **или** открыть прямую ссылку ниже.
2. Клик по названию → форма элемента.
3. Прокрутить до блока **«Детальное описание»** (это текст вкладки «Описание» на сайте).
4. **Не путать** с «Описание для анонса» — это короткий текст в карточке.
5. В **конец** «Детального описания» вставить абзац из `snippets/e4-project-service-appends.html`.
6. Режим **HTML** (или визуальный редактор — в конец текста).

| id блока | Проект | ID | Прямая ссылка в админку |
|----------|--------|-----|-------------------------|
| `dwh-5element` | DWH «5 элемент» | 481 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=481 |
| `dwh-beltamozh` | DWH Белтаможсервис | 429 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=429 |
| `dwh-lakehouse` | Data Lakehouse | 557 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=557 |
| `dwh-telecom` | DWH телеком (обследование) | 588 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=588 |
| `bi-gippo` | BI «ГИППО» | 600 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=600 |
| `bi-governor` | BI «Рабочее место губернатора» | 618 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=618 |
| `bi-tri-tseny` | BI «Три цены» | 264 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=264 |
| `ai-gippo` | AI «ГИППО» | 263 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=263 |
| `ai-tender` | AI тендерная экспертиза | 591 | https://a2c.by/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=41&type=aspro_allcorp3_content&lang=ru&ID=591 |

**Лайфхак:** откройте кейс на сайте (например https://a2c.by/projects/riteyl-e-kom/ai-assistent-dlya-seti-magazinov-gippo/) — в верхней панели Bitrix должна быть кнопка **«Изменить элемент»** / карандаш.

После правок — сброс кеша: https://a2c.by/bitrix/admin/cache.php?lang=ru

## Проверка

- На `/services/dwh/`, `/services/bi/`, `/services/ai-rpa-ml/` — блок H2 «Примеры проектов» с 3–4 ссылками на конкретные кейсы.
- На каждом из 9 кейсов — в тексте ссылка на родительский кластер услуги с коммерческим анкором.
