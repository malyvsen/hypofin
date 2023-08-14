import { useState } from "react";
import SituationPage from "./SituationPage";
import "./App.css";

function App() {
  const [currentSavings, setCurrentSavings] = useState<number | undefined>();
  const [monthlyIncome, setMonthlyIncome] = useState<number | undefined>();
  const [goalKnown, setGoalKnown] = useState<boolean | undefined>();
  const [goalPrice, setGoalPrice] = useState<number | undefined>();

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
