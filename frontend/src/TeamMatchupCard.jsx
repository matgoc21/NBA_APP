import React from 'react';

const TeamMatchupCard = ({ matchupData }) => {
    if (!matchupData) return null;
    const { win_probability, predicted_winner, point_differential } = matchupData;

    return (
        <div className="w-full max-w-md mx-auto bg-gray-900 text-white rounded-xl shadow-lg p-5">
            <h3 className="text-center text-sm font-medium text-gray-400 uppercase mb-4">
                Analiza Spotkania
            </h3>

            <div className="flex justify-between items-end mb-2">
                <span className="text-2xl font-bold text-green-400">{predicted_winner}</span>
                <span className="text-sm text-gray-300">
                    Przewaga: <strong className="text-white">{point_differential} pkt</strong>
                </span>
            </div>

            {/*Probability bar*/}
            <div className="w-full bg-gray-700 rounded-full h-3 mt-4 overflow-hidden relative">
                <div
                className="bg-green-500 h-3 rounded-full transition-all duration-1000 ease-out"
                style={{width : `${win_probability}%` }}
                ></div>
            </div>
            <div className="text-right mt-1 text-xs text-gray-400">
                Szansa na wygraną: {win_probability}%
            </div>
        </div>
    );
};

export default TeamMatchupCard;