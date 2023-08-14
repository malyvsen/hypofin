import { SetStateAction } from "react";
import { numericFormatter } from "react-number-format";
import numericFormatProps from "./numericFormatProps";

function DeliberationPage({
  monthlyIncome,
  savedFraction,
  setSavedFraction,
}: {
  monthlyIncome: number;
  savedFraction: number;
  setSavedFraction: React.Dispatch<SetStateAction<number>>;
}) {
  const savedMonthly = Math.round(monthlyIncome * savedFraction);
  const spentMonthly = monthlyIncome - savedMonthly;
  return (
    <div className="Page">
      <h1>Czas na rozważania</h1>
      Ile zamierzasz odkładać, a ile wydawać?
      <div>
        <input
          type="range"
          min={0}
          step={0.01}
          max={1}
          value={savedFraction}
          onChange={(e) => setSavedFraction(parseFloat(e.target.value))}
        />
      </div>
      Odkładasz {numericFormatter(savedMonthly.toString(), numericFormatProps)},
      wydajesz {numericFormatter(spentMonthly.toString(), numericFormatProps)}.
    </div>
  );
}

export default DeliberationPage;
