import React from 'react';
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Series,
  AbsoluteFill,
} from 'remotion';

// ─── Design tokens ───────────────────────────────────────────────────────────
const BG = '#05050f';
const BLUE = '#00d4ff';
const PURPLE = '#8b5cf6';
const WHITE = '#ffffff';
const GRAY = '#8892a4';

// ─── Helpers ─────────────────────────────────────────────────────────────────
function fadeIn(frame: number, fps: number, delay = 0, duration = 0.6) {
  return interpolate(frame, [delay * fps, (delay + duration) * fps], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
}

function slideUp(frame: number, fps: number, delay = 0, duration = 0.5) {
  const sp = spring({ frame: frame - delay * fps, fps, config: { damping: 20, stiffness: 80 } });
  return interpolate(sp, [0, 1], [40, 0]);
}

// ─── Shared layout ────────────────────────────────────────────────────────────
const Scene: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      background: BG,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '80px',
      fontFamily: "'Inter', 'Segoe UI', sans-serif",
      overflow: 'hidden',
    }}
  >
    {/* subtle grid */}
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px)`,
        backgroundSize: '60px 60px',
      }}
    />
    {/* top accent line */}
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: `linear-gradient(90deg, ${PURPLE}, ${BLUE})`,
      }}
    />
    {children}
  </AbsoluteFill>
);

const Tag: React.FC<{ label: string; opacity: number }> = ({ label, opacity }) => (
  <div
    style={{
      opacity,
      fontSize: 18,
      fontWeight: 600,
      letterSpacing: '0.2em',
      textTransform: 'uppercase',
      color: BLUE,
      marginBottom: 24,
    }}
  >
    {label}
  </div>
);

const Headline: React.FC<{ text: string; opacity: number; translateY: number; size?: number }> = ({
  text, opacity, translateY, size = 72,
}) => (
  <div
    style={{
      opacity,
      transform: `translateY(${translateY}px)`,
      fontSize: size,
      fontWeight: 800,
      color: WHITE,
      lineHeight: 1.15,
      textAlign: 'center',
      maxWidth: 1000,
    }}
  >
    {text}
  </div>
);

const Sub: React.FC<{ text: string; opacity: number }> = ({ text, opacity }) => (
  <div
    style={{
      opacity,
      fontSize: 28,
      color: GRAY,
      textAlign: 'center',
      marginTop: 24,
      maxWidth: 900,
      lineHeight: 1.5,
    }}
  >
    {text}
  </div>
);

// ─── Scene 1: Die Filmindustrie stirbt ───────────────────────────────────────
export const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Scene>
      <Tag label="Breaking" opacity={fadeIn(frame, fps, 0)} />
      <Headline
        text="Die Filmindustrie, wie wir sie kennen, stirbt gerade."
        opacity={fadeIn(frame, fps, 0.2)}
        translateY={slideUp(frame, fps, 0.2)}
        size={64}
      />
      <Sub text="Nicht irgendwann. Jetzt." opacity={fadeIn(frame, fps, 1.0)} />
    </Scene>
  );
};

// ─── Scene 2: iQiyi Stats ─────────────────────────────────────────────────
export const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const count = Math.floor(
    interpolate(frame, [0.5 * fps, 2.5 * fps], [0, 107], { extrapolateRight: 'clamp' })
  );

  return (
    <Scene>
      <Tag label="iQiyi" opacity={fadeIn(frame, fps, 0)} />
      <div
        style={{
          opacity: fadeIn(frame, fps, 0.3),
          transform: `translateY(${slideUp(frame, fps, 0.3)}px)`,
          fontSize: 120,
          fontWeight: 900,
          background: `linear-gradient(135deg, ${BLUE}, ${PURPLE})`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          lineHeight: 1,
        }}
      >
        {count} Mio.
      </div>
      <Sub text="zahlende Abonnenten — Chinas größte Streamingplattform" opacity={fadeIn(frame, fps, 1.2)} />
    </Scene>
  );
};

// ─── Scene 3: Nadou Pro Launch ────────────────────────────────────────────────
export const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Scene>
      <Tag label="30. März 2026" opacity={fadeIn(frame, fps, 0)} />
      <Headline
        text="Nadou Pro"
        opacity={fadeIn(frame, fps, 0.3)}
        translateY={slideUp(frame, fps, 0.3)}
        size={110}
      />
      <div
        style={{
          opacity: fadeIn(frame, fps, 0.8),
          fontSize: 28,
          color: BLUE,
          marginTop: 16,
          letterSpacing: '0.05em',
          textAlign: 'center',
        }}
      >
        Chinas erstes K I-System für professionelle Film- & TV-Produktion
      </div>
    </Scene>
  );
};

// ─── Scene 4: Features ────────────────────────────────────────────────────────
export const FEATURES = ['Drehbuch', 'Charakterdesign', 'Storyboard', 'Art Direction', 'Visual Effects', 'Tongestaltung'];

export const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Scene>
      <Tag label="End-to-End K I Workflow" opacity={fadeIn(frame, fps, 0)} />
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '20px 32px',
          justifyContent: 'center',
          maxWidth: 1000,
          marginTop: 16,
        }}
      >
        {FEATURES.map((f, i) => {
          const delay = 0.3 + i * 0.2;
          return (
            <div
              key={f}
              style={{
                opacity: fadeIn(frame, fps, delay),
                transform: `translateY(${slideUp(frame, fps, delay)}px)`,
                padding: '16px 32px',
                borderRadius: 12,
                border: `1px solid ${BLUE}44`,
                background: `${BLUE}0a`,
                fontSize: 28,
                fontWeight: 600,
                color: WHITE,
              }}
            >
              {f}
            </div>
          );
        })}
      </div>
      <Sub text="Alles in einem System — ohne Plattformwechsel" opacity={fadeIn(frame, fps, 1.6)} />
    </Scene>
  );
};

// ─── Scene 5: 16 Filme ────────────────────────────────────────────────────────
export const Scene5: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const genres = ['Science-Fiction', 'Fantasy', 'Historische Dramen', 'Zeitgenössisch'];
  return (
    <Scene>
      <Tag label="Peter Pau × iQiyi AI Theater" opacity={fadeIn(frame, fps, 0)} />
      <div
        style={{
          opacity: fadeIn(frame, fps, 0.3),
          transform: `translateY(${slideUp(frame, fps, 0.3)}px)`,
          fontSize: 140,
          fontWeight: 900,
          background: `linear-gradient(135deg, ${BLUE}, ${PURPLE})`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          lineHeight: 1,
        }}
      >
        16
      </div>
      <div style={{ opacity: fadeIn(frame, fps, 0.8), fontSize: 32, color: WHITE, fontWeight: 700 }}>
        neue Filmwerke — komplett mit Nadou Pro produziert
      </div>
      <div
        style={{
          display: 'flex',
          gap: 20,
          marginTop: 28,
          flexWrap: 'wrap',
          justifyContent: 'center',
        }}
      >
        {genres.map((g, i) => (
          <div
            key={g}
            style={{
              opacity: fadeIn(frame, fps, 1.2 + i * 0.15),
              fontSize: 20,
              color: BLUE,
              padding: '8px 20px',
              borderRadius: 8,
              border: `1px solid ${BLUE}55`,
            }}
          >
            {g}
          </div>
        ))}
      </div>
    </Scene>
  );
};

// ─── Scene 6: 400 Titel ───────────────────────────────────────────────────────
export const Scene6: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const count = Math.floor(
    interpolate(frame, [0.4 * fps, 2.0 * fps], [0, 400], { extrapolateRight: 'clamp' })
  );

  return (
    <Scene>
      <Tag label="CEO Gong Yu" opacity={fadeIn(frame, fps, 0)} />
      <div
        style={{
          opacity: fadeIn(frame, fps, 0.3),
          fontSize: 180,
          fontWeight: 900,
          background: `linear-gradient(135deg, ${PURPLE}, ${BLUE})`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          lineHeight: 1,
        }}
      >
        {count}
      </div>
      <div style={{ opacity: fadeIn(frame, fps, 0.5), fontSize: 34, color: WHITE, fontWeight: 700 }}>
        neue Titel für 2026
      </div>
      <Sub
        text="Kein einziges Wort darüber, was mit den Menschen passiert."
        opacity={fadeIn(frame, fps, 1.5)}
      />
    </Scene>
  );
};

// ─── Scene 7: BIFF ────────────────────────────────────────────────────────────
export const Scene7: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Scene>
      <Tag label="16. Pekinger Filmfestival" opacity={fadeIn(frame, fps, 0)} />
      <Headline
        text="Offizieller K I-Produktionsagent des Festivals"
        opacity={fadeIn(frame, fps, 0.3)}
        translateY={slideUp(frame, fps, 0.3)}
        size={58}
      />
      <Sub text="Die Filmelite Chinas feiert dieses Tool auf dem roten Teppich." opacity={fadeIn(frame, fps, 1.2)} />
    </Scene>
  );
};

// ─── Scene 8: Fazit ───────────────────────────────────────────────────────────
export const Scene8: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Scene>
      <div
        style={{
          opacity: fadeIn(frame, fps, 0.2),
          transform: `translateY(${slideUp(frame, fps, 0.2)}px)`,
          fontSize: 56,
          fontWeight: 800,
          color: WHITE,
          textAlign: 'center',
          lineHeight: 1.3,
        }}
      >
        K I ist nicht die Zukunft
        <br />
        <span
          style={{
            background: `linear-gradient(90deg, ${BLUE}, ${PURPLE})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          der Filmbranche.
        </span>
      </div>
      <div
        style={{
          opacity: fadeIn(frame, fps, 1.2),
          transform: `translateY(${slideUp(frame, fps, 1.2)}px)`,
          fontSize: 56,
          fontWeight: 800,
          color: WHITE,
          textAlign: 'center',
          marginTop: 20,
        }}
      >
        K I{' '}
        <span
          style={{
            background: `linear-gradient(90deg, ${PURPLE}, ${BLUE})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          ist die Gegenwart.
        </span>
      </div>
    </Scene>
  );
};

// ─── Root B-Roll composition ──────────────────────────────────────────────────
const SCENE_FRAMES = 180; // 6s per scene at 30fps

export const BRoll: React.FC = () => {
  const scenes = [Scene1, Scene2, Scene3, Scene4, Scene5, Scene6, Scene7, Scene8];
  return (
    <Series>
      {scenes.map((SceneComp, i) => (
        <Series.Sequence key={i} durationInFrames={SCENE_FRAMES}>
          <SceneComp />
        </Series.Sequence>
      ))}
    </Series>
  );
};

export const BROLL_DURATION = 180 * 8; // 1440 frames = 48s
