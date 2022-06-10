import React, { useEffect, useState } from 'react';
import { CircularProgress } from '@material-ui/core';
import AlgoView from 'src/views/algo/AlgoView';

const AlgoPage = ({
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
        <AlgoView
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
