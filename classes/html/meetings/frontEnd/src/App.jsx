import { useState, useEffect } from "react";
import { readAll, add, editById, deleteById } from "./utils/api.js"; //readById,
import "./App.css";

function getDate(init_date) {
  if (!init_date) {
    return;
  }
  const year = init_date.substring(0, 4);
  const month = init_date.substring(5, 7);
  const day = init_date.substring(8, 10);
  return `${year}-${month}-${day}`;
}

function getDuration(start, end) {
  const duration = (end - start + 24) % 24;
  return duration;
}

function EditMeeting(props) {
  const [date, setDate] = useState(getDate(props.date) || "");
  const [title, setTitle] = useState(props.title || "");
  const [startHour, setStartHour] = useState(props.start_hour || 11);
  const [endHour, setEndHour] = useState(props.end_hour || 12);
  const [isOnline, setIsOnline] = useState(props.is_online || false);
  const [address, setAddress] = useState(props.address || "");
  const [isLoading, setIsLoading] = useState(false);
  const [showErrors, setShowErrors] = useState(false);
  const [savingError, setSavingError] = useState(null);
  const errors =
    !title ||
    !date ||
    (!address && !isOnline) ||
    startHour < 0 ||
    startHour > 23 ||
    endHour < 0 ||
    endHour > 23;
  const saveFunc = () => {
    if (errors) {
      setShowErrors(true);
    } else {
      setIsLoading(true);
      const meeting = {
        title,
        date,
        start_hour: startHour,
        end_hour: endHour,
        is_online: isOnline,
      };
      if (!isOnline) {
        meeting.address = address;
      }
      props.onSave(meeting).catch((error) => {
        setSavingError(error.toString());
        setIsLoading(false);
      });
    }
  };
  return (
    <div className="meeting">
      <div className="line">
        <span>Title: </span>
        <input
          disabled={isLoading}
          style={{ borderColor: showErrors && !title ? "red" : "#02122b" }}
          type="text"
          value={title}
          placeholder={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
      <div className="line">
        <span>Date: </span>
        <input
          disabled={isLoading}
          style={{ borderColor: showErrors && !date ? "red" : "#02122b" }}
          type="date"
          value={date}
          placeholder={date}
          onChange={(e) => setDate(e.target.value)}
        />
      </div>
      <div className="line">
        <span>Start hour: </span>
        <input
          disabled={isLoading}
          style={{
            borderColor:
              showErrors && (startHour < 0 || startHour > 23)
                ? "red"
                : "#02122b",
          }}
          className="hour"
          type="number"
          min={0}
          max={23}
          value={startHour}
          onChange={(e) => {
            setStartHour(e.target.value);
          }}
        />
      </div>
      <div className="line">
        <span>End hour: </span>
        <input
          disabled={isLoading}
          style={{
            borderColor:
              showErrors && (endHour < 0 || endHour > 23) ? "red" : "#02122b",
          }}
          className="hour"
          type="number"
          min={0}
          max={23}
          value={endHour}
          onChange={(e) => {
            setEndHour(e.target.value);
          }}
        />
      </div>
      <div className="line">
        <span>Duration: </span>
        <span>{getDuration(startHour, endHour)} hr(s)</span>
      </div>
      <div className="line">
        <span>Online: </span>
        <input
          disabled={isLoading}
          className="checkbox"
          type="checkbox"
          checked={isOnline}
          onChange={(e) => setIsOnline(e.target.checked)}
        />
      </div>
      {!isOnline && (
        <div className="line">
          <span>Address: </span>
          <input
            disabled={isLoading}
            style={{
              borderColor: showErrors && !address ? "red" : "#02122b",
            }}
            type="text"
            value={address}
            placeholder={address}
            onChange={(e) => setAddress(e.target.value)}
          />
        </div>
      )}
      {showErrors && errors && (
        <span style={{ color: "red" }}>All Fields Must Be Filled</span>
      )}
      {isLoading && <span>Loading...</span>}
      <div className="buttons">
        <button
          style={{
            backgroundColor: isLoading ? "gray" : "",
            color: isLoading ? "black" : "green",
          }}
          disabled={isLoading}
          className="save"
          onClick={saveFunc}
        >
          SAVE
        </button>
        <button
          style={{
            backgroundColor: isLoading ? "gray" : "",
            color: isLoading ? "black" : "red",
          }}
          disabled={isLoading}
          className="cancel"
          onClick={props.cancelButtonClick}
        >
          CANCEL
        </button>
        {savingError && (
          <span style={{ color: "red" }}>Saving Error: {savingError}</span>
        )}
      </div>
    </div>
  );
}

function Filter(props) {
  const [title, setTitle] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [online, setOnline] = useState("");
  const [order, setOrder] = useState("_id");
  const [desc, setDesc] = useState(false);
  const orderOpt = ["title", "date", "_id"];
  useEffect(() => {
    props.onFilter({ title, from, to, online, order, desc });
  }, [title, from, to, online, order, desc]);
  return (
    <div className="filter">
      <div>
        <input
          value={title}
          type="text"
          placeholder="Search by title..."
          onChange={(e) => {
            setTitle(e.target.value);
          }}
        />
        <span>From: </span>
        <input
          value={from}
          type="date"
          onChange={(e) => {
            setFrom(e.target.value);
          }}
        />
        <span>To: </span>
        <input
          value={to}
          type="date"
          onChange={(e) => {
            setTo(e.target.value);
          }}
        />
      </div>
      <div>
        <div>
          <span>Online?</span>
        <select value={online} onChange={(e) => setOnline(e.target.value)}>
          <option value="">choose</option>
          {[true, false].map((bool) =>
            bool ? (
              <option value={bool} key={String(bool)}>
                Only Online
              </option>
            ) : (
              <option value={bool} key={String(bool)}>
                Not Online
              </option>
            ),
          )}
        </select>
          </div>
        <div>
          <span>Sort by: </span>
          <select value={order} onChange={(e) => setOrder(e.target.value)}>
            {orderOpt.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
        <div>
          <span>Order: </span>
          <button onClick={() => setDesc((prev) => !prev)}>
            {desc ? "esc" : "desc"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Meeting(props) {
  const duration = getDuration(props.start_hour, props.end_hour);
  const date = getDate(props.date);
  return (
    <div className="meeting">
      <div className="line">
        <span>Title: </span>
        <span>{props.title || "Empty"}</span>
      </div>
      <div className="line">
        <span>Date: </span>
        <span> {date || "Empty"}</span>
      </div>
      <div className="line">
        <span>
          {props.start_hour.toString().padStart(2, "0") + ":00" || "Empty"}-
          {props.end_hour.toString().padStart(2, "0") + ":00" || "Empty"}
        </span>
        <span>{duration} hr(s)</span>
      </div>
      <div className="line">
        {props.is_online ? (
          <span>Online</span>
        ) : (
          <>
            <span>Address: </span>
            <span>{props.address || "Empty"}</span>
          </>
        )}
      </div>
      <div className="buttons">
        <button
          disabled={props.disabled}
          onClick={() => {
            props.onEdit(props.id);
          }}
          className="edit"
        >
          EDIT
        </button>
        <button
          className="delete"
          disabled={props.disabled}
          onClick={() => props.onDelete(props.id)}
        >
          DELETE
        </button>
      </div>
    </div>
  );
}

function App() {
  const [meetings, setMeetings] = useState([]);
  const [action, setAction] = useState("");
  const [editId, setEditId] = useState(null);
  const addButtonClick = () => {
    setAction("add");
  };
  const cancelButtonClick = () => {
    setAction("");
  };
  const onSave = (meeting) => {
    if (action == "add") {
      return add(meeting)
        .then(readAll)
        .then(setMeetings)
        .then(() => setAction(""));
    } else if (action == "edit") {
      return editById(meeting, editId)
        .then(readAll)
        .then(setMeetings)
        .then(setAction(""));
    }
  };
  const onDelete = (id) => {
    deleteById(id).then(readAll).then(setMeetings);
  };
  const onEdit = (id) => {
    setAction("edit");
    setEditId(id);
  };
  const onFilter = (query) => {
    readAll(query).then(setMeetings);
  };
  return (
    <>
      <Filter onFilter={onFilter} />
      {action == "add" ? (
        <EditMeeting cancelButtonClick={cancelButtonClick} onSave={onSave} />
      ) : (
        <button className="add_button" onClick={addButtonClick} disabled={action != ""}>
          Add new meeting
        </button>
      )}
      <h1>My meetings</h1>
      <div className="cont">
        {meetings.length > 0 ? (
          meetings.map((meeting) =>
            action == "edit" && editId == meeting._id ? (
              <EditMeeting
                date={meeting.date}
                title={meeting.title}
                start_hour={meeting.start_hour}
                end_hour={meeting.end_hour}
                is_online={meeting.is_online}
                address={meeting.address}
                key={meeting._id}
                cancelButtonClick={cancelButtonClick}
                onSave={onSave}
              />
            ) : (
              <Meeting
                key={meeting._id}
                id={meeting._id}
                date={meeting.date}
                title={meeting.title}
                start_hour={meeting.start_hour}
                end_hour={meeting.end_hour}
                is_online={meeting.is_online}
                address={meeting.address}
                disabled={action != ""}
                onDelete={onDelete}
                onEdit={onEdit}
              />
            ),
          )
        ) : (
          <span style={{ color: "red" }}>No meetings found</span>
        )}
      </div>
    </>
  );
}

export default App;
