function SituationPage({ currentSavings, setCurrentSavings }) {
  console.log(currentSavings);
  return (
    <div className="Page">
      <h1>Twoja sytuacja</h1>
      <div>
        Twoje obecne oszczędności{" "}
        <input
          type="number"
          min={0}
          step={1000}
          value={currentSavings === undefined ? 0 : currentSavings}
          onChange={(e) => setCurrentSavings(e.target.value)}
        />{" "}
        zł
      </div>
    </div>
  );
}

export default SituationPage;
