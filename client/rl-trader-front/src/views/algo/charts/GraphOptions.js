import React, { useRef, useState, memo } from 'react';
import {
  ListItemText,
  Tooltip,
  IconButton,
  Menu,
  MenuItem,
  makeStyles
} from '@material-ui/core';
import MoreIcon from '@material-ui/icons/MoreVert';

const useStyles = makeStyles(() => ({
  menu: {
    width: 256,
    maxWidth: '100%'
  }
}));

const GraphOptions = ({ onPeriodChange }) => {
  const classes = useStyles();
  const moreRef = useRef(null);
  const [openMenu, setOpenMenu] = useState(false);

  const handleMenuOpen = () => {
    setOpenMenu(true);
  };

  const handleMenuClose = period => {
    if (onPeriodChange) onPeriodChange(period);
    setOpenMenu(false);
  };

  return (
    <>
      <Tooltip title="More options">
        <IconButton onClick={handleMenuOpen} ref={moreRef}>
          <MoreIcon fontSize="small" />
        </IconButton>
      </Tooltip>
      <Menu
        anchorEl={moreRef.current}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left'
        }}
        open={openMenu}
        PaperProps={{ className: classes.menu }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left'
        }}
      >
        <MenuItem>
          {/* <ListItemIcon>
            <GetAppIcon />
          </ListItemIcon> */}
          <ListItemText
            primary="10 Hours"
            onClick={() => {
              handleMenuClose(10);
            }}
          />
        </MenuItem>
        <MenuItem>
          {/* <ListItemIcon>
            <FileCopyIcon />
          </ListItemIcon> */}
          <ListItemText
            primary="24 Hours"
            onClick={() => {
              handleMenuClose(24);
            }}
          />
        </MenuItem>
        <MenuItem>
          {/* <ListItemIcon>
            <PictureAsPdfIcon />
          </ListItemIcon> */}
          <ListItemText
            primary="48 Hours"
            onClick={() => {
              handleMenuClose(48);
            }}
          />
        </MenuItem>
        <MenuItem>
          {/* <ListItemIcon>
            <ArchiveIcon />
          </ListItemIcon> */}
          <ListItemText
            primary="7 Days"
            onClick={() => {
              handleMenuClose(168);
            }}
          />
        </MenuItem>
      </Menu>
    </>
  );
};

export default memo(GraphOptions);
