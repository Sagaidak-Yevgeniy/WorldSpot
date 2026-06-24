import type { Lang } from "../types";
import { tr } from "../lib/i18n";
import { LangToggle } from "../components/ui";

interface Props {
  lang: Lang;
  onLang: (l: Lang) => void;
  onClassic: () => void;
  onRanked: () => void;
}

export function MenuScreen({ lang, onLang, onClassic, onRanked }: Props) {
  return (
    <div className="screen screen--menu">
      <div className="menu__bg" />
      <LangToggle lang={lang} onChange={onLang} />

      <header className="menu__hero">
        <div className="menu__logo">
          <span className="menu__logo-icon">🌍</span>
          <h1>WorldSpot</h1>
        </div>
        <p className="menu__tagline">{tr(lang, "tagline")}</p>
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
      </div>

      <footer className="menu__footer">{tr(lang, "footer")}</footer>
    </div>
  );
}
