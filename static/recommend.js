$(function () {
  // Button will be disabled until we type anything inside the input field
  const source = document.getElementById("autoComplete");
  const inputHandler = function (e) {
    if (e.target.value == "") {
      $(".movie-button").attr("disabled", true);
    } else {
      $(".movie-button").attr("disabled", false);
    }
  };
  source.addEventListener("input", inputHandler);

  $(".movie-button").on("click", function () {
    var my_api_key = "YOUR_API_KEY";
    var title = $(".movie").val();
    if (title == "") {
      $(".results").css("display", "none");
      $(".fail").css("display", "block");
    } else {
      load_details(my_api_key, title);
    }
  });
});
