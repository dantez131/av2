export default function FlyingPlane() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      <div className="plane-container">
        <svg
          width="80"
          height="60"
          viewBox="0 0 80 60"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M40 10 L50 20 L70 18 L65 30 L75 35 L60 35 L50 45 L45 30 L30 30 L25 45 L20 35 L5 35 L15 30 L10 18 L30 20 Z"
            fill="#FFD700"
            stroke="#FFA500"
            strokeWidth="1.5"
            strokeLinejoin="round"
          />
          <circle cx="35" cy="32" r="2" fill="#FFF" />
        </svg>
      </div>
      <style>{`
        .plane-container {
          position: absolute;
          animation: flyPlane 15s linear infinite;
          filter: drop-shadow(0 2px 8px rgba(255, 215, 0, 0.6));
        }

        @keyframes flyPlane {
          0% {
            left: -10%;
            top: 20%;
            transform: rotate(-15deg);
          }
          25% {
            left: 30%;
            top: 10%;
            transform: rotate(-5deg);
          }
          50% {
            left: 60%;
            top: 25%;
            transform: rotate(-20deg);
          }
          75% {
            left: 90%;
            top: 15%;
            transform: rotate(-10deg);
          }
          100% {
            left: 120%;
            top: 30%;
            transform: rotate(-15deg);
          }
        }
      `}</style>
    </div>
  );
}
