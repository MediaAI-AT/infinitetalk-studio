import React from 'react';
import {staticFile} from 'remotion';
import type {CalculateMetadataFunction} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {Video} from '@remotion/media';

// Frames for the crossfade between clips (~0.33s at 30fps)
const TRANSITION_FRAMES = 10;

export type StitcherProps = {
  parts: string[];
  partDurationsInFrames: number[];
  width?: number;
  height?: number;
};

export const calculateMetadata: CalculateMetadataFunction<StitcherProps> = async ({props}) => {
  const {parts, partDurationsInFrames} = props;

  if (parts.length === 0) {
    return {durationInFrames: 1};
  }

  const totalFrames =
    partDurationsInFrames.reduce((sum, d) => sum + d, 0) -
    TRANSITION_FRAMES * Math.max(0, parts.length - 1);

  return {
    durationInFrames: Math.max(totalFrames, 1),
    width: props.width ?? 1280,
    height: props.height ?? 720,
  };
};

export const Stitcher: React.FC<StitcherProps> = ({parts, partDurationsInFrames}) => {
  return (
    <TransitionSeries>
      {parts.map((part, i) => (
        <React.Fragment key={part}>
          <TransitionSeries.Sequence durationInFrames={partDurationsInFrames[i] ?? 90}>
            <Video
              src={staticFile(part)}
              objectFit="cover"
              style={{width: '100%', height: '100%'}}
            />
          </TransitionSeries.Sequence>
          {i < parts.length - 1 && (
            <TransitionSeries.Transition
              presentation={fade()}
              timing={linearTiming({durationInFrames: TRANSITION_FRAMES})}
            />
          )}
        </React.Fragment>
      ))}
    </TransitionSeries>
  );
};
