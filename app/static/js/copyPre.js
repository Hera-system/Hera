function CopyStdout() {
  var copyText = document.querySelector('#pre-for-copy').innerHTML;
  navigator.clipboard.writeText(copyText);

  var tooltip = document.getElementById("myTooltip");
  tooltip.innerHTML = "Copied!";
}

function ResultCopy() {
  var tooltip = document.getElementById("myTooltip");
  tooltip.innerHTML = "Copy to clipboard";
}
