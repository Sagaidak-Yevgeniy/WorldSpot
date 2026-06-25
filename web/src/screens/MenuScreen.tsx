import type { Lang } from "../types";
import { tr } from "../lib/i18n";
import { AUTHOR } from "../lib/site";
import { LangToggle } from "../components/ui";

interface Props {
  lang: Lang;
  poolSize: number;
  onLang: (l: Lang) => void;
  onClassic: () => void;
  onRanked: () => void;
  onDuel: () => void;
}

export function MenuScreen({ lang, poolSize, onLang, onClassic, onRanked, onDuel }: Props) {
  return (
    <div className="screen screen--menu">
      <div className="menu__bg" aria-hidden>
        <div className="menu__bg-aurora" />
        <div className="menu__bg-grid" />
        <div className="menu__bg-horizon" />
        <div className="menu__bg-glow" />
      </div>
      <LangToggle lang={lang} onChange={onLang} />

      <header className="menu__hero">
        <div className="menu__logo">
          <span className="menu__logo-icon">🌍</span>
          <h1>WorldSpot</h1>
        </div>
        <p className="menu__tagline">{tr(lang, "tagline")}</p>
        {poolSize > 0 && (
          <p className="menu__pool-badge">
            {poolSize} {tr(lang, "citiesInPool")}
          </p>
        )}
      </header>

      <div className="menu__cards">
        <button type="button" className="menu-card menu-card--primary" onClick={onClassic}>
          <div className="menu-card__glow" />
          <div className="menu-card__content">
            <span className="menu-card__emoji">🧭</span>
            <div>
              <h2>{tr(lang, "classic")}</h2>
              <p>{tr(lang, "classicDesc")}</p>
            </div>
            <span className="menu-card__arrow">→</span>
          </div>
        </button>

        <button type="button" className="menu-card" onClick={onRanked}>
          <div className="menu-card__content">
            <span className="menu-card__emoji">⏱️</span>
            <div>
              <h2>{tr(lang, "ranked")}</h2>
              <p>{tr(lang, "rankedDesc")}</p>
            </div>
            <span className="menu-card__arrow">→</span>
          </div>
        </button>

        <button type="button" className="menu-card menu-card--duel" onClick={onDuel}>
          <div className="menu-card__content">
            <span className="menu-card__emoji">⚔️</span>
            <div>
              <h2>{tr(lang, "duel")}</h2>
              <p>{tr(lang, "duelMenuDesc")}</p>
            </div>
            <span className="menu-card__arrow">→</span>
          </div>
        </button>
      </div>

      <footer className="menu__footer">
        {tr(lang, "footerAuthor")}{" "}
        <a
          className="menu__footer-link"
          href={AUTHOR.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          {AUTHOR.name}
        </a>
      </footer>
    </div>
  );
}
