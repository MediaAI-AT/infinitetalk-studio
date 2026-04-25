import React from 'react';
import {Composition} from 'remotion';
import {Stitcher, calculateMetadata} from './Stitcher';
import type {StitcherProps} from './Stitcher';
import {BRoll, BROLL_DURATION} from './BRoll';
import {CombinedVideo, calculateMetadata as combinedMeta} from './CombinedVideo';
import type {CombinedVideoProps} from './CombinedVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Stitcher"
        component={Stitcher}
        durationInFrames={300}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{
          parts: [] as string[],
          partDurationsInFrames: [] as number[],
        } satisfies StitcherProps}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="BRoll"
        component={BRoll}
        durationInFrames={BROLL_DURATION}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="CombinedVideo"
        component={CombinedVideo}
        durationInFrames={6563}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{
          mainVideo: '4-final.mp4',
          totalFrames: 6563,
        } satisfies CombinedVideoProps}
        calculateMetadata={combinedMeta}
      />
    </>
  );
};
