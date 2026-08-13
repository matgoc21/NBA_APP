import { useState } from 'react';
import './App.css';

function App() {
  // stany dla trzech cech, z domyślnymi wartościami
  const [pts, setPts] = useState(25.5);
  const [rest, setRest] = useState(1);
  const [home, setHHome] = useState(1);

  // stan do przechowywania wyniku z backendu
  const [prediction, setPrediction] = useState(null);

  // funkcja wywołana po kliknięciu przycisku

  const handleSubmit = async (e) => {
    e.preventdefault(); // zapobiega przeładowaniu strony po wysłaniu formularza

    try {
      const response = await fetch('http://127.0.0.1:8000/a[i/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          PTS_5G_AVG: parsFloat(pts),
          DAYS_REST: parseFloat(rest),
          HOME_GAME: parseInt(home)
        })
      });

      const data = await response.json();
      setPrediction(data.predicted_pts);
    } catch (error) {
      console.error('Błąd komunikacji z backendem:', error);
    }
  };

  return (
    <div className="app-container">
      <h1>NBA Stats Predictor AI </h1>
      <p> Wprowadź statystyki zawodnika, aby przewidzieć jego wynik </p>
      <form onSubmit={handleSubmit} className="prediction-form">
        <div className="form-group">
          <label>Średnia punktów (5 ostatnich spotkań): </label>
          <input type="number" step="0.1" value={pts} onChange={(e) => setPts(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Liczba dni odpoczynku: </label>
          <input type="number" value={rest} onChange={(e) => setRest(e.target.value)} />
      </div>
        <div className="form-group">
          <label>Mecz u siebie (1 = Dom, 0 = Wyjazd): </label>
          <input type="number" min="0" max="1" value={home} onChange={(e) => setHome(e.target.value)} />
        </div>
        <button type="submit">Generuj predykcję</button>
      </form>

      {/*sekcja wyniku predykcji, pojawia się tylko jeśli prediction nie jest null */}
      {prediction !== null && (
        <div className="result-box">
          <h2>Przewidywana liczba punktów: {prediction.toFixed(1)}</h2>
        </div>
      )}
    </div>
  );
}
export default App;


    