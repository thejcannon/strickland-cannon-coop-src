import Decimal from "decimal.js";
import Vue from "vue";
import { pull } from "lodash-es";

type Optional<T> = undefined | T;

function decimalize(values: Optional<number>[]) {
  return values.map((value: Optional<number>) =>
    value === undefined ? value : new Decimal(value)
  );
}

function mapMean(arrays: (Decimal | undefined)[][]) {
  return arrays.map((arrayValues: Optional<Decimal>[]) => {
    const definedValues = pull(arrayValues, undefined) as Decimal[];
    return definedValues.length !== 0
      ? definedValues
          .reduce((a: Decimal, b: Decimal) => a.plus(b), new Decimal(0))
          .div(definedValues.length)
          .toDecimalPlaces(2)
      : undefined;
  });
}

function rollingMean(
  values: Optional<number>[],
  windowsSize = 1
): Optional<Decimal>[] {
  return mapMean(
    decimalize(values).map(
      (val: Optional<Decimal>, index: number, array: Optional<Decimal>[]) => {
        return array.slice(
          Math.max(0, index - windowsSize),
          Math.min(array.length, index + windowsSize)
        );
      }
    )
  );
}

function wrappingRollingMean(
  values: Optional<number>[],
  windowsSize = 1
): Optional<Decimal>[] {
  return mapMean(
    decimalize(values).map(
      (val: Optional<Decimal>, index: number, array: Optional<Decimal>[]) => {
        const lowerIndex = index - windowsSize;
        const upperIndex = index + windowsSize;
        if (lowerIndex < 0) {
          return array
            .slice(array.length + lowerIndex, array.length)
            .concat(array.slice(0, upperIndex));
        } else if (upperIndex > array.length) {
          return array
            .slice(lowerIndex, array.length)
            .concat(array.slice(0, upperIndex - array.length));
        } else {
          return array.slice(lowerIndex, upperIndex);
        }
      }
    )
  );
}

declare module "vue/types/vue" {
  interface Vue {
    $rollingMean: typeof rollingMean;
    $wrappingRollingMean: typeof wrappingRollingMean;
  }
}

Vue.prototype.$rollingMean = rollingMean;
Vue.prototype.$wrappingRollingMean = wrappingRollingMean;
