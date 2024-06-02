import { useState } from "react";
import { teams } from "./data/teams.json";
import { cities } from "./data/all_cities.json";
import { countries } from "./data/all_countries.json";
import { tournaments } from "./data/all_tournaments.json";
import axios from "axios";
import Winner from "./components/Winner";

function App() {
  const [selectedTeam1, setSelectedTeam1] = useState("");
  const [selectedTeam2, setSelectedTeam2] = useState("");
  const [loading, setLoading] = useState(false);
  const [winner, setWinner] = useState<null | {
    team: string;
    country_code: string;
    prediction_score: number;
  }>(null);

  const searchTeamByCode = (code: string) => {
    return teams.find((team) => team.country_code === code)?.team;
  };

  const searchTeameByName = (team: string) => {
    return teams.find((t) => t.team === team);
  };

  const handleSimulate = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    setWinner(null);
    setLoading(true);
    try {
      if (!selectedTeam1 || !selectedTeam2) {
        return alert("Please select two teams");
      }

      const response = await axios.post("http://localhost:8000/predict", {
        team1: searchTeamByCode(selectedTeam1),
        team2: searchTeamByCode(selectedTeam2),
      });

      const data = await response.data;

      const getWinner = searchTeameByName(data.winner as string);

      if (getWinner) {
        setWinner({ ...getWinner, prediction_score: data.prediction_score });
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen flex flex-col gap-10 justify-center items-center py-10 overflow-auto">
      <h1 className="text-6xl font-bold text-center font-ferveur">
        The {selectedTeam2 === "AR" ? "Pessitor 💀" : "Predictor ⚽️"}
      </h1>
      <div className="max-w-xl w-full px-9 pt-14 pb-10 border-4 border-white rounded-2xl flex flex-col gap-14 items-center">
        <div className="flex gap-10 items-center">
          <div className="flex flex-col items-center gap-10">
            <img
              src={
                selectedTeam1.length
                  ? `https://flagcdn.com/${selectedTeam1.toLowerCase()}.svg`
                  : "/no_team.svg"
              }
              className="rounded-xl object-cover w-[200px] aspect-[4.5/3]"
            />

            <select
              className="w-full p-2 border border-white rounded-lg text-black"
              onChange={(e) => setSelectedTeam1(e.target.value)}
            >
              <option value="" disabled selected>
                Select a team
              </option>
              {teams
                .sort((a, b) => a.team.localeCompare(b.team))
                .map((country, index) => (
                  <option key={index} value={country.country_code}>
                    {country.team}
                  </option>
                ))}
            </select>
          </div>

          <div className="h-32 w-[1px] bg-white font-ferveur relative">
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-primary px-4 py-2">
              <span className="animate-pulse text-white text-4xl">VS</span>
            </div>
          </div>

          <div className="flex flex-col items-center gap-10">
            <img
              src={
                selectedTeam2.length
                  ? selectedTeam2 === "AR"
                    ? "/pessi.webp"
                    : `https://flagcdn.com/${selectedTeam2.toLowerCase()}.svg`
                  : "/no_team.svg"
              }
              className="rounded-xl object-cover w-[200px] aspect-[4.5/3]"
            />

            <select
              className="w-full p-2 border border-white rounded-lg text-black"
              onChange={(e) => setSelectedTeam2(e.target.value)}
            >
              <option value="" disabled selected>
                Select a team
              </option>
              {teams
                // .filter((team) => team.country_code !== selectedTeam1)
                .sort((a, b) => a.team.localeCompare(b.team))
                .map((country, index) => (
                  <option key={index} value={country.country_code}>
                    {country.team}
                  </option>
                ))}
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-4 w-full">
        <h1>Paramètres</h1>
        <select
            className="w-full p-2 border border-white rounded-lg text-black"
          >
            <option value="" disabled selected>
              Select a tournament
            </option>
            {tournaments.map((tournament, index) => (
              <option key={index} value={tournament}>
                {tournament}
              </option>
            ))}
          </select>

          <select
            className="w-full p-2 border border-white rounded-lg text-black"
          >
            <option value="" disabled selected>
              Select a city
            </option>
            {cities.map((city, index) => (
              <option key={index} value={city}>
                {city}
              </option>
            ))}
          </select>
          <select
            className="w-full p-2 border border-white rounded-lg text-black"
          >
            <option value="" disabled selected>
              Select a country
            </option>
            {countries.map((country, index) => (
              <option key={index} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>

        <button
          className="bg-[#003DA8] hover:bg-[#043275] text-white px-4 py-4 rounded-lg font-bold uppercase text-xl w-full transition-all duration-300"
          onClick={handleSimulate}
        >
          {!loading ? "Simuler" : "Simulation en cours..."}
        </button>
      </div>

      {winner ? <Winner winner={winner} /> : null}
    </div>
  );
}

export default App;
