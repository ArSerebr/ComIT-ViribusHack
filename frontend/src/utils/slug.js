/**
 * Кириллица → латиница и ASCII-slug для hash-маршрутов (как на backend `app.core.slug`).
 * Иначе в URL попадает `%D0%...` и ломаются ссылки.
 */

const CYR_TO_LAT = {
  а: "a",
  б: "b",
  в: "v",
  г: "g",
  д: "d",
  е: "e",
  ё: "e",
  ж: "zh",
  з: "z",
  и: "i",
  й: "y",
  к: "k",
  л: "l",
  м: "m",
  н: "n",
  о: "o",
  п: "p",
  р: "r",
  с: "s",
  т: "t",
  у: "u",
  ф: "f",
  х: "h",
  ц: "ts",
  ч: "ch",
  ш: "sh",
  щ: "sch",
  ъ: "",
  ы: "y",
  ь: "",
  э: "e",
  ю: "yu",
  я: "ya",
  і: "i",
  ї: "yi",
  є: "ye",
  ґ: "g",
  ў: "u",
  җ: "zh",
  қ: "k",
  ң: "n",
  ү: "u",
  ұ: "u",
  һ: "h",
  ә: "a",
  ө: "o"
};

export function transliterateCyrillicToLatin(text) {
  let out = "";
  for (const ch of text) {
    const mapped = CYR_TO_LAT[ch.toLowerCase()];
    out += mapped !== undefined ? mapped : ch;
  }
  return out;
}

/** Slug из [a-z0-9-], до 48 символов; пустая строка если нечего взять. */
export function createSlug(value) {
  if (value === undefined || value === null) {
    return "";
  }
  const raw = String(value).trim();
  if (!raw) {
    return "";
  }
  let t = transliterateCyrillicToLatin(raw).toLowerCase();
  t = t.replace(/[^a-z0-9]+/g, "-");
  t = t.replace(/-+/g, "-").replace(/^-|-$/g, "");
  return t.slice(0, 48);
}
