import MoneyInput from "./MoneyInput";

function SituationPage({ currentSavings, setCurrentSavings }) {
  return (
    <div className="Page">
      <h1>Twoja sytuacja</h1>
      <MoneyInput
        value={currentSavings}
        setValue={setCurrentSavings}
        help="Kwota, którą jesteś w stanie zainwestować w tej chwili."
      />
    </div>
  );
}

export default SituationPage;
