import React from 'react';
import clsx from 'clsx';
import {
  Box,
  Button,
  Grid,
  Hidden,
  Typography,
  makeStyles,
  CircularProgress
} from '@material-ui/core';
import BackupOutlinedIcon from '@material-ui/icons/BackupOutlined';
import { coinIcon } from 'src/assets/icons';
import { green } from '@material-ui/core/colors';

const useStyles = makeStyles(theme => ({
  root: {},
  action: {
    backgroundColor: green[600],
    color: theme.palette.common.white,
    '&:hover': {
      color: theme.palette.common.black
    }
  },
  image: {
    width: '100%',
    maxHeight: 400
  },
  deployContainer: {
    display: 'flex',
    alignItems: 'center'
  },
  progress: {
    marginLeft: theme.spacing(2)
  }
}));

const Header = ({
  className,
  expirement,
  checkpoint,
  deploying,
  onDeploy,
  ...rest
}) => {
  const classes = useStyles();

  const CoinIcon = coinIcon(expirement);

  return (
    <div className={clsx(classes.root, className)} {...rest}>
      <Grid alignItems="center" container justify="space-between" spacing={3}>
        <Grid item md={6} xs={12}>
          <Typography variant="overline" color="textSecondary">
            Expirement
          </Typography>
          <Typography variant="h3" color="textPrimary">
            {expirement}
          </Typography>
          <Typography variant="subtitle1" color="textPrimary">
            {checkpoint}
          </Typography>
          <Box>
            <Typography></Typography>
          </Box>
          <Box mt={2} className={classes.deployContainer}>
            <Button
              className={classes.action}
              variant="contained"
              startIcon={<BackupOutlinedIcon />}
              color="success"
              disabled={deploying}
              onClick={onDeploy}
            >
              Deploy
            </Button>

            {deploying && <CircularProgress className={classes.progress} />}
          </Box>
        </Grid>
        <Hidden smDown>
          <Grid item md={6}>
            <CoinIcon size="400" />
          </Grid>
        </Hidden>
      </Grid>
    </div>
  );
};

export default Header;
