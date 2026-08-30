import { useState, useEffect } from "react";
function App() {
  //states for games
  const [games, setGames] = useState([]);
  const [selectedGameId, setSelectedGameId] = useState("");
  // states for teams and players
  const [selectedTeam, setSelectedTeam] = useState("");
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState("");


  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/games/');
        const data = await response.json();
        setGames(data);
      } catch (error) {
        console.error('Error fetching games:', error);
      }
    };
    fetchGames();
  }, []);

  //Fetching Players based on selected team
  useEffect(() => {
    if (!selectedTeam) {
      setPlayers([]);
      setSelectedPlayer("");
      return;
    }
    const fetchPlayers = async () => {
      try {
        const response = await fetch(`http://127.0.0.1/api/teams/${selectedTeam}/players/`);
        const data = await response.json();
        setPlayers(data);
        setSelectedPlayer(""); //reset player after changing teams
      } catch (error) {
        console.error("Error fetching players: ", error)
      }
  };
  fetchPlayers();
}, [selectedTeam]);

//function reseting "cascade" by game change

const handleGameChange = (e) => {
  setSelectedGameId(e.target.value);
  setSelectedTeam(""); //hides players
  setSelectedPlayer(""); //resets choice
};
return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>NBA AI Predictor</h1>
      
      {/* KROK 1: WYBÓR MECZU */}
      <h2>1. Wybierz mecz</h2>
      <select value={selectedGameId} onChange={handleGameChange} style={{ width: '100%', padding: '8px' }}>
        <option value="">-- Wybierz mecz --</option>
        {games.map((game) => (
          <option key={game.id} value={game.id}>
            {game.game_date}: {game.away_team.name} @ {game.home_team.name}
          </option>
        ))}
      </select>

      {/* KROK 2: WYBÓR DRUŻYNY (Pojawia się tylko gdy wybrano mecz) */}
      {selectedGameObj && (
        <div style={{ marginTop: '20px' }}>
          <h2>2. Wybierz drużynę</h2>
          <select 
            value={selectedTeam} 
            onChange={(e) => setSelectedTeam(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="">-- Z jakiej drużyny jest zawodnik? --</option>
            {/* Wyciągamy Gości z wybranego meczu */}
            <option value={selectedGameObj.away_team.id}>
              Goście: {selectedGameObj.away_team.name}
            </option>
            {/* Wyciągamy Gospodarzy z wybranego meczu */}
            <option value={selectedGameObj.home_team.id}>
              Gospodarze: {selectedGameObj.home_team.name}
            </option>
          </select>
        </div>
      )}

      {/* KROK 3: WYBÓR ZAWODNIKA (Pojawia się tylko gdy wybrano drużynę) */}
      {selectedTeam && (
        <div style={{ marginTop: '20px' }}>
          <h2>3. Wybierz zawodnika</h2>
          <select 
            value={selectedPlayer} 
            onChange={(e) => setSelectedPlayer(e.target.value)}
            disabled={players.length === 0}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="">-- Kogo chcesz sprawdzić? --</option>
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.full_name} ({player.position || "Brak pozycji"})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* PODSUMOWANIE GOTOWOŚCI DO PREDYKCJI */}
      {selectedPlayer && (
        <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f0f8ff', borderRadius: '8px' }}>
          <h3>Przygotowanie do wyliczeń</h3>
          <p>Będziemy przewidywać statystyki dla zawodnika o ID <strong>{selectedPlayer}</strong>.</p>
          <p>
            Gra on przeciwko drużynie o ID:{' '}
            <strong>
              {/* Sprytne obliczenie: jeśli wybrałeś drużynę gości, przeciwnikiem jest gospodarz (i na odwrót) */}
              {selectedTeam.toString() === selectedGameObj.away_team.id.toString() 
                ? selectedGameObj.home_team.id 
                : selectedGameObj.away_team.id}
            </strong>
          </p>
          <button style={{ marginTop: '10px', padding: '10px 20px', cursor: 'pointer' }}>
            Rozpocznij Predykcję AI
          </button>
        </div>
      )}
    </div>
  );
}

export default App;