import { useState } from "react";
import { Routes, Route } from "react-router-dom";

import SituationPage from "./SituationPage";
import DeliberationPage from "./DeliberationPage";

function App() {
  const [currentSavings, setCurrentSavings] = useState<number | undefined>();
  const [monthlyIncome, setMonthlyIncome] = useState<number | undefined>();
  const [goalKnown, setGoalKnown] = useState<boolean | undefined>();
  const [goalPrice, setGoalPrice] = useState<number | undefined>();
  const [savedFraction, setSavedFraction] = useState(0.5);
  const [riskPreference, setRiskPreference] = useState(0);

  return (
    <Routes>
      <Route
        path="situation"
        element={
          <SituationPage
            currentSavings={currentSavings}
            setCurrentSavings={setCurrentSavings}
            monthlyIncome={monthlyIncome}
            setMonthlyIncome={setMonthlyIncome}
            goalKnown={goalKnown}
            setGoalKnown={setGoalKnown}
            goalPrice={goalPrice}
            setGoalPrice={setGoalPrice}
          />
        }
      />
      <Route
        path="deliberation"
        element={
          <DeliberationPage
            currentSavings={currentSavings as number}
            monthlyIncome={monthlyIncome as number}
            savedFraction={savedFraction}
            setSavedFraction={setSavedFraction}
            riskPreference={riskPreference}
            setRiskPreference={setRiskPreference}
          />
        }
      />
    </Routes>
  );
}

export default App;
