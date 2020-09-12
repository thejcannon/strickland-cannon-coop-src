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
      chartTypes: ["week" /*"month"*/],
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
              } gallons`;
            },
          },
        },
        scales: {
          yAxes: [
            {
              ticks: {
                suggestedMin: 0,
                callback: (value) => value + " gallons",
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
              data: this.$rollingMean(dataset.data, this.rollingMeanWidth),
            })),
          },
        };
      });
    },
    week() {
      const today = new Date();
      const values = []; // [label, total]
      this.$_.takeRightWhile(this.usageData, (datum) => {
        const [year, month, day] = datum[0].split("-");
        const date = new Date(
          parseInt(year),
          parseInt(month) - 1,
          parseInt(day)
        );
        if ((today - date) / (1000 * 60 * 60 * 24) < 8) {
          values.unshift([
            (date.getMonth() + 1).toString().padStart(2, "0") +
              "-" +
              date.getDate().toString().padStart(2, "0"),
            datum[1],
          ]);

          return true;
        }

        return false;
      });

      return {
        labels: values.map((value) => value[0]),
        datasets: [
          {
            label: `Water Usage`,
            data: values.map((value) => value[1]),
          },
        ],
      };
    },
  },
};
</script>