import { assets } from "../assets";

/** Разделитель в `library_article.description`: краткое описание + полный текст. */
export const ARTICLE_BODY_SEPARATOR = "\n\n---\n\n";

export function buildArticleDescriptionForApi(summary, content) {
  const s = (summary ?? "").trim();
  const c = (content ?? "").trim();
  return `${s}${ARTICLE_BODY_SEPARATOR}${c}`;
}

export function parseStoredArticleDescription(description) {
  const raw = (description ?? "").trim();
  if (!raw) {
    return { summary: "", content: "" };
  }
  if (raw.includes(ARTICLE_BODY_SEPARATOR)) {
    const [summary, ...rest] = raw.split(ARTICLE_BODY_SEPARATOR);
    return { summary: summary.trim(), content: rest.join(ARTICLE_BODY_SEPARATOR).trim() };
  }
  return { summary: raw, content: "" };
}

/**
 * Каталог тегов из статей бандла: совпадение по `id` или по тексту label (без #), без учёта регистра.
 * @param {Array<{ tags?: Array<{ id: string; label: string }> }>} articles
 */
export function buildTagIdLookupFromArticles(articles) {
  /** @type {Map<string, string>} */
  const map = new Map();
  for (const article of articles || []) {
    for (const t of article.tags || []) {
      if (t.id) {
        map.set(String(t.id).toLowerCase(), t.id);
      }
      const label = (t.label || "").replace(/^#/, "").trim().toLowerCase();
      if (label) {
        map.set(label, t.id);
      }
    }
  }
  return map;
}

/**
 * @param {string[]} userTags - слова из поля «теги» (без обязательного совпадения с каталогом)
 * @param {Map<string, string>} lookup - из `buildTagIdLookupFromArticles`
 */
export function resolveTagIdsFromUserTags(userTags, lookup) {
  const ids = [];
  const seen = new Set();
  for (const raw of userTags || []) {
    const key = String(raw).replace(/^#/, "").trim().toLowerCase();
    if (!key) {
      continue;
    }
    const id = lookup.get(key);
    if (id && !seen.has(id)) {
      seen.add(id);
      ids.push(id);
    }
  }
  return ids;
}

/** Формат для `ArticleReaderPage` / `ArticleMode` из ответа `GET /api/library` → `articles[]`. */
export function mapApiLibraryArticleToReaderArticle(article) {
  const { summary, content } = parseStoredArticleDescription(article.description);
  const textForParagraphs = (content || summary || "").trim();
  const paragraphs = textForParagraphs
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean)
    .slice(0, 40);
  const points = (content || summary || "")
    .split(/[.!?]\s+/)
    .map((p) => p.trim())
    .filter(Boolean)
    .slice(0, 5)
    .map((p) => (p.endsWith(".") ? p : `${p}.`));

  return {
    title: article.title,
    updatedLabel: "На платформе",
    viewsLabel: "—",
    paragraphs: paragraphs.length ? paragraphs : [summary || article.title],
    points: points.length ? points : ["Материал из библиотеки."],
    heroImageUrl: assets.posterTechConf,
    relatedCourseSlug: "machine-learning-from-zero"
  };
}

export function buildLibraryArticleCreateBody({
  id,
  title,
  summary,
  content,
  tagIds,
  authorName,
  authorAvatarUrl
}) {
  return {
    id,
    title,
    description: buildArticleDescriptionForApi(summary, content),
    authorName,
    authorAvatarUrl,
    tagIds: tagIds ?? []
  };
}
