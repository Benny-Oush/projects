import { useState } from "react";
import "./App.css";

// import { sendNewAmount } from "./utils/api.js";

function ExpenseItem(props) {
  const [editing, setEditing] = useState(false);
  const [newAmount, setNewAmount] = useState(props.amount);
  return (
    <div className="item">
      <span>Category: {props.category}</span>
      <span>Name: {props.name}</span>
      <span>Amount: {props.amount}</span>
      <button onClick={() => setEditing(true)}>Edit amount</button>
      {editing && (
        <div className="editing">
          <span>Enter new amount: </span>
          <input
            value={newAmount}
            onChange={(e) => setNewAmount(Number(e.target.value))}
            type="number"
            min={0}
          />
          <button
            onClick={() => {
              if (newAmount > 0) {
                props.onAmountUpdate(props._id, newAmount);
                setEditing(false);
              }
            }}
          >
            Save
          </button>
          <button
            onClick={() => {
              setNewAmount(props.amount);
              setEditing(false);
            }}
          >
            Cancel
          </button>
        </div>
      )}
      <button onClick={() => props.onDelete(props._id)}>Delete</button>
    </div>
  );
}

function App() {
  // For now
  const [expenses, setExpenses] = useState([
    { amount: 23, name: "Coffee", category: "food", id: 0 },
    { amount: 45, name: "basketball", category: "sport", id: 1 },
  ]);
  const onAmountUpdate = (id, newAmount) => {
    setExpenses(
      expenses.map((item) =>
        item.id === id ? { ...item, amount: newAmount } : item,
      ),
    );
  };

  const onDelete = (id) => {
    setExpenses(expenses.filter((item) => item.id !== id));
  };
  return (
    <div>
      {expenses.map((expense) => (
        <ExpenseItem
          _id={expense.id}
          name={expense.name}
          amount={expense.amount}
          category={expense.category}
          onAmountUpdate={onAmountUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

export default App;
