<template>
  <v-layout>
    <v-flex>
      <h1 align="center">
        <v-icon x-large class="mr-2 mb-2">mdi-water</v-icon>Water Info
      </h1>
      <v-card>
        <h1 align="center">Overall</h1>
        <WaterOverall v-if="usageData" :usage-data="usageData" />
      </v-card>
      <v-card class="mt-4">
        <h1 align="center">Average</h1>
        <WaterAverage v-if="usageData" :usage-data="usageData" />
      </v-card>
      <v-card class="mt-4">
        <h1 align="center">Previous</h1>
        <WaterPrevious v-if="usageData" :usage-data="usageData" />
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import Vue from "vue";


export default Vue.extend({
  async asyncData({ $axios }) {
    return {
      usageData: (await $axios.$get("data/water.json")).usageData
    };
  }
});
</script>