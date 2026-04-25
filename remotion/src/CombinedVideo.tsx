import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame, interpolate, Easing} from 'remotion';
import {Video} from '@remotion/media';
import {staticFile} from 'remotion';
import type {CalculateMetadataFunction} from 'remotion';
import {Scene1, Scene2, Scene3, Scene4, Scene5, Scene6, Scene7, Scene8} from './BRoll';

// ─── Constants ────────────────────────────────────────────────────────────────
const FADE = 20;       // 0.67s crossfade
const SCENE_FRAMES = 180; // 6s per b-roll scene

// ─── Timings for KI News (script 4) — 30fps ──────────────────────────────────
// Part durations from stitch output:
//   Part1: 48.8s=1464f  Part2: 51.0s=1530f  Part3: 51.7s=1551f
//   Part4: 43.9s=1317f  Part5: 24.7s=741f
// TRANSITION_FRAMES=10 between each part
const PART2_START = 1454;   // 1464 - 10
const PART3_START = 2974;   // 1454 + 1530 - 10
const PART4_START = 4515;   // 2974 + 1551 - 10
const PART5_START = 5822;   // 4515 + 1317 - 10
const TOTAL_FRAMES = 6563;  // 5822 + 741

// B-roll scene placements — timed to match spoken content
const BROLL_PLACEMENTS: { from: number; Scene: React.FC }[] = [
  { from: 90,              Scene: Scene1 }, // 3s   "Die Filmindustrie stirbt gerade"
  { from: 780,             Scene: Scene2 }, // 26s  iQiyi stats
  { from: PART2_START,     Scene: Scene3 }, // 48s  Nadou Pro launch date
  { from: PART2_START + 600, Scene: Scene4 }, // 68s features list
  { from: PART3_START,     Scene: Scene5 }, // 99s  Peter Pau / 16 Filme
  { from: PART3_START + 870, Scene: Scene6 }, // 128s CEO 400 Titel
  { from: PART4_START,     Scene: Scene7 }, // 150s BIFF
  { from: PART5_START,     Scene: Scene8 }, // 194s Fazit
];

// ─── B-Roll overlay with smooth crossfade ────────────────────────────────────
const BRollLayer: React.FC<{ from: number; SceneComp: React.FC }> = ({ from, SceneComp }) => {
  const frame = useCurrentFrame();
  const rel = frame - from;

  const opacity = interpolate(
    rel,
    [0, FADE, SCENE_FRAMES - FADE, SCENE_FRAMES],
    [0, 1, 1, 0],
    {
      easing: Easing.inOut(Easing.quad),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <Sequence from={from} durationInFrames={SCENE_FRAMES} premountFor={30}>
      <AbsoluteFill style={{ opacity }}>
        <SceneComp />
      </AbsoluteFill>
    </Sequence>
  );
};

// ─── Props ───────────────────────────────────────────────────────────────────
export type CombinedVideoProps = {
  mainVideo: string;
  totalFrames: number;
};

export const calculateMetadata: CalculateMetadataFunction<CombinedVideoProps> = ({ props }) => ({
  durationInFrames: props.totalFrames,
  width: 1280,
  height: 720,
});

// ─── Main composition ─────────────────────────────────────────────────────────
export const CombinedVideo: React.FC<CombinedVideoProps> = ({ mainVideo }) => {
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {/* Layer 1: Talking head — always visible, audio always on */}
      <Video
        src={staticFile(mainVideo)}
        style={{ width: '100%', height: '100%' }}
      />

      {/* Layer 2: B-Roll overlays at specific timestamps */}
      {BROLL_PLACEMENTS.map(({ from, Scene: SceneComp }) => (
        <BRollLayer key={from} from={from} SceneComp={SceneComp} />
      ))}
    </AbsoluteFill>
  );
};
