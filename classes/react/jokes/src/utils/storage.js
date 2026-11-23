function addId(id) {
  const liked = JSON.parse(localStorage.getItem("liked")) || [];
  if (!liked.includes(id)) {
    liked.push(id);
  }
  localStorage.setItem("liked", JSON.stringify(liked));
}

function removeId(id) {
  const liked = JSON.parse(localStorage.getItem("liked")) || [];
  localStorage.setItem(
    "liked",
    JSON.stringify(liked.filter((list_id) => list_id != id)),
  );
}

export { addId, removeId };
