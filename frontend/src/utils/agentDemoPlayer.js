/**
 * Последовательное воспроизведение сценария агента (запись на курс).
 * @param {Array<{ action: string, target?: string, value?: string, delay_after_ms?: number, params?: object }>} actions
 * @param {{ navigateTo: (path: string) => void }} ctx
 */
export async function runAgentDemoActions(actions, { navigateTo }) {
  const delay = (ms) => new Promise((r) => setTimeout(r, Math.max(0, ms ?? 600)));

  const queryTarget = (target) => {
    if (!target || typeof target !== "string") return null;
    const safe = String(target).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
    return document.querySelector(`[data-agent-target="${safe}"]`);
  };

  const clearHighlights = () => {
    document.querySelectorAll(".agent-demo-highlight").forEach((el) => {
      el.classList.remove("agent-demo-highlight");
    });
  };

  const typeSlow = async (el, text) => {
    if (!el || typeof text !== "string") return;
    el.focus();
    el.value = "";
    el.dispatchEvent(new Event("input", { bubbles: true }));
    for (let i = 0; i < text.length; i += 1) {
      el.value += text[i];
      el.dispatchEvent(new Event("input", { bubbles: true }));
      await delay(42);
    }
  };

  for (const step of actions) {
    const after = typeof step.delay_after_ms === "number" ? step.delay_after_ms : 800;

    switch (step.action) {
      case "navigate": {
        const rawPath = step.params?.path;
        if (typeof rawPath === "string" && navigateTo) {
          const path = rawPath.startsWith("#") ? rawPath.slice(1) : rawPath;
          navigateTo(path.startsWith("/") ? path : `/${path}`);
        }
        await delay(after);
        break;
      }
      case "wait": {
        await delay(after);
        break;
      }
      case "scroll_to": {
        const el = queryTarget(step.target);
        el?.scrollIntoView({ behavior: "smooth", block: "center" });
        await delay(after);
        break;
      }
      case "focus": {
        const el = queryTarget(step.target);
        el?.focus({ preventScroll: false });
        await delay(after);
        break;
      }
      case "type": {
        const el = queryTarget(step.target);
        if (el && "value" in el) {
          await typeSlow(el, String(step.value ?? ""));
        }
        await delay(after);
        break;
      }
      case "click": {
        const el = queryTarget(step.target);
        el?.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));
        await delay(after);
        break;
      }
      case "highlight": {
        clearHighlights();
        const el = queryTarget(step.target);
        el?.classList.add("agent-demo-highlight");
        await delay(after);
        el?.classList.remove("agent-demo-highlight");
        break;
      }
      default:
        await delay(after);
    }
  }

  clearHighlights();
}
