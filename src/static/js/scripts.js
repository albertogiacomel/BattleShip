document.addEventListener('dragstart', function (event) {
  event.preventDefault();
});


function onCellClick(element) {
  var row_index = element.dataset.row;
  var col_index = element.dataset.col;
  if (col_index < 0) {
    col_index = 0;
  }
  document.getElementById('row').value = row_index;
  document.getElementById('col').value = col_index;
  document.getElementById('fire').click();
}

function onOptionClick(element) {
  var optionMenu = document.getElementsByClassName('option_menu');
  optionMenu[0].style.display = true
}

document.ready(function () {
    ("#show-options-menu").click(function () {
      $("#options-menu").show();
    });

    ("#hide-options-menu").click(function () {
      ("#options-menu").hide();
    });
});
