import React from 'react';

const PlayerPredictionCard = ({ playerData, predictions}) => {
    if (!predictions) return null;

    return (
        <div className="w-full max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden p-4 mb-4">
            <div className="border-b pb-2 mb-3">
                <h2 className="text-xl font-bold text-gray-800">{playerData.name}</h2>
                <p className="text-sm text-gray-500">Przewidywane statystyki</p>
            </div>

            {/*Dynamic grid for mobile devices (3 columns) */}
            <div className="grid grid-cols-3 gap-3 text-center">
                {Object.entries(predictions).map(([statName, value]) => (
                    <div key={statName} className="bg-gray-50 p-2 rounded-lg border border-gray-100">
                        <span className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">
                            {statName}
                        </span>
                        <span className="block text-lg font-black text-blue-600">
                            {value}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PlayerPredictionCard;