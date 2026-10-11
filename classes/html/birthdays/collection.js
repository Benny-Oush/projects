const collection = [];
let nextId = 1;

function add(name, birthdate) {
  let id = nextId++;
  collection.push({ id, name: name.toLowerCase(), birthdate });
  return id;
}

function read(id) {
  return collection.find((obj) => obj.id == id);
}

function remove(id) {
  const idx = collection.findIndex((obj) => obj.id == id);
  if (idx !== -1) {
    collection.splice(idx, 1)
    return id;
  }
}

function edit(id, name, birthdate) {
  const obj = read(id);
  if (name !== undefined) {
    obj.name = name;
  }
  if (birthdate !== undefined) {
    obj.birthdate = birthdate;
  }
  return obj;
}

function readMany(options) {
  let result = [...collection];
  if (options.name) {
    result = result.filter((obj) => obj.name.includes(options.name));
  }
  if (options.month) {
    result = result.filter(
      (obj) => +obj.birthdate.slice(5, 7) === +options.month,
    );
  }
  if (options.sortBy) {
    const asc = options.sortDir !== "desc";
    const key = options.sortBy;
    result.sort((obj1, obj2) => {
      return obj1[key] < obj2[key] === asc ? -1 : 1;
    });
  }
  return result;
}

module.exports = {
  add,
  read,
  remove,
  edit,
  readMany,
};
