<template>
  <v-layout>
    <v-flex>
      <h1 align="center">
        <v-icon x-large class="mr-2 mb-2">mdi-home-lightbulb</v-icon>Electricty Info
      </h1>
      <v-card>
        <h1 align="center">Overall</h1>
        <ElectrictyOverall v-if="usageData" :usage-data="usageData" />
      </v-card>
      <v-card class="mt-4">
        <h1 align="center">Average</h1>
        <ElectrictyAverage v-if="usageData" :usage-data="usageData" />
      </v-card>
      <v-card class="mt-4">
        <h1 align="center">Previous</h1>
        <ElectrictyPrevious v-if="usageData" :usage-data="usageData" />
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  async asyncData({ $axios }) {
    return {
      usageData: (await $axios.$get("data/electricity.json")).usageData
    };
  }
});
</script>