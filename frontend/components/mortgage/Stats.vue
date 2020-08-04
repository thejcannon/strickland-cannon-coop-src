<template>
  <div align="center">
    <v-data-table
      :headers="headers"
      :items="numbers"
      :style="{maxWidth: 'fit-content'}"
      class="mx-5 table-middle-line"
      hide-default-header
      hide-default-footer
      dense
    />

    <slot></slot>
  </div>
</template>

<style>
.table-middle-line > div > table > tbody > tr > td:nth-child(1) {
  border-right: 2px solid white;
}
</style>

<script>
import Decimal from "decimal.js";

export default {
  props: {
    mortgageInfo: {
      type: Object,
      required: true
    },
    currentLoanAmount: { type: Decimal, requred: true },
    numProjectedMonths: { type: Number, required: true },
    projectedInterestPaid: { type: Decimal },
    avgPayment: { type: Decimal, required: true },
    extraPayment: { type: Number, required: true }
  },
  data() {
    return {
      headers: [
        { text: "", value: "name" },
        { text: "", value: "value" }
      ]
    };
  },
  computed: {
    monthlyRate() {
      return new Decimal(this.mortgageInfo.interestRateInPercent).div(12 * 100);
    },
    numbers() {
      const [month, year] = this.mortgageInfo.firstPaymentDate
        .split("/")
        .map(d => parseInt(d));
      const startDate = new Date(year, month);
      const lastPaymentDate = new Date(
        startDate.setMonth(startDate.getMonth() + this.numProjectedMonths - 2)
      );
      return [
        {
          name: "Original Loan Amount",
          value: this.$money(this.mortgageInfo.originalAmount)
        },
        {
          name: "Term in Months",
          value: this.mortgageInfo.termInMonths
        },
        {
          name: "Interest Rate",
          value: this.mortgageInfo.interestRateInPercent + "%"
        },
        {
          name: "Current Loan Amount",
          value: this.$money(this.currentLoanAmount)
        },
        {
          name: "Expected Last Payment",
          value:
            (lastPaymentDate.getMonth() + 1).toString().padStart(2, "0") +
            "/" +
            lastPaymentDate.getFullYear()
        },
        {
          name: "Projected Interest Saved",
          value: this.$money(
            this.monthlyRate
              .times(this.mortgageInfo.termInMonths)
              .times(this.mortgageInfo.originalAmount)
              .toNumber() - this.projectedInterestPaid
          )
        },
        {
          name: "Average Payment Amount",
          value:
            this.$money(this.avgPayment) +
            (this.extraPayment ? ` + ${this.$money(this.extraPayment)}` : "")
        }
      ];
    }
  }
};
</script>