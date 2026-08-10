<?php
if (!defined('B_PROLOG_INCLUDED') || B_PROLOG_INCLUDED !== true) {
	return;
}

global $APPLICATION;

$name = '';
$description = '';
$url = '';

// На detail.php переменная $arSection — родительский раздел, не текущая услуга.
// Поэтому GetTitle важнее, чем $arSection['NAME'].
if (!empty($arResult['NAME'])) {
	$name = trim($arResult['NAME']);
} elseif (!empty($arElement['NAME'])) {
	$name = trim($arElement['NAME']);
} else {
	$name = trim((string)$APPLICATION->GetTitle(false));
	if ($name === '') {
		$name = trim((string)$APPLICATION->GetTitle());
	}
	// section.php: если title ещё не выставлен — берём текущий раздел
	if ($name === '' && !empty($arSection['NAME'])) {
		$name = trim($arSection['NAME']);
	}
}

if (!empty($arResult['IPROPERTY_VALUES']['ELEMENT_META_DESCRIPTION'])) {
	$description = trim($arResult['IPROPERTY_VALUES']['ELEMENT_META_DESCRIPTION']);
} elseif (!empty($arResult['IPROPERTY_VALUES']['SECTION_META_DESCRIPTION'])) {
	$description = trim($arResult['IPROPERTY_VALUES']['SECTION_META_DESCRIPTION']);
} elseif (!empty($arResult['PREVIEW_TEXT'])) {
	$description = trim(HTMLToTxt($arResult['PREVIEW_TEXT']));
} elseif (!empty($arResult['DESCRIPTION'])) {
	$description = trim(HTMLToTxt($arResult['DESCRIPTION']));
} else {
	$description = trim((string)$APPLICATION->GetPageProperty('description'));
	if ($description === '' && !empty($arSection['DESCRIPTION'])) {
		$description = trim(HTMLToTxt($arSection['DESCRIPTION']));
	}
}

// URL всегда текущей страницы (на detail $arSection указывает на родителя)
$url = $APPLICATION->GetCurPage(false);
if ($url && strpos($url, 'http') !== 0) {
	$host = SITE_SERVER_NAME ?: ($_SERVER['HTTP_HOST'] ?? 'a2c.by');
	$url = 'https://' . $host . $url;
}

if ($name === '' || $url === '') {
	return;
}

$payload = [
	'@context' => 'https://schema.org',
	'@type' => 'Service',
	'name' => $name,
	'url' => $url,
	'provider' => [
		'@type' => 'Organization',
		'@id' => 'https://a2c.by/#organization',
		'name' => 'А2 Консалтинг',
		'url' => 'https://a2c.by/',
	],
	'areaServed' => [
		['@type' => 'Country', 'name' => 'BY'],
		['@type' => 'Country', 'name' => 'RU'],
	],
];

if ($description !== '') {
	$payload['description'] = $description;
}

$json = class_exists('\\Bitrix\\Main\\Web\\Json')
	? \Bitrix\Main\Web\Json::encode($payload)
	: json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

echo "\n" . '<script type="application/ld+json">' . $json . '</script>' . "\n";
