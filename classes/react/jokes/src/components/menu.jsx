import { useNavigate, useLocation } from "react-router-dom";

function Menu() {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <div className="menu-container">
      <div className="menu">
        <button
          style={{
            backgroundColor:
              location.pathname === "/"
                ? "rgb(255, 99, 99)"
                : " rgb(102, 102, 238)",
          }}
          disabled={location.pathname === "/"}
          onClick={() => {
            navigate("/");
          }}
          className="menu-button"
        >
          Home
        </button>
        <button
          style={{
            backgroundColor:
              location.pathname === "/brows"
                ? "rgb(255, 99, 99)"
                : " rgb(102, 102, 238)",
          }}
          disabled={location.pathname === "/brows"}
          onClick={() => {
            navigate("/brows");
          }}
          className="menu-button"
        >
          Brows
        </button>
        <button
          style={{
            backgroundColor:
              location.pathname === "/favorites"
                ? "rgb(255, 99, 99)"
                : " rgb(102, 102, 238)",
          }}
          disabled={location.pathname === "/favorites"}
          onClick={() => {
            navigate("/favorites");
          }}
          className="menu-button"
        >
          Favorites
        </button>
      </div>
    </div>
  );
}

export default Menu;
