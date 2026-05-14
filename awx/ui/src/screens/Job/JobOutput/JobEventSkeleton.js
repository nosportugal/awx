import React, { useEffect } from 'react';
import {
  JobEventLine,
  JobEventLineToggle,
  JobEventLineNumber,
  JobEventLineText,
} from './shared';

function JobEventSkeletonContent({ contentLength }) {
  return (
    <JobEventLineText>
      <span className="content">{' '.repeat(contentLength)}</span>
    </JobEventLineText>
  );
}

function JobEventSkeleton({ counter, contentLength, style, measure, registerChild }) {
  useEffect(() => {
    measure();
  }, [measure]);

  return (
    counter > 1 && (
      <div style={style}>
        <div ref={registerChild}>
          <JobEventLine key={counter}>
            <JobEventLineToggle />
            <JobEventLineNumber />
            <JobEventSkeletonContent contentLength={contentLength} />
          </JobEventLine>
        </div>
      </div>
    )
  );
}

export default JobEventSkeleton;
