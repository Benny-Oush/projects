const dogButton = document.getElementById("my-button");
const breedSelection = document.getElementById("breeds");
const container = document.getElementById("cont");

fetch("https://dog.ceo/api/breeds/list/all")
  .then((response) => response.json())
  .then((result) => {
    for (let key in result["message"]) {
      breedSelection.innerHTML += `<option value="${key}">${key}</option>`;
    }
  })
  .catch((error) => console.error("Failed :(", error));

dogButton.addEventListener("click", async () => {
  const breed = breedSelection.value;
  if (breed === "select") {
    return;
  }
  try {
    const response = await fetch(
      `https://dog.ceo/api/breed/${breed}/images/random`,
    );
    const result = await response.json();
    const imageURL = result.message;
    const img = document.createElement("img");
    img.src = imageURL;
    container.appendChild(img);
  } catch (error) {
    console.error("Failed :(", error.message);
  }
});

// function sleep(time) {
//   return new Promise((resolve) => {
//     setTimeout(() => resolve(time), time);
//   });
// }

// async function check() {
//   console.log("Start");
//   const num = await sleep(1000);
//   console.log("Done", num);
// }

// check()

