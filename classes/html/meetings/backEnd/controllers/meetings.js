const Meeting = require("../models/meetings.js");

async function read(id) {
  return await Meeting.findById(id);
}

async function readAll() {
  return await Meeting.find();
}

async function add(meeting) {
  const newMeeting = new Meeting(meeting);
  await newMeeting.save();
  return newMeeting;
}

async function edit(id, meeting) {
  const updatedMeeting = await Meeting.findByIdAndUpdate(id, meeting, {
    new: true,
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
