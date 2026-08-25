import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { AutomationSetup } from "./components/onboarding/AutomationSetup";
import { DEFAULT_PREFERENCES, type AutomationPreferences } from "./types/automation";
import "./styles.css";

const nav = ["Overview", "Products", "Trends", "Videos", "Schedule", "Connections", "Settings"];

function App() {
  const [prefs, setPrefs] = useState<AutomationPreferences>(() => {
    const saved = localStorage.getItem("automation_preferences");
    return saved ? JSON.parse(saved) : DEFAULT_PREFERENCES;
  });
  const [active, setActive] = useState("Overview");

  const save = (next: AutomationPreferences) => {
    setPrefs(next);
    localStorage.setItem("automation_preferences", JSON.stringify(next));
  };

  if (!prefs.onboardingCompleted) return <AutomationSetup initial={prefs} onSave={save} />;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">M</span><div><strong>Creator Auto</strong><small>Meesho automation</small></div></div>
        <nav>{nav.map((item) => <button className={active === item ? "nav-item active" : "nav-item"} onClick={() => setActive(item)} key={item}>{item}</button>)}</nav>
        <div className="side-footer"><span className="status-dot"/> Automation ready</div>
      </aside>
      <main className="main">
        <header className="topbar"><div><p className="eyebrow">CONTROL CENTER</p><h1>{active}</h1></div><button className="profile">Creator account</button></header>
        <section className="content">
          {active === "Overview" && <Overview prefs={prefs} />}
          {active === "Products" && <Panel title="Product research" text="AI will research eligible products using your saved audience and category constraints." />}
          {active === "Trends" && <Panel title="Trend research" text="Daily trend signals and recent trend history will appear here." />}
          {active === "Videos" && <Panel title="Video pipeline" text="Veo 3 generation status, generated reels and history will appear here." />}
          {active === "Schedule" && <Schedule prefs={prefs} onSave={save} />}
          {active === "Connections" && <Connections />}
          {active === "Settings" && <AutomationSetup initial={prefs} onSave={save} />}
        </section>
      </main>
    </div>
  );
}

function Overview({ prefs }: { prefs: AutomationPreferences }) {
  return <>
    <div className="hero-card"><div><span className="pill">● DAILY AUTOMATION</span><h2>Your next video is scheduled.</h2><p>AI will follow your saved preferences without silently changing the audience, category or language.</p></div><div className="next-time">{prefs.scheduleTimes[0] || "06:00"}<small>next run</small></div></div>
    <div className="stats"><Stat title="Videos / day" value={String(prefs.dailyVideos)} /><Stat title="Audience" value={prefs.audience} /><Stat title="Language" value={prefs.language} /><Stat title="Categories" value={prefs.productCategories.length ? String(prefs.productCategories.length) : "All"} /></div>
    <div className="grid-two"><Panel title="Pipeline" text="Trend → Product → Images → ChatGPT prompt → Veo 3 video + voice → Meesho / Instagram" /><Panel title="Preference lock" text="Saved preferences are treated as hard constraints. Change them from Settings." /></div>
  </>;
}
function Stat({ title, value }: { title: string; value: string }) { return <div className="stat"><span>{title}</span><strong>{value}</strong></div>; }
function Panel({ title, text }: { title: string; text: string }) { return <div className="panel"><h3>{title}</h3><p>{text}</p><span className="muted">Waiting for backend connection</span></div>; }
function Schedule({ prefs, onSave }: { prefs: AutomationPreferences; onSave: (p: AutomationPreferences) => void }) { return <div className="panel"><h2>Schedule</h2><p>Choose when the daily automation starts.</p><input type="time" value={prefs.scheduleTimes[0] || "06:00"} onChange={(e) => onSave({ ...prefs, scheduleTimes: [e.target.value] })}/></div>; }
function Connections() { return <div className="grid-two"><Panel title="Meesho Creator Club" text="Browser session connection will be configured here."/><Panel title="Instagram" text="Browser session connection will be configured here."/></div>; }

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
