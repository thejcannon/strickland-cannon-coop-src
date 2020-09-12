<template>
  <TabbedCharts :charts="charts">
    <div align="center" class="mt-auto pl-2">
      <v-select
        v-model="rollingMeanWidth"
        :items="[1, 2, 3, 4, 5, 6, 7]"
        label="Rolling Mean Units"
        :style="{maxWidth:'100px'}"
      ></v-select>
    </div>
  </TabbedCharts>
</template>

<script>
const QUARTER_HOURS_IN_A_DAY = 24 * 4;

export default {
  props: {
    usageData: {
      type: Array
    }
  },
  data() {
    return {
      rollingMeanWidth: 1,
      chartTypes: ["day", "week"]
    };
  },
  computed: {
    charts() {
      const options = {
        tooltips: {
          callbacks: {
            label: (tooltipItem, data) => {
              return `${data.datasets[tooltipItem.datasetIndex].label}: ${
                tooltipItem.yLabel
              } kWh`;
            }
          }
        },
        scales: {
          yAxes: [
            {
              ticks: {
                suggestedMin: 0,
                callback: value => value + "kWh"
              }
            }
          ]
        }
      };
      return this.chartTypes.map(key => {
        return {
          key,
          options,
          data: {
            labels: this[key].labels,
            datasets: this[key].datasets.map(dataset => ({
              label: dataset.label,
              data: this.$rollingMean(dataset.data, this.rollingMeanWidth)
            }))
          }
        };
      });
    },
    day() {
      const yesterday = this.$_.last(this.usageData)[0].split("@")[0];
      const data = this.$_.takeRightWhile(this.usageData, data =>
        data[0].startsWith(yesterday)
      );
      const labels = data.map(datum => datum[0].split("@")[1]);
      const values = data.map(datum => datum[1]);
      return {
        labels,
        datasets: [
          {
            label: `Energy Usage`,
            data: values
          }
        ]
      };
    },
    week() {
      const today = new Date();
      const values = []; // [label, total, count]
      let currentHour = null;
      this.$_.takeRightWhile(this.usageData, datum => {
        const [datestring, timestring] = datum[0].split("@");
        const [year, month, day] = datestring.split("-");
        const date = new Date(
          parseInt(year),
          parseInt(month) - 1,
          parseInt(day)
        );
        if ((today - date) / (1000 * 60 * 60 * 24) < 8) {
          const parsedHour = parseInt(timestring.slice(0, 2));
          const hour =
            (parsedHour === 12 ? 0 : parsedHour) +
            (timestring.slice(-2) == "pm" ? 12 : 0);
          if (hour !== currentHour) {
            values.unshift([
              datum[0].slice(5, 11) + hour.toString().padStart(2, "0") + ":00",
              0.0,
              0
            ]);
            currentHour = hour;
          }
          values[0][1] += datum[1];
          ++values[0][2];

          return true;
        }

        return false;
      });

      return {
        labels: values.map(value => value[0]),
        datasets: [
          {
            label: `Energy Usage`,
            data: values.map(value => value[1] / value[2])
          }
        ]
      };
    }
  }
};
</script>