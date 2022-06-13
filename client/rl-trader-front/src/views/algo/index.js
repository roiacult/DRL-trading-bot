import React, { useEffect } from 'react';
import { CircularProgress } from '@material-ui/core';
import { useState } from 'react';
import Algo from 'src/views/algo/AlgoView';

export const AlgoPage = ({
  match: {
    params: { algo, reward, expirement, checkpoint }
  }
}) => {
  const [refresh, setRefresh] = useState(true);

  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

  useEffect(() => {
    setRefresh(true);
  }, [algo, reward, expirement, checkpoint]);

  const updateState = async () => {
    await delay(100);
    setRefresh(false);
  };

  if (refresh) updateState();

  console.log('refresh => ', refresh);

  return (
    <>
      {!refresh ? (
        <Algo
          algo={algo}
          reward={reward}
          expirement={expirement}
          checkpoint={checkpoint}
        />
      ) : (
        <CircularProgress />
      )}
    </>
  );
};

export default AlgoPage;
