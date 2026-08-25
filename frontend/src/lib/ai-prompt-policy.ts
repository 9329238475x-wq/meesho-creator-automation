import type { AutomationPreferences } from "../types/automation";

/**
 * Prompt policy: the prompt sent to the LLM is ALWAYS written in English.
 * The user's selected language controls ONLY the spoken dialogue/caption language,
 * never the instruction language.
 */
export function buildVideoPromptPolicy(prefs: AutomationPreferences): string {
  const languageNames: Record<AutomationPreferences["language"], string> = {
    hindi: "Hindi",
    hinglish: "Hinglish",
    english: "English",
    tamil: "Tamil",
    telugu: "Telugu",
    bengali: "Bengali",
    marathi: "Marathi",
    other: "the user's selected language",
  };

  const audience = prefs.audience === "both" ? "male and female" : prefs.audience;
  const categories = prefs.productCategories.length
    ? prefs.productCategories.join(", ")
    : "any suitable Meesho product category";

  return `
You are generating a production-ready social-commerce video package.

IMPORTANT LANGUAGE RULE:
- Write ALL instructions, scene directions, constraints, validation rules, and metadata in ENGLISH ONLY.
- The spoken dialogue/voiceover MUST be in ${languageNames[prefs.language]}.
- The caption may be in ${languageNames[prefs.language]} unless the publishing configuration says otherwise.
- Never translate the technical prompt itself into the selected language.

USER REQUIREMENTS (HARD CONSTRAINTS):
- Target audience: ${audience}.
- Allowed product categories: ${categories}.
- Daily videos requested: ${prefs.dailyVideos}.
- Use the saved user preferences exactly; do not silently change audience, category, language, or schedule intent.
- Product selection must remain within the selected category when categories are specified.
- Product visuals must match the supplied reference images exactly.
- Use ALL supplied product reference images at the video-generation stage when the provider supports them.
- Never invent product specifications, price, discount, reviews, ratings, or urgency claims.

DIALOGUE RULES:
- Create a fresh dialogue for every product/video.
- Do not reuse previous dialogue.
- Mention the verified product name or one verified distinctive feature when natural.
- Keep dialogue concise enough for the selected video duration.
- Price claims must use the latest verified product price.
- Do not claim that a price will increase unless verified price-history data supports that claim.
`.trim();
}
