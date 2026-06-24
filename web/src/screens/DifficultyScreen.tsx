import type { DifficultyId, Lang } from "../types";
import { DIFFICULTY_ORDER, getDifficulty } from "../lib/difficulty";
import { tr, diffLabel, diffDesc } from "../lib/i18n";
import { GuessButton, LangToggle } from "../components/ui";

interface Props {
  lang: Lang;
  ranked: boolean;
  selected: DifficultyId;
  onSelect: (d: DifficultyId) => void;
  onPlay: () => void;
  onBack: () => void;
  onLang: (l: Lang) => void;
}

export function DifficultyScreen({ lang, ranked, selected, onSelect, onPlay, onBack, onLang }: Props) {
  return (
    <div className="screen screen--difficulty">
      <div className="menu__bg" />
      <LangToggle lang={lang} onChange={onLang} />

      <header className="difficulty__header">
        <button type="button" className="btn-ghost" onClick={onBack}>
          ← {tr(lang, "back")}
        </button>
        <h1>{tr(lang, "difficulty")}</h1>
        <p>{ranked ? tr(lang, "rankedDesc") : tr(lang, "classicDesc")}</p>
      </header>

      <div className="difficulty__grid">
        {DIFFICULTY_ORDER.map((id) => {
          const cfg = getDifficulty(id);
          const sel = id === selected;
          return (
            <button
              key={id}
              type="button"
              className={`diff-card ${sel ? "diff-card--sel" : ""}`}
              onClick={() => onSelect(id)}
            >
              <h3>{diffLabel(lang, id)}</h3>
              <p>{diffDesc(lang, id)}</p>
              <span className="diff-card__meta">
                {cfg.rounds} {tr(lang, "rounds")}
                {ranked && cfg.timerRanked ? ` · ${cfg.timerRanked}s` : ""}
              </span>
            </button>
          );
        })}
      </div>

      <div className="difficulty__play">
        <GuessButton label={tr(lang, "play")} enabled onClick={onPlay} lang={lang} />
      </div>
    </div>
  );
}
