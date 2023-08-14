import { useState } from "react";
import SituationPage from "./SituationPage";

function App() {
  const [currentSavings, setCurrentSavings] = useState();
  const [monthlyIncome, setMonthlyIncome] = useState();
  const [goalKnown, setGoalKnown] = useState();
  const [goalPrice, setGoalPrice] = useState();
  return (
    <div className="App">
      <SituationPage
        currentSavings={currentSavings}
        setCurrentSavings={setCurrentSavings}
        monthlyIncome={monthlyIncome}
        setMonthlyIncome={setMonthlyIncome}
        goalKnown={goalKnown}
        setGoalKnown={setGoalKnown}
        goalPrice={goalPrice}
        setGoalPrice={setGoalPrice}
      ></SituationPage>
    </div>
  );
}

export default App;
