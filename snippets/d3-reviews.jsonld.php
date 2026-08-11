<?php
/**
 * D3: JSON-LD Review (+ AggregateRating) для списка отзывов Aspro
 *
 * Куда подключать (в КОНЕЦ файла, в PHP-блоке):
 *   шаблон списка отзывов — обычно:
 *   /bitrix/templates/aspro-allcorp3/components/bitrix/news.list/review-list-inner/template.php
 *   или рядом (list-inner / reviews-list) — смотрим по папке news.list
 *
 * Подключение:
 *   <?php include $_SERVER['DOCUMENT_ROOT'].'/include/reviews_jsonld.php'; ?>
 *
 * Не вставлять в footer — иначе Review на всём сайте.
 *
 * Ожидание по Google: звёзды в выдаче Google по «своим» отзывам о себе
 * часто не показывают (self-serving). Разметка всё равно полезна для Яндекса
 * и связки с Organization (D1). Ставить только реальные отзывы с сайта.
 */
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) {
	return;
}

// Не дублировать разметку при ajax-подгрузке списка
if (!empty($arParams['IS_AJAX'])) {
	return;
}

if (empty($arResult['ITEMS']) || !is_array($arResult['ITEMS'])) {
	return;
}

$reviews = [];
$ratings = [];

foreach ($arResult['ITEMS'] as $item) {
	$name = trim((string)($item['NAME'] ?? ''));
	if ($name === '') {
		continue;
	}

	$body = '';
	if (!empty($item['PREVIEW_TEXT'])) {
		$body = trim(HTMLToTxt($item['PREVIEW_TEXT']));
	} elseif (!empty($item['DETAIL_TEXT'])) {
		$body = trim(HTMLToTxt($item['DETAIL_TEXT']));
	}
	if ($body === '') {
		continue;
	}

	$date = '';
	if (!empty($item['ACTIVE_FROM'])) {
		$ts = MakeTimeStamp($item['ACTIVE_FROM']);
		if ($ts) {
			$date = date('Y-m-d', $ts);
		}
	} elseif (!empty($item['DATE_ACTIVE_FROM'])) {
		$ts = MakeTimeStamp($item['DATE_ACTIVE_FROM']);
		if ($ts) {
			$date = date('Y-m-d', $ts);
		}
	}

	$ratingValue = null;
	// Типичные поля Aspro / кастом
	foreach (['RATING', 'GRADE', 'OCENKA', 'STARS'] as $code) {
		if (!empty($item['PROPERTIES'][$code]['VALUE'])) {
			$raw = $item['PROPERTIES'][$code]['VALUE'];
			if (is_array($raw)) {
				$raw = reset($raw);
			}
			$raw = preg_replace('/[^\d.]/', '', (string)$raw);
			if ($raw !== '' && is_numeric($raw)) {
				$ratingValue = (float)$raw;
				break;
			}
		}
		if (!empty($item['DISPLAY_PROPERTIES'][$code]['VALUE'])) {
			$raw = $item['DISPLAY_PROPERTIES'][$code]['VALUE'];
			if (is_array($raw)) {
				$raw = reset($raw);
			}
			$raw = preg_replace('/[^\d.]/', '', (string)$raw);
			if ($raw !== '' && is_numeric($raw)) {
				$ratingValue = (float)$raw;
				break;
			}
		}
	}

	// Если в карточке всегда 5 залитых звёзд, а свойства нет — не выдумываем рейтинг
	$review = [
		'@type' => 'Review',
		'author' => [
			'@type' => 'Person',
			'name' => $name,
		],
		'reviewBody' => $body,
		'itemReviewed' => [
			'@type' => 'Organization',
			'@id' => 'https://a2c.by/#organization',
			'name' => 'А2 Консалтинг',
			'url' => 'https://a2c.by/',
		],
	];

	if ($date !== '') {
		$review['datePublished'] = $date;
	}

	if ($ratingValue !== null && $ratingValue > 0) {
		if ($ratingValue > 5) {
			$ratingValue = 5.0;
		}
		$review['reviewRating'] = [
			'@type' => 'Rating',
			'ratingValue' => $ratingValue,
			'bestRating' => 5,
			'worstRating' => 1,
		];
		$ratings[] = $ratingValue;
	}

	$reviews[] = $review;
}

if (!$reviews) {
	return;
}

$graph = $reviews;

if (count($ratings) > 0) {
	$graph[] = [
		'@type' => 'Organization',
		'@id' => 'https://a2c.by/#organization',
		'name' => 'А2 Консалтинг',
		'url' => 'https://a2c.by/',
		'aggregateRating' => [
			'@type' => 'AggregateRating',
			'ratingValue' => round(array_sum($ratings) / count($ratings), 1),
			'reviewCount' => count($ratings),
			'bestRating' => 5,
			'worstRating' => 1,
		],
	];
}

$payload = [
	'@context' => 'https://schema.org',
	'@graph' => $graph,
];

$json = class_exists('\\Bitrix\\Main\\Web\\Json')
	? \Bitrix\Main\Web\Json::encode($payload)
	: json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

echo "\n" . '<script type="application/ld+json">' . $json . '</script>' . "\n";
