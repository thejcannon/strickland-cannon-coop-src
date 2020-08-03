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
      type: Array,
    },
  },
  data() {
    return {
      rollingMeanWidth: 1,
      chartTypes: ["daily", "weekly", "monthly", "yearly"],
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
            },
          },
        },
        scales: {
          yAxes: [
            {
              ticks: {
                suggestedMin: 0,
                callback: (value) => value + "kWh",
              },
            },
          ],
        },
      };
      return this.chartTypes.map((key) => {
        return {
          key,
          options,
          data: {
            labels: this[key].labels,
            datasets: this[key].datasets.map((dataset) => ({
              label: dataset.label,
              data: this.$wrappingRollingMean(
                dataset.data.map(([total, count]) => total / count),
                this.rollingMeanWidth
              ),
            })),
          },
        };
      });
    },
    daily() {
      const labels = new Array(QUARTER_HOURS_IN_A_DAY);
      const values = new Array(QUARTER_HOURS_IN_A_DAY); // [total, count]
      this.usageData.forEach(([dateTime, usage]) => {
        const [time, ampm] = dateTime.split("@")[1].split(" ");
        const [hour, minute] = time.split(":");
        const hourIndex = (hour === "12" ? 0 : parseInt(hour)) * 4;
        const minuteIndex = { "0": 0, "1": 1, "3": 2, "4": 3 }[minute[0]];
        const index = hourIndex + minuteIndex + (ampm === "pm" ? 48 : 0);

        labels[index] = `${
          parseInt(hour) + (ampm === "pm" ? 12 : 0)
        }:${minute}`;
        if (values[index] === undefined) {
          values[index] = [0.0, 0];
        }
        values[index][0] += usage;
        ++values[index][1];
      });
      return {
        labels,
        datasets: [
          {
            label: `Energy Usage`,
            data: values,
          },
        ],
      };
    },
    weekly() {
      const labels = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
      ];
      const values = new Array(7); // [total, count]
      this.usageData.forEach(([dateTime, usage]) => {
        const [year, month, day] = dateTime.split("@")[0].split("-");

        const index = new Date(
          parseInt(year),
          parseInt(month) - 1,
          parseInt(day)
        ).getDay();

        if (values[index] === undefined) {
          values[index] = [0.0, 0];
        }
        values[index][0] += usage;
        ++values[index][1];
      });
      return {
        labels,
        datasets: [
          {
            label: `Energy Usage`,
            data: values.map(([total, count]) => [
              total,
              count / QUARTER_HOURS_IN_A_DAY,
            ]),
          },
        ],
      };
    },
    monthly() {
      const labels = this.$_.times(31, (num) => num + 1);
      const values = new Array(31); // [total, count]
      this.usageData.forEach(([dateTime, usage]) => {
        const [year, month, day] = dateTime.split("@")[0].split("-");

        const index =
          new Date(
            parseInt(year),
            parseInt(month) - 1,
            parseInt(day)
          ).getDate() - 1;

        if (values[index] === undefined) {
          values[index] = [0.0, 0];
        }
        values[index][0] += usage;
        ++values[index][1];
      });
      return {
        labels,
        datasets: [
          {
            label: `Energy Usage`,
            data: values.map(([total, count]) => [
              total,
              count / QUARTER_HOURS_IN_A_DAY,
            ]),
          },
        ],
      };
    },
    yearly() {
      const labels = this.$_.times(365, (dateIndex) => {
        const date = new Date(2019 /* non-leap year */, 0, dateIndex + 1);
        return (
          (date.getMonth() + 1).toString().padStart(2, "0") +
          "-" +
          date.getDate().toString().padStart(2, "0")
        );
      });
      const values = new Array(365); // [total, count]
      this.usageData.forEach(([dateTime, usage]) => {
        const [year, month, day] = dateTime.split("@")[0].split("-");

        if (!(month === "02" && day === "29")) {
          const index = Math.floor(
            (new Date(2019, parseInt(month) - 1, parseInt(day)) -
              new Date(2019, 0, 1)) /
              (1000 * 60 * 60 * 24)
          );
          if (values[index] === undefined) {
            values[index] = [0.0, 0];
          }
          values[index][0] += usage;
          ++values[index][1];
        }
      });
      return {
        labels,
        datasets: [
          {
            label: `Energy Usage`,
            data: values.map(([total, count]) => [
              total,
              count / QUARTER_HOURS_IN_A_DAY,
            ]),
          },
        ],
      };
    },
  },
};
</script>