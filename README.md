<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>ComIT</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: "SF Pro Text", "SF Pro Icons", "Helvetica Neue", Helvetica, sans-serif;
    background: #010101;
    color: #ffffff;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* ── Decorative blobs ── */
  .blobs {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
  }
  .blob {
    position: absolute; border-radius: 50%; opacity: .32; filter: blur(90px);
  }
  .blob-1 {
    width: 820px; height: 820px; top: -260px; right: -180px;
    background: radial-gradient(circle, #f43f5e 0%, #a855f7 60%, transparent 100%);
  }
  .blob-2 {
    width: 700px; height: 700px; bottom: -200px; left: -160px;
    background: radial-gradient(circle, #6366f1 0%, #a855f7 55%, transparent 100%);
  }

  /* ── Layout ── */
  .page { position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 64px 32px 100px; }

  /* ── Glass card ── */
  .card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 23px;
    backdrop-filter: blur(28px) saturate(120%);
    -webkit-backdrop-filter: blur(28px) saturate(120%);
    box-shadow: 0 0 40px rgba(0,0,0,0.48), inset 0 1px 0 rgba(255,255,255,0.07);
    padding: 36px 40px;
    margin-bottom: 24px;
  }

  /* ── Hero ── */
  .hero { text-align: center; padding: 80px 40px 72px; margin-bottom: 24px; }
  .hero-logo {
    display: inline-flex; align-items: center; gap: 14px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 100px; padding: 10px 24px 10px 10px;
    margin-bottom: 40px;
  }
  .hero-logo-dot {
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #f43f5e, #a855f7);
    box-shadow: 0 0 18px rgba(244,63,94,0.5);
  }
  .hero-logo-text { font-size: 18px; font-weight: 700; letter-spacing: -.3px; }

  .hero h1 {
    font-size: clamp(42px, 6vw, 72px);
    font-weight: 700;
    letter-spacing: -1.5px;
    line-height: 1.05;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #ffffff 30%, rgba(255,255,255,0.55) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero-sub {
    font-size: 18px; color: rgba(255,255,255,0.55); max-width: 500px;
    margin: 0 auto 40px; line-height: 1.55;
  }
  .hero-links { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 12px 24px; border-radius: 100px;
    font-size: 14px; font-weight: 600; text-decoration: none;
    transition: opacity .2s, transform .2s;
  }
  .btn:hover { opacity: .85; transform: translateY(-1px); }
  .btn-primary {
    background: linear-gradient(135deg, #f43f5e, #a855f7);
    color: #fff;
    box-shadow: 0 4px 24px rgba(244,63,94,0.35);
  }
  .btn-ghost {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.8);
  }

  /* ── Section heading ── */
  .section-title {
    font-size: 13px; font-weight: 600; letter-spacing: 1.4px;
    text-transform: uppercase; color: rgba(255,255,255,0.35);
    margin-bottom: 20px;
  }
  h2 {
    font-size: 26px; font-weight: 700; letter-spacing: -.5px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, #fff 50%, rgba(255,255,255,0.5));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  }

  /* ── Stack grid ── */
  .stack-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
  }
  .stack-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px 20px;
  }
  .stack-label {
    font-size: 11px; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 8px;
  }
  .stack-value { font-size: 14px; color: rgba(255,255,255,0.85); line-height: 1.5; }

  /* ── Services table ── */
  .services { display: flex; flex-direction: column; gap: 10px; }
  .service-row {
    display: flex; align-items: center; gap: 16px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 14px 18px;
  }
  .service-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #30d158, #0a84ff);
    box-shadow: 0 0 8px rgba(48,209,88,0.5);
  }
  .service-name { font-size: 14px; font-weight: 600; min-width: 130px; }
  .service-url { font-size: 13px; color: rgba(255,255,255,0.4); font-family: "SF Mono", Monaco, monospace; }

  /* ── Code block ── */
  .code-block {
    background: rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 14px 0;
    overflow-x: auto;
  }
  pre {
    font-family: "SF Mono", Monaco, "Cascadia Code", monospace;
    font-size: 13px; line-height: 1.65; color: rgba(255,255,255,0.82);
  }
  .comment { color: rgba(255,255,255,0.28); }
  .cmd { color: #30d158; }
  .flag { color: #0a84ff; }

  /* ── Repo tree ── */
  .tree { display: flex; flex-direction: column; gap: 6px; }
  .tree-row {
    display: flex; gap: 14px; align-items: baseline;
    font-family: "SF Mono", Monaco, monospace; font-size: 13px;
  }
  .tree-name { color: #0a84ff; min-width: 200px; }
  .tree-desc { color: rgba(255,255,255,0.45); font-size: 12px; }

  /* ── Env vars ── */
  .env-list { display: flex; flex-direction: column; gap: 8px; }
  .env-row {
    display: flex; align-items: baseline; gap: 12px;
    padding: 10px 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
  }
  .env-key {
    font-family: "SF Mono", Monaco, monospace; font-size: 12px;
    color: #f43f5e; min-width: 220px; flex-shrink: 0;
  }
  .env-desc { font-size: 13px; color: rgba(255,255,255,0.45); }

  /* ── Architecture ── */
  .arch-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
  }
  .arch-node {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px; padding: 14px 16px;
    font-size: 13px;
  }
  .arch-node-name { font-weight: 700; margin-bottom: 4px; font-size: 14px; }
  .arch-node-tech { font-size: 12px; color: rgba(255,255,255,0.4); line-height: 1.5; }
  .arch-node.core { background: rgba(244,63,94,0.08); border-color: rgba(244,63,94,0.25); }
  .arch-node.data { background: rgba(10,132,255,0.08); border-color: rgba(10,132,255,0.22); }
  .arch-node.ai { background: rgba(168,85,247,0.08); border-color: rgba(168,85,247,0.22); }
  .arch-node.infra { background: rgba(48,209,88,0.06); border-color: rgba(48,209,88,0.18); }

  /* ── Gradient divider ── */
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 28px 0;
  }

  /* ── Footer ── */
  .footer { text-align: center; margin-top: 60px; color: rgba(255,255,255,0.2); font-size: 13px; }
  .footer a { color: rgba(255,255,255,0.35); text-decoration: none; }
  .footer a:hover { color: rgba(255,255,255,0.6); }

  @media (max-width: 640px) {
    .page { padding: 40px 16px 80px; }
    .card { padding: 24px 20px; }
    .hero { padding: 60px 20px 52px; }
    .stack-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<div class="blobs">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
</div>

<div class="page">

  <!-- ── HERO ── -->
  <div class="card hero">
    <div class="hero-logo">
      <div class="hero-logo-dot"></div>
      <span class="hero-logo-text">ComIT</span>
    </div>
    <h1>Платформа для студентов нового поколения</h1>
    <p class="hero-sub">
      Командные проекты, хакатоны, новости, AI-ассистент и групповые чаты —
      всё в одном месте.
    </p>
    <div class="hero-links">
      <a class="btn btn-primary" href="https://comit.robofirst.ru/" target="_blank">Открыть сайт →</a>
      <a class="btn btn-ghost" href="https://www.figma.com/design/4ferZ0muDwZe9Qh8iPRtiO/%D0%A5%D0%90%D0%9A%D0%90%D0%A2%D0%9E%D0%9D?node-id=0-1" target="_blank">Figma</a>
      <a class="btn btn-ghost" href="https://docs.google.com/presentation/d/1NHAbkkhbvQBN345mIWRH_dMzHc0q7kk20pPSl6MKEZY/edit?slide=id.p#slide=id.p" target="_blank">Презентация</a>
    </div>
  </div>

  <!-- ── СТЕК ── -->
  <div class="card">
    <p class="section-title">Технологический стек</p>
    <div class="stack-grid">
      <div class="stack-item">
        <div class="stack-label">Frontend</div>
        <div class="stack-value">React 18 + Vite<br>Framer Motion · TanStack Query</div>
      </div>
      <div class="stack-item">
        <div class="stack-label">Backend</div>
        <div class="stack-value">FastAPI · Python 3.12<br>PostgreSQL 16 · Redis 7</div>
      </div>
      <div class="stack-item">
        <div class="stack-label">Чаты (QmsgCore)</div>
        <div class="stack-value">Go 1.24 · WebSocket<br>gorilla/websocket · pgx</div>
      </div>
      <div class="stack-item">
        <div class="stack-label">AI (PulseCore)</div>
        <div class="stack-value">FastAPI · MongoDB<br>RAG · async agents</div>
      </div>
      <div class="stack-item">
        <div class="stack-label">ML</div>
        <div class="stack-value">GigaChat embeddings<br>Персонализированные рекомендации</div>
      </div>
      <div class="stack-item">
        <div class="stack-label">Инфраструктура</div>
        <div class="stack-value">Docker Compose<br>Drone CI · nginx · Let's Encrypt</div>
      </div>
    </div>
  </div>

  <!-- ── АРХИТЕКТУРА ── -->
  <div class="card">
    <p class="section-title">Архитектура</p>
    <div class="arch-grid">
      <div class="arch-node core">
        <div class="arch-node-name">frontend</div>
        <div class="arch-node-tech">React SPA</div>
      </div>
      <div class="arch-node core">
        <div class="arch-node-name">backend</div>
        <div class="arch-node-tech">FastAPI · центральный API-шлюз</div>
      </div>
      <div class="arch-node data">
        <div class="arch-node-name">PostgreSQL</div>
        <div class="arch-node-tech">основная БД</div>
      </div>
      <div class="arch-node data">
        <div class="arch-node-name">Redis</div>
        <div class="arch-node-tech">кэш · очереди</div>
      </div>
      <div class="arch-node ai">
        <div class="arch-node-name">PulseCore</div>
        <div class="arch-node-tech">AI-агент · MongoDB</div>
      </div>
      <div class="arch-node ai">
        <div class="arch-node-name">ML API</div>
        <div class="arch-node-tech">GigaChat · рекомендации</div>
      </div>
      <div class="arch-node infra">
        <div class="arch-node-name">QmsgCore</div>
        <div class="arch-node-tech">Go · WebSocket-чаты</div>
      </div>
      <div class="arch-node infra">
        <div class="arch-node-name">hackathon-parser</div>
        <div class="arch-node-tech">парсер хакатонов и новостей</div>
      </div>
    </div>
    <p style="margin-top:18px; font-size:13px; color:rgba(255,255,255,0.35);">
      backend — центральный API-шлюз для всех фронтов и точка интеграции с ML, PulseCore и QmsgCore.
    </p>
  </div>

  <!-- ── БЫСТРЫЙ СТАРТ ── -->
  <div class="card">
    <p class="section-title">Быстрый старт</p>
    <div class="code-block">
<pre><span class="comment"># 1. Настрой окружение</span>
<span class="cmd">cp</span> .env.example .env

<span class="comment"># 2. Подними весь стек</span>
<span class="cmd">docker compose</span> <span class="flag">--profile</span> core up <span class="flag">-d --build</span></pre>
    </div>
    <div class="divider"></div>
    <p class="section-title">Сервисы</p>
    <div class="services">
      <div class="service-row">
        <div class="service-dot"></div>
        <div class="service-name">Frontend</div>
        <div class="service-url">http://localhost:8080</div>
      </div>
      <div class="service-row">
        <div class="service-dot"></div>
        <div class="service-name">Backend API</div>
        <div class="service-url">http://localhost:8000/docs</div>
      </div>
      <div class="service-row">
        <div class="service-dot"></div>
        <div class="service-name">Admin panel</div>
        <div class="service-url">http://localhost:8010/admin/</div>
      </div>
      <div class="service-row">
        <div class="service-dot"></div>
        <div class="service-name">Analytics</div>
        <div class="service-url">http://localhost:8081</div>
      </div>
    </div>
  </div>

  <!-- ── СТРУКТУРА ── -->
  <div class="card">
    <p class="section-title">Структура репозитория</p>
    <div class="tree">
      <div class="tree-row">
        <div class="tree-name">backend/</div>
        <div class="tree-desc">FastAPI backend, миграции Alembic, seed</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">frontend/</div>
        <div class="tree-desc">React SPA — основной интерфейс</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">frontend_analytics/</div>
        <div class="tree-desc">Аналитика университетов</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">admin-panel/</div>
        <div class="tree-desc">Django admin</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">hackathon-parser/</div>
        <div class="tree-desc">Парсер хакатонов и IT-новостей</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">ML/</div>
        <div class="tree-desc">Сервис персонализированных рекомендаций</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">PulseCore/</div>
        <div class="tree-desc">AI-агент, пайплайны, очереди задач</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">QmsgCore/</div>
        <div class="tree-desc">Групповые чаты на Go</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">openapi/</div>
        <div class="tree-desc">OpenAPI spec (авто-экспорт при старте backend)</div>
      </div>
      <div class="tree-row">
        <div class="tree-name">deploy/</div>
        <div class="tree-desc">Nginx-конфиг, прод-инструкции</div>
      </div>
    </div>
  </div>

  <!-- ── ЛОКАЛЬНАЯ РАЗРАБОТКА ── -->
  <div class="card">
    <p class="section-title">Локальная разработка</p>
    <h2 style="font-size:16px; margin-bottom:10px;">Backend</h2>
    <div class="code-block">
<pre><span class="cmd">cd</span> backend
<span class="cmd">pip install</span> -r requirements.txt -r requirements-dev.txt
<span class="cmd">alembic</span> upgrade head <span class="comment">&amp;&amp; python -m scripts.seed_db</span>
<span class="cmd">uvicorn</span> app.main:app <span class="flag">--reload</span></pre>
    </div>
    <h2 style="font-size:16px; margin-bottom:10px; margin-top:20px;">Frontend</h2>
    <div class="code-block">
<pre><span class="cmd">cd</span> frontend
<span class="cmd">npm</span> ci <span class="comment">&amp;&amp;</span> <span class="cmd">npm</span> run dev

<span class="comment"># Перегенерировать типы из OpenAPI</span>
<span class="cmd">npm</span> run generate:api</pre>
    </div>
    <p style="margin-top:14px; font-size:13px; color:rgba(255,255,255,0.35);">
      Остальные сервисы — см. README в их папках.
    </p>
  </div>

  <!-- ── ENV ── -->
  <div class="card">
    <p class="section-title">Ключевые переменные окружения</p>
    <div class="env-list">
      <div class="env-row">
        <div class="env-key">DATABASE_URL · REDIS_URL</div>
        <div class="env-desc">Подключение к PostgreSQL и Redis</div>
      </div>
      <div class="env-row">
        <div class="env-key">JWT_SECRET</div>
        <div class="env-desc">Должен совпадать с GC_JWT_SECRET в QmsgCore</div>
      </div>
      <div class="env-row">
        <div class="env-key">PULSE_CORE_BASE_URL</div>
        <div class="env-desc">URL AI-агента PulseCore</div>
      </div>
      <div class="env-row">
        <div class="env-key">QMSG_CORE_BASE_URL</div>
        <div class="env-desc">URL сервиса групповых чатов</div>
      </div>
      <div class="env-row">
        <div class="env-key">ML_SERVICE_URL</div>
        <div class="env-desc">URL ML-сервиса рекомендаций</div>
      </div>
      <div class="env-row">
        <div class="env-key">VITE_API_BASE_URL</div>
        <div class="env-desc">Задать до docker compose build frontend</div>
      </div>
      <div class="env-row">
        <div class="env-key">GIGACHAT_AUTH_KEY</div>
        <div class="env-desc">Ключ для GigaChat embeddings в ML</div>
      </div>
    </div>
  </div>

  <div class="footer">
    ComIT · ViribusHack 2025 &nbsp;·&nbsp;
    <a href="https://comit.robofirst.ru/">comit.robofirst.ru</a>
  </div>

</div>
</body>
</html>
