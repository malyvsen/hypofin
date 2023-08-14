import { useState } from "react";
import SituationPage from "./SituationPage";

function App() {
  const [currentSavings, setCurrentSavings] = useState();
  const [monthlyIncome, setMonthlyIncome] = useState();
  const [goalKnown, setGoalKnown] = useState();
  const [goalCost, setGoalCost] = useState();
  return (
    <div className="App">
      <SituationPage
        currentSavings={currentSavings}
        setCurrentSavings={setCurrentSavings}
        monthlyIncome={monthlyIncome}
        setMonthlyIncome={setMonthlyIncome}
      ></SituationPage>
    </div>
  );
}

export default App;
