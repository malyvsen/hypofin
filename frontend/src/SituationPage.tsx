import { SetStateAction } from "react";
import MoneyInput from "./MoneyInput";

function SituationPage({
  currentSavings,
  setCurrentSavings,
  monthlyIncome,
  setMonthlyIncome,
  goalKnown,
  setGoalKnown,
  goalPrice,
  setGoalPrice,
}: {
  currentSavings: number | undefined;
  setCurrentSavings: React.Dispatch<SetStateAction<number | undefined>>;
  monthlyIncome: number | undefined;
  setMonthlyIncome: React.Dispatch<SetStateAction<number | undefined>>;
  goalKnown: boolean | undefined;
  setGoalKnown: React.Dispatch<SetStateAction<boolean | undefined>>;
  goalPrice: number | undefined;
  setGoalPrice: React.Dispatch<SetStateAction<number | undefined>>;
}) {
  return (
    <div className="Page">
      <h1>Twoja sytuacja</h1>
      <MoneyInput
        title="Twoje obecne oszczędności:"
        help="Kwota, którą jesteś w stanie zainwestować w tej chwili."
        value={currentSavings}
        setValue={setCurrentSavings}
      />
      <MoneyInput
        title="Twoje miesięczne przychody:"
        help="Twoje zarobki i inne wpływy, np. z wynajmu. Nie odejmuj wydatków, zrobimy to osobno."
        value={monthlyIncome}
        setValue={setMonthlyIncome}
      />
      <div>
        Wiesz już, na co zbierasz?{" "}
        <button type="button" onClick={() => setGoalKnown(true)}>
          {goalKnown === true ? <b>Tak</b> : "Tak"}
        </button>
        <button type="button" onClick={() => setGoalKnown(false)}>
          {goalKnown === false ? <b>Nie</b> : "Nie"}
        </button>
      </div>
      {goalKnown === true ? (
        <MoneyInput
          title="Ile to kosztuje?"
          help="Orientacyjna cena twojego celu. Jeśli nie jesteś w ogóle w stanie jej określić, zaznacz, że cel nie jest ci znany."
          value={goalPrice}
          setValue={setGoalPrice}
        ></MoneyInput>
      ) : goalKnown === false ? (
        "Bez obaw! Wciąż jesteśmy w stanie ci pomóc."
      ) : (
        <></>
      )}
    </div>
  );
}

export default SituationPage;
