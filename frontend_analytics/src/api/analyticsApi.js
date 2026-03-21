import { apiBase } from "./client.js";

/**
 * @typedef {Object} UniversityListItem
 * @property {string} id
 * @property {string} name
 * @property {number} studentsCount
 * @property {number} projectsCount
 * @property {number} articlesCount
 * @property {number} eventParticipationsCount
 * @property {number} joinRequestsCount
 * @property {number} [interestsCount]
 */

/**
 * @typedef {Object} UniversityDashboard
 * @property {string} universityId
 * @property {string} universityName
 * @property {number} studentsCount
 * @property {number} eventParticipationsCount
 * @property {number} joinRequestsCount
 * @property {number} projectsCount
 * @property {number} articlesCount
 * @property {number} [interestsCount]
 */

/**
 * List universities with aggregated metrics.
 * @returns {Promise<UniversityListItem[]>}
 */
export async function fetchUniversities() {
  const res = await fetch(`${apiBase}/api/analytics/universities`);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

/**
 * Get dashboard for a single university.
 * @param {string} universityId
 * @returns {Promise<UniversityDashboard | null>}
 */
export async function fetchUniversityDashboard(universityId) {
  const res = await fetch(
    `${apiBase}/api/analytics/universities/${encodeURIComponent(universityId)}/dashboard`,
  );
  if (res.status === 404) return null;
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

/**
 * Get export URL for a CSV endpoint.
 * @param {string} universityId
 * @param {string} type - students | participation | projects | articles | join-requests
 * @returns {string}
 */
export function getExportUrl(universityId, type) {
  const path = `/api/analytics/universities/${encodeURIComponent(universityId)}/export/${type}`;
  return `${apiBase}${path}`;
}

/**
 * Trigger CSV download via fetch (blob) to avoid CORS issues with direct links.
 * @param {string} universityId
 * @param {string} type - students | participation | projects | articles | join-requests
 * @param {string} filename - e.g. "students.csv"
 */
export async function downloadExport(universityId, type, filename) {
  const url = getExportUrl(universityId, type);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition");
  const match = disposition && disposition.match(/filename="?([^";\n]+)"?/);
  const finalFilename = match ? match[1] : filename;

  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = finalFilename;
  a.click();
  URL.revokeObjectURL(a.href);
}
