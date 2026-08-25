export type Audience = "male" | "female" | "both";
export type VideoLanguage = "hindi" | "hinglish" | "english" | "tamil" | "telugu" | "bengali" | "marathi" | "other";

export interface AutomationPreferences {
  dailyVideos: number;
  scheduleTimes: string[];
  audience: Audience;
  productCategories: string[];
  language: VideoLanguage;
  onboardingCompleted: boolean;
}

export const DEFAULT_PREFERENCES: AutomationPreferences = {
  dailyVideos: 1,
  scheduleTimes: ["06:00"],
  audience: "female",
  productCategories: [],
  language: "hindi",
  onboardingCompleted: false,
};
