import type { Lang } from "../types";

interface Props {
  label: string;
  enabled: boolean;
  onClick: () => void;
  lang: Lang;
}

export function GuessButton({ label, enabled, onClick }: Props) {
  return (
    <button type="button" className={`guess-btn ${enabled ? "guess-btn--on" : ""}`} disabled={!enabled} onClick={onClick}>
      {label}
    </button>
  );
}

export function LangToggle({ lang, onChange }: { lang: Lang; onChange: (l: Lang) => void }) {
  const next: Record<Lang, Lang> = { ru: "en", en: "kk", kk: "ru" };
  return (
    <button type="button" className="lang-btn" onClick={() => onChange(next[lang])} aria-label="Language">
      {lang.toUpperCase()}
    </button>
  );
}
