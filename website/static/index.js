function deleteProperty(propId) {
  fetch("/delete-property", {
    method: "POST",
    body: JSON.stringify({ propId: propId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
