// import { useState, useEffect } from 'react'
// import { useState } from "react";
import "./App.css";

function Meeting(props) {
  return (
    <div className="meeting">
      <div className="line">
        <span>Title: </span>
        <span>{props.title || "Empty"}</span>
      </div>
      <div className="line">
        <span>Date: </span>
        <span> {props.date || "Empty"}</span>
      </div>
      <div className="line">
        <span>Start Hour: </span>
        <span>{props.start_hour || "Empty"} </span>
      </div>
      <div className="line">
        <span>End Hour: </span>
        <span>{props.end_hour || "Empty"}</span>
      </div>
      <div className="line">
        <span>Online: </span>
        <span> {props.is_online.toString() || "Empty"}</span>
      </div>
      <div className="line">
        <span>Address: </span>
        <span>{props.address || "Empty"}</span>
      </div>
      <div className='buttons'>
        <button className="delete">DELETE</button>
        <button className="edit">EDIT</button>
      </div>
    </div>
  );
}

function App() {
  return (
    <>
      <Meeting date={"2026-07-22"} title={'Year end'} start_hour={2} end_hour={3} is_online={true} address={"maneger's home"}/>
    </>
  );
}

export default App;
