const form = document.querySelector("#word-form");
const wordInput = document.querySelector("#word-input");
const resultText = document.querySelector("#result-text");

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const word = wordInput.value.trim();

  if (word === "") {
    resultText.textContent = "请先输入一个德语单词。";
    return;
  }

  resultText.textContent = `正在查询 “${word}”……（这是第一步的模拟结果）`;
});
