const form = document.querySelector("#word-form");
const wordInput = document.querySelector("#word-input");
const resultText = document.querySelector("#result-text");
const wordCard = document.querySelector("#word-card");
const resultWord = document.querySelector("#result-word");
const resultMeaning = document.querySelector("#result-meaning");
const resultPartOfSpeech = document.querySelector("#result-part-of-speech");
const resultExample = document.querySelector("#result-example");
let conversationId = null;
let conversationMode = false;

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
    const endpoint = conversationMode
      ? `http://127.0.0.1:8001/api/conversation?session=${encodeURIComponent(conversationId)}&message=${encodeURIComponent(word)}`
      : `http://127.0.0.1:8001/api/agent?message=${encodeURIComponent(word)}`;
    const response = await fetch(endpoint);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "查询失败");
    }

    if (data.result?.error) {
      throw new Error(data.result.error);
    }

    if (data.error) {
      throw new Error(data.error);
    }

    if (conversationMode) {
      resultText.textContent = "餐厅对话继续：";
      resultWord.textContent = "服务员";
      resultMeaning.textContent = "你的回答：" + word;
      resultPartOfSpeech.textContent = "下一句";
      resultExample.textContent = data.reply;
    } else if (data.intent === "grammar") {
      resultText.textContent = "Agent 判断：你想学习语法。";
      resultWord.textContent = data.result.topic;
      resultMeaning.textContent = data.result.explanation;
      resultPartOfSpeech.textContent = "语法讲解";
      resultExample.textContent = data.result.exercise;
    } else if (data.intent === "conversation") {
      resultText.textContent = "Agent 判断：你想练习场景对话。";
      conversationId = data.result.conversation_id;
      conversationMode = true;
      resultWord.textContent = data.result.scene;
      resultMeaning.textContent = data.result.role;
      resultPartOfSpeech.textContent = "对话开场";
      resultExample.textContent = `${data.result.opening} 提示：${data.result.hint}`;
    } else {
      resultText.textContent = "Agent 判断：你想查词。";
      resultWord.textContent = data.result.word || word.split(" ").pop();
      resultMeaning.textContent = data.result.meaning;
      resultPartOfSpeech.textContent = data.result.partOfSpeech;
      resultExample.textContent = data.result.example;
    }
    wordCard.hidden = false;
  } catch (error) {
    wordCard.hidden = true;
    resultText.textContent = error.message;
  }
});
