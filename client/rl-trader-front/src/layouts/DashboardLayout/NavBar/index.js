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
  Hidden,
  Link,
  List,
  ListSubheader,
  Typography,
  makeStyles,
  CircularProgress,
  Button
} from '@material-ui/core';
import {
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Layers as LayersIcon
} from 'react-feather';
import Logo from 'src/components/Logo';
import useAuth from 'src/hooks/useAuth';
import API from 'src/Api';
import NavItem from './NavItem';
import { AdaCoinIcon, BitCoinIcon, BnbCoinIcon, EthCoinIcon } from './icons';

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
  desktopDrawer: {
    width: 400,
    top: 64,
    height: 'calc(100% - 64px)'
  },
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
    return {
      // PPO-simple_profit
      subheader: key
        .toUpperCase()
        .split('-')
        .join(' '),
      items: mapExpirements(val)
    };
  });

  // return structure;
};

const mapExpirements = expirements => {
  return Object.entries(expirements.items).map(([key, val]) => {
    return {
      // binance-BTCUSDT-1h-lite-LSTM_0_2022-05-14_02-08-09
      title: key,
      icon: coinIcon(key),
      // link to the best checkpoints
      // href: '/app/management/customers',
      items: mapCheckpoints(val)
    };
  });
};

const coinIcon = name => {
  if (name.includes('ADA')) {
    return AdaCoinIcon;
  } else if (name.includes('BTC')) {
    return BitCoinIcon;
  } else if (name.includes('BNB')) {
    return BnbCoinIcon;
  } else if (name.includes('ETH')) {
    return EthCoinIcon;
  }
};

const mapCheckpoints = checkpoints => {
  return Object.entries(checkpoints.items).map(([key]) => {
    return {
      // checkpoint_000175
      title: key,
      // link to the best checkpoints
      href: '/app/management/customers'
    };
  });
};

const NavBar = ({ onMobileClose, openMobile }) => {
  const classes = useStyles();
  const location = useLocation();
  const { user } = useAuth();
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

  useEffect(() => {
    if (openMobile && onMobileClose) {
      onMobileClose();
    }
  }, [location.pathname]);

  const content = (
    <Box height="100%" display="flex" flexDirection="column">
      <PerfectScrollbar options={{ suppressScrollX: true }}>
        <Hidden lgUp>
          <Box p={2} display="flex" justifyContent="center">
            <RouterLink to="/">
              <Logo />
            </RouterLink>
          </Box>
        </Hidden>
        <Box p={2}>
          <Box display="flex" justifyContent="center">
            <RouterLink to="/app/account">
              <Avatar alt="User" className={classes.avatar} src={user.avatar} />
            </RouterLink>
          </Box>
          <Box mt={2} textAlign="center">
            <Link
              component={RouterLink}
              to="/app/account"
              variant="h5"
              color="textPrimary"
              underline="none"
            >
              {user.name}
            </Link>
            <Typography variant="body2" color="textSecondary">
              Your tier:
              <Link component={RouterLink} to="/pricing">
                {user.tier}
              </Link>
            </Typography>
          </Box>
        </Box>
        <Divider />
        <Box p={2}>
          <ListSubheader disableGutters disableSticky>
            Report
          </ListSubheader>
          {renderNavItems({
            items: [
              {
                title: 'Dashboard',
                icon: PieChartIcon,
                href: '/app/reports/dashboard'
              },
              {
                title: 'Dashboard Alternative',
                icon: BarChartIcon,
                href: '/app/reports/dashboard-alternative'
              }
            ],
            pathname: location.pathname
          })}
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
              Need Help?
            </Typography>
            <Link
              variant="subtitle1"
              color="secondary"
              component={RouterLink}
              to="/docs"
            >
              Check our docs
            </Link>
          </Box>
        </Box>
      </PerfectScrollbar>
    </Box>
  );

  return (
    <>
      <Hidden lgUp>
        <Drawer
          anchor="left"
          classes={{ paper: classes.mobileDrawer }}
          onClose={onMobileClose}
          open={openMobile}
          variant="temporary"
        >
          {content}
        </Drawer>
      </Hidden>
      <Hidden mdDown>
        <Drawer
          anchor="left"
          classes={{ paper: classes.desktopDrawer }}
          open
          variant="persistent"
        >
          {content}
        </Drawer>
      </Hidden>
    </>
  );
};

NavBar.propTypes = {
  onMobileClose: PropTypes.func,
  openMobile: PropTypes.bool
};

export default NavBar;
