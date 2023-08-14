import { SetStateAction } from "react";

function FractionSlider({
  value,
  setValue,
}: {
  value: number;
  setValue: React.Dispatch<SetStateAction<number>>;
}) {
  return (
    <div>
      <input
        type="range"
        min={0}
        step={0.01}
        max={1}
        value={value}
        onChange={(e) => setValue(parseFloat(e.target.value))}
      />
    </div>
  );
}

export default FractionSlider;
