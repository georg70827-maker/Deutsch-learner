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

  const entry = dictionary[word.toLowerCase()];

  if (entry === undefined) {
    resultText.textContent = `暂时没有找到 “${word}”。`;
    return;
  }

  resultText.textContent = `${word}：${entry.meaning}；${entry.partOfSpeech}。例句：${entry.example}`;
});
