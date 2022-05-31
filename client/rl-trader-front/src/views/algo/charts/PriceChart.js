import React from 'react';
import clsx from 'clsx';
import PropTypes from 'prop-types';
import { Line } from 'react-chartjs-2';
import { fade, makeStyles, useTheme } from '@material-ui/core';
import numeral from 'numeral';
import moment from 'moment';

const PRICES_TO_SHOW = 10;

const useStyles = makeStyles(() => ({
  root: {
    position: 'relative'
  }
}));

const PriceChart = ({ className, data: dataProp, label, color, ...rest }) => {
  const classes = useStyles();
  const theme = useTheme();

  const buyColor =
    theme.palette.type === 'light'
      ? theme.palette.success.light
      : theme.palette.success.dark;
  const sellColor =
    theme.palette.type === 'light'
      ? theme.palette.error.light
      : theme.palette.error.dark;
  const holdColor =
    theme.palette.type === 'light'
      ? theme.palette.grey[400]
      : theme.palette.grey[200];

  const getTradeData = index => {
    const indexOffsted = index + dataProp.windowStart;
    const trades = dataProp.trades.filter(
      trade => parseInt(trade.step) === indexOffsted
    );
    return trades && trades.length > 0 ? trades[0] : null;
  };

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
          borderColor: color,
          //   pointBorderColor: holdColor,
          pointBorderWidth: contex => {
            const trade = getTradeData(contex.dataIndex);
            return trade ? 1 : null;
          },
          pointRadius: context => {
            const trade = getTradeData(context.dataIndex);
            return trade ? 8 : null;
          },
          pointBorderColor: color,
          pointBackgroundColor: pointItem => {
            const trade = getTradeData(pointItem.dataIndex);
            return trade
              ? trade.type === 'buy'
                ? buyColor
                : sellColor
              : holdColor;
          }
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
      backgroundColor: theme.palette.background.default,
      titleFontColor: theme.palette.text.primary,
      bodyFontColor: theme.palette.text.secondary,
      footerFontColor: theme.palette.text.secondary,
      callbacks: {
        title: () => {},
        label: tooltipItem => {
          //   console.log(tooltipItem);

          const trade = getTradeData(tooltipItem.index);
          //   console.log('index ', tooltipItem.index, '  trade', trade);

          if (trade) {
            return `${trade.type}: ${numeral(trade.total).format('0,0.00')}$`;
          } else {
            return `Holding`;
          }
        },
        labelColor: tooltipItem => {
          const trade = getTradeData(tooltipItem.index);
          const color = trade
            ? trade.type === 'buy'
              ? buyColor
              : sellColor
            : holdColor;

          return {
            borderColor: color,
            backgroundColor: color,
            borderWidth: 2,
            borderDash: [2, 2],
            borderRadius: 2
          };
        }
      }
    }
  };

  return (
    <div className={clsx(classes.root, className)} {...rest}>
      <Line data={data} options={options} />
    </div>
  );
};

PriceChart.propTypes = {
  className: PropTypes.string,
  data: PropTypes.array.isRequired,
  labels: PropTypes.array.isRequired
};

export default PriceChart;
