/* eslint-disable no-use-before-define */
import React, { useEffect, useState } from 'react';
import { useLocation, matchPath, Link as RouterLink } from 'react-router-dom';
import PerfectScrollbar from 'react-perfect-scrollbar';
import PropTypes from 'prop-types';
import {
  Avatar,
  Box,
  Divider,
  Drawer,
  List,
  ListSubheader,
  Typography,
  makeStyles,
  CircularProgress,
  Button
} from '@material-ui/core';
import { Layers as LayersIcon } from 'react-feather';
import API from 'src/Api';
import NavItem from './NavItem';
import { coinIcon } from '../../../assets/icons';

function renderNavItems({ items, pathname, depth = 0 }) {
  return (
    <List disablePadding>
      {items.reduce(
        (acc, item) => reduceChildRoutes({ acc, item, pathname, depth }),
        []
      )}
    </List>
  );
}

function reduceChildRoutes({ acc, pathname, item, depth }) {
  const key = item.title + depth;

  if (item.items) {
    const open = matchPath(pathname, {
      path: item.href,
      exact: false
    });

    acc.push(
      <NavItem
        depth={depth}
        icon={item.icon}
        info={item.info}
        key={key}
        open={Boolean(open)}
        title={item.title}
      >
        {renderNavItems({
          depth: depth + 1,
          pathname,
          items: item.items
        })}
      </NavItem>
    );
  } else {
    acc.push(
      <NavItem
        depth={depth}
        href={item.href}
        icon={item.icon}
        info={item.info}
        key={key}
        title={item.title}
      />
    );
  }

  return acc;
}

const useStyles = makeStyles(theme => ({
  mobileDrawer: {
    width: 400
  },
  // desktopDrawer: {
  //   width: 400,
  //   top: 64,
  //   height: 'calc(100% - 64px)'
  // },
  avatar: {
    cursor: 'pointer',
    width: 64,
    height: 64
  },
  modelTitleContainer: {
    display: 'flex',
    // justifyContent: 'center',
    alignItems: 'center',
    // margin: '0.5rem 1rem',
    marginTop: theme.spacing(2),
    marginLeft: theme.spacing(2)
  },
  modelTitle: {
    marginLeft: theme.spacing(2)
  }
}));

const mapStructures = structure => {
  // return Object.keys(structure).map((key) => {})
  return Object.entries(structure.items).map(([key, val]) => {
    const keyNames = key.toUpperCase().split('-');
    return {
      // PPO-simple_profit
      subheader: keyNames.join(' '),
      items: mapExpirements(val, keyNames[0], keyNames[1])
    };
  });

  // return structure;
};

const mapExpirements = (expirements, algo, reward) => {
  return Object.entries(expirements.items).map(([key, val]) => {
    return {
      // binance-BTCUSDT-1h-lite-LSTM_0_2022-05-14_02-08-09
      title: key,
      icon: coinIcon(key),
      // link to the best checkpoints
      // href: '/app/management/customers',
      items: mapCheckpoints(val, algo, reward, key)
    };
  });
};

const mapCheckpoints = (checkpoints, algo, reward, expirement) => {
  const entries = Object.entries(checkpoints.items).sort(([key1], [key2]) => {
    // console.log('key1 ', key1, '  key2 ', key2);
    // const val1 = parseInt(key1.split('_')[1]);
    // const val2 = parseInt(key2.split('_')[1]);

    return parseInt(key1.split('_')[1]) - parseInt(key2.split('_')[1]);
  });
  // console.log(entries);

  return entries.map(([key]) => {
    return {
      // checkpoint_000175
      title: key,
      // link to the best checkpoints
      // href:
      //   '/app/algo?algo=PPO&expirement=binance-BTCUSDT-1h-lite-LSTM_0_2022-05-14_02-08-09&checkpoint=checkpoint_000175'
      href: `/app/algo/${algo}/${reward}/${expirement}/${key}`
    };
  });
};

const NavBar = ({ openMobile }) => {
  const classes = useStyles();
  const location = useLocation();
  const [items, setItems] = useState(null);
  const [failure, setFailure] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await API.get('/models');
      setItems(mapStructures(response.data));
    } catch (e) {
      setFailure(e);
    } finally {
      setLoading(false);
    }
  };

  const content = (
    <Box height="100%" display="flex" flexDirection="column" pt={8}>
      <PerfectScrollbar options={{ suppressScrollX: true }}>
        {/* <Hidden lgUp>
          <Box p={2} display="flex" justifyContent="center">
            <RouterLink to="/">
              <Logo />
            </RouterLink>
          </Box>
        </Hidden> */}
        <Box p={2}>
          <Box display="flex" justifyContent="center">
            <RouterLink to="/app/account">
              <Avatar
                alt="logo"
                className={classes.avatar}
                src="/static/logo.png"
              />
            </RouterLink>
          </Box>
          <Box mt={2} textAlign="center">
            <Typography variant="h5" color="textPrimary">
              Crypto Currency Trading
            </Typography>
            <Typography variant="body2" color="textSecondary">
              With Deep Reinforcement Learning
            </Typography>
          </Box>
        </Box>
        <Divider />
        <ListSubheader
          disableGutters
          disableSticky
          className={classes.modelTitleContainer}
        >
          <LayersIcon />{' '}
          <Typography className={classes.modelTitle}>Models</Typography>
        </ListSubheader>
        {/* <Divider /> */}
        <Box p={2}>
          {loading && <CircularProgress />}
          {failure && <Button title="Refresh" />}
          {items &&
            items.map(section => (
              <List
                key={section.subheader}
                subheader={
                  <ListSubheader disableGutters disableSticky>
                    {section.subheader}
                  </ListSubheader>
                }
              >
                {renderNavItems({
                  items: section.items,
                  pathname: location.pathname
                })}
              </List>
            ))}
        </Box>
        <Divider />
        <Box p={2}>
          <Box p={2} borderRadius="borderRadius" bgcolor="background.dark">
            <Typography variant="h6" color="textPrimary">
              All operation in here are simulations using historical data
            </Typography>
          </Box>
        </Box>
      </PerfectScrollbar>
    </Box>
  );

  return (
    <>
      {/* <Hidden lgUp> */}
      <Drawer
        anchor="left"
        classes={{ paper: classes.mobileDrawer }}
        open={openMobile}
        variant="persistent"
      >
        {content}
      </Drawer>
    </>
  );
};

NavBar.propTypes = {
  onMobileClose: PropTypes.func,
  openMobile: PropTypes.bool
};

export default NavBar;
