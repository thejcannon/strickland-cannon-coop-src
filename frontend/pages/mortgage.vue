<template>
  <v-layout>
    <v-flex>
      <h1 align="center">
        <v-icon x-large class="mr-2 mb-2">mdi-home-analytics</v-icon>Mortgage Info
      </h1>
      <v-card class="pb-2">
        <h1 align="center">Numbers</h1>
        <Stats
          :v-if="mortgageInfo"
          :mortgage-info="mortgageInfo"
          :current-loan-amount="$_.last(chartInfo.loanAmount.actual)"
          :num-projected-months="numProjectedMonths"
          :projected-interest-paid="$_.last(projections.interestPaid)"
          :avg-payment="avgPayment"
          :extra-payment="extraPayment"
        >
          <v-slider
            v-model="extraPayment"
            :style="{maxWidth:'500px'}"
            max="2000"
            min="0"
            step="100"
            hide-details
          >
            <template v-slot:append>
              <v-text-field
                v-model="extraPayment"
                type="number"
                class="mt-0 pt-0"
                style="width: 60px"
                hide-details
                single-line
              ></v-text-field>
            </template>
          </v-slider>
        </Stats>
      </v-card>
      <v-divider class="my-4" />
      <v-card>
        <h1 align="center">Charts</h1>
        <Charts
          :v-if="mortgageInfo"
          :mortgage-info="mortgageInfo"
          :chart-info="chartInfo"
          :num-displayed-months="numDisplayedMonths"
          :projecting="projecting"
          @triggerProjections="projecting = !projecting"
        />
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import Vue from "vue";
import Decimal from "decimal.js";
import regression from "regression";

import Charts from "@/components/mortgage/Charts.vue";
import Stats from "@/components/mortgage/Stats.vue";

interface MortgageInfo {
  firstPaymentDate: string;
  originalAmount: number;
  termInMonths: number;
  interestRateInPercent: string;
  principal: string[];
  interest: string[];
}

export default Vue.extend({
  async asyncData({ $axios }) {
    return { mortgageInfo: await $axios.$get("data/mortgage.json") };
  },
  components: {
    Stats,
    Charts,
  },
  data() {
    const mortgageInfo = null as null | MortgageInfo;
    const projections: Record<string, Array<Decimal | undefined | string>> = {
      loanAmount: [],
      principal: [],
      interest: [],
      totalPaid: [],
      interestPaid: [],
    };
    return {
      mortgageInfo,
      projecting: false,
      numProjectedMonths: 0,
      projections,
      extraPayment: 0,
    };
  },
  mounted() {
    this.calculateProjections();
  },
  watch: {
    extraPayment() {
      this.calculateProjections();
    },
  },
  computed: {
    originalAmount(): Decimal {
      return new Decimal(this.mortgageInfo!.originalAmount);
    },
    monthlyRate(): Decimal {
      return new Decimal(this.mortgageInfo!.interestRateInPercent).div(
        12 * 100
      );
    },
    opr_n(): Decimal {
      return this.monthlyRate.plus(1).pow(this.mortgageInfo!.termInMonths);
    },
    paymentAmount(): Decimal {
      return new Decimal(
        this.monthlyRate
          .times(this.opr_n)
          .div(this.opr_n.minus(1))
          .times(this.originalAmount)
      );
    },
    numDisplayedMonths(): number {
      return this.projecting
        ? this.numProjectedMonths
        : this.mortgageInfo!.principal.length;
    },
    actualPayments(): Array<Decimal> {
      return this.$_.zipWith(
        this.mortgageInfo!.principal,
        this.mortgageInfo!.interest,
        (p: string, i: string) => new Decimal(p).plus(i)
      );
    },
    avgPayment(): Decimal {
      return this.$_.reduce(this.actualPayments, (sum: Decimal, n: Decimal) =>
        sum.plus(n)
      )!.div(this.actualPayments.length);
    },
    linearAppx() {
      const result = regression.linear(
        this.actualPayments.map((payment, index) => [index, payment.toNumber()])
      );
      return (x: number) => result.predict(x)[1];
    },
    chartInfo(): Record<
      string,
      Record<string, Array<undefined | Decimal | string>>
    > {
      const expectedLoanAmounts: Decimal[] = this.$_.times(
        this.numDisplayedMonths,
        (index: number) => {
          return this.opr_n
            .minus(this.monthlyRate.plus(1).pow(index + 1))
            .div(this.opr_n.minus(1))
            .times(this.originalAmount)
            .toDecimalPlaces(2);
        }
      );
      const expectedInterests: Array<Decimal> = this.$_.times(
        this.numDisplayedMonths,
        (index: number) => {
          const previous =
            expectedLoanAmounts[index - 1] || this.originalAmount;
          return new Decimal(previous)
            .times(this.monthlyRate)
            .toDecimalPlaces(2);
        }
      );
      const expectedPrincipals: Array<Decimal> = expectedInterests.map(
        (interest) => {
          return this.paymentAmount.minus(interest).toDecimalPlaces(2);
        }
      );
      return {
        loanAmount: {
          expected: expectedLoanAmounts,
          actual: this.accumulatingTotal(
            this.mortgageInfo!.principal
          ).map((total: Decimal) =>
            this.originalAmount.minus(total).toDecimalPlaces(2)
          ),
          projection: this.projections.loanAmount,
        },
        principal: {
          expected: expectedPrincipals,
          actual: this.mortgageInfo!.principal,
          projection: this.projections.principal,
        },
        interest: {
          expected: expectedInterests,
          actual: this.mortgageInfo!.interest,
          projection: this.projections.interest,
        },
        totalPaid: {
          expected: this.accumulatingTotal(
            expectedPrincipals,
            expectedInterests
          ),
          actual: this.accumulatingTotal(this.actualPayments),
          projection: this.projections.totalPaid,
        },
        interestPaid: {
          expected: this.accumulatingTotal(expectedInterests),
          actual: this.accumulatingTotal(this.mortgageInfo!.interest),
          projection: this.projections.interestPaid,
        },
      };
    },
  },
  methods: {
    accumulatingTotal(...iterables: (Decimal | string)[][]): Decimal[] {
      let total = new Decimal(0);
      return this.$_.zipWith(
        ...iterables,
        (...values: (Decimal | string)[]) => {
          values.forEach((value) => {
            total = total.add(value);
          });
          return total.toDecimalPlaces(2);
        }
      );
    },

    calculateProjections(): void {
      Object.keys(this.projections).map((key: string) => {
        this.projections[key] = [];
      });

      const startIndex = this.mortgageInfo!.principal.length;
      let paidOff = false;
      let loanAmount = new Decimal(
        this.$_.last(this.chartInfo.loanAmount.actual)!
      );
      let totalPaid = new Decimal(
        this.$_.last(this.chartInfo.totalPaid.actual)!
      );
      let interestPaid = new Decimal(
        this.$_.last(this.chartInfo.interestPaid.actual)!
      );

      this.$_.times(startIndex - 1, () => {
        this.projections.loanAmount.push(undefined);
        this.projections.interest.push(undefined);
        this.projections.principal.push(undefined);
        this.projections.totalPaid.push(undefined);
        this.projections.interestPaid.push(undefined);
      });

      this.projections.loanAmount.push(
        this.$_.last(this.chartInfo.loanAmount.actual)
      );
      this.projections.interest.push(
        this.$_.last(this.chartInfo.interest.actual)
      );
      this.projections.principal.push(
        this.$_.last(this.chartInfo.principal.actual)
      );
      this.projections.totalPaid.push(
        this.$_.last(this.chartInfo.totalPaid.actual)
      );
      this.projections.interestPaid.push(
        this.$_.last(this.chartInfo.interestPaid.actual)
      );

      let index = startIndex;
      while (!paidOff) {
        const payment = new Decimal(this.linearAppx(index) + this.extraPayment);
        const interest = loanAmount.times(this.monthlyRate);
        const principal = Decimal.min(payment.minus(interest), loanAmount);
        loanAmount = loanAmount.minus(principal);
        totalPaid = totalPaid.plus(interest).plus(principal);
        interestPaid = interestPaid.plus(interest);

        this.projections.loanAmount.push(loanAmount.toDecimalPlaces(2));
        this.projections.interest.push(interest.toDecimalPlaces(2));
        this.projections.principal.push(principal.toDecimalPlaces(2));
        this.projections.totalPaid.push(totalPaid.toDecimalPlaces(2));
        this.projections.interestPaid.push(interestPaid.toDecimalPlaces(2));

        if (loanAmount.lessThanOrEqualTo(0)) {
          paidOff = true;
        }
        index++;
      }
      this.numProjectedMonths = index;
    },
  },
});
</script>