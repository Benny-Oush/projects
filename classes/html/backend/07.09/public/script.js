const input = document.getElementById("name-input");
const nameButton = document.getElementById("name-button");

nameButton.addEventListener("click", async () => {
  const name = input.value;
  if (!name) {
    return;
  }
  const response = await fetch("/names", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ name }),
  });
  const obj = await response.json();
  if (!obj.success) {
    console.error(obj.error);
    return;
  }
  const namesResponse = await fetch("/names");
  const namesObj = await namesResponse.json();
  const newList = namesObj.names.map((n) => `<li>${n}</li>`).join("");
  document.querySelector("ol").innerHTML = newList;
  input.value = ''
});
