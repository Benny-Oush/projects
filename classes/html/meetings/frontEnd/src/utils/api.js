const baseURL = "http://localhost:3000/meeting/";

async function apiCall(method, url, body, query) {
  let targetURL = baseURL;
  if (query) {
    const params = new URLSearchParams(
      Object.entries(query ?? {}).filter(([, value]) => value !== ""),
    );
    targetURL += `?${params}`;
  } else if (url) {
    targetURL += url;
  }
  const options = { method };
  if (body) {
    options.body = JSON.stringify(body);
    options.headers = {
      "Content-Type": "application/json",
    };
  }
  const response = await fetch(targetURL, options);
  const resultObj = await response.json();
  if (resultObj.success) {
    return resultObj.result;
  } else {
    return resultObj.error;
  }
}

export const readAll = (query) => apiCall("GET", null, null, query);
export const readById = (id) => apiCall("GET", id);
export const add = (meeting) => apiCall("POST", null, meeting);
export const editById = (meeting, id) => apiCall("PATCH", id, meeting);
export const deleteById = (id) => apiCall("DELETE", id);
