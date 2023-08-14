import { Tooltip } from "react-tooltip";
import "react-tooltip/dist/react-tooltip.css";
import { CiCircleQuestion } from "react-icons/ci";

function MoneyInput({ title, help, value, setValue }) {
  return (
    <div>
      {title}{" "}
      <input
        type="number"
        min={0}
        step={1000}
        value={value === undefined ? "" : value}
        onChange={(e) => setValue(parseInt(e.target.value))}
      />{" "}
      zł{" "}
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
