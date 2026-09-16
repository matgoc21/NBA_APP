import { useState, useEffect } from "react";
import PlayerPredictionCard from "./PlayerPredictionCard";
import TeamMatchupCard from "./TeamMatchupCard";
import SkeletonCard from "./SkeletonCard";

function App() {
  //states for games
  const [games, setGames] = useState([]);
  const [selectedGameId, setSelectedGameId] = useState("");
  // states for teams and players
  const [selectedTeam, setSelectedTeam] = useState("");
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  // states for ai
  const [predictionResult, setPredictionResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const [matchupResult, setMatchupResult] = useState(null);

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
        const response = await fetch(`http://127.0.0.1:8000/api/teams/${selectedTeam}/players/`);
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
const selectedGameObj = games.find(g => g.id.toString() === selectedGameId.toString());
const selectedPlayerObj = players.find(p => p.id.toString() === selectedPlayer.toString());


const handlePredictClick = async () => {
  setIsLoading(true);
  setPredictionResult(null);
  setMatchupResult(null);
  // Getting opponent id

  const opponentTeamId = selectedTeam.toString() === selectedGameObj.away_team.id.toString() ? selectedGameObj.home_team.id : selectedGameObj.away_team.id;
  try {
    const playerResponse = await fetch('http://127.0.0.1:8000/api/predict-score/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        player_id: selectedPlayer,
        opponent_team_id: opponentTeamId,
        game_id: selectedGameId
      })
    });

    const playerData = await playerResponse.json();
    console.log("Player Prediction Data:", playerData);
    setPredictionResult(playerData);

    const matchupResponse = await fetch('http://127.0.0.1:8000/api/predict-matchup/', {

      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        game_id: selectedGameId
      })
    });
    const teamData = await matchupResponse.json();
    console.log("Matchup Prediction Data:", teamData);
    setMatchupResult(teamData);
  }catch (error){
    console.error("Prediction Error:", error);
  } finally {
    setIsLoading(false);
  }
};

return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <h1>NBA AI Predictor</h1>
      
      {/* Selecting a game*/}
      <h2>1. Pick a game.</h2>
      <select value={selectedGameId} onChange={handleGameChange} style={{ width: '100%', padding: '8px' }}>
        <option value="">-- Pick a game --</option>
        {games.map((game) => (
          <option key={game.id} value={game.id}>
            {game.game_date}: {game.away_team.name} @ {game.home_team.name}
          </option>
        ))}
      </select>

      {/*Seleccting a team*/}
      {selectedGameObj && (
        <div style={{ marginTop: '20px' }}>
          <h2>2. Pick a team</h2>
          <select 
            value={selectedTeam} 
            onChange={(e) => setSelectedTeam(e.target.value)}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="">-- Which team is the player on? --</option>
            {/* Fetching away team */}
            <option value={selectedGameObj.away_team.id}>
              Away Team: {selectedGameObj.away_team.name}
            </option>
            {/* Fetching home team */}
            <option value={selectedGameObj.home_team.id}>
              Home Team: {selectedGameObj.home_team.name}
            </option>
          </select>
        </div>
      )}

      {/* Picking a player (only if there is a team selected) */}
      {selectedTeam && (
        <div style={{ marginTop: '20px' }}>
          <h2>3. Pick a player</h2>
          <select 
            value={selectedPlayer} 
            onChange={(e) => setSelectedPlayer(e.target.value)}
            disabled={players.length === 0}
            style={{ width: '100%', padding: '8px' }}
          >
            <option value="">-- Who do you want to check? --</option>
            {players.map((player) => (
              <option key={player.id} value={player.id}>
                {player.full_name} ({player.position || "No position"})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Prediction summary*/}
      {selectedPlayer && (
        <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f0f8ff', borderRadius: '8px' }}>
          <h3>Prepering to calculate</h3>
          <p>Predictiong stats for a player with ID <strong>{selectedPlayer}</strong>.</p>
          <button 
            onClick={handlePredictClick}
            disabled={isLoading}
            style={{ marginTop: '10px', padding: '10px 20px', cursor: 'pointer' }}
            >
              {isLoading ? "Calculating...": "Start Prediction"}
          </button>
          {/*Skeleton Cards*/}
          <div style={{ marginTop: '20px'}}>
            {isLoading && (
              <>
                <SkeletonCard />
                <SkeletonCard />
              </>
            )}

            {!isLoading && predictionResult && selectedPlayerObj && predictionResult.predictions &&(
              <PlayerPredictionCard
              playerData={{name: selectedPlayerObj.full_name}}
              predictions={predictionResult.predictions}
              />
            )}

            {!isLoading && matchupResult && (
              <TeamMatchupCard
                matchupData={matchupResult}
              />
            )}
            </div>
          {/*Rendering new cards*/}
          <div style={{ marginTop: '20px' }}>
            {predictionResult && selectedPlayerObj && predictionResult.predictions && (
              <PlayerPredictionCard
              playerData={{name: selectedPlayerObj.full_name}}
              predictions={predictionResult.predictions}
              />
            )}
            {matchupResult && (
              <TeamMatchupCard
              matchupData={matchupResult}
              />
            )}
            </div>
        </div>
      )}
    </div>
  );
}

export default App;