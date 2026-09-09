const nameInput = document.getElementById("name-input");
const ageinput = document.getElementById("age-input");
const addButton = document.getElementById("add-button");

addButton.addEventListener("click", async () => {
  const name = nameInput.value;
  const age = ageinput.value;
  if (!name || !age) {
    return;
  }
  const response = await fetch("/names", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ name, age }),
  });
  const obj = await response.json();
  if (!obj.success) {
    console.error(obj.error);
    return;
  }
  const namesResponse = await fetch("/names");
  const namesObj = await namesResponse.json();
  const newList = namesObj.visitors.map((visitor) => `<tr><td>${visitor.name}</td> <td>${visitor.age}</td></tr>`).join("");
  document.querySelector("table").innerHTML = `<tr><th>Name</th><th>Age</th></tr>` + newList;
  const cells = document.querySelectorAll("td") 
  cells.forEach((cell) => cell.style.borderTop = "1px black solid")
  nameInput.value = "";
  ageinput.value = "";
});
