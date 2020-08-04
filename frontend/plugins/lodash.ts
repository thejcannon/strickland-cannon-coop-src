import {
  last,
  reduce,
  startCase,
  takeRightWhile,
  times,
  zipWith
} from "lodash-es";

import Vue from "vue";

Vue.prototype.$_ = {
  last,
  reduce,
  startCase,
  takeRightWhile,
  times,
  zipWith
};

declare module "vue/types/vue" {
  interface Vue {
    $_: typeof Vue.prototype.$_;
  }
}
