<template>
  <TabbedCharts :charts="charts">
    <div align="center" class="mt-auto pl-2">
      <v-select
        v-model="rollingMeanDays"
        :items="[1, 2, 3, 4, 5, 6, 7]"
        label="Rolling Mean Days"
        :style="{maxWidth:'100px'}"
      ></v-select>
    </div>
  </TabbedCharts>
</template>

<script>
export default {
  props: {
    usageData: {
      type: Array
    }
  },
  data() {
    return {
      rollingMeanDays: 1,
      chartTypes: ["allTime", "yearOverYear"]
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
              data: this.$rollingMean(dataset.data, this.rollingMeanDays)
            }))
          }
        };
      });
    },
    usageByDate() {
      const ret = [];
      this.usageData.forEach(([dateTime, usage]) => {
        const date = dateTime.substring(0, 10);
        if (ret.length === 0 || date !== this.$_.last(ret)[0]) {
          ret.push([date, 0.0]);
        }
        this.$_.last(ret)[1] += usage;
      });
      return ret;
    },
    allTime() {
      return {
        labels: this.usageByDate.map(data => data[0]),
        datasets: [
          {
            label: "Energy Usage",
            data: this.usageByDate.map(data => data[1])
          }
        ]
      };
    },
    yearOverYear() {
      const labels = this.$_.times(365, dateIndex => {
        const date = new Date(2019 /* non-leap year */, 0, dateIndex + 1);
        return (
          (date.getMonth() + 1).toString().padStart(2, "0") +
          "-" +
          date
            .getDate()
            .toString()
            .padStart(2, "0")
        );
      });
      const datasets = [];
      let currentYear = undefined;
      this.usageByDate.forEach(data => {
        const [year, month, day] = data[0].split("-");
        if (year !== currentYear) {
          datasets.push({
            label: year,
            data: new Array(365)
          });
          currentYear = year;
        }
        if (!(month === "02" && day === "29")) {
          const dateIndex = Math.floor(
            (new Date(2019, parseInt(month) - 1, parseInt(day)) -
              new Date(2019, 0, 1)) /
              (1000 * 60 * 60 * 24)
          );
          this.$_.last(datasets).data[dateIndex] = data[1];
        }
      });

      return {
        labels,
        datasets
      };
    }
  }
};
</script>