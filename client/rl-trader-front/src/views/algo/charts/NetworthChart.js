import React from 'react';
import clsx from 'clsx';
import PropTypes from 'prop-types';
import { Line } from 'react-chartjs-2';
import { fade, makeStyles, useTheme } from '@material-ui/core';
import moment from 'moment';

const useStyles = makeStyles(() => ({
  root: {
    position: 'relative'
  }
}));

const PRICES_TO_SHOW = 10;

const NetworthChart = ({
  className,
  data: dataProp,
  label,
  color,
  ...rest
}) => {
  const classes = useStyles();
  const theme = useTheme();

  const data = canvas => {
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);

    gradient.addColorStop(0, fade(color, 0.2));
    gradient.addColorStop(0.9, 'rgba(255,255,255,0)');
    gradient.addColorStop(1, 'rgba(255,255,255,0)');
    return {
      datasets: [
        {
          data: dataProp.values,
          label: label,
          backgroundColor: gradient,
          borderColor: color
          // pointBorderColor: theme.palette.background.default,
          // pointBorderWidth: 3,
          // pointRadius: 6,
          // pointBackgroundColor: color
        }
      ],
      labels: dataProp.labels
    };
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    legend: {
      display: false
    },
    layout: {
      padding: 0
    },
    scales: {
      xAxes: [
        {
          gridLines: {
            display: false,
            drawBorder: false
          },
          ticks: {
            padding: 20,
            fontColor: theme.palette.text.secondary,
            callback: (value, index, values) => {
              const step = parseInt(values.length / PRICES_TO_SHOW);
              if (index % step === 0) {
                return moment(value).format('YYYY-MM-DD, h:mm a');
              }
            }
          }
        }
      ],
      yAxes: [
        {
          gridLines: {
            borderDash: [2],
            borderDashOffset: [2],
            color: theme.palette.divider,
            drawBorder: false,
            zeroLineBorderDash: [2],
            zeroLineBorderDashOffset: [2],
            zeroLineColor: theme.palette.divider
          },
          ticks: {
            padding: 20,
            fontColor: theme.palette.text.secondary,
            beginAtZero: false,
            callback: value => (value > 0 ? `${value}$` : value)
          }
        }
      ]
    },
    tooltips: {
      enabled: true,
      mode: 'index',
      intersect: false,
      caretSize: 10,
      yPadding: 20,
      xPadding: 20,
      borderWidth: 1,
      borderColor: theme.palette.divider,
      backgroundColor: theme.palette.background.default,
      titleFontColor: theme.palette.text.primary,
      bodyFontColor: theme.palette.text.secondary,
      footerFontColor: theme.palette.text.secondary
      // callbacks: {
      //   title: () => {},
      //   label: tooltipItem => {
      //     let label = `Income: ${tooltipItem.yLabel}`;

      //     if (tooltipItem.yLabel > 0) {
      //       label += '$';
      //     }

      //     return label;
      //   }
      // }
    }
  };

  return (
    <div className={clsx(classes.root, className)} {...rest}>
      <Line data={data} options={options} />
    </div>
  );
};

NetworthChart.propTypes = {
  className: PropTypes.string,
  data: PropTypes.array.isRequired,
  labels: PropTypes.array.isRequired
};

export default NetworthChart;
