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
  Button,
  Chip
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
import {
  Briefcase as BriefcaseIcon,
  Calendar as CalendarIcon,
  ShoppingCart as ShoppingCartIcon,
  Folder as FolderIcon,
  Lock as LockIcon,
  UserPlus as UserPlusIcon,
  AlertCircle as AlertCircleIcon,
  Trello as TrelloIcon,
  User as UserIcon,
  Layout as LayoutIcon,
  Edit as EditIcon,
  DollarSign as DollarSignIcon,
  Mail as MailIcon,
  MessageCircle as MessageCircleIcon,
  Share2 as ShareIcon,
  Users as UsersIcon
} from 'react-feather';
import ReceiptIcon from '@material-ui/icons/ReceiptOutlined';
import { coinIcon } from '../../../assets/icons';

const sections = [
  {
    subheader: 'Reports',
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
    ]
  },
  {
    subheader: 'Management',
    items: [
      {
        title: 'Customers',
        icon: UsersIcon,
        href: '/app/management/customers',
        items: [
          {
            title: 'List Customers',
            href: '/app/management/customers'
          },
          {
            title: 'View Customer',
            href: '/app/management/customers/1'
          },
          {
            title: 'Edit Customer',
            href: '/app/management/customers/1/edit'
          }
        ]
      },
      {
        title: 'Products',
        icon: ShoppingCartIcon,
        href: '/app/management/products',
        items: [
          {
            title: 'List Products',
            href: '/app/management/products'
          },
          {
            title: 'Create Product',
            href: '/app/management/products/create'
          }
        ]
      },
      {
        title: 'Orders',
        icon: FolderIcon,
        href: '/app/management/orders',
        items: [
          {
            title: 'List Orders',
            href: '/app/management/orders'
          },
          {
            title: 'View Order',
            href: '/app/management/orders/1'
          }
        ]
      },
      {
        title: 'Invoices',
        icon: ReceiptIcon,
        href: '/app/management/invoices',
        items: [
          {
            title: 'List Invoices',
            href: '/app/management/invoices'
          },
          {
            title: 'View Invoice',
            href: '/app/management/invoices/1'
          }
        ]
      }
    ]
  },
  {
    subheader: 'Applications',
    items: [
      {
        title: 'Projects Platform',
        href: '/app/projects',
        icon: BriefcaseIcon,
        items: [
          {
            title: 'Overview',
            href: '/app/projects/overview'
          },
          {
            title: 'Browse Projects',
            href: '/app/projects/browse'
          },
          {
            title: 'Create Project',
            href: '/app/projects/create'
          },
          {
            title: 'View Project',
            href: '/app/projects/1'
          }
        ]
      },
      {
        title: 'Social Platform',
        href: '/app/social',
        icon: ShareIcon,
        items: [
          {
            title: 'Profile',
            href: '/app/social/profile'
          },
          {
            title: 'Feed',
            href: '/app/social/feed'
          }
        ]
      },
      {
        title: 'Kanban',
        href: '/app/kanban',
        icon: TrelloIcon
      },
      {
        title: 'Mail',
        href: '/app/mail',
        icon: MailIcon
      },
      {
        title: 'Chat',
        href: '/app/chat',
        icon: MessageCircleIcon,
        info: () => <Chip color="secondary" size="small" label="Updated" />
      },
      {
        title: 'Calendar',
        href: '/app/calendar',
        icon: CalendarIcon,
        info: () => <Chip color="secondary" size="small" label="Updated" />
      }
    ]
  },
  {
    subheader: 'Auth',
    items: [
      {
        title: 'Login',
        href: '/login-unprotected',
        icon: LockIcon
      },
      {
        title: 'Register',
        href: '/register-unprotected',
        icon: UserPlusIcon
      }
    ]
  },
  {
    subheader: 'Pages',
    items: [
      {
        title: 'Account',
        href: '/app/account',
        icon: UserIcon
      },
      {
        title: 'Error',
        href: '/404',
        icon: AlertCircleIcon
      },
      {
        title: 'Pricing',
        href: '/pricing',
        icon: DollarSignIcon
      }
    ]
  },
  {
    subheader: 'Extra',
    items: [
      {
        title: 'Charts',
        href: '/app/extra/charts',
        icon: BarChartIcon,
        items: [
          {
            title: 'Apex Charts',
            href: '/app/extra/charts/apex'
          }
        ]
      },
      {
        title: 'Forms',
        href: '/app/extra/forms',
        icon: EditIcon,
        items: [
          {
            title: 'Formik',
            href: '/app/extra/forms/formik'
          },
          {
            title: 'Redux Forms',
            href: '/app/extra/forms/redux'
          }
        ]
      },
      {
        title: 'Editors',
        href: '/app/extra/editors',
        icon: LayoutIcon,
        items: [
          {
            title: 'DraftJS Editor',
            href: '/app/extra/editors/draft-js'
          },
          {
            title: 'Quill Editor',
            href: '/app/extra/editors/quill'
          }
        ]
      }
    ]
  }
];

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
          {sections.map(section => (
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
