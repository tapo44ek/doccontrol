import { useEffect } from "react";

function Player({ kp_id }) {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://kinobd.net/js/player_.js";
    script.async = true;
    document.body.appendChild(script);

    return () => {
      // Опционально: удаляем при размонтировании
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div>
      <div data-kinopoisk={kp_id} id="kinobd" />
    </div>
  );
}

export default Player;