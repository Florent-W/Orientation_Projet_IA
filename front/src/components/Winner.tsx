import type { Winner } from "../../types.ts";

export default function Winner({ winner }: { winner: Winner }) {
  return (
    <div className="flex flex-col gap-10 items-center">
      <img
        src={`https://flagcdn.com/${winner.country_code.toLowerCase()}.svg`}
        className="rounded-xl object-cover w-[200px] aspect-[4.5/3]"
      />
      <div className="flex flex-col gap-5 items-center text-center">
        <h2 className="text-6xl font-bold text-white font-ferveur">
          {winner.team} 🏆
        </h2>
        <p className="text-white text-2xl font-bold">
          <span className="bg-white text-primary px-3">
            {Math.round(winner.prediction_score)}%
          </span>{" "}
          de probabilité de{" "}
          {winner.country_code === "AR" ? "pénalty" : "gagner"}
        </p>
      </div>
    </div>
  );
}
