import React, { useCallback, useEffect, useState } from 'react';
import { Box, Container, makeStyles } from '@material-ui/core';
import Page from 'src/components/Page';
import Stats from './Stats';
import Header from './Header';
import { SOCKET_URL } from 'src/constants';
import DashboardView from './Dashbord';
import useWebSocket, { ReadyState } from 'react-use-websocket';

const useStyles = makeStyles(theme => ({
  root: {
    backgroundColor: theme.palette.background.dark,
    paddingTop: theme.spacing(3),
    paddingBottom: theme.spacing(3)
  }
}));

const AlgoView = ({
  match: {
    params: { algo, reward, expirement, checkpoint }
  }
}) => {
  const classes = useStyles();
  const [loading, setLoading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [data, setData] = useState(null);
  const [deployed, setDeployed] = useState(false);
  const [starting, setStarting] = useState(false);
  const [started, setStarted] = useState(false);
  const [paused, setPaused] = useState(false);

  const [pricesPeriod, setPricesPeriod] = useState(48);

  const {
    // sendMessage,
    sendJsonMessage,
    lastMessage,
    readyState
    //  readyState
  } = useWebSocket(socket);

  // console.log('last message =>', lastMessage);

  useEffect(() => {
    // console.log('last message =>', lastMessage);

    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      switch (data.action) {
        case 'deploy':
          // console.log('recived deployed');
          setLoading(false);
          setDeployed(true);
          break;
        case 'start':
          // console.log('recived started', data);
          setData(data);
          setStarting(false);
          setStarted(true);
          sendNextRequest();
          break;
        case 'next':
          console.log('recived next', data);
          setData(data);
          if (!paused) setTimeout(sendNextRequest, 1000);
      }
    }
  }, [lastMessage]);

  useEffect(() => {
    if (readyState == ReadyState.CONNECTING) {
      sendJsonMessage({
        deploy: true,
        algo,
        reward,
        expirement,
        checkpoint
      });
    }
  }, [readyState]);

  // console.log('data => ', data);

  const sendNextRequest = () => {
    // console.log('sending next request', socket != null);
    sendJsonMessage({
      next: true,
      price_period: pricesPeriod
    });
  };

  const sendStartRequest = () => {
    // console.log('sending next request', socket != null);
    sendJsonMessage({
      start: true,
      price_period: pricesPeriod
    });
    setStarting(true);
  };

  const startSocket = useCallback(() => {
    setSocket(SOCKET_URL + '/deploy_ws');
  }, []);

  const deploy = () => {
    setLoading(true);
    startSocket();
  };

  return (
    <Page className={classes.root} title={expirement}>
      {!deployed ? (
        <Container maxWidth="lg">
          <Header
            expirement={expirement}
            checkpoint={checkpoint}
            onDeploy={deploy}
            deploying={loading}
          />
          <Box mt={3}>
            <Stats
              expirement={expirement}
              checkpoint={checkpoint}
              algo={algo}
              reward={reward}
            />
          </Box>
        </Container>
      ) : (
        <DashboardView
          expirement={expirement}
          checkpoint={checkpoint}
          algo={algo}
          reward={reward}
          onStart={sendStartRequest}
          onPause={() => {
            setPaused(!paused);
            sendNextRequest();
          }}
          started={started}
          starting={starting}
          paused={paused}
          networths={data ? data.net_worth : []}
          labels={data ? data.labels : []}
          assetHeld={data ? data.asset_held : 0}
          balance={data ? data.balance : 0}
          prices={data ? data.prices : []}
          trades={data ? data.trades : []}
          windowStart={data ? data.window_start : 0}
          setPricesPeriod={setPricesPeriod}
        />
      )}
    </Page>
  );
};

export default AlgoView;
