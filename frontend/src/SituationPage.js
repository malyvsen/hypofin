import MoneyInput from "./MoneyInput";

function SituationPage({
  currentSavings,
  setCurrentSavings,
  monthlyIncome,
  setMonthlyIncome,
}) {
  return (
    <div className="Page">
      <h1>Twoja sytuacja</h1>
      <MoneyInput
        title="Twoje obecne oszczędności"
        help="Kwota, którą jesteś w stanie zainwestować w tej chwili."
        value={currentSavings}
        setValue={setCurrentSavings}
      />
      <MoneyInput
        title="Twoje miesięczne przychody"
        help="Twoje zarobki i inne wpływy, np. z wynajmu. Nie odejmuj wydatków, zrobimy to osobno."
        value={monthlyIncome}
        setValue={setMonthlyIncome}
      />
    </div>
  );
}

export default SituationPage;
