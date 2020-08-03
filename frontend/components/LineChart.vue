
<template>
  <!-- Options arent reactive, so force rerender the hard way-->
  <ChartImpl v-if="render" :data="data" :options="options" />
</template>

<script>
import { Line } from "vue-chartjs";
import colors from "vuetify/lib/util/colors";

const chartColors = [
  colors.cyan.lighten1,
  colors.purple.lighten4,
  colors.teal.lighten1,
];

const ChartImpl = {
  extends: Line,
  props: ["data", "options"],
  data() {
    const options = Object.assign(
      {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          easing: "easeInOutQuint",
        },
        scales: {},
        tooltips: {},
        legend: {},
      },
      this.options
    );

    const scales = options.scales;
    if (scales.xAxes === undefined || scales.yAxes.length === 0) {
      scales.xAxes = [{}];
    }
    scales.xAxes[0].gridLines = {
      color: colors.grey.darken3,
    };

    if (scales.yAxes === undefined || scales.yAxes.length === 0) {
      scales.yAxes = [{}];
    }
    scales.yAxes[0].gridLines = {
      color: colors.grey.darken3,
    };

    options.tooltips.mode = "index";
    options.tooltips.intersect = false;
    options.legend.display = this.data.datasets.length > 1;

    return {
      mergedOptions: options,
    };
  },
  computed: {
    chartData() {
      return {
        labels: this.data.labels,
        datasets: this.data.datasets.map((dataset, index) =>
          Object.assign(
            {
              pointRadius: 0,
              lineTension: 0,
              borderColor: chartColors[index],
            },
            dataset
          )
        ),
      };
    },
  },
  mounted() {
    this.renderChart(this.chartData, this.mergedOptions);
  },
  watch: {
    chartData() {
      this.renderChart(this.chartData, this.mergedOptions);
    },
  },
};

export default {
  components: { ChartImpl },
  props: {
    data: {
      type: Object,
      default: null,
    },
    options: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      render: true,
    };
  },
  methods: {
    forceRender() {
      this.render = false;
      this.$nextTick(() => {
        this.render = true;
      });
    },
  },
  watch: {
    options() {
      this.forceRender();
    },
  },
};
</script>