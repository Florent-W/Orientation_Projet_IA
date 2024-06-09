import { useEffect, useState } from "react";
import axios from "axios";
import { teams } from "../data/teams.json";

interface MatchPrediction {
  home_team: string;
  away_team: string;
  winner: string;
  prediction_score: number;
  home_score: number;
  away_score: number;
  group: string;
  city: string;
}

const getTeamByCode = (teamName: string) => {
  return teams.find((team) => team.team === teamName)?.country_code.toLowerCase();
};

function Euro() {
  const [predictions, setPredictions] = useState<MatchPrediction[]>([]);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await axios.get("http://localhost:8000/predictions");
        setPredictions(response.data);
      } catch (error) {
        console.error("Error fetching predictions:", error);
      }
    };

    fetchPredictions();
  }, []);

  const predictionsByGroup = predictions.reduce((groups, match) => {
    const group = match.group || "Unknown";
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(match);
    return groups;
  }, {} as { [key: string]: MatchPrediction[] });

  return (
    <div className="min-h-screen w-screen flex flex-col gap-10 justify-center items-center py-10 overflow-auto">
      <h1 className="text-6xl font-bold text-center font-ferveur">Prédictions de l'Euro 2024 ⚽️</h1>
      <div className="max-w-7xl w-full px-4 grid grid-cols-1 md:grid-cols-2 gap-8">
        {Object.keys(predictionsByGroup).map((group) => (
          <div key={group} className="p-6 border-4 border-white rounded-lg">
            <h2 className="text-4xl font-bold text-center mb-6">Groupe {group}</h2>
            {predictionsByGroup[group].map((match, index) => (
              <div key={index} className="w-full border-b-2 border-gray-200 py-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2 w-1/3 justify-end overflow-hidden text-ellipsis">
                    <img
                      src={`https://flagcdn.com/${getTeamByCode(match.home_team)}.svg`}
                      className="w-8 h-5 object-contain"
                      alt={`${match.home_team} flag`}
                    />
                    <span className="text-xl font-bold truncate">{match.home_team}</span>
                  </div>
                  <div className="text-2xl w-1/3 text-center">{match.home_score} - {match.away_score}</div>
                  <div className="flex items-center gap-2 w-1/3 justify-start overflow-hidden text-ellipsis">
                    <span className="text-xl font-bold truncate">{match.away_team}</span>
                    <img
                      src={`https://flagcdn.com/${getTeamByCode(match.away_team)}.svg`}
                      className="w-8 h-5 object-contain"
                      alt={`${match.away_team} flag`}
                    />
                  </div>
                </div>
                <div className="text-center text-lg mt-2">{match.city}</div>
                {match.winner !== "draw" ? (
                  <div className="text-center text-lg">
                    Gagnant : {match.winner} ({match.prediction_score}%)
                  </div>
                ) : (
                  <div className="text-center text-lg">
                    Match nul ({match.prediction_score}%)
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Euro;
