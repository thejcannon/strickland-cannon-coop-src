<template>
  <v-tabs @change="changedTabs" vertical>
    <v-tab v-for="chart in charts" :key="chart.key">{{ $_.startCase(chart.key) }}</v-tab>
    <slot></slot>
    <v-tab-item
      v-for="chart in charts"
      :key="chart.key"
      :transition="false"
      :reverse-transition="false"
    >
      <LineChart :ref="`chart-${chart.key}`" :data="chart.data" :options="chart.options" />
    </v-tab-item>
  </v-tabs>
</template>

<script>
export default {
  props: {
    charts: {
      type: Array,
      required: true
    }
  },
  methods: {
    changedTabs(index) {
      const chart = this.$refs[`chart-${this.charts[index].key}`];
      if (chart !== undefined) {
        chart[0].forceRender();
      }
    }
  }
};
</script>