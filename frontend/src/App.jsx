import { useState } from "react";
function App() {
  const [pts, setPts] = useState(25.5);
  const [rest, setRest] = useState(1);
  const [home, setHome] = useState(1);
  const [prediction, setPrediction] = useState(null);
  const handleSubmit = async (e) => {
    e.preventDefault(); // Blokuje domyślne przeładowanie strony po wysłaniu formularza
    try {
      const response = await fetch('http://127.0.0.1:8000/api/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          PTS_5G_AVG: parseFloat(pts),
          DAYS_REST: parseInt(rest),
          HOME_GAME: parseFloat(home)
        })
      });
      const data = await response.json();
      setPrediction(data.predicted_pts);
    } catch(error){
      console.error("Błąd zapytania:", error);

    }
  };
  return (
    <div>
      <h1>NBA stats prediction </h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>PTS (Avarage from 5 games):</label>
          <input type="number" step= "0.1" value = {pts} onChange = {(e) => setPts(e.target.value)} />
        </div>
        <div>
          <label>Rest days:</label>
          <input type="number" value={rest} onChange={(e) => setRest(e.target.value)} />
        </div>
        <div>
          <label> Home game: </label>
          <input type="number" min="0" max="1" value={home} onChange={(e) => setHome(e.target.value)} />
        </div>
        <button type="submit">Predict</button>
      </form>
      {/* warunkowe renderowanie - div pojawi się tylko, gdy prediction nie jest null */}
      {prediction !== null && (
        <h2>Predicted points: {prediction.toFixed(1)}</h2>
      )}
    </div>
  );
}

export default App;