import { useEffect, useState } from "react";
import { useDebounce } from "use-debounce";
import Plot from "react-plotly.js";
import { Data } from "plotly.js";
import axios from "axios";

function Plots({
  currentSavings,
  monthlySavings,
  riskPreference,
  goalPrice,
}: {
  currentSavings: number;
  monthlySavings: number;
  riskPreference: number;
  goalPrice: number | undefined;
}) {
  const [debouncedMonthlySavings] = useDebounce(monthlySavings, 100);
  const [debouncedRiskPreference] = useDebounce(riskPreference, 100);
  const [response, setResponse] = useState<BackendResponse>();
  useEffect(() => {
    axios
      .post("http://localhost:8000/", {
        initial_investment: currentSavings,
        monthly_addition: debouncedMonthlySavings,
        bond_fraction: 1 - debouncedRiskPreference,
        goal_price: goalPrice === undefined ? null : goalPrice,
      })
      .then(({ data }) => {
        setResponse(data);
      });
  }, [
    currentSavings,
    debouncedMonthlySavings,
    debouncedRiskPreference,
    goalPrice,
  ]);

  if (response === undefined) return <></>;
  return (
    <>
      <Plot
        layout={{ title: "Prawdopodobieństwa" }}
        data={[
          {
            type: "scatter",
            name: "Szanse na zysk",
            y: response.gain_probability,
          },
          {
            type: "scatter",
            name: "Szanse na stratę",
            y: response.loss_probability,
          },
        ]}
      />
      <Plot
        layout={{ title: "Przykładowe scenariusze" }}
        data={[
          {
            type: "scatter",
            name: "Zainwestowana kwota",
            y: response.bank_trajectory,
          } as Data,
        ].concat(
          response.scenarios.map((scenario) => {
            return {
              type: "scatter",
              name: "Przykładowa wartość inwestycji",
              showlegend: false,
              line: { color: "green" },
              y: scenario.savings_trajectory,
            } as Data;
          })
        )}
      />
    </>
  );
}

type BackendResponse = {
  success_probability: number[] | null;
  gain_probability: number[];
  loss_probability: number[];
  bank_trajectory: number[];
  scenarios: Scenario[];
};

type Scenario = {
  savings_trajectory: number[];
  goal_trajectory: number[] | null;
};

export default Plots;
