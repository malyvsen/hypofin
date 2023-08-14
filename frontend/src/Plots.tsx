import { useEffect, useState } from "react";
import Plot from "react-plotly.js";
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
  const [response, setResponse] = useState<BackendResponse>();
  useEffect(() => {
    axios
      .post("http://localhost:8000/", {
        initial_investment: currentSavings,
        monthly_addition: monthlySavings,
        bond_fraction: riskPreference,
        goal_price: goalPrice === undefined ? null : goalPrice,
      })
      .then(({ data }) => {
        setResponse(data);
      });
  }, [currentSavings, monthlySavings, riskPreference, goalPrice]);

  if (response === undefined) return <></>;
  return (
    <Plot
      layout={{ title: "Prawdopodobieństwa" }}
      data={[{ type: "scatter", y: response.gain_probability }]}
    />
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
