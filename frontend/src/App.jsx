import { useState, useEffect } from "react";
function App() {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState("");
  useEffect(() => {
    const mockTeams = [
      { id: 1, name: "Boston Celtics"},
      { id: 2, name: "Los Angeles Lakers"},
      { id: 3, name: "Chicago Bulls"},
      { id: 4, name: "Miami Heat"},
      { id: 5, name: "Golden State Warriors"},
    ];
    setTeams(mockTeams);
  }, []);
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
          <option key = {team.id} value = {team.name}>
            {team.name}
          </option>
        ))}
      </select>
      {selectedTeam !== "" && (
        <p>Chosen team: <strong>{selectedTeam}</strong></p>
      )}
      </div>
  );
}

export default App;