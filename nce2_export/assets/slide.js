(function () {
  const slides = Array.from(document.querySelectorAll(".slide"));
  let index = 0;
  function show(i) {
    if (i < 0 || i >= slides.length) return;
    slides[index].classList.remove("active");
    index = i;
    slides[index].classList.add("active");
  }
  document.addEventListener("keydown", (e) => {
    if (["ArrowRight", "ArrowDown", " ", "PageDown"].includes(e.key)) {
      e.preventDefault();
      show(index + 1);
    } else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(e.key)) {
      e.preventDefault();
      show(index - 1);
    } else if (e.key === "Home") {
      e.preventDefault();
      show(0);
    } else if (e.key === "End") {
      e.preventDefault();
      show(slides.length - 1);
    }
  });
})();
