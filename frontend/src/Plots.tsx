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
    const controller = new AbortController();
    axios
      .post(
        "http://localhost:8000/",
        {
          initial_investment: currentSavings,
          monthly_addition: debouncedMonthlySavings,
          bond_fraction: 1 - debouncedRiskPreference,
          goal_price: goalPrice === undefined ? null : goalPrice,
        },
        { signal: controller.signal }
      )
      .then(({ data }) => {
        setResponse(data);
      })
      .catch((error) => {
        if (error.code === "ERR_CANCELED") return;
        throw error;
      });
    return () => {
      controller.abort();
    };
  }, [
    currentSavings,
    debouncedMonthlySavings,
    debouncedRiskPreference,
    goalPrice,
  ]);

  if (response === undefined) return <></>;
  return (
    <div>
      <Plot
        layout={{
          title: "Prawdopodobieństwa",
          showlegend: true,
          yaxis: { range: [-0.05, 1.05] },
        }}
        data={
          goalPrice === undefined
            ? [
                {
                  type: "scatter",
                  name: "Szanse zysku",
                  y: response.gain_probability,
                },
                {
                  type: "scatter",
                  name: "Szanse straty",
                  y: response.loss_probability,
                },
              ]
            : [
                {
                  type: "scatter",
                  name: "Szanse osiągnięcia celu",
                  y: response.success_probability,
                } as Data,
              ]
        }
      />
      <Plot
        layout={{ title: "Przykładowe scenariusze" }}
        data={[
          {
            type: "scatter",
            name: "Zainwestowana kwota",
            y: response.bank_trajectory,
          } as Data,
        ]
          .concat(
            response.scenarios.map((scenario) => {
              return {
                type: "scatter",
                name: "Wartość inwestycji",
                showlegend: false,
                line: { color: "green" },
                y: scenario.savings_trajectory,
              } as Data;
            })
          )
          .concat(
            goalPrice === undefined
              ? []
              : response.scenarios.map((scenario) => {
                  return {
                    type: "scatter",
                    name: "Cena celu",
                    showlegend: false,
                    line: { color: "blue" },
                    y: scenario.goal_trajectory,
                  } as Data;
                })
          )}
      />
    </div>
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
