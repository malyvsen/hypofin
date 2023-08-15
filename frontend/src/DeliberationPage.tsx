import { SetStateAction } from "react";

import FractionSlider from "./FractionSlider";
import Plots from "./Plots";
import formatMoney from "./formatMoney";
import { Link } from "react-router-dom";

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
        Ile zamierzasz miesięcznie odkładać, a ile wydawać?
        <FractionSlider value={savedFraction} setValue={setSavedFraction} />
        Odkładasz {formatMoney(monthlySavings)}, wydajesz{" "}
        {formatMoney(monthlySpending)}.
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
      Wiesz już, jak wygląda twoja optymalna inwestycja? Jeśli tak,{" "}
      <Link to="/results">przejdź do prezentacji wyników</Link>.
    </div>
  );
}

export default DeliberationPage;
