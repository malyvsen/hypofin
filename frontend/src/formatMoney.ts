import { numericFormatter, NumericFormatProps } from "react-number-format";

function formatMoney(amount: number) {
  return numericFormatter(amount.toString(), numericFormatProps);
}

const numericFormatProps: NumericFormatProps = {
  thousandsGroupStyle: "thousand",
  thousandSeparator: " ",
  suffix: " zł",
  allowNegative: false,
  decimalScale: 0,
};

export default formatMoney;
export { numericFormatProps };
