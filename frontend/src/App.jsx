import { useState, useEffect } from "react";
function App() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState("");
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState("");
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/teams/');
        const data = await response.json();
        setTeams(data);
      } catch (error) {
        console.error("Error fetching teams:", error);
      }
    };
    fetchTeams();
  }, []);

  useEffect( () => {
    if(!selectedTeam) {
      setPlayers([]);
      setSelectedPlayer("");
      return;
    }

    const fetchPlayers = async () => {
      try {
        console.log(`Fetching players for team_id : ${selectedTeam}`);
        const response = await fetch(`http://127.0.0.1:8000/api/teams/${selectedTeam}/players/`);
        const data = await response.json();
        setPlayers(data);
        setSelectedPlayer("");

      } catch (error) {
        console.error("Error fetching players:", error); 
      }
    };
    fetchPlayers();
  }, [selectedTeam]); // This effect runs whenever selectedTeam changes
  return (
    <div>
      <h1>NBA stats prediction </h1>
      <h2> Select a team: </h2>
      <select
        value={selectedTeam}
        onChange={(e) => setSelectedTeam(e.target.value)}
      >
        <option value ="">--Please select a team --</option>
        {teams.map((team) => (
          <option key = {team.id} value = {team.id}>
            {team.name}
          </option>
        ))}
      </select>
     {/* Display players only if a team is selected */}
     { selectedTeam && (
      <>
        <h2> Select a player: </h2>
        <select 
          value={selectedPlayer}
          onChange={(e) => setSelectedPlayer(e.target.value)}
          disabled={players.length === 0} // Disable if no players are available
        >
          <option value="">--Please select a player --</option>
          {players.map((player => (
            <option key={player.id} value={player.id}>
              {player.full_name} ({player.position || "Unknown Position"})
            </option>
          )))}
        </select>
      </>
     )}
      {selectedPlayer && (
        <p>Selected player by id: <strong> {selectedPlayer} </strong></p>
      )}
      </div>
  );
}

export default App;