import formatMoney from "./formatMoney";

function ResultsPage({
  currentSavings,
  monthlyIncome,
  savedFraction,
  riskPreference,
}: {
  currentSavings: number;
  monthlyIncome: number;
  savedFraction: number;
  riskPreference: number;
}) {
  const stocksPercent = Math.round(riskPreference * 100);
  const bondsPercent = 100 - stocksPercent;
  const monthlySavings = monthlyIncome * savedFraction;
  const monthlyStocks = monthlySavings * riskPreference;
  const monthlyBonds = monthlySavings - monthlyStocks;
  return (
    <div className="Page">
      <h1>Twój wynik</h1>
      Inwestycja wybrana przez ciebie w poprzednim kroku to:
      {riskPreference > 0 ? (
        <div>
          <h2>{stocksPercent}% akcje</h2>
          {formatMoney(currentSavings * riskPreference)} na start, a potem{" "}
          {formatMoney(monthlyStocks)} co miesiąc.
        </div>
      ) : (
        <></>
      )}
      {riskPreference < 1 ? (
        <div>
          <h2>{bondsPercent}% obligacje</h2>
          {formatMoney(currentSavings - currentSavings * riskPreference)} na
          start, a potem {formatMoney(monthlyBonds)} co miesiąc.
        </div>
      ) : (
        <></>
      )}
      {riskPreference > 0 ? (
        <>
          Polecamy nie sprawdzać zbyt często swojego progresu - krótkoterminowe
          straty są oczekiwane, a bolą.{" "}
        </>
      ) : (
        <>To wszystko! </>
      )}
      Wróć za około rok, aby rozważyć swoją ponownie sytuację w świetle nowych
      warunków na rynkach i w życiu osobistym.
    </div>
  );
}

export default ResultsPage;
