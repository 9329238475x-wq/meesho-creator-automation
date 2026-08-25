import { useState } from "react";
import type { AutomationPreferences, Audience, VideoLanguage } from "../../types/automation";

const categories = ["Saree", "Kurti", "Suit", "Shirt", "T-Shirt", "Jeans", "Pants", "Shoes", "Dress", "Jewellery", "Bags", "Beauty", "Home", "Other"];

interface Props {
  initial: AutomationPreferences;
  onSave: (preferences: AutomationPreferences) => void;
}

export function AutomationSetup({ initial, onSave }: Props) {
  const [prefs, setPrefs] = useState(initial);

  const toggleCategory = (category: string) => {
    setPrefs((current) => ({
      ...current,
      productCategories: current.productCategories.includes(category)
        ? current.productCategories.filter((item) => item !== category)
        : [...current.productCategories, category],
    }));
  };

  const save = () => {
    if (!prefs.scheduleTimes.length || !prefs.audience || !prefs.language) return;
    onSave({ ...prefs, onboardingCompleted: true });
  };

  return (
    <section aria-labelledby="setup-title" className="mx-auto max-w-3xl space-y-8 p-6">
      <header>
        <p className="text-sm font-medium">First-time setup</p>
        <h1 id="setup-title" className="text-3xl font-bold">Set up your daily video automation</h1>
        <p className="mt-2 text-sm opacity-70">These preferences are hard constraints for the automation pipeline.</p>
      </header>

      <label className="block space-y-2">
        <span className="font-medium">Videos per day</span>
        <input
          type="number"
          min={1}
          max={10}
          value={prefs.dailyVideos}
          onChange={(e) => setPrefs({ ...prefs, dailyVideos: Number(e.target.value) })}
          className="w-full rounded-lg border p-3"
        />
      </label>

      <label className="block space-y-2">
        <span className="font-medium">Daily processing time</span>
        <input
          type="time"
          value={prefs.scheduleTimes[0] ?? "06:00"}
          onChange={(e) => setPrefs({ ...prefs, scheduleTimes: [e.target.value] })}
          className="w-full rounded-lg border p-3"
        />
      </label>

      <fieldset className="space-y-3">
        <legend className="font-medium">Product audience</legend>
        <div className="grid gap-3 sm:grid-cols-3">
          {(["male", "female", "both"] as Audience[]).map((value) => (
            <label key={value} className="cursor-pointer rounded-lg border p-3">
              <input type="radio" name="audience" checked={prefs.audience === value} onChange={() => setPrefs({ ...prefs, audience: value })} />
              <span className="ml-2 capitalize">{value}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset className="space-y-3">
        <legend className="font-medium">Product categories (optional)</legend>
        <p className="text-sm opacity-70">Leave empty for all supported categories.</p>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              type="button"
              key={category}
              aria-pressed={prefs.productCategories.includes(category)}
              onClick={() => toggleCategory(category)}
              className="rounded-full border px-3 py-2 text-sm"
            >
              {category}
            </button>
          ))}
        </div>
      </fieldset>

      <label className="block space-y-2">
        <span className="font-medium">Video language</span>
        <select
          value={prefs.language}
          onChange={(e) => setPrefs({ ...prefs, language: e.target.value as VideoLanguage })}
          className="w-full rounded-lg border p-3"
        >
          <option value="hindi">Hindi</option>
          <option value="hinglish">Hinglish</option>
          <option value="english">English</option>
          <option value="tamil">Tamil</option>
          <option value="telugu">Telugu</option>
          <option value="bengali">Bengali</option>
          <option value="marathi">Marathi</option>
          <option value="other">Other</option>
        </select>
      </label>

      <button type="button" onClick={save} className="w-full rounded-lg border px-4 py-3 font-semibold">
        Save preferences & continue
      </button>
    </section>
  );
}
