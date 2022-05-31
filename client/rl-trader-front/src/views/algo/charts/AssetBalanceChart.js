import React from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import { Bar } from 'react-chartjs-2';
import { makeStyles, useTheme } from '@material-ui/core';
import numeral from 'numeral';
import moment from 'moment';

const useStyles = makeStyles(() => ({
  root: {
    position: 'relative',
    height: '100%'
  }
}));

const PRICES_TO_SHOW = 10;

const AssetBalanceChart = ({ data: dataProp }) => {
  const classes = useStyles();
  const theme = useTheme();

  const assetColor =
    theme.palette.type === 'light'
      ? theme.palette.success.light
      : theme.palette.success.dark;
  const balanceColor =
    theme.palette.type === 'light'
      ? theme.palette.error.light
      : theme.palette.error.dark;

  const data = {
    datasets: [
      {
        label: 'Asset held',
        backgroundColor: assetColor,
        data: dataProp.values.assetsHeld,
        barThickness: 12,
        maxBarThickness: 10,
        barPercentage: 0.5,
        categoryPercentage: 0.5
      },
      {
        label: 'Balance',
        backgroundColor: balanceColor,
        data: dataProp.values.balances,
        barThickness: 12,
        maxBarThickness: 10,
        barPercentage: 0.5,
        categoryPercentage: 0.5
      }
    ],
    labels: dataProp.labels.slice(
      dataProp.labels.length - dataProp.values.assetsHeld.length,
      dataProp.labels.length
    )
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    cornerRadius: 20,
    legend: {
      display: true
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
            beginAtZero: true,
            min: 0,
            callback: value =>
              value > 0.5
                ? numeral(value).format('$0,0')
                : numeral(0).format('$0,0')
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
      backgroundColor: theme.palette.background.dark,
      titleFontColor: theme.palette.text.primary,
      bodyFontColor: theme.palette.text.secondary,
      footerFontColor: theme.palette.text.secondary,
      callbacks: {
        title: () => {},
        label: tooltipItem => {
          console.log(tooltipItem);

          if (tooltipItem.datasetIndex === 0) {
            return `Asset held: ${tooltipItem.yLabel}$`;
          } else {
            return `Balance: ${tooltipItem.yLabel}$`;
          }
        }
      }
    }
  };

  return (
    <div className={clsx(classes.root)}>
      <Bar data={data} options={options} />
    </div>
  );
};

AssetBalanceChart.propTypes = {
  className: PropTypes.string,
  data: PropTypes.object.isRequired,
  labels: PropTypes.array.isRequired
};

export default AssetBalanceChart;
