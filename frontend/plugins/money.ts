import Vue from "vue";

declare module "vue/types/vue" {
  interface Vue {
    $money(value: string): string;
  }
}

Vue.prototype.$money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD"
}).format;
