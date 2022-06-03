import React from 'react';
import {
  Avatar,
  Box,
  Breadcrumbs,
  Button,
  Card,
  CardContent,
  CardHeader,
  CircularProgress,
  Container,
  Divider,
  Grid,
  Link,
  makeStyles,
  Slider,
  Typography,
  useTheme
} from '@material-ui/core';
import { useHistory } from 'react-router';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import Label from 'src/components/Label';
import AttachMoneyIcon from '@material-ui/icons/AttachMoney';
import clsx from 'clsx';
import numeral from 'numeral';
import { coinIcon } from 'src/assets/icons';
import PerfectScrollbar from 'react-perfect-scrollbar';
import PriceChart from './charts/PriceChart';
import { PlayArrow } from '@material-ui/icons';
import PauseIcon from '@material-ui/icons/Pause';
import NetworthChart from './charts/NetworthChart';
import GraphOptions from './charts/GraphOptions';
import AssetBalanceChart from './charts/AssetBalanceChart';
// const FAKE_DATA = {
//   values: [
//     127.07,
//     126.04,
//     126.92,
//     126.89,
//     129.3,
//     129.21,
//     129.17,
//     128.86,
//     132.15,
//     132.35,
//     132.04,
//     132.46,
//     132.23,
//     133.54,
//     131.68,
//     132.53,
//     133.51,
//     133.97,
//     133.5,
//     133.49,
//     133.45,
//     132.5,
//     133.04,
//     134.35,
//     133.7,
//     133.01,
//     133.47,
//     133.34,
//     133.67,
//     133.66,
//     133.95,
//     133.91,
//     133.6,
//     134.13,
//     133.4,
//     133.77,
//     132.79,
//     132.9,
//     133.06,
//     133.26,
//     133.09
//   ],
//   labels: [
//     '2020-01-03T00:00',
//     '2020-01-03T01:00',
//     '2020-01-03T02:00',
//     '2020-01-03T03:00',
//     '2020-01-03T04:00',
//     '2020-01-03T05:00',
//     '2020-01-03T06:00',
//     '2020-01-03T07:00',
//     '2020-01-03T08:00',
//     '2020-01-03T09:00',
//     '2020-01-03T10:00',
//     '2020-01-03T11:00',
//     '2020-01-03T12:00',
//     '2020-01-03T13:00',
//     '2020-01-03T14:00',
//     '2020-01-03T15:00',
//     '2020-01-03T16:00',
//     '2020-01-03T17:00',
//     '2020-01-03T18:00',
//     '2020-01-03T19:00',
//     '2020-01-03T20:00',
//     '2020-01-03T21:00',
//     '2020-01-03T22:00',
//     '2020-01-03T23:00',
//     '2020-01-04T00:00',
//     '2020-01-04T01:00',
//     '2020-01-04T02:00',
//     '2020-01-04T03:00',
//     '2020-01-04T04:00',
//     '2020-01-04T05:00',
//     '2020-01-04T06:00',
//     '2020-01-04T07:00',
//     '2020-01-04T08:00',
//     '2020-01-04T09:00',
//     '2020-01-04T10:00',
//     '2020-01-04T11:00',
//     '2020-01-04T12:00',
//     '2020-01-04T13:00',
//     '2020-01-04T14:00',
//     '2020-01-04T15:00',
//     '2020-01-04T16:00'
//   ],
//   trades: [
//     { step: 14, amount: 245.53576539, total: 3333.33333329, type: 'buy' },
//     { step: 16, amount: 161.98003061, total: 2222.2222222, type: 'buy' },
//     { step: 17, amount: 108.22948353, total: 1481.48148155, type: 'buy' },
//     { step: 18, amount: 72.25989017, total: 987.65432093, type: 'buy' },
//     { step: 19, amount: 72.19740452, total: 987.65432096, type: 'buy' }
//   ],
//   windowStart: 0
// };

const useStyles = makeStyles(theme => ({
  cardRoot: {
    padding: theme.spacing(3),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  label: {
    marginLeft: theme.spacing(1)
  },
  avatar: {
    backgroundColor: theme.palette.secondary.main,
    color: theme.palette.secondary.contrastText,
    height: 48,
    width: 48
  },
  chart: {
    height: '100%'
  },
  controllerContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  }
}));

const MAX_SPEED = 100;
const MIN_SPEED = 2000;

const DashboardView = ({
  expirement,
  algo,
  reward,
  checkpoint,
  onStart,
  onPause,
  started,
  starting,
  paused,
  setPricesPeriod,
  simulationSpeed,
  setSimulationSpeed,
  networths = [],
  labels = [],
  assetsHeld = [],
  balances = [],
  prices = [],
  trades = [],
  windowStart = 0
}) => {
  const history = useHistory();
  const classes = useStyles();
  const theme = useTheme();

  const intialBalance = 10000;

  const currentNetworth =
    networths && networths.length > 0
      ? networths[networths.length - 1]
      : intialBalance;

  const currentPrice =
    prices && prices.length > 0 ? prices[prices.length - 1] : 0;

  const assetHeld =
    assetsHeld && assetsHeld.length > 1 ? assetsHeld[assetsHeld.length - 1] : 0;
  const balance =
    balances && balances.length > 1 ? balances[balances.length - 1] : 0;

  //   const difference =
  // networths && networths.length > 0
  //   ? (networths[networths.length - 1] / intialBalance - 1) * 100
  //   : 0;
  const difference = (currentNetworth / intialBalance - 1) * 100;

  const CoinIcon = coinIcon(expirement);

  return (
    <Container maxWidth={false}>
      <Grid container spacing={3} justify="space-between">
        <Grid item>
          <Breadcrumbs
            separator={<NavigateNextIcon fontSize="small" />}
            aria-label="breadcrumb"
          >
            <Link variant="body1" color="inherit" onClick={() => history.go(0)}>
              {algo}
            </Link>
            <Link variant="body1" color="inherit" onClick={() => history.go(0)}>
              {reward}
            </Link>
          </Breadcrumbs>
          <Typography variant="h3" color="textPrimary">
            {expirement + ' ' + checkpoint}
          </Typography>
        </Grid>
        <Grid item className={classes.controllerContainer}>
          <Box>
            <Typography id="discrete-slider" color="textPrimary" gutterBottom>
              Simulation speed
            </Typography>

            <Slider
              width={300}
              style={{ width: '20rem' }}
              aria-labelledby="discrete-slider"
              valueLabelDisplay="auto"
              valueLabelFormat={value =>
                `${((MAX_SPEED + MIN_SPEED - value) / 1000).toFixed(1)} s`
              }
              marks
              disabled={!paused || starting}
              value={MAX_SPEED + MIN_SPEED - simulationSpeed}
              onChange={(event, newValue) =>
                setSimulationSpeed(MAX_SPEED + MIN_SPEED - newValue)
              }
              step={100}
              min={MAX_SPEED}
              max={MIN_SPEED}
            />
          </Box>

          <Box ml={4}>
            {!started ? (
              <Button
                variant="outlined"
                color="primary"
                onClick={onStart}
                disabled={starting}
                startIcon={
                  starting && <CircularProgress size={24} color="inherit" />
                }
              >
                Start
              </Button>
            ) : (
              <Button
                variant="outlined"
                color="primary"
                onClick={onPause}
                startIcon={paused ? <PlayArrow /> : <PauseIcon />}
              >
                {paused ? 'Continue' : 'Pause'}
              </Button>
            )}
          </Box>
        </Grid>
      </Grid>

      <Grid container spacing={1} style={{ marginTop: theme.spacing(2) }}>
        <Grid item lg={4} sm={6} xs={12}>
          <Card className={clsx(classes.cardRoot)}>
            <Box flexGrow={1}>
              <Typography
                component="h3"
                gutterBottom
                variant="overline"
                color="textSecondary"
              >
                Net worth
              </Typography>
              <Box display="flex" alignItems="center" flexWrap="wrap">
                <Typography variant="h3" color="textPrimary">
                  {numeral(currentNetworth).format('$0,0.00')}
                </Typography>
                <Label
                  className={classes.label}
                  color={difference > 0 ? 'success' : 'error'}
                >
                  {difference > 0 ? '+' : ''}
                  {numeral(difference).format('0.0')}
                </Label>
              </Box>
            </Box>
            <Avatar className={classes.avatar}>
              <AttachMoneyIcon />
            </Avatar>
          </Card>
        </Grid>
        <Grid item lg={4} sm={6} xs={12}>
          <Card className={clsx(classes.cardRoot)}>
            <Box flexGrow={1}>
              <Typography
                component="h3"
                gutterBottom
                variant="overline"
                color="textSecondary"
              >
                Asset held
              </Typography>
              <Box display="flex" alignItems="center" flexWrap="wrap">
                <Typography variant="h3" color="textPrimary">
                  {assetHeld > 0.5
                    ? numeral(assetHeld).format('0,0.00')
                    : numeral(10000.123).format('0,0.00')}{' '}
                  (
                  {assetHeld > 0.5
                    ? numeral(assetHeld * currentPrice).format('$0,0.00')
                    : numeral(10000.123).format('0,0.00$')}
                  )
                </Typography>
              </Box>
            </Box>
            {/* <Avatar className={classes.avatar}> */}
            <CoinIcon size={50} />
            {/* </Avatar> */}
          </Card>
        </Grid>
        <Grid item lg={4} sm={6} xs={12}>
          <Card className={clsx(classes.cardRoot)}>
            <Box flexGrow={1}>
              <Typography
                component="h3"
                gutterBottom
                variant="overline"
                color="textSecondary"
              >
                Balance
              </Typography>
              <Box display="flex" alignItems="center" flexWrap="wrap">
                <Typography variant="h3" color="textPrimary">
                  {balance > 0.5
                    ? numeral(balance).format('$0,0.00')
                    : numeral(0).format('$0,0.00')}
                </Typography>
              </Box>
            </Box>
            <Avatar className={classes.avatar}>
              <AttachMoneyIcon />
            </Avatar>
          </Card>
        </Grid>
        <Grid item lg={3} sm={6} xs={12}>
          {/* <RoiPerCustomer /> */}
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardHeader
              action={<GraphOptions onPeriodChange={setPricesPeriod} />}
              title="Asset price + Actions over time"
            />
            <Divider />
            <CardContent>
              <PerfectScrollbar>
                <Box height={500} minWidth={500}>
                  <PriceChart
                    className={classes.chart}
                    data={{
                      values: prices,
                      labels: labels,
                      trades: trades,
                      windowStart: windowStart
                    }}
                    // data={FAKE_DATA}
                    label={'Net Worth'}
                    color={theme.palette.secondary.main}
                  />
                </Box>
              </PerfectScrollbar>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader
              action={<GraphOptions onPeriodChange={setPricesPeriod} />}
              title="Networth"
            />
            <Divider />
            <CardContent>
              <PerfectScrollbar>
                <Box height={375} minWidth={500}>
                  <NetworthChart
                    className={classes.chart}
                    data={{ values: networths, labels: labels }}
                    // data={FAKE_DATA}
                    label={'Networth over time'}
                    color={theme.palette.error.main}
                  />
                </Box>
              </PerfectScrollbar>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} lg={6}>
          <Card>
            <CardHeader title="Asset/Balance ratio" />
            <Divider />
            <CardContent>
              <PerfectScrollbar>
                <Box height={375} minWidth={500}>
                  <AssetBalanceChart
                    className={classes.chart}
                    // data={{
                    //   values: {
                    //     assetsHeld: FAKE_DATA.values.slice(0, 10),
                    //     balances: FAKE_DATA.values.slice(0, 10)
                    //   },
                    //   labels: FAKE_DATA.labels
                    // }}
                    data={{ values: { assetsHeld, balances }, labels: labels }}
                    label={'Asset/Balance ratio'}
                    color={theme.palette.error.main}
                  />
                </Box>
              </PerfectScrollbar>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardView;
