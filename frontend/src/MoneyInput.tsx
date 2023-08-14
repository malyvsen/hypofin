import { SetStateAction } from "react";
import { NumericFormat } from "react-number-format";
import { Tooltip } from "react-tooltip";
import "react-tooltip/dist/react-tooltip.css";
import { CiCircleQuestion } from "react-icons/ci";

function MoneyInput({
  title,
  help,
  value,
  setValue,
}: {
  title: string;
  help: string | undefined;
  value: number | undefined;
  setValue: React.Dispatch<SetStateAction<number | undefined>>;
}) {
  return (
    <div>
      {title}{" "}
      <NumericFormat
        thousandsGroupStyle="thousand"
        thousandSeparator=" "
        suffix=" zł"
        allowNegative={false}
        decimalScale={0}
        value={value === undefined ? "" : value}
        onValueChange={(values) => setValue(parseInt(values.value))}
      />{" "}
      {help === undefined ? (
        <></>
      ) : (
        <>
          <CiCircleQuestion
            data-tooltip-id="tooltip"
            data-tooltip-content={help}
          />
          <Tooltip id="tooltip" />
        </>
      )}
    </div>
  );
}

export default MoneyInput;
