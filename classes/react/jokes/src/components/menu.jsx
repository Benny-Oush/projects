function Menu({ setCurrentPage, currentPage }) {
  return (
    <div className="menu-container">
      <div className="menu">
        <button style={{backgroundColor: currentPage === 0 ? "rgb(255, 99, 99)" : " rgb(102, 102, 238)"}} disabled={currentPage === 0} onClick={() => setCurrentPage(0)} className="menu-button">
          Home
        </button>
        <button style={{backgroundColor: currentPage === 1 ? "rgb(255, 99, 99)" : " rgb(102, 102, 238)"}} disabled={currentPage === 1} onClick={() => setCurrentPage(1)} className="menu-button">
          Brows
        </button>
        <button style={{backgroundColor: currentPage === 2 ? "rgb(255, 99, 99)" : " rgb(102, 102, 238)"}} disabled={currentPage === 2} onClick={() => setCurrentPage(2)} className="menu-button">
          Favorites
        </button>
      </div>
    </div>
  );
}

export default Menu;
