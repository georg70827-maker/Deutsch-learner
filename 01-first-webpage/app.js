const form = document.querySelector("#word-form");
const wordInput = document.querySelector("#word-input");
const resultText = document.querySelector("#result-text");
const wordCard = document.querySelector("#word-card");
const resultWord = document.querySelector("#result-word");
const resultMeaning = document.querySelector("#result-meaning");
const resultPartOfSpeech = document.querySelector("#result-part-of-speech");
const resultExample = document.querySelector("#result-example");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const word = wordInput.value.trim();

  if (word === "") {
    wordCard.hidden = true;
    resultText.textContent = "请先输入一个德语单词。";
    return;
  }

  resultText.textContent = "正在查询……";

  try {
    const response = await fetch(
      `http://127.0.0.1:8001/api/lookup?word=${encodeURIComponent(word)}`,
    );
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "查询失败");
    }

    resultText.textContent = "已找到这个单词：";
    resultWord.textContent = data.word;
    resultMeaning.textContent = data.meaning;
    resultPartOfSpeech.textContent = data.partOfSpeech;
    resultExample.textContent = data.example;
    wordCard.hidden = false;
  } catch (error) {
    wordCard.hidden = true;
    resultText.textContent = error.message;
  }
});
