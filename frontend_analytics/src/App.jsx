import { useState } from "react";
import { UniversitySelector } from "./components/UniversitySelector/UniversitySelector";
import { Dashboard } from "./components/Dashboard/Dashboard";

export default function App() {
  const [universityId, setUniversityId] = useState(null);

  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">ComIT — Аналитика университетов</h1>
        <UniversitySelector
          value={universityId}
          onChange={setUniversityId}
        />
      </header>
      <main className="app__main">
        <Dashboard universityId={universityId} />
      </main>
    </div>
  );
}
