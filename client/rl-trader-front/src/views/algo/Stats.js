import React from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import numeral from 'numeral';
import { Box, Card, Grid, Typography, makeStyles } from '@material-ui/core';

const useStyles = makeStyles(theme => ({
  root: {},
  item: {
    padding: theme.spacing(3),
    textAlign: 'center',
    [theme.breakpoints.up('md')]: {
      '&:not(:last-of-type)': {
        borderRight: `1px solid ${theme.palette.divider}`
      }
    },
    [theme.breakpoints.down('sm')]: {
      '&:not(:last-of-type)': {
        borderBottom: `1px solid ${theme.palette.divider}`
      }
    }
  },
  label: {
    marginLeft: theme.spacing(1)
  },
  overline: {
    marginTop: theme.spacing(1)
  }
}));

const Stats = ({ className, checkpoint, algo, reward, ...rest }) => {
  const classes = useStyles();

  return (
    <Card className={clsx(classes.root, className)} {...rest}>
      <Grid alignItems="center" container justify="space-between">
        <Grid className={classes.item} item md={3} sm={6} xs={12}>
          <Typography variant="h2" color="textPrimary">
            {algo}
          </Typography>
          <Typography
            className={classes.overline}
            variant="overline"
            color="textSecondary"
          >
            Algorithm
          </Typography>
        </Grid>
        <Grid className={classes.item} item md={3} sm={6} xs={12}>
          <Typography variant="h2" color="textPrimary">
            {/* {numeral(statistics.totalIncome).format('$0,0.00')} */}
            {reward}
          </Typography>
          <Typography
            className={classes.overline}
            variant="overline"
            color="textSecondary"
          >
            Reward
          </Typography>
        </Grid>
        <Grid className={classes.item} item md={3} sm={6} xs={12}>
          <Typography variant="h2" color="textPrimary">
            {checkpoint}
          </Typography>
          <Typography
            className={classes.overline}
            variant="overline"
            color="textSecondary"
          >
            Checkpoint
          </Typography>
        </Grid>
        <Grid className={classes.item} item md={3} sm={6} xs={12}>
          <Box display="flex" alignItems="center" justifyContent="center">
            <Typography component="span" variant="h2" color="textPrimary">
              {numeral(10000).format('$0,0.00')}
            </Typography>
          </Box>
          <Typography
            className={classes.overline}
            variant="overline"
            color="textSecondary"
          >
            Starting balance
          </Typography>
        </Grid>
      </Grid>
    </Card>
  );
};

Stats.propTypes = {
  className: PropTypes.string
};

export default Stats;
