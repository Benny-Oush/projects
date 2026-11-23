const Meeting = require("../models/meetings.js");

async function read(id) {
  return await Meeting.findById(id);
}

async function readAll(query) {
  if (Object.keys(query).length == 0) {
    return await Meeting.find();
  }
  let filters = {};
  let sort = {
    _id:
      "desc" in query && (query.desc == 'true' || query.desc === true) ? -1 : 1,
  };
  if ("title" in query) {
    const search_regex = new RegExp(query.title, "i");
    filters.title = search_regex;
  }
  if ("from" in query) {
    filters.date = { $gte: new Date(query.from) };
  }
  if ("to" in query) {
    if (!filters.date) {
      filters.date = {};
    }
    filters.date.$lte = new Date(query.to);
  }
  if ("online" in query) {
    filters.is_online = query.online;
  }

  if ("order" in query) {
    sort = {
      [query.order]:
        "desc" in query && (query.desc == 'true' || query.desc === true)
          ? -1
          : 1,
    };
  }
  return await Meeting.find(filters, {}, { sort: sort });
}

async function add(meeting) {
  const newMeeting = new Meeting(meeting);
  await newMeeting.save();
  return newMeeting;
}

async function edit(id, meeting) {
  const updatedMeeting = await Meeting.findByIdAndUpdate(id, meeting, {
    returnDocument: "after",
    runValidators: true,
  });
  return updatedMeeting;
}

async function remove(id) {
  const meeting = await Meeting.findByIdAndDelete(id);
  return meeting;
}

module.exports = {
  read,
  readAll,
  add,
  edit,
  remove,
};
