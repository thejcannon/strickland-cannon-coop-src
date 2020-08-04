<template>
  <TabbedCharts :charts="charts">
    <v-btn @click.stop="$emit('triggerProjections')" class="mx-2 mt-auto mb-2">Projections</v-btn>
  </TabbedCharts>
</template>

<script>
import Decimal from "decimal.js";

export default {
  props: {
    mortgageInfo: { type: Object, required: true },
    chartInfo: { type: Object, required: true },
    numDisplayedMonths: { type: Number, required: true },
    projecting: { type: Boolean, required: true }
  },
  data() {
    return {
      types: [
        "loanAmount",
        "principal",
        "interest",
        "totalPaid",
        "interestPaid"
      ],
      options: {
        tooltips: {
          callbacks: {
            footer: (tooltipItems, data) => {
              if (tooltipItems[1] !== undefined) {
                return `Difference: ${this.$money(
                  new Decimal(tooltipItems[0].value)
                    .minus(tooltipItems[1].value)
                    .abs()
                    .toNumber()
                )}`;
              }
            },
            label: (tooltipItem, data) => {
              return `${
                data.datasets[tooltipItem.datasetIndex].label
              }: ${this.$money(tooltipItem.yLabel)}`;
            }
          }
        },
        scales: {
          yAxes: [
            {
              ticks: {
                suggestedMin: 0,
                callback: value => `${this.$money(value)}`
              }
            }
          ]
        }
      }
    };
  },
  computed: {
    chartLabels() {
      let [month, year] = this.mortgageInfo.firstPaymentDate
        .split("/")
        .map(d => parseInt(d));
      return this.$_.times(this.numDisplayedMonths, () => {
        const label = `${month.toString().padStart(2, "0")}/${year}`;

        if (++month == 13) {
          month = 1;
          year++;
        }

        return label;
      });
    },
    charts() {
      return this.types.map(chartType => {
        const datasets = [
          {
            label: "Expected",
            data: this.chartInfo[chartType].expected
          },
          {
            label: "Actual",
            data: this.chartInfo[chartType].actual
          }
        ];
        if (this.projecting) {
          datasets.push({
            label: "Projected",
            borderDash: [10, 10],
            data: this.chartInfo[chartType].projection
          });
        }

        return {
          key: chartType,
          data: {
            labels: this.chartLabels,
            datasets
          },
          options: this.options
        };
      });
    }
  }
};
</script>