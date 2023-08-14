import { useEffect, useState, SetStateAction } from "react";
import Plot from "react-plotly.js";
import axios from "axios";
import { numericFormatter } from "react-number-format";

import FractionSlider from "./FractionSlider";
import numericFormatProps from "./numericFormatProps";

function DeliberationPage({
  currentSavings,
  monthlyIncome,
  savedFraction,
  setSavedFraction,
  riskPreference,
  setRiskPreference,
}: {
  currentSavings: number;
  monthlyIncome: number;
  savedFraction: number;
  setSavedFraction: React.Dispatch<SetStateAction<number>>;
  riskPreference: number;
  setRiskPreference: React.Dispatch<SetStateAction<number>>;
}) {
  const savedMonthly = Math.round(monthlyIncome * savedFraction);
  const spentMonthly = monthlyIncome - savedMonthly;

  const [response, setResponse] = useState();
  useEffect(() => {
    axios
      .post("http://localhost:8000/", {
        initial_investment: currentSavings,
        monthly_addition: savedMonthly,
        bond_fraction: riskPreference,
        goal_price: null,
      })
      .then(({ data }) => {
        setResponse(data);
      });
  }, [currentSavings, savedMonthly, riskPreference]);

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
        {numericFormatter(savedMonthly.toString(), numericFormatProps)},
        wydajesz {numericFormatter(spentMonthly.toString(), numericFormatProps)}
        .
      </div>
      <div>
        Zysk krótko- i długoterminowy nie idą w parze. Inwestycje, na których
        można polegać w krótkim terminie, nie przynoszą tak dużego zysku. Z
        kolei inwestycje długoterminowe wahają się mocno z miesiąca na miesiąc i
        roku na rok, nieraz tracąc sporo na wartości. Stąd pytanie: jak dobrze
        znosisz takie wahania?
        <FractionSlider value={riskPreference} setValue={setRiskPreference} />
      </div>
      <Plot
        layout={{ title: "Prawdopodobieństwa" }}
        data={[{ type: "scatter", y: response.gain_probability }]}
      />
    </div>
  );
}

export default DeliberationPage;
