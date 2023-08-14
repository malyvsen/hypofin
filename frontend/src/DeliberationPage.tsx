import { SetStateAction } from "react";
import { numericFormatter } from "react-number-format";

import FractionSlider from "./FractionSlider";
import Plots from "./Plots";
import numericFormatProps from "./numericFormatProps";

function DeliberationPage({
  currentSavings,
  monthlyIncome,
  goalPrice,
  savedFraction,
  setSavedFraction,
  riskPreference,
  setRiskPreference,
}: {
  currentSavings: number;
  monthlyIncome: number;
  goalPrice: number | undefined;
  savedFraction: number;
  setSavedFraction: React.Dispatch<SetStateAction<number>>;
  riskPreference: number;
  setRiskPreference: React.Dispatch<SetStateAction<number>>;
}) {
  const monthlySavings = Math.round(monthlyIncome * savedFraction);
  const monthlySpending = monthlyIncome - monthlySavings;

  return (
    <div className="Page">
      <h1>Czas na rozważania</h1>
      <i>
        Poeksperymentuj nieco z ustawieniami poniższych suwaków, aby zobaczyć,
        jak wpływa to na możliwe wyniki.
      </i>
      <div>
        Ile zamierzasz odkładać, a ile wydawać?
        <FractionSlider value={savedFraction} setValue={setSavedFraction} />
        Odkładasz{" "}
        {numericFormatter(monthlySavings.toString(), numericFormatProps)},
        wydajesz{" "}
        {numericFormatter(monthlySpending.toString(), numericFormatProps)}.
      </div>
      <div>
        Zysk krótko- i długoterminowy nie idą w parze. Inwestycje, na których
        można polegać w krótkim terminie, nie przynoszą tak dużego zysku. Z
        kolei inwestycje długoterminowe wahają się mocno z miesiąca na miesiąc i
        roku na rok, nieraz tracąc sporo na wartości. Stąd pytanie: jak dobrze
        znosisz takie wahania?
        <FractionSlider value={riskPreference} setValue={setRiskPreference} />
      </div>
      <Plots
        currentSavings={currentSavings}
        monthlySavings={monthlySavings}
        riskPreference={riskPreference}
        goalPrice={goalPrice}
      />
    </div>
  );
}

export default DeliberationPage;
