const controls = ["width", "height", "pixel_size", "frames"];

function onSubmit() {
  controls.forEach((input) => {
    let element = document.getElementById(input);
    if (element.value === "") {
      element.value = element.placeholder;
    }
  });
  return true;
}
