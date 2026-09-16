import React from 'react';

const SkeletonCard = () => {
    return (
        <div className="w-full max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden p-4 mb-4 animate-pulse">
            <div className="border-b pb-2 mb-3 space-y-2">
                <div className="h-6 bg-gray-300 rounded w-1/2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            </div>

            <div className="grid grid-cols-3 gap-3">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="bg-gray-100 p-2 rounded-lg h-16 w-full"></div>
                ))}
            </div>
        </div>
    );
};

export default SkeletonCard;